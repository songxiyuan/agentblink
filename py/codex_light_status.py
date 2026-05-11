#!/usr/bin/env python3
"""Map Codex lifecycle hook events to the ESP32 light controller.

Usage:
  Codex runs this script from ~/.codex/hooks.json and passes a hook JSON payload
  on stdin. Keep the hook command synchronous; Codex CLI 0.130.0-alpha.5 reports
  that async hooks are not supported yet.

Manual test:
  printf '%s' '{"hook_event_name":"UserPromptSubmit"}' | \
    CODEX_LIGHT_LOG=true python3 codex_light_status.py
"""

from __future__ import annotations

import json
import logging
import os
import signal
import subprocess
import sys


HOOK_DIR = os.path.dirname(os.path.abspath(__file__))

# Configure logging
LOG_ENABLED = os.getenv("CODEX_LIGHT_LOG", "false").lower() == "true"
if LOG_ENABLED:
    log_file = os.path.join(HOOK_DIR, "codex_light_status.log")
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
else:
    logging.basicConfig(level=logging.CRITICAL)  # Disable all logs

logger = logging.getLogger(__name__)


CONTROL_SCRIPT = os.path.join(HOOK_DIR, "esp32_light_control.py")
IDLE_MONITOR_SCRIPT = os.path.join(HOOK_DIR, "light_idle_monitor.py")
IDLE_MONITOR_PID_FILE = os.path.join(HOOK_DIR, "light_idle_monitor.pid")
PYTHON_CANDIDATES = (
    os.path.join(HOOK_DIR, ".venv", "bin", "python"),
    sys.executable,
)
PYTHON = next((path for path in PYTHON_CANDIDATES if os.path.exists(path)), sys.executable)


def read_hook_input() -> dict:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        logger.info(f"Read hook input: {payload}")
        return payload
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse hook input JSON: {e}")
        return {}


def send_light_command(*command: str) -> None:
    logger.info(f"Sending light command: {command}")
    if command != ("solid", "0", "255", "0"):
        stop_idle_monitor()

    args = [
        PYTHON,
        CONTROL_SCRIPT,
        "--quiet",
        "--no-read",
        "--cache-port",
        *command,
    ]
    try:
        result = subprocess.run(
            args,
            cwd=HOOK_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=8,
            check=False,
        )
        logger.info(f"Light command executed with return code: {result.returncode}")
    except subprocess.TimeoutExpired:
        logger.error("Light command timed out")
    except Exception as e:
        logger.error(f"Failed to send light command: {e}")


def start_idle_monitor() -> None:
    logger.info("Starting idle monitor")
    stop_idle_monitor()
    process = subprocess.Popen(
        [PYTHON, IDLE_MONITOR_SCRIPT],
        cwd=HOOK_DIR,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    try:
        with open(IDLE_MONITOR_PID_FILE, "w", encoding="utf-8") as file:
            file.write(str(process.pid))
        logger.info(f"Idle monitor started with PID: {process.pid}")
    except OSError as e:
        logger.error(f"Failed to write PID file: {e}")


def stop_idle_monitor() -> None:
    logger.info("Stopping idle monitor")
    try:
        with open(IDLE_MONITOR_PID_FILE, "r", encoding="utf-8") as file:
            pid = int(file.read().strip() or "0")
    except (OSError, ValueError) as e:
        logger.warning(f"Failed to read PID file: {e}")
        return

    if pid > 0:
        try:
            os.kill(pid, signal.SIGTERM)
            logger.info(f"Sent SIGTERM to idle monitor PID: {pid}")
        except OSError as e:
            logger.warning(f"Failed to kill process {pid}: {e}")

    try:
        os.unlink(IDLE_MONITOR_PID_FILE)
        logger.info("Removed PID file")
    except OSError as e:
        logger.warning(f"Failed to remove PID file: {e}")


def stop_action(payload: dict) -> tuple[str, ...]:
    logger.info("Processing stop action")
    if stop_was_interrupted(payload):
        logger.info("Stop was interrupted, turning off lights")
        return ("off",)

    if waiting_for_user_input(payload):
        logger.info("Waiting for popup permission or selection, setting yellow light")
        return ("yellow",)

    logger.info("Normal stop, setting green solid light")
    return ("solid", "0", "255", "0")


def waiting_for_user_input(payload: dict) -> bool:
    logger.debug("Checking if waiting for user input")

    event = str(payload.get("hook_event_name") or "").lower()
    if event in {
        "permissionrequest",
        "permission_request",
        "approvalrequested",
        "approval_requested",
        "approval-requested",
    }:
        logger.info("Found popup permission event")
        return True

    tool_name = str(payload.get("tool_name") or "").lower()
    tool_parts = tool_name.replace("-", "_").replace(".", "_").split("_")
    if tool_name.replace("-", "_").endswith("request_user_input") or tool_parts[-3:] == [
        "request",
        "user",
        "input",
    ]:
        logger.info("Found popup user input tool call")
        return True

    logger.debug("No popup permission or selection request found")
    return False


def stop_was_interrupted(payload: dict) -> bool:
    logger.debug("Checking if stop was interrupted")
    status_text = json.dumps(payload, ensure_ascii=False).lower()
    interrupted_markers = (
        "abort",
        "aborted",
        "cancel",
        "cancelled",
        "canceled",
        "interrupt",
        "interrupted",
        "stop_requested",
        "user_stopped",
        "turn_aborted",
    )
    if any(marker in status_text for marker in interrupted_markers):
        logger.info("Found interruption markers in payload")
        return True

    transcript_path = payload.get("transcript_path")
    turn_id = payload.get("turn_id")
    if transcript_path and turn_id:
        logger.debug(f"Checking transcript file for interruption: {transcript_path} for turn_id: {turn_id}")
        try:
            with open(transcript_path, "r", encoding="utf-8") as file:
                for line in file:
                    lowered = line.lower()
                    if turn_id in line and ("turn_aborted" in lowered or "interrupted" in lowered):
                        logger.info("Found interruption markers in transcript")
                        return True
        except OSError as e:
            logger.warning(f"Failed to read transcript file: {e}")

    logger.debug("No interruption markers found")
    return False


def command_for_event(payload: dict) -> tuple[str, ...]:
    event = payload.get("hook_event_name")
    logger.info(f"Processing event: {event}")
    if event == "SessionStart":
        command = ("off",)
    elif event == "UserPromptSubmit":
        command = ("chase",)
    elif event == "PreToolUse":
        if waiting_for_user_input(payload):
            command = ("yellow",)
        else:
            command = ("chase",)
    elif event == "PostToolUse":
        if waiting_for_user_input(payload):
            command = ("yellow",)
        else:
            command = ("chase",)
    elif event == "PermissionRequest":
        command = ("yellow",)
    elif event in ("Stop", "SessionEnd"):
        command = stop_action(payload)
    else:
        command = ("off",)
    logger.info(f"Command for event {event}: {command}")
    return command


def main() -> int:
    logger.info("Starting codex_light_status script")
    payload = read_hook_input()
    try:
        command = command_for_event(payload)
        send_light_command(*command)
        if command == ("solid", "0", "255", "0"):
            start_idle_monitor()
        logger.info("Script completed successfully")
    except Exception as e:
        logger.error(f"Exception in main: {e}")
        pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
