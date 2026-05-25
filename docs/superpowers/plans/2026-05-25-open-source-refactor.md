# Open Source Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure agentblink into modular, well-documented open-source project with esp32-device-control library, serial-interface tool, ai-status-lights integration, and comprehensive examples.

**Architecture:** Separate concerns into independent modules with clear interfaces. Each module can be used standalone or combined. Python code uses type annotations and tests. C firmware is modular with clear responsibilities. Documentation is layered for different audiences.

**Tech Stack:** ESP-IDF (C/C++), Python 3.8+, pytest, pyserial, GitHub Actions

---

## Phase 1: Directory Restructuring

### Task 1: Create new directory structure

**Files:**
- Create: `esp32-device-control/firmware/` (copy from `firmware/`)
- Create: `serial-interface/` (new)
- Create: `ai-status-lights/` (new)
- Create: `examples/` (new)
- Modify: `.gitignore` (add build artifacts)

- [ ] **Step 1: Create top-level module directories**

```bash
cd /Users/sxy/Documents/esp32/agentblink
mkdir -p esp32-device-control/firmware
mkdir -p esp32-device-control/docs
mkdir -p serial-interface/tests
mkdir -p ai-status-lights
mkdir -p examples/{basic-led-blink,motor-control,ai-status-integration}
```

- [ ] **Step 2: Copy firmware to esp32-device-control**

```bash
cp -r firmware/* esp32-device-control/firmware/
```

- [ ] **Step 3: Move serial tools to serial-interface**

```bash
mv tools/serial/*.py serial-interface/
mv tests/pytest_blink.py serial-interface/tests/
```

- [ ] **Step 4: Move AI hooks to ai-status-lights**

```bash
mv ai/hooks/*.py ai-status-lights/
mv scripts/install_*.py ai-status-lights/
```

- [ ] **Step 5: Create examples structure**

```bash
# Create basic-led-blink example
cat > examples/basic-led-blink/README.md << 'EOF'
# Basic LED Blink Example

Simple GPIO LED control example for ESP32.

## Hardware Setup
- LED connected to GPIO 2
- GND connected to LED cathode

## Build and Flash
```bash
cd ../../esp32-device-control/firmware
idf.py build
idf.py -p /dev/ttyUSB0 flash
```

## Expected Output
LED blinks every 1 second.
EOF

# Create motor-control example
cat > examples/motor-control/README.md << 'EOF'
# Motor Control Example

Vibration motor control example.

## Hardware Setup
- Motor connected to GPIO 4

## Build and Flash
```bash
cd ../../esp32-device-control/firmware
idf.py build
idf.py -p /dev/ttyUSB0 flash
```

## Expected Output
Motor vibrates in patterns.
EOF

# Create ai-status-integration example
cat > examples/ai-status-integration/README.md << 'EOF'
# AI Status Lights Integration

Full integration example with Codex/Claude Code.

## Setup
1. Install serial-interface: `pip install -e ../../serial-interface`
2. Install ai-status-lights: `pip install -e ../../ai-status-lights`
3. Run: `python run_example.py`

## Expected Output
Status lights respond to AI tool lifecycle events.
EOF
```

- [ ] **Step 6: Update .gitignore**

```bash
cat >> .gitignore << 'EOF'

# Build artifacts
build/
dist/
*.egg-info/
__pycache__/
*.pyc
.pytest_cache/

# ESP-IDF
esp32-device-control/firmware/build/
esp32-device-control/firmware/sdkconfig

# IDE
.vscode/settings.json
.idea/

# Secrets
.env
*.key
EOF
```

- [ ] **Step 7: Commit**

```bash
git add esp32-device-control/ serial-interface/ ai-status-lights/ examples/ .gitignore
git commit -m "refactor: restructure into modular directories"
```

---

## Phase 2: Python Code Quality

### Task 2: Add type annotations to serial-interface

**Files:**
- Modify: `serial-interface/esp32_light_control.py`
- Modify: `serial-interface/esp32_event_control.py`
- Create: `serial-interface/py.typed`

- [ ] **Step 1: Add type annotations to esp32_light_control.py**

Read the file first to understand current structure, then add type hints to all functions:

```python
from typing import Optional, Dict, List, Tuple
import serial

class ESP32LightControl:
    def __init__(self, port: str, baudrate: int = 115200) -> None:
        self.port: str = port
        self.baudrate: int = baudrate
        self.ser: Optional[serial.Serial] = None
    
    def connect(self) -> bool:
        """Connect to ESP32 device."""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            return True
        except serial.SerialException:
            return False
    
    def send_command(self, command: str) -> str:
        """Send command and return response."""
        if not self.ser:
            raise RuntimeError("Not connected")
        self.ser.write(command.encode())
        return self.ser.readline().decode().strip()
    
    def disconnect(self) -> None:
        """Disconnect from device."""
        if self.ser:
            self.ser.close()
```

- [ ] **Step 2: Add type annotations to esp32_event_control.py**

Similar process - add type hints to all functions and class methods.

- [ ] **Step 3: Create py.typed marker**

```bash
touch serial-interface/py.typed
```

- [ ] **Step 4: Run type checker**

```bash
cd serial-interface
pip install mypy
mypy *.py --ignore-missing-imports
```

Expected: No errors

- [ ] **Step 5: Commit**

```bash
git add serial-interface/
git commit -m "feat: add type annotations to serial-interface"
```

### Task 3: Add docstrings to serial-interface

**Files:**
- Modify: `serial-interface/esp32_light_control.py`
- Modify: `serial-interface/esp32_event_control.py`

- [ ] **Step 1: Add module docstring**

```python
"""
ESP32 Serial Communication Interface

Provides high-level API for controlling ESP32 devices over serial connection.
Supports LED, motor, and buzzer control with command queuing and response handling.
"""
```

- [ ] **Step 2: Add class docstrings**

```python
class ESP32LightControl:
    """Control LED patterns on ESP32 device.
    
    Manages serial communication with ESP32 firmware for LED control.
    Supports predefined patterns (blink, chase, pulse) and custom commands.
    
    Example:
        >>> control = ESP32LightControl('/dev/ttyUSB0')
        >>> control.connect()
        >>> control.set_pattern('chase')
        >>> control.disconnect()
    """
```

- [ ] **Step 3: Add function docstrings**

```python
def send_command(self, command: str) -> str:
    """Send command to ESP32 and return response.
    
    Args:
        command: Command string to send (e.g., 'LED_ON', 'MOTOR_VIBRATE')
    
    Returns:
        Response string from device (e.g., 'OK', 'ERROR')
    
    Raises:
        RuntimeError: If device is not connected
        serial.SerialException: If communication fails
    """
```

- [ ] **Step 4: Commit**

```bash
git add serial-interface/
git commit -m "docs: add comprehensive docstrings to serial-interface"
```

### Task 4: Add pytest tests to serial-interface

**Files:**
- Create: `serial-interface/tests/test_esp32_light_control.py`
- Create: `serial-interface/tests/conftest.py`
- Create: `serial-interface/requirements-dev.txt`

- [ ] **Step 1: Create conftest.py with mock serial**

```python
# serial-interface/tests/conftest.py
import pytest
from unittest.mock import Mock, patch
import serial

@pytest.fixture
def mock_serial():
    """Mock serial connection for testing."""
    with patch('serial.Serial') as mock:
        mock_instance = Mock()
        mock_instance.write = Mock()
        mock_instance.readline = Mock(return_value=b'OK\n')
        mock_instance.close = Mock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def light_control(mock_serial):
    """Create ESP32LightControl instance with mocked serial."""
    from esp32_light_control import ESP32LightControl
    control = ESP32LightControl('/dev/ttyUSB0')
    control.connect()
    return control
```

- [ ] **Step 2: Create test file**

```python
# serial-interface/tests/test_esp32_light_control.py
import pytest
from esp32_light_control import ESP32LightControl

def test_connect_success(mock_serial):
    """Test successful connection."""
    control = ESP32LightControl('/dev/ttyUSB0')
    assert control.connect() == True

def test_send_command(light_control, mock_serial):
    """Test sending command."""
    mock_serial.readline.return_value = b'OK\n'
    response = light_control.send_command('LED_ON')
    assert response == 'OK'
    mock_serial.write.assert_called_once()

def test_disconnect(light_control, mock_serial):
    """Test disconnection."""
    light_control.disconnect()
    mock_serial.close.assert_called_once()

def test_not_connected_error():
    """Test error when not connected."""
    control = ESP32LightControl('/dev/ttyUSB0')
    with pytest.raises(RuntimeError):
        control.send_command('LED_ON')
```

- [ ] **Step 3: Create requirements-dev.txt**

```bash
cat > serial-interface/requirements-dev.txt << 'EOF'
pytest>=7.0
pytest-cov>=4.0
mypy>=1.0
black>=23.0
EOF
```

- [ ] **Step 4: Run tests**

```bash
cd serial-interface
pip install -r requirements-dev.txt
pytest tests/ -v
```

Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add serial-interface/tests/ serial-interface/requirements-dev.txt
git commit -m "test: add unit tests for serial-interface"
```

---

## Phase 3: Module Documentation

### Task 5: Create esp32-device-control README

**Files:**
- Create: `esp32-device-control/README.md`
- Create: `esp32-device-control/docs/API.md`

- [ ] **Step 1: Create main README**

```markdown
# esp32-device-control

Hardware abstraction library for ESP32 device control (LED, motor, buzzer).

## Features

- Unified device control interface
- Support for LED patterns (blink, chase, pulse)
- Motor vibration control
- Buzzer sound patterns
- Serial command protocol
- Minimal dependencies (ESP-IDF only)

## Quick Start

### Prerequisites
- ESP-IDF 5.0+
- ESP32 development board

### Build and Flash

\`\`\`bash
cd firmware
idf.py build
idf.py -p /dev/ttyUSB0 flash
idf.py -p /dev/ttyUSB0 monitor
\`\`\`

### Serial Protocol

Send commands via serial (115200 baud):

\`\`\`
LED_ON          # Turn LED on
LED_OFF         # Turn LED off
LED_BLINK       # Blink pattern
MOTOR_VIBRATE   # Vibrate motor
BUZZER_BEEP     # Beep buzzer
\`\`\`

## Architecture

- `main/blink_main.c` - Main entry point and command dispatcher
- `main/led_control.c` - LED control logic
- `main/vibration_motor.c` - Motor control logic
- `main/buzzer.c` - Buzzer control logic

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md)
```

- [ ] **Step 2: Create API documentation**

```markdown
# API Reference

## Command Protocol

All commands are sent as ASCII strings terminated with newline.

### LED Commands

- `LED_ON` - Turn LED on
- `LED_OFF` - Turn LED off
- `LED_BLINK` - Blink at 1Hz
- `LED_CHASE` - Chase pattern
- `LED_PULSE` - Pulse pattern

### Motor Commands

- `MOTOR_VIBRATE` - Single vibration
- `MOTOR_PATTERN_1` - Pattern 1
- `MOTOR_PATTERN_2` - Pattern 2

### Buzzer Commands

- `BUZZER_BEEP` - Single beep
- `BUZZER_ALARM` - Alarm pattern

### Response Format

All commands return:
- `OK` - Command executed successfully
- `ERROR` - Invalid command or execution failed
```

- [ ] **Step 3: Commit**

```bash
git add esp32-device-control/README.md esp32-device-control/docs/
git commit -m "docs: add esp32-device-control documentation"
```

### Task 6: Create serial-interface README

**Files:**
- Create: `serial-interface/README.md`
- Create: `serial-interface/requirements.txt`

- [ ] **Step 1: Create README**

```markdown
# serial-interface

Python tool for serial communication with ESP32 devices.

## Installation

\`\`\`bash
pip install -e .
\`\`\`

## Quick Start

\`\`\`python
from esp32_light_control import ESP32LightControl

# Connect to device
control = ESP32LightControl('/dev/ttyUSB0')
control.connect()

# Send commands
control.send_command('LED_ON')
control.send_command('LED_BLINK')

# Disconnect
control.disconnect()
\`\`\`

## Command Line Usage

\`\`\`bash
python esp32_light_control.py --port /dev/ttyUSB0 --command LED_ON
\`\`\`

## API Reference

See [API.md](docs/API.md)

## Testing

\`\`\`bash
pip install -r requirements-dev.txt
pytest tests/ -v
\`\`\`
```

- [ ] **Step 2: Create requirements.txt**

```bash
cat > serial-interface/requirements.txt << 'EOF'
pyserial>=3.5
colorama>=0.4.6
EOF
```

- [ ] **Step 3: Create setup.py**

```python
# serial-interface/setup.py
from setuptools import setup

setup(
    name='esp32-device-control',
    version='0.1.0',
    description='Python serial interface for ESP32 device control',
    py_modules=['esp32_light_control', 'esp32_event_control'],
    install_requires=[
        'pyserial>=3.5',
        'colorama>=0.4.6',
    ],
    python_requires='>=3.8',
)
```

- [ ] **Step 4: Commit**

```bash
git add serial-interface/README.md serial-interface/requirements.txt serial-interface/setup.py
git commit -m "docs: add serial-interface documentation and setup"
```

### Task 7: Create ai-status-lights README

**Files:**
- Create: `ai-status-lights/README.md`
- Create: `ai-status-lights/requirements.txt`

- [ ] **Step 1: Create README**

```markdown
# ai-status-lights

AI tool lifecycle integration for status lights (Codex, Claude Code).

## Installation

\`\`\`bash
# Install dependencies
pip install -e ../serial-interface

# Install hooks
python install.py
\`\`\`

## Supported Tools

- Codex
- Claude Code

## How It Works

Hooks into AI tool lifecycle events:
- Tool start → LED chase pattern
- Tool running → LED pulse
- Tool complete → LED green
- Tool error → LED red

## Configuration

Edit `~/.esp32_status_lights/config.json`:

\`\`\`json
{
  "port": "/dev/ttyUSB0",
  "baudrate": 115200,
  "enabled": true
}
\`\`\`

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
```

- [ ] **Step 2: Create requirements.txt**

```bash
cat > ai-status-lights/requirements.txt << 'EOF'
# Requires serial-interface to be installed
EOF
```

- [ ] **Step 3: Commit**

```bash
git add ai-status-lights/README.md ai-status-lights/requirements.txt
git commit -m "docs: add ai-status-lights documentation"
```

---

## Phase 4: Project-Level Documentation

### Task 8: Create project documentation

**Files:**
- Create: `docs/ARCHITECTURE.md`
- Create: `docs/GETTING_STARTED.md`
- Create: `docs/CONTRIBUTING.md`
- Modify: `README.md` (project overview)

- [ ] **Step 1: Create ARCHITECTURE.md**

```markdown
# Architecture

## Overview

agentblink is organized into three independent modules:

1. **esp32-device-control** - Hardware abstraction library
2. **serial-interface** - Python serial communication tool
3. **ai-status-lights** - AI tool integration

## Module Interactions

\`\`\`
AI Tool (Codex/Claude Code)
    ↓
ai-status-lights (hooks)
    ↓
serial-interface (Python)
    ↓
ESP32 Device (firmware)
    ↓
Hardware (LED, motor, buzzer)
\`\`\`

## Data Flow

1. AI tool triggers lifecycle event
2. ai-status-lights hook captures event
3. Hook sends command via serial-interface
4. serial-interface sends command to ESP32
5. ESP32 firmware executes command
6. Hardware responds (LED lights, motor vibrates, etc.)

## Module Boundaries

Each module has clear responsibilities and interfaces:

- **esp32-device-control**: Firmware only, no Python dependencies
- **serial-interface**: Python only, no firmware dependencies
- **ai-status-lights**: Depends on serial-interface, integrates with AI tools

This allows each module to be used independently or combined.
```

- [ ] **Step 2: Create GETTING_STARTED.md**

```markdown
# Getting Started

## For Beginners

Start with the examples:

1. [Basic LED Blink](../examples/basic-led-blink/README.md)
2. [Motor Control](../examples/motor-control/README.md)
3. [AI Status Integration](../examples/ai-status-integration/README.md)

## For Embedded Developers

Use esp32-device-control as a library:

1. Copy firmware to your project
2. Modify commands as needed
3. Build with ESP-IDF

## For AI Tool Users

Install ai-status-lights:

\`\`\`bash
cd ai-status-lights
python install.py
\`\`\`

## Hardware Setup

### Required
- ESP32 development board
- USB cable for programming and serial communication

### Optional
- LED (GPIO 2)
- Vibration motor (GPIO 4)
- Buzzer (GPIO 5)

## Troubleshooting

### Device not found
\`\`\`bash
ls /dev/tty*
\`\`\`

### Permission denied
\`\`\`bash
sudo usermod -a -G dialout $USER
\`\`\`

### Build fails
Ensure ESP-IDF is installed and sourced:
\`\`\`bash
. $IDF_PATH/export.sh
\`\`\`
```

- [ ] **Step 3: Create CONTRIBUTING.md**

```markdown
# Contributing

## Development Setup

1. Clone repository
2. Install dependencies:
   \`\`\`bash
   pip install -r serial-interface/requirements-dev.txt
   \`\`\`
3. Create feature branch

## Code Style

- Python: PEP 8, type annotations required
- C: Clear comments, modular design
- Commit messages: Conventional commits

## Testing

Run tests before submitting PR:

\`\`\`bash
cd serial-interface
pytest tests/ -v
mypy *.py
\`\`\`

## Pull Request Process

1. Create feature branch
2. Make changes with tests
3. Ensure all tests pass
4. Submit PR with description
5. Address review feedback

## Reporting Issues

Use GitHub Issues with:
- Clear title
- Reproduction steps
- Expected vs actual behavior
- Environment details
```

- [ ] **Step 4: Update main README.md**

```markdown
# agentblink

ESP32 device control library with AI tool integration.

## Features

- 🎛️ Unified hardware control (LED, motor, buzzer)
- 🐍 Python serial interface
- 🤖 AI tool lifecycle integration (Codex, Claude Code)
- 📚 Comprehensive documentation
- ✅ Type-safe Python code
- 🧪 Full test coverage

## Quick Start

### For Beginners
See [Getting Started](docs/GETTING_STARTED.md)

### For Developers
```bash
# Install serial interface
pip install -e serial-interface

# Install AI hooks
cd ai-status-lights && python install.py
```

### For Embedded Engineers
```bash
cd esp32-device-control/firmware
idf.py build
idf.py -p /dev/ttyUSB0 flash
```

## Modules

- [esp32-device-control](esp32-device-control/) - Hardware library
- [serial-interface](serial-interface/) - Python tool
- [ai-status-lights](ai-status-lights/) - AI integration
- [examples](examples/) - Learning resources

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Getting Started](docs/GETTING_STARTED.md)
- [Contributing](docs/CONTRIBUTING.md)

## License

MIT License - see LICENSE file

## Support

- 📖 [Documentation](docs/)
- 🐛 [Issues](https://github.com/sxy/agentblink/issues)
- 💬 [Discussions](https://github.com/sxy/agentblink/discussions)
```

- [ ] **Step 5: Commit**

```bash
git add docs/ README.md
git commit -m "docs: add comprehensive project documentation"
```

---

## Phase 5: Open Source Cleanup

### Task 9: Clean git history and prepare for release

**Files:**
- Create: `LICENSE`
- Create: `SECURITY.md`
- Modify: `.gitignore` (final check)
- Modify: `.vscode/settings.json` (remove personal settings)

- [ ] **Step 1: Create LICENSE**

```bash
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 agentblink contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
EOF
```

- [ ] **Step 2: Create SECURITY.md**

```bash
cat > SECURITY.md << 'EOF'
# Security Policy

## Reporting Security Issues

Please do NOT open public issues for security vulnerabilities.

Email security concerns to: [your-email@example.com]

Include:
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will acknowledge receipt within 48 hours and provide updates as we work on a fix.
EOF
```

- [ ] **Step 3: Clean .vscode/settings.json**

Remove personal settings, keep only project-relevant ones:

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.python"
  },
  "C_Cpp.default.configurationProvider": "ms-vscode.cmake-tools"
}
```

- [ ] **Step 4: Verify .gitignore completeness**

```bash
cat .gitignore | grep -E "build|dist|__pycache__|\.pyc|\.egg-info|\.env|\.vscode/settings"
```

Expected: All patterns present

- [ ] **Step 5: Commit**

```bash
git add LICENSE SECURITY.md .vscode/settings.json
git commit -m "chore: add open source files and clean settings"
```

### Task 10: Add CI/CD configuration

**Files:**
- Create: `.github/workflows/test.yml`
- Create: `.github/workflows/lint.yml`

- [ ] **Step 1: Create test workflow**

```bash
mkdir -p .github/workflows

cat > .github/workflows/test.yml << 'EOF'
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r serial-interface/requirements-dev.txt
    
    - name: Run tests
      run: |
        cd serial-interface
        pytest tests/ -v --cov
    
    - name: Type check
      run: |
        cd serial-interface
        mypy *.py --ignore-missing-imports
EOF
```

- [ ] **Step 2: Create lint workflow**

```bash
cat > .github/workflows/lint.yml << 'EOF'
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install black flake8 isort
    
    - name: Check formatting
      run: |
        black --check serial-interface/
        isort --check-only serial-interface/
    
    - name: Lint
      run: |
        flake8 serial-interface/ --max-line-length=100
EOF
```

- [ ] **Step 3: Commit**

```bash
git add .github/
git commit -m "ci: add GitHub Actions workflows"
```

---

## Phase 6: Final Verification

### Task 11: Verify all modules work independently

**Files:**
- Test: All modules

- [ ] **Step 1: Test esp32-device-control builds**

```bash
cd esp32-device-control/firmware
idf.py build
```

Expected: Build succeeds

- [ ] **Step 2: Test serial-interface installation**

```bash
cd serial-interface
pip install -e .
python -c "from esp32_light_control import ESP32LightControl; print('OK')"
```

Expected: Import succeeds

- [ ] **Step 3: Test ai-status-lights installation**

```bash
cd ai-status-lights
pip install -e ../serial-interface
python -c "import status_light; print('OK')"
```

Expected: Import succeeds

- [ ] **Step 4: Run all tests**

```bash
cd serial-interface
pytest tests/ -v
```

Expected: All tests pass

- [ ] **Step 5: Commit verification results**

```bash
git add -A
git commit -m "test: verify all modules work independently"
```

### Task 12: Final documentation review

**Files:**
- Review: All README.md files
- Review: All documentation

- [ ] **Step 1: Check all READMEs exist**

```bash
find . -name "README.md" -type f | sort
```

Expected output:
```
./README.md
./docs/ARCHITECTURE.md
./docs/CONTRIBUTING.md
./docs/GETTING_STARTED.md
./esp32-device-control/README.md
./examples/basic-led-blink/README.md
./examples/motor-control/README.md
./examples/ai-status-integration/README.md
./serial-interface/README.md
./ai-status-lights/README.md
```

- [ ] **Step 2: Verify documentation links**

Check that all cross-references in documentation are valid:
- ARCHITECTURE.md references correct files
- GETTING_STARTED.md links to examples
- Module READMEs link to parent docs

- [ ] **Step 3: Final commit**

```bash
git log --oneline | head -15
```

Verify commit history is clean and follows conventional commits

- [ ] **Step 4: Create release tag**

```bash
git tag -a v0.1.0 -m "Initial open source release"
```

---

## Summary

This plan transforms agentblink into a professional open-source project through:

1. **Modular structure** - Independent modules with clear boundaries
2. **Code quality** - Type annotations, docstrings, tests
3. **Documentation** - Layered for different audiences
4. **CI/CD** - Automated testing and linting
5. **Open source readiness** - License, security policy, contribution guidelines

Each phase produces working, testable software that can be reviewed independently.
