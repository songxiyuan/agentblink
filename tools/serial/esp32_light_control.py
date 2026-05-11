#!/usr/bin/env python3
"""Send serial light commands to the ESP32 blink firmware.

Usage:
  python3 tools/serial/esp32_light_control.py --list-ports
  python3 tools/serial/esp32_light_control.py --cache-port chase
  python3 tools/serial/esp32_light_control.py -p /dev/cu.usbserial-0001 solid 0 255 0
  python3 tools/serial/esp32_light_control.py -p /dev/cu.usbserial-0001 interactive

Notes:
  If --port is omitted, the script probes serial ports for ESP32_LIGHT_OK.
  Use --cache-port after flashing the firmware so hooks can reuse the detected
  port from ~/.codex/hooks/light_port.
  Common commands: off, chase, rainbow, yellow, alert, blink, solid R G B,
  speed MS, raw TEXT.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from dataclasses import dataclass

try:
    import serial
    from serial.tools import list_ports
except ImportError:  # pragma: no cover - shown to users at runtime
    serial = None
    list_ports = None


DEFAULT_BAUD = 115200
READ_TIMEOUT = 0.2
PROBE_COMMAND = "probe"
PROBE_RESPONSE = "ESP32_LIGHT_OK"
PROBE_SETTLE_SECONDS = 1.2
PROBE_ATTEMPTS = 3
ESP32_PORT_KEYWORDS = (
    "usbserial",
    "usbmodem",
    "wchusbserial",
    "ch340",
    "ch910",
    "cp210",
    "silicon labs",
    "uart",
)


@dataclass
class PortCandidate:
    device: str
    description: str
    score: int


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Control ESP32 lights over serial.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-p", "--port", help="Serial port. If omitted, the script tries to find the ESP32 automatically")
    parser.add_argument("-b", "--baud", type=int, default=DEFAULT_BAUD, help="Serial baud rate")
    parser.add_argument("--cache-port", action="store_true", help="Remember the detected port for later runs")
    parser.add_argument("--quiet", action="store_true", help="Only print errors")
    parser.add_argument("--no-read", action="store_true", help="Do not read ESP32 response after sending")
    parser.add_argument("--list-ports", action="store_true", help="List available serial ports and exit")

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    for name in ("help", "off", "auto", "chase", "alternate", "rainbow", "yellow", "alert", "on", "blink"):
        subparsers.add_parser(name, help=f"Send '{name}'")

    solid = subparsers.add_parser("solid", help="Set a solid RGB color")
    solid.add_argument("r", type=rgb_value, help="Red value 0-255")
    solid.add_argument("g", type=rgb_value, help="Green value 0-255")
    solid.add_argument("b", type=rgb_value, help="Blue value 0-255")

    speed = subparsers.add_parser("speed", help="Set effect delay in milliseconds")
    speed.add_argument("ms", type=speed_value, help="Delay from 10 to 5000 ms")

    raw = subparsers.add_parser("raw", help="Send a raw command line")
    raw.add_argument("text", nargs="+", help="Raw command text")

    subparsers.add_parser("interactive", help="Start an interactive prompt")
    return parser


def rgb_value(value: str) -> int:
    return ranged_int(value, 0, 255, "RGB value")


def speed_value(value: str) -> int:
    return ranged_int(value, 10, 5000, "speed")


def ranged_int(value: str, minimum: int, maximum: int, name: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{name} must be an integer") from exc
    if parsed < minimum or parsed > maximum:
        raise argparse.ArgumentTypeError(f"{name} must be between {minimum} and {maximum}")
    return parsed


def list_serial_ports() -> None:
    ensure_pyserial()
    ports = list(list_ports.comports())
    if not ports:
        print("No serial ports found.")
        return

    for port in ports:
        description = port.description or "serial device"
        print(f"{port.device}\t{description}")


def port_is_ignored(port) -> bool:
    device = (port.device or "").lower()
    description = (port.description or "").lower()
    text = f"{device} {description}"
    return "bluetooth" in text or "debug-console" in text


def score_serial_port(port) -> int:
    device = (port.device or "").lower()
    description = (port.description or "").lower()
    manufacturer = (port.manufacturer or "").lower()
    hwid = (port.hwid or "").lower()
    text = " ".join((device, description, manufacturer, hwid))

    score = 0
    if device.startswith("/dev/cu."):
        score += 4
    if "bluetooth" in text or "debug-console" in text:
        score -= 100
    for keyword in ESP32_PORT_KEYWORDS:
        if keyword in text:
            score += 10
    if "usb" in text:
        score += 3
    return score


def probe_port(port: str, baud: int) -> bool:
    busy_message = serial_port_busy_message(port)
    if busy_message:
        print(busy_message, file=sys.stderr)
        return False

    try:
        connection = serial.Serial(port=port, baudrate=baud, timeout=READ_TIMEOUT, write_timeout=1)
    except serial.SerialException as exc:
        print(f"Skipping {port}: {exc}", file=sys.stderr)
        return False

    with connection:
        # Opening the port may reset ESP32 boards. Wait for the app to boot,
        # then send the harmless probe command a few times.
        time.sleep(PROBE_SETTLE_SECONDS)
        connection.reset_input_buffer()
        for _ in range(PROBE_ATTEMPTS):
            connection.write((PROBE_COMMAND + "\n").encode("utf-8"))
            connection.flush()
            deadline = time.monotonic() + 0.7
            response = bytearray()
            while time.monotonic() < deadline:
                chunk = connection.read(connection.in_waiting or 1)
                if chunk:
                    response.extend(chunk)
                    if PROBE_RESPONSE.encode("utf-8") in response:
                        return True
            time.sleep(0.1)
    return False


def serial_port_busy_message(port: str) -> str | None:
    if os.name != "posix":
        return None

    paths = [port]
    if "/dev/cu." in port:
        paths.append(port.replace("/dev/cu.", "/dev/tty.", 1))
    elif "/dev/tty." in port:
        paths.append(port.replace("/dev/tty.", "/dev/cu.", 1))

    for path in paths:
        try:
            result = subprocess.run(
                ["lsof", path],
                check=False,
                capture_output=True,
                text=True,
                timeout=1,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if result.returncode == 0:
            lines = [line for line in result.stdout.splitlines() if line.strip()]
            owner = lines[1].split(None, 2)[:2] if len(lines) > 1 else []
            process = " ".join(owner) if owner else "another process"
            return f"Skipping {port}: serial port is busy ({process}). Close ESP-IDF monitor or other serial tools."
    return None


def find_esp32_port(baud: int, quiet: bool = False) -> str:
    ensure_pyserial()
    ports = [port for port in list_ports.comports() if not port_is_ignored(port)]
    candidates = [
        PortCandidate(
            device=port.device,
            description=port.description or "serial device",
            score=score_serial_port(port),
        )
        for port in ports
    ]
    candidates.sort(key=lambda candidate: candidate.score, reverse=True)

    if not candidates:
        print("Could not find any serial ports to probe. Plug in the board or use --list-ports.", file=sys.stderr)
        raise SystemExit(2)

    for candidate in candidates:
        if not quiet:
            print(f"Probing {candidate.device} ({candidate.description})...")
        if probe_port(candidate.device, baud):
            if not quiet:
                print(f"Auto-selected ESP32 serial port: {candidate.device}")
            return candidate.device

    print(f"No ESP32 responded with {PROBE_RESPONSE!r}.", file=sys.stderr)
    print("Make sure the latest firmware is flashed, or specify the port with --port.", file=sys.stderr)
    raise SystemExit(2)


def ensure_pyserial() -> None:
    if serial is None:
        print("pyserial is required. Install it with: python3 -m pip install pyserial", file=sys.stderr)
        raise SystemExit(2)


def command_text(args: argparse.Namespace) -> str | None:
    if args.command in {"help", "off", "auto", "chase", "alternate", "rainbow", "yellow", "alert", "on", "blink"}:
        return args.command
    if args.command == "solid":
        return f"solid {args.r} {args.g} {args.b}"
    if args.command == "speed":
        return f"speed {args.ms}"
    if args.command == "raw":
        return " ".join(args.text)
    return None


def open_serial(port: str, baud: int) -> serial.Serial:
    ensure_pyserial()
    try:
        connection = serial.Serial(port=port, baudrate=baud, timeout=READ_TIMEOUT, write_timeout=1)
    except serial.SerialException as exc:
        print(f"Failed to open serial port {port}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    # Some USB serial adapters reset the ESP32 when the port opens.
    time.sleep(0.8)
    connection.reset_input_buffer()
    return connection


def send_command(connection: serial.Serial, text: str, read_response: bool, quiet: bool = False) -> None:
    line = text.strip()
    if not line:
        return

    connection.write((line + "\n").encode("utf-8"))
    connection.flush()
    if not quiet:
        print(f"> {line}")

    if read_response:
        time.sleep(0.1)
        response = connection.read(connection.in_waiting or 256)
        if response and not quiet:
            print(response.decode("utf-8", errors="replace").rstrip())


def interactive(connection: serial.Serial, read_response: bool, quiet: bool = False) -> None:
    print("Interactive mode. Type ESP32 commands, or 'quit'/'exit' to leave.")
    while True:
        try:
            line = input("esp32> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if line.strip().lower() in {"quit", "exit"}:
            return
        send_command(connection, line, read_response, quiet=quiet)


def cache_path() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "light_port")


def read_cached_port() -> str | None:
    try:
        with open(cache_path(), "r", encoding="utf-8") as file:
            port = file.read().strip()
    except OSError:
        return None
    if port and os.path.exists(port):
        return port
    return None


def write_cached_port(port: str) -> None:
    try:
        os.makedirs(os.path.dirname(cache_path()), exist_ok=True)
        with open(cache_path(), "w", encoding="utf-8") as file:
            file.write(port + "\n")
    except OSError:
        pass


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.list_ports:
        list_serial_ports()
        return 0

    if args.command is None:
        parser.print_help()
        return 2

    port = args.port or read_cached_port() or find_esp32_port(args.baud, quiet=args.quiet)
    if args.cache_port:
        write_cached_port(port)

    connection = open_serial(port, args.baud)
    with connection:
        if args.command == "interactive":
            interactive(connection, read_response=not args.no_read, quiet=args.quiet)
        else:
            text = command_text(args)
            if text is None:
                parser.error("unknown command")
            send_command(connection, text, read_response=not args.no_read, quiet=args.quiet)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
