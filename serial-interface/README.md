# Serial Interface

Python serial interface for ESP32 device control. Provides command-line tools and Python APIs for controlling LED patterns, audio output, and event handling on ESP32 microcontrollers.

## Installation

### From Source

```bash
pip install -r requirements.txt
```

Or install as a package:

```bash
pip install -e .
```

### Requirements

- Python 3.8+
- pyserial>=3.5
- colorama>=0.4.6

## Quick Start

### Python API

```python
from esp32_light_control import ESP32LightControl

# Create a controller instance
controller = ESP32LightControl()

# Auto-detect ESP32 device
controller.probe_and_connect()

# Send commands
controller.send_command("solid 255 0 0")  # Red light
controller.send_command("chase")           # Chase pattern
controller.send_command("off")             # Turn off
```

### Command Line Usage

List available serial ports:
```bash
python esp32_light_control.py --list-ports
```

Send a light command:
```bash
python esp32_light_control.py -p /dev/cu.usbserial-0001 solid 255 0 0
```

Interactive mode:
```bash
python esp32_light_control.py -p /dev/cu.usbserial-0001 interactive
```

Common commands:
- `off` - Turn off lights
- `solid R G B` - Set solid color (RGB values 0-255)
- `chase` - Chase pattern
- `rainbow` - Rainbow pattern
- `blink` - Blinking pattern
- `beep FREQ MS` - Beep sound
- `vibrate MS` - Vibration duration

## API Reference

### ESP32LightControl

Main class for controlling LED patterns and audio on ESP32 devices.

**Methods:**
- `probe_and_connect()` - Auto-detect and connect to ESP32
- `send_command(command)` - Send a command string
- `close()` - Close the serial connection

### ESP32EventControl

Event handling and configuration for ESP32 devices.

See `esp32_event_control.py` for detailed API documentation.

## Testing

Run the test suite:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=. tests/
```

Type checking:

```bash
mypy esp32_light_control.py esp32_event_control.py
```
