#!/usr/bin/env python3
"""Build the single-file ESP32 control executable."""

from __future__ import annotations

import argparse
import shutil
import stat
import sys
import zipapp
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SERIAL_DIR = REPO_ROOT / "tools" / "serial"
DEFAULT_OUTPUT = REPO_ROOT / "dist" / "esp32-control"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the ESP32 control zipapp executable.")
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT, help="Output executable path")
    parser.add_argument(
        "--python",
        default="/usr/bin/env python3",
        help="Shebang interpreter stored in the executable",
    )
    return parser


def copy_required_sources(build_dir: Path) -> None:
    package_dir = build_dir / "tools" / "serial"
    package_dir.mkdir(parents=True)
    (build_dir / "tools" / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "__init__.py").write_text("", encoding="utf-8")

    for name in (
        "esp32_light_control.py",
        "esp32_event_control.py",
        "esp32_event_config_server.py",
        "esp32_event_control.json",
    ):
        shutil.copy2(SERIAL_DIR / name, package_dir / name)

    shutil.copy2(SERIAL_DIR / "esp32_bundle_launcher.py", build_dir / "__main__.py")


def copy_pyserial(build_dir: Path) -> None:
    candidates = [
        REPO_ROOT / ".venv" / "lib",
        Path(sys.prefix) / "lib",
    ]
    for base in candidates:
        for serial_dir in base.glob("python*/site-packages/serial"):
            if serial_dir.is_dir():
                shutil.copytree(serial_dir, build_dir / "serial")
                return
    raise SystemExit("Could not find pyserial package. Install it in .venv or the active Python environment.")


def main() -> int:
    args = build_parser().parse_args()
    output = args.output.resolve()
    build_dir = REPO_ROOT / "build" / "esp32-control-zipapp"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)

    copy_required_sources(build_dir)
    copy_pyserial(build_dir)

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    zipapp.create_archive(build_dir, target=output, interpreter=args.python, compressed=True)
    output.chmod(output.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
