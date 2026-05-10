#!/usr/bin/env python3
"""Turn off the ESP32 status light when user input resumes after green."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import time


HOOK_DIR = os.path.dirname(os.path.abspath(__file__))
CONTROL_SCRIPT = os.path.join(HOOK_DIR, "esp32_light_control.py")
PYTHON = os.path.join(HOOK_DIR, ".venv", "bin", "python")
PID_FILE = os.path.join(HOOK_DIR, "light_idle_monitor.pid")
IDLE_RE = re.compile(r'"HIDIdleTime"\s=\s(\d+)')


def current_idle_ms() -> int | None:
    try:
        output = subprocess.check_output(["ioreg", "-c", "IOHIDSystem"], text=True, timeout=1)
    except (OSError, subprocess.SubprocessError):
        return None

    match = IDLE_RE.search(output)
    if not match:
        return None
    return int(match.group(1)) // 1_000_000


def turn_off() -> None:
    python = PYTHON if os.path.exists(PYTHON) else sys.executable
    subprocess.run(
        [python, CONTROL_SCRIPT, "--quiet", "--no-read", "--cache-port", "off"],
        cwd=HOOK_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=8,
        check=False,
    )


def remove_pid_file() -> None:
    try:
        if os.path.exists(PID_FILE):
            with open(PID_FILE, "r", encoding="utf-8") as file:
                pid = int(file.read().strip() or "0")
            if pid == os.getpid():
                os.unlink(PID_FILE)
    except (OSError, ValueError):
        pass


def main() -> int:
    # Give the hook and serial writes a moment to settle before arming movement detection.
    time.sleep(1.0)

    deadline = time.monotonic() + 300
    while time.monotonic() < deadline:
        idle_ms = current_idle_ms()
        if idle_ms is not None and idle_ms < 350:
            turn_off()
            break
        time.sleep(0.25)

    remove_pid_file()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
