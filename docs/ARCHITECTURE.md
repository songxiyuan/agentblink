# Architecture

## Overview

agentblink is a modular system for controlling ESP32-based status lights through AI tool integrations. The project consists of three independent modules that work together to provide visual feedback for AI coding assistants.

## Three Modules

### 1. ESP32 Device Control
**Location:** `esp32-device-control/`

Hardware abstraction layer for ESP32 microcontrollers. Provides firmware and low-level control for:
- Addressable LED strips (WS2812B/NeoPixel)
- GPIO-based LEDs
- Passive buzzers
- Vibration motors

**Responsibilities:**
- Firmware implementation for ESP32 devices
- Serial command protocol handling
- LED effect rendering (chase, rainbow, breathing, etc.)
- Audio and haptic feedback

**Key Files:**
- `firmware/main/blink_main.c` - Main application and serial handler
- `firmware/main/buzzer.c/h` - Buzzer control
- `firmware/main/vibration_motor.c/h` - Vibration motor control

### 2. Serial Interface
**Location:** `serial-interface/`

Python library for communicating with ESP32 devices over serial connections. Provides:
- Command-line tools for device control
- Python API for programmatic access
- Device auto-detection and port management
- Event handling and configuration

**Responsibilities:**
- Serial port discovery and connection management
- Command serialization and transmission
- Device probing and identification
- Python package distribution

**Key Files:**
- `esp32_light_control.py` - Main control class
- `esp32_event_control.py` - Event handling
- `setup.py` - Package configuration

### 3. AI Status Lights
**Location:** `ai-status-lights/`

Integration layer for AI coding assistants (Codex, Claude Code). Maps AI tool lifecycle events to visual feedback:
- Session start/end
- Task execution
- User input requests
- Tool usage and errors

**Responsibilities:**
- Hook script installation for AI tools
- Event payload processing
- Lifecycle event mapping to LED states
- Idle monitoring and automatic state transitions

**Key Files:**
- `status_light.py` - Main event processor
- `light_idle_monitor.py` - Idle state detection
- `install_codex_hooks.py` - Codex integration
- `install_claude_hooks.py` - Claude Code integration

## Module Interactions

```
AI Tool (Codex/Claude Code)
         |
         | Hook Events
         v
AI Status Lights Module
         |
         | Serial Commands
         v
Serial Interface Module
         |
         | USB/UART
         v
ESP32 Device Control
         |
         v
Hardware (LEDs, Buzzer, Motor)
```

## Data Flow

1. **Event Generation**: AI tool triggers a lifecycle event (e.g., task start, user input needed)
2. **Hook Execution**: Global hook script in `~/.codex/hooks.json` or `~/.claude/settings.json` is invoked
3. **Event Processing**: `status_light.py` receives event payload and determines appropriate LED state
4. **Command Generation**: Converts LED state to serial command (e.g., "chase", "solid 0 255 0")
5. **Serial Transmission**: `serial-interface` sends command to ESP32 via USB/UART
6. **Hardware Control**: ESP32 firmware executes command and updates LED/buzzer/motor state

## Module Boundaries

### ESP32 Device Control
- **Owns:** Firmware, hardware drivers, low-level command execution
- **Depends on:** ESP-IDF, hardware specifications
- **Does NOT:** Manage serial connections, process AI events, or handle Python integration

### Serial Interface
- **Owns:** Serial communication, device discovery, Python API
- **Depends on:** pyserial, ESP32 Device Control (firmware)
- **Does NOT:** Process AI events, manage hooks, or control hardware directly

### AI Status Lights
- **Owns:** Hook installation, event processing, state mapping
- **Depends on:** Serial Interface (Python API)
- **Does NOT:** Manage serial connections, control hardware, or modify AI tool code

## Independence

Each module can be used independently:

- **ESP32 Device Control** can be flashed and controlled via any serial tool
- **Serial Interface** can control any ESP32 running the firmware, from any Python environment
- **AI Status Lights** can be installed without the other modules (though it requires Serial Interface to function)

## Communication Protocols

### Serial Protocol (ESP32 Device Control ↔ Serial Interface)
Plain text commands over UART/USB-Serial:
```
COMMAND [ARG1] [ARG2] ...
```

Examples:
- `off` - Turn off
- `solid 255 0 0` - Red light
- `chase` - Chase animation
- `beep 2000 200` - Beep at 2000 Hz for 200 ms

### Hook Event Protocol (AI Tool ↔ AI Status Lights)
JSON payload passed as environment variable or file:
```json
{
  "hook_event_name": "UserPromptSubmit",
  "tool_name": "claude_code",
  "notification_type": "permission_prompt",
  "transcript_path": "/path/to/transcript",
  "turn_id": "turn_123"
}
```

## State Machine

AI Status Lights implements a simple state machine:

```
OFF (idle)
  ↓
CHASE (task running)
  ↓
YELLOW (waiting for input)
  ↓
SOLID_GREEN (task complete)
  ↓
OFF (idle monitor detects user activity)
```

## Configuration

- **ESP32 Device Control**: Configured via `idf.py menuconfig` in firmware directory
- **Serial Interface**: Auto-detects device, can specify port manually
- **AI Status Lights**: Installed globally in AI tool configuration files
