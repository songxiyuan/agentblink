#!/usr/bin/env python3
"""Install the ESP32 status light hooks for Codex and Claude Code.

The installer copies the hook scripts into each client's hook directory, merges
the hook configuration, and optionally prepares a local virtualenv with pyserial
for the serial controller.
"""

from __future__ import annotations

import argparse
import json
import shutil
import shlex
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

HOOK_SCRIPTS = (
    ("ai/hooks/status_light.py", "status_light.py"),
    ("ai/hooks/light_idle_monitor.py", "light_idle_monitor.py"),
    ("tools/serial/esp32_light_control.py", "esp32_light_control.py"),
)

CODEX_EVENTS = {
    "SessionStart": None,
    "UserPromptSubmit": None,
    "PreToolUse": "*",
    "PostToolUse": "*",
    "PermissionRequest": "*",
    "Stop": None,
    "SessionEnd": None,
}

CLAUDE_EVENTS = {
    "SessionStart": None,
    "UserPromptSubmit": None,
    "PreToolUse": None,
    "PostToolUse": None,
    "PostToolUseFailure": None,
    "PermissionRequest": None,
    "PermissionDenied": None,
    "Notification": "permission_prompt|idle_prompt|elicitation_dialog",
    "Stop": None,
    "SessionEnd": None,
}


@dataclass(frozen=True)
class Client:
    name: str
    config_dir: Path
    config_name: str
    events: dict[str, str | None]
    log_env: str


def default_clients() -> dict[str, Client]:
    return {
        "codex": Client(
            name="codex",
            config_dir=Path.home() / ".codex",
            config_name="hooks.json",
            events=CODEX_EVENTS,
            log_env="CODEX_LIGHT_LOG=true",
        ),
        "claude": Client(
            name="claude",
            config_dir=Path.home() / ".claude",
            config_name="settings.json",
            events=CLAUDE_EVENTS,
            log_env="CLAUDE_LIGHT_LOG=true",
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install ESP32 status light hooks.")
    parser.add_argument(
        "--target",
        choices=("codex", "claude", "all"),
        default="codex",
        help="Client to install hooks for.",
    )
    parser.add_argument(
        "--codex-dir",
        type=Path,
        default=Path.home() / ".codex",
        help="Codex configuration directory.",
    )
    parser.add_argument(
        "--claude-dir",
        type=Path,
        default=Path.home() / ".claude",
        help="Claude Code configuration directory.",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=REPO_ROOT,
        help="Repository root containing ai/hooks and tools/serial.",
    )
    parser.add_argument(
        "--no-deps",
        action="store_true",
        help="Do not create hook virtualenvs or install pyserial.",
    )
    parser.add_argument(
        "--no-log",
        action="store_true",
        help="Install hook commands without status light log env vars.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without writing files.",
    )
    return parser


def selected_clients(args: argparse.Namespace) -> list[Client]:
    clients = default_clients()
    clients["codex"] = Client(
        name="codex",
        config_dir=args.codex_dir,
        config_name=clients["codex"].config_name,
        events=clients["codex"].events,
        log_env=clients["codex"].log_env,
    )
    clients["claude"] = Client(
        name="claude",
        config_dir=args.claude_dir,
        config_name=clients["claude"].config_name,
        events=clients["claude"].events,
        log_env=clients["claude"].log_env,
    )
    if args.target == "all":
        return [clients["codex"], clients["claude"]]
    return [clients[args.target]]


def copy_hook_scripts(source_dir: Path, hook_dir: Path, dry_run: bool) -> None:
    missing = [source for source, _ in HOOK_SCRIPTS if not (source_dir / source).is_file()]
    if missing:
        raise SystemExit(f"Missing hook script(s) in {source_dir}: {', '.join(missing)}")

    if dry_run:
        for source, destination in HOOK_SCRIPTS:
            print(f"Would copy {source_dir / source} -> {hook_dir / destination}")
        return

    hook_dir.mkdir(parents=True, exist_ok=True)
    for source, name in HOOK_SCRIPTS:
        destination = hook_dir / name
        shutil.copy2(source_dir / source, destination)
        destination.chmod(destination.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print(f"Installed {destination}")


def install_dependencies(hook_dir: Path, dry_run: bool) -> None:
    venv_dir = hook_dir / ".venv"
    python = venv_dir / "bin" / "python"
    pip = venv_dir / "bin" / "pip"

    if dry_run:
        print(f"Would create venv at {venv_dir}")
        print("Would install pyserial into the hook venv")
        return

    if not python.exists():
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        print(f"Created {venv_dir}")

    subprocess.run([str(python), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(pip), "install", "pyserial"], check=True)
    print("Installed pyserial")


def load_hooks_config(path: Path) -> dict:
    if not path.exists():
        return {"hooks": {}}

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise SystemExit(f"{path} must contain a JSON object")
    hooks = data.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise SystemExit(f"{path}: 'hooks' must be a JSON object")
    return data


def hook_command(script_path: Path, log_env: str, enable_log: bool) -> str:
    parts = ["env"]
    if enable_log:
        parts.append(log_env)
    parts.extend(["python3", str(script_path)])
    return " ".join(shlex.quote(part) for part in parts)


def hook_entry(command: str, matcher: str | None) -> dict:
    entry = {
        "hooks": [
            {
                "type": "command",
                "command": command,
                "timeout": 10,
            }
        ]
    }
    if matcher is not None:
        entry["matcher"] = matcher
    return entry


def entry_uses_light_hook(entry: object) -> bool:
    if not isinstance(entry, dict):
        return False
    for hook in entry.get("hooks", []):
        if not isinstance(hook, dict):
            continue
        command = str(hook.get("command", ""))
        if "status_light.py" in command or "codex_light_status.py" in command:
            return True
    return False


def merge_hooks_config(config: dict, command: str, events: dict[str, str | None]) -> dict:
    hooks = config.setdefault("hooks", {})
    for event, matcher in events.items():
        event_entries = hooks.setdefault(event, [])
        if not isinstance(event_entries, list):
            raise SystemExit(f"hooks.{event} must be a JSON array")
        event_entries[:] = [entry for entry in event_entries if not entry_uses_light_hook(entry)]
        event_entries.append(hook_entry(command, matcher))
    return config


def write_hooks_config(path: Path, config: dict, dry_run: bool) -> None:
    rendered = json.dumps(config, indent=2, ensure_ascii=False) + "\n"
    if dry_run:
        print(f"Would write {path}:")
        print(rendered)
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        backup = path.with_suffix(path.suffix + ".bak")
        shutil.copy2(path, backup)
        print(f"Backed up {path} -> {backup}")

    with path.open("w", encoding="utf-8") as file:
        file.write(rendered)
    print(f"Updated {path}")


def install_client(client: Client, source_dir: Path, no_deps: bool, no_log: bool, dry_run: bool) -> None:
    config_dir = client.config_dir.expanduser().resolve()
    hook_dir = config_dir / "hooks"
    config_path = config_dir / client.config_name
    status_script = hook_dir / "status_light.py"

    print(f"Installing {client.name} hooks")
    copy_hook_scripts(source_dir, hook_dir, dry_run)
    if not no_deps:
        install_dependencies(hook_dir, dry_run)

    config = load_hooks_config(config_path)
    command = hook_command(status_script, log_env=client.log_env, enable_log=not no_log)
    merge_hooks_config(config, command, client.events)
    write_hooks_config(config_path, config, dry_run)


def main() -> int:
    args = build_parser().parse_args()
    source_dir = args.source_dir.expanduser().resolve()
    for client in selected_clients(args):
        install_client(client, source_dir, args.no_deps, args.no_log, args.dry_run)

    if args.dry_run:
        print("Dry run complete; no files were changed.")
    else:
        print("Status light hooks are installed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
