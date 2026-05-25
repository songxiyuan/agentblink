#!/usr/bin/env python3
"""Unified launcher used by the ESP32 control zipapp."""

from __future__ import annotations

import importlib.resources
import runpy
import sys
from pathlib import Path


CONFIG_NAME = "esp32_event_control.json"


def bundle_path() -> Path:
    return Path(sys.argv[0]).resolve()


def sidecar_config_path() -> Path:
    return bundle_path().with_name(CONFIG_NAME)


def ensure_sidecar_config() -> Path:
    path = sidecar_config_path()
    if not path.exists():
        text = importlib.resources.files("tools.serial").joinpath(CONFIG_NAME).read_text(encoding="utf-8")
        path.write_text(text, encoding="utf-8")
    return path


def has_option(args: list[str], *names: str) -> bool:
    return any(arg == name or arg.startswith(name + "=") for arg in args for name in names)


def run_module(module: str, args: list[str]) -> None:
    old_argv = sys.argv[:]
    sys.argv = [module.rsplit(".", 1)[-1] + ".py", *args]
    try:
        runpy.run_module(module, run_name="__main__")
    finally:
        sys.argv = old_argv


def event_args(args: list[str]) -> list[str]:
    result = list(args)
    if not has_option(result, "--config", "-c"):
        result = ["--config", str(ensure_sidecar_config()), *result]
    if not has_option(result, "--control-script"):
        result = ["--control-script", str(bundle_path()), *result]
    return result


def server_args(args: list[str]) -> list[str]:
    result = list(args)
    if not has_option(result, "--config"):
        result = ["--config", str(ensure_sidecar_config()), *result]
    return result


def print_help() -> None:
    print(
        """ESP32 control bundle

Usage:
  esp32-control light [esp32_light_control.py args...]
  esp32-control event [esp32_event_control.py args...]
  esp32-control config-server [esp32_event_config_server.py args...]

Shortcuts:
  esp32-control [light args...]        Defaults to the light command.
  esp32-control server [args...]       Alias for config-server.

Examples:
  esp32-control rainbow
  esp32-control beep 2000 200
  esp32-control event --tool codex PermissionRequest
  esp32-control config-server --port 8765
"""
    )


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in {"-h", "--help", "help"}:
        print_help()
        return

    command = args[0]
    rest = args[1:]
    if command == "light":
        run_module("tools.serial.esp32_light_control", rest)
    elif command == "event":
        run_module("tools.serial.esp32_event_control", event_args(rest))
    elif command in {"config-server", "server"}:
        run_module("tools.serial.esp32_event_config_server", server_args(rest))
    else:
        run_module("tools.serial.esp32_light_control", args)


if __name__ == "__main__":
    main()
