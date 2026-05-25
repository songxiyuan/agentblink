# ESP32 Device Control

Hardware abstraction library for ESP32-based status lights with LED strips, buzzers, and vibration motors.

## Features

- **Addressable LED Strip Control**: Support for WS2812B/NeoPixel LED strips with multiple effects
  - Solid colors
  - Chase (running light with fading tail)
  - Alternating colors
  - Rainbow flow
  - Yellow breathing effect
  - Auto-cycling through effects
- **GPIO LED Support**: Simple on/off LED control for basic GPIO-based LEDs
- **Buzzer Control**: Passive buzzer support with frequency and duration control
  - Beep with custom frequency and duration
  - Tone generation
  - Water drop sound effect
- **Vibration Motor**: Haptic feedback with configurable duration
- **Serial Command Interface**: UART/USB-Serial communication for remote control
- **FreeRTOS Integration**: Multi-tasking support for concurrent operations

## Prerequisites

- ESP-IDF (v5.0 or later)
- ESP32, ESP32-C3, or ESP32-S3 development board
- Optional: WS2812B LED strip (for addressable LED effects)
- Optional: Passive buzzer module
- Optional: Vibration motor module

## Build and Flash

### Configure the project

```bash
cd esp32-device-control/firmware
idf.py menuconfig
```

Key configuration options:
- `CONFIG_BLINK_GPIO`: GPIO pin for LED (default: GPIO8)
- `CONFIG_BLINK_LED_STRIP`: Enable addressable LED strip support
- `CONFIG_BLINK_LED_GPIO`: Enable simple GPIO LED support
- `CONFIG_BUZZER_ENABLE`: Enable buzzer support
- `CONFIG_VIBRATION_MOTOR_ENABLE`: Enable vibration motor support

### Build the firmware

```bash
idf.py build
```

### Flash to device

```bash
idf.py flash
```

### Monitor serial output

```bash
idf.py monitor
```

## Serial Protocol

The device communicates via UART (typically exposed as USB-Serial on development boards). Commands are sent as plain text followed by a newline character.

### Command Format

```
COMMAND [ARG1] [ARG2] ...
```

### LED Commands

- `off` - Turn all LEDs off
- `on` - Turn LED on (GPIO mode only)
- `blink` - Blink LED (GPIO mode) or cycle effects (LED strip mode)
- `auto` - Cycle through chase, alternate, and rainbow effects
- `chase` - Running light with fading tail
- `alternate` - Alternating orange/blue colors
- `rainbow` - Flowing rainbow effect
- `yellow` - Blinking yellow breathing effect
- `solid R G B` - Set solid color (LED strip only, values 0-255)
- `speed MS` - Set animation delay in milliseconds (10-5000)

### Buzzer Commands

- `beep [FREQ] [MS]` - Play a beep (default: 2000 Hz, 200 ms)
- `tone FREQ [DUTY]` - Generate continuous tone (duty cycle 1-90%)
- `drop [COUNT]` - Play water drop sound (1-10 repetitions)
- `buzzer off` - Turn off buzzer

### Vibration Motor Commands

- `vibrate MS` - Vibrate for specified milliseconds (1-60000)
- `motor MS` - Alias for vibrate

### System Commands

- `probe` - Identify device (responds with "ESP32_LIGHT_OK")
- `help` - Display available commands

## Architecture

### Main Files

- `firmware/main/blink_main.c` - Main application logic and serial command handler
- `firmware/main/buzzer.c/h` - Buzzer control implementation
- `firmware/main/vibration_motor.c/h` - Vibration motor control implementation
- `firmware/main/led_strip.h` - LED strip driver interface

### Key Components

**Serial Command Task**: Reads commands from UART/USB-Serial and dispatches to appropriate handlers.

**LED Effect Engine**: Manages LED state and renders effects at configurable intervals using FreeRTOS tasks.

**Peripheral Drivers**: Abstractions for buzzer, motor, and LED strip hardware.

## Contributing

See the main project [CONTRIBUTING.md](../docs/CONTRIBUTING.md) for guidelines on submitting issues and pull requests.
