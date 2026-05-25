# agentblink

Visual feedback for AI coding assistants through ESP32-based status lights.

## Features

- **AI Tool Integration** - Automatic status lights for Codex and Claude Code
- **Multiple LED Effects** - Chase, rainbow, breathing, solid colors, and more
- **Audio & Haptic Feedback** - Buzzer and vibration motor support
- **Easy Installation** - Global hooks for seamless AI tool integration
- **Cross-Platform** - Works on macOS, Linux, and Windows (WSL)
- **Modular Design** - Use components independently or together

## Quick Start

### For AI Tool Users (5 minutes)

```bash
# 1. Flash firmware to ESP32
cd esp32-device-control/firmware
idf.py set-target esp32
idf.py flash

# 2. Install serial interface
cd ../../serial-interface
python3 install.py

# 3. Install AI tool hooks
cd ../ai-status-lights
python3 scripts/install_claude_hooks.py

# 4. Test the light
python3 ../serial-interface/esp32_light_control.py rainbow
```

### For Developers

See [Getting Started](docs/GETTING_STARTED.md) for detailed setup instructions for different audiences.

## Modules

agentblink consists of three independent modules:

### ESP32 Device Control
Hardware abstraction for ESP32-based status lights. Provides firmware with support for addressable LED strips, GPIO LEDs, buzzers, and vibration motors.

**Location:** `esp32-device-control/`  
**See:** [README](esp32-device-control/README.md)

### Serial Interface
Python library for communicating with ESP32 devices. Includes command-line tools and Python API for device control and auto-detection.

**Location:** `serial-interface/`  
**See:** [README](serial-interface/README.md)

### AI Status Lights
Integration layer for AI coding assistants. Maps AI tool lifecycle events to visual feedback through hook scripts.

**Location:** `ai-status-lights/`  
**See:** [README](ai-status-lights/README.md)

## Documentation

- **[Getting Started](docs/GETTING_STARTED.md)** - Setup guides for different audiences
- **[Architecture](docs/ARCHITECTURE.md)** - System design and module interactions
- **[Contributing](docs/CONTRIBUTING.md)** - Development guidelines and contribution process

## Supported Hardware

| Supported Targets | ESP32 | ESP32-C2 | ESP32-C3 | ESP32-C5 | ESP32-C6 | ESP32-C61 | ESP32-H2 | ESP32-H21 | ESP32-H4 | ESP32-P4 | ESP32-S2 | ESP32-S3 |
| ----------------- | ----- | -------- | -------- | -------- | -------- | --------- | -------- | --------- | -------- | -------- | -------- | -------- |

**Optional Components:**
- Addressable LED strip (WS2812B/NeoPixel)
- Passive buzzer module
- Vibration motor

## Examples

See the `examples/` directory for complete working examples:
- Basic LED control
- Serial communication patterns
- Hook integration examples

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/agentblink/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/agentblink/discussions)
- **Documentation**: See `docs/` directory
