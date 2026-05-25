#!/usr/bin/env python3
"""Run ESP32 light controller commands from an event configuration file.

Examples:
  python3 tools/serial/esp32_event_control.py --tool codex PermissionRequest
  printf '%s' '{"hook_event_name":"PermissionRequest"}' | python3 tools/serial/esp32_event_control.py --stdin
  python3 tools/serial/esp32_event_control.py --tool claude_code --config my_events.json UserPromptSubmit

The config maps tool names to event names to esp32_light_control.py arguments.
For example: config["codex"]["PermissionRequest"].
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG = SCRIPT_DIR / "esp32_event_control.json"
DEFAULT_CONTROL_SCRIPT = SCRIPT_DIR / "esp32_light_control.py"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Map an event name to ESP32 light/buzzer/vibration commands.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("event", nargs="?", help="Event name, for example PermissionRequest")
    parser.add_argument("--tool", default="codex", help="Tool profile in the config, for example codex or claude_code")
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="JSON event mapping file",
    )
    parser.add_argument(
        "--control-script",
        type=Path,
        default=DEFAULT_CONTROL_SCRIPT,
        help="Path to esp32_light_control.py",
    )
    parser.add_argument("-p", "--port", help="Serial port passed to esp32_light_control.py")
    parser.add_argument("-b", "--baud", type=int, help="Serial baud rate passed to esp32_light_control.py")
    parser.add_argument("--cache-port", action="store_true", help="Ask esp32_light_control.py to cache the detected port")
    parser.add_argument("--quiet", action="store_true", help="Suppress normal output")
    parser.add_argument("--no-read", action="store_true", help="Do not read ESP32 response after sending")
    parser.add_argument("--stdin", action="store_true", help="Read a hook JSON payload from stdin")
    parser.add_argument("--dry-run", action="store_true", help="Print the resolved command without sending it")
    parser.add_argument("--list-events", action="store_true", help="List configured events and exit")
    return parser


def load_config(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except OSError as exc:
        raise SystemExit(f"Failed to read config {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Failed to parse config {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise SystemExit(f"{path} must contain a JSON object")
    for tool_name, events in data.items():
        if not isinstance(tool_name, str) or not tool_name:
            raise SystemExit(f"{path}: tool names must be non-empty strings")
        if not isinstance(events, dict):
            raise SystemExit(f"{path}: tool profile {tool_name!r} must be a JSON object")
    return data


def payload_from_stdin() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Failed to parse stdin JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit("stdin JSON must be an object")
    return payload


def event_from_payload(payload: dict[str, Any]) -> str | None:
    event = payload.get("hook_event_name") or payload.get("event") or payload.get("name")
    return str(event) if event else None


def tool_from_payload(payload: dict[str, Any], fallback: str) -> str:
    tool = payload.get("tool") or payload.get("client") or payload.get("app") or payload.get("source")
    return normalize_tool_name(str(tool)) if tool else fallback


def normalize_tool_name(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def normalize_command(entry: object, config_path: Path) -> list[str]:
    if isinstance(entry, list):
        command: list[str] | None = entry
    elif isinstance(entry, str):
        command = entry.split()
    elif isinstance(entry, dict):
        command = entry.get("command")
    else:
        command = None

    if not isinstance(command, list) or not command:
        raise SystemExit(f"{config_path}: event entry must define a non-empty command list")
    if not all(isinstance(part, (str, int, float)) for part in command):
        raise SystemExit(f"{config_path}: command values must be strings or numbers")
    return [str(part) for part in command]


def command_lines_for_entry(entry: object, config_path: Path) -> list[str]:
    if not isinstance(entry, dict):
        return [" ".join(normalize_command(entry, config_path))]

    if "command" in entry:
        return [" ".join(normalize_command(entry, config_path))]

    command_lines = []
    for section in ("light", "buzzer", "vibration"):
        section_entry = entry.get(section)
        if section_entry is None:
            continue
        command_lines.append(" ".join(normalize_command(section_entry, config_path)))

    if not command_lines:
        raise SystemExit(
            f"{config_path}: event entry must define command, light, buzzer, or vibration"
        )
    return command_lines


def command_lines_for_event(config: dict[str, Any], tool: str, event: str, config_path: Path) -> list[str]:
    events = config.get(tool)
    if not isinstance(events, dict):
        available = ", ".join(sorted(config)) or "none"
        raise SystemExit(f"No tool profile {tool!r} in {config_path}. Available: {available}")
    entry = events.get(event)
    if entry is None:
        raise SystemExit(f"No command configured for tool {tool!r}, event {event!r}")
    return command_lines_for_entry(entry, config_path)


def list_events(config: dict[str, Any]) -> None:
    for tool in sorted(config):
        events = config[tool]
        if not isinstance(events, dict):
            continue
        for event in sorted(events):
            command_lines = command_lines_for_entry(events[event], DEFAULT_CONFIG)
            print(f"{tool}\t{event}\t{'; '.join(command_lines)}")


def control_args(args: argparse.Namespace, command_lines: list[str]) -> list[str]:
    control_script = args.control_script.resolve()
    result = [sys.executable, str(control_script)]
    if args.port:
        result.extend(["--port", args.port])
    if args.baud is not None:
        result.extend(["--baud", str(args.baud)])
    if args.cache_port:
        result.append("--cache-port")
    if args.quiet:
        result.append("--quiet")
    if args.no_read:
        result.append("--no-read")
    for command_line in command_lines:
        result.extend(["--command-line", command_line])
    return result


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    config_path = args.config.resolve()
    config = load_config(config_path)

    if args.list_events:
        list_events(config)
        return 0

    if args.stdin:
        payload = payload_from_stdin()
        event = event_from_payload(payload)
        tool = tool_from_payload(payload, normalize_tool_name(args.tool))
    else:
        event = args.event
        tool = normalize_tool_name(args.tool)
    if not event:
        parser.error("event is required unless --stdin provides hook_event_name")

    command_lines = command_lines_for_event(config, tool, event, config_path)
    invocation = control_args(args, command_lines)
    if args.dry_run:
        print(" ".join(shlex.quote(part) for part in invocation))
        return 0

    try:
        return subprocess.run(invocation, check=False).returncode
    except OSError as exc:
        raise SystemExit(f"Failed to run {args.control_script}: {exc}") from exc


if __name__ == "__main__":
    raise SystemExit(main())
