#!/usr/bin/env python3
"""Run ESP32 light controller commands from an event configuration file.

Examples:
  python3 tools/serial/esp32_event_control.py PermissionRequest
  printf '%s' '{"hook_event_name":"PermissionRequest"}' | python3 tools/serial/esp32_event_control.py --stdin
  python3 tools/serial/esp32_event_control.py --config my_events.json UserPromptSubmit

The config maps event names to esp32_light_control.py arguments. The default
PermissionRequest mapping explicitly sends a yellow breathing light command,
a short buzzer beep command, and a short vibration command.
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
    events = data.get("events", {})
    if not isinstance(events, dict):
        raise SystemExit(f"{path}: 'events' must be a JSON object")
    return data


def event_from_stdin() -> str | None:
    raw = sys.stdin.read()
    if not raw.strip():
        return None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Failed to parse stdin JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit("stdin JSON must be an object")
    event = payload.get("hook_event_name") or payload.get("event") or payload.get("name")
    return str(event) if event else None


def normalize_command(entry: object, config_path: Path) -> list[str]:
    if isinstance(entry, list):
        command = entry
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


def command_lines_for_event(config: dict[str, Any], event: str, config_path: Path) -> list[str]:
    events = config.get("events", {})
    entry = events.get(event)
    if entry is None:
        entry = config.get("default")
    if entry is None:
        raise SystemExit(f"No command configured for event {event!r}, and no default is set")
    return command_lines_for_entry(entry, config_path)


def list_events(config: dict[str, Any]) -> None:
    events = config.get("events", {})
    for event in sorted(events):
        entry = events[event]
        command_lines = command_lines_for_entry(entry, DEFAULT_CONFIG)
        print(f"{event}\t{'; '.join(command_lines)}")


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

    event = event_from_stdin() if args.stdin else args.event
    if not event:
        parser.error("event is required unless --stdin provides hook_event_name")

    command_lines = command_lines_for_event(config, event, config_path)
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
