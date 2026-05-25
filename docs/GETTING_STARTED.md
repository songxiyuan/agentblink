# Getting Started

## For Beginners

New to agentblink? Start here to understand what this project does and how to use it.

### What is agentblink?

agentblink provides visual feedback for AI coding assistants through an ESP32-based status light. When you're using Codex or Claude Code, the light automatically shows what's happening:
- **Off** - Idle or session starting
- **Chase animation** - Task running or tool in use
- **Yellow breathing** - Waiting for your input
- **Solid green** - Task complete

### Quick Start (5 minutes)

1. **Flash the firmware** to your ESP32:
   ```bash
   cd esp32-device-control/firmware
   idf.py set-target esp32
   idf.py flash monitor
   ```

2. **Install the serial interface**:
   ```bash
   cd serial-interface
   python3 install.py
   ```

3. **Install AI tool hooks**:
   ```bash
   cd ai-status-lights
   python3 scripts/install_claude_hooks.py
   ```

4. **Test the light**:
   ```bash
   python3 serial-interface/esp32_light_control.py rainbow
   ```

### Examples

See the `examples/` directory for complete working examples:
- Basic LED control
- Serial communication patterns
- Hook integration examples

## For Embedded Developers

Working with the ESP32 firmware? This section covers hardware setup and development.

### Hardware Setup

**Required:**
- ESP32 development board (ESP32, ESP32-C3, ESP32-S3, etc.)
- USB cable for power and programming
- Addressable LED strip (WS2812B/NeoPixel) OR GPIO LED

**Optional:**
- Passive buzzer module (for audio feedback)
- Vibration motor (for haptic feedback)
- Breadboard and jumper wires

### Firmware Development

1. **Install ESP-IDF**:
   ```bash
   # Follow https://docs.espressif.com/projects/esp-idf/en/latest/get-started/
   ```

2. **Configure the project**:
   ```bash
   cd esp32-device-control/firmware
   idf.py set-target <chip_name>
   idf.py menuconfig
   ```

3. **Key configuration options**:
   - `CONFIG_BLINK_GPIO` - GPIO pin for LED (default: GPIO8)
   - `CONFIG_BLINK_LED_STRIP` - Enable addressable LED strip
   - `CONFIG_BUZZER_ENABLE` - Enable buzzer support
   - `CONFIG_VIBRATION_MOTOR_ENABLE` - Enable vibration motor

4. **Build and flash**:
   ```bash
   idf.py build
   idf.py flash
   idf.py monitor
   ```

### Serial Protocol

The firmware communicates via UART (USB-Serial on dev boards). Send plain text commands:

```bash
# LED commands
off
solid 255 0 0
chase
rainbow
yellow
speed 100

# Buzzer commands
beep 2000 200
tone 1000

# Vibration commands
vibrate 500

# System commands
probe
help
```

### Testing

Run the test suite:
```bash
cd esp32-device-control
pytest tests/
```

## For AI Tool Users

Using agentblink with Codex or Claude Code? This section covers installation and usage.

### Installation

1. **Flash the firmware** (one-time setup):
   ```bash
   cd esp32-device-control/firmware
   idf.py set-target esp32
   idf.py flash
   ```

2. **Install the serial interface**:
   ```bash
   cd serial-interface
   python3 install.py
   ```

3. **Install hooks for your AI tool**:
   ```bash
   cd ai-status-lights
   
   # For Claude Code
   python3 scripts/install_claude_hooks.py
   
   # For Codex
   python3 scripts/install_codex_hooks.py
   
   # For both
   python3 scripts/install_codex_hooks.py --target all
   ```

4. **Verify installation**:
   ```bash
   # Test the light manually
   python3 serial-interface/esp32_light_control.py solid 0 255 0
   ```

### How It Works

Once installed, the light automatically responds to AI tool events:

- **Session starts** → Light turns off
- **You submit a prompt** → Light enters chase mode
- **Tool is running** → Chase animation continues
- **Waiting for input** → Yellow breathing light
- **Task completes** → Solid green light
- **You resume activity** → Light turns off (idle monitor)

### Configuration

The hooks are installed globally:
- **Codex**: `~/.codex/hooks.json`
- **Claude Code**: `~/.claude/settings.json`

The serial port is auto-detected on first use and cached in:
- `~/.codex/hooks/light_port` (Codex)
- `~/.claude/hooks/light_port` (Claude Code)

### Manual Control

You can also control the light manually from the command line:

```bash
# List available ports
python3 serial-interface/esp32_light_control.py --list-ports

# Send commands
python3 serial-interface/esp32_light_control.py solid 255 0 0
python3 serial-interface/esp32_light_control.py chase
python3 serial-interface/esp32_light_control.py off

# Interactive mode
python3 serial-interface/esp32_light_control.py interactive
```

## Troubleshooting

### Light not responding

**Problem:** Light doesn't turn on or respond to commands

**Solutions:**
1. Verify ESP32 is powered and connected via USB
2. Check that firmware is flashed: `idf.py monitor` should show startup messages
3. Verify serial port: `python3 serial-interface/esp32_light_control.py --list-ports`
4. Try manual command: `python3 serial-interface/esp32_light_control.py solid 255 0 0`

### Hooks not running

**Problem:** Light doesn't respond to AI tool events

**Solutions:**
1. Verify hooks are installed: Check `~/.codex/hooks.json` or `~/.claude/settings.json`
2. Check hook permissions: `ls -la ~/.codex/hooks/` or `ls -la ~/.claude/hooks/`
3. Make scripts executable: `chmod +x ~/.codex/hooks/*.py`
4. Enable logging: `STATUS_LIGHT_LOG=true` environment variable
5. Check logs: `cat ~/.codex/hooks/status_light.log` or `cat ~/.claude/hooks/status_light.log`

### Serial port not detected

**Problem:** "No ESP32 device found" error

**Solutions:**
1. Verify USB cable is connected
2. Check device manager for serial port
3. Install USB drivers if needed (CH340, CP2102, etc.)
4. Specify port manually: `python3 serial-interface/esp32_light_control.py -p /dev/cu.usbserial-0001 solid 255 0 0`

### Permission errors

**Problem:** "Permission denied" when running scripts

**Solutions:**
1. Make scripts executable: `chmod +x script.py`
2. Check file ownership: `ls -la ~/.codex/hooks/`
3. Reinstall hooks: `python3 scripts/install_codex_hooks.py`

### Idle monitor not working

**Problem:** Light doesn't turn off after task completes

**Solutions:**
1. Verify you're on macOS (idle monitor uses `ioreg` command)
2. Check that `light_idle_monitor.py` is running
3. Enable logging: `STATUS_LIGHT_LOG=true`
4. Manually turn off: `python3 serial-interface/esp32_light_control.py off`

## Next Steps

- Read the [Architecture](ARCHITECTURE.md) guide to understand how modules work together
- Check [Contributing](CONTRIBUTING.md) if you want to contribute
- See `examples/` for complete working code samples
- Visit the [ESP-IDF documentation](https://docs.espressif.com/projects/esp-idf/) for firmware details
