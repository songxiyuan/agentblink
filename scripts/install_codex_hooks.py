#!/usr/bin/env python3
"""Install the ESP32 Codex status light hooks.

The installer copies the hook scripts into ~/.codex/hooks, merges the Codex
hook configuration into ~/.codex/hooks.json, and optionally prepares a local
virtualenv with pyserial for the serial controller.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import shlex
import stat
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

HOOK_EVENTS = {
    "SessionStart": None,
    "UserPromptSubmit": None,
    "PreToolUse": "*",
    "PostToolUse": "*",
    "PermissionRequest": "*",
    "Stop": None,
    "SessionEnd": None,
}
HOOK_SCRIPTS = (
    ("codex/hooks/codex_light_status.py", "codex_light_status.py"),
    ("codex/hooks/light_idle_monitor.py", "light_idle_monitor.py"),
    ("tools/serial/esp32_light_control.py", "esp32_light_control.py"),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install ESP32 status light hooks for Codex.")
    parser.add_argument(
        "--codex-dir",
        type=Path,
        default=Path.home() / ".codex",
        help="Codex configuration directory.",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=REPO_ROOT,
        help="Repository root containing codex/hooks and tools/serial.",
    )
    parser.add_argument(
        "--no-deps",
        action="store_true",
        help="Do not create a hook virtualenv or install pyserial.",
    )
    parser.add_argument(
        "--no-log",
        action="store_true",
        help="Install hook commands without CODEX_LIGHT_LOG=true.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without writing files.",
    )
    return parser


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


def hook_command(script_path: Path, enable_log: bool) -> str:
    parts = ["env"]
    if enable_log:
        parts.append("CODEX_LIGHT_LOG=true")
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
        if "codex_light_status.py" in str(hook.get("command", "")):
            return True
    return False


def merge_hooks_config(config: dict, command: str) -> dict:
    hooks = config.setdefault("hooks", {})
    for event, matcher in HOOK_EVENTS.items():
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


def main() -> int:
    args = build_parser().parse_args()
    codex_dir = args.codex_dir.expanduser().resolve()
    source_dir = args.source_dir.expanduser().resolve()
    hook_dir = codex_dir / "hooks"
    hooks_json = codex_dir / "hooks.json"
    status_script = hook_dir / "codex_light_status.py"

    copy_hook_scripts(source_dir, hook_dir, args.dry_run)
    if not args.no_deps:
        install_dependencies(hook_dir, args.dry_run)

    config = load_hooks_config(hooks_json)
    command = hook_command(status_script, enable_log=not args.no_log)
    merge_hooks_config(config, command)
    write_hooks_config(hooks_json, config, args.dry_run)

    if args.dry_run:
        print("Dry run complete; no files were changed.")
    else:
        print("Codex status light hooks are installed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
