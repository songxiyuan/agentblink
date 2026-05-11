#!/usr/bin/env python3
"""Install ESP32 status light hooks for Claude Code."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


INSTALLER = Path(__file__).with_name("install_codex_hooks.py")


def main() -> int:
    sys.argv = [str(INSTALLER), "--target", "claude", *sys.argv[1:]]
    runpy.run_path(str(INSTALLER), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
