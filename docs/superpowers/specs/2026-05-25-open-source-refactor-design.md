# Open Source Refactor Design

**Date:** 2026-05-25  
**Project:** agentblink  
**Goal:** Optimize and refactor code for open-sourcing as a clean template/example project

## Overview

Transform agentblink from a monolithic project into a modular, well-documented open-source project that serves mixed audiences: beginners learning ESP32 development, experienced embedded developers seeking reference implementations, and AI tool users integrating status lights.

## Target Audience & Use Cases

- **Beginners:** Learn ESP32 GPIO, LED control, and device communication through examples
- **Embedded Developers:** Use esp32-device-control as a library or reference implementation
- **AI Tool Users:** Install ai-status-lights hooks for Codex/Claude Code integration
- **Integrators:** Combine modules for custom applications

## Project Structure

```
agentblink/
├── esp32-device-control/          # Core library - hardware abstraction
│   ├── firmware/                  # ESP-IDF project
│   │   ├── main/                  # Device control logic (LED, motor, buzzer)
│   │   ├── components/            # Reusable components
│   │   └── CMakeLists.txt
│   ├── README.md                  # Library documentation
│   └── docs/                      # API documentation
│
├── serial-interface/              # Python serial communication tool
│   ├── esp32_device_control.py    # Main control script
│   ├── requirements.txt           # Dependencies
│   ├── README.md
│   └── tests/                     # Unit tests
│
├── ai-status-lights/              # AI integration hooks
│   ├── codex_hooks.py
│   ├── claude_hooks.py
│   ├── README.md
│   └── install.py                 # Global installation script
│
├── examples/                      # Integration examples
│   ├── basic-led-blink/
│   ├── motor-control/
│   ├── ai-status-integration/
│   └── README.md
│
├── docs/                          # Project-level documentation
│   ├── ARCHITECTURE.md            # System architecture
│   ├── GETTING_STARTED.md         # Quick start guide
│   ├── CONTRIBUTING.md            # Contribution guidelines
│   └── superpowers/specs/         # Design documents
│
└── README.md                      # Project overview
```

## Module Responsibilities

### esp32-device-control (Core Library)

**Purpose:** Hardware abstraction layer for ESP32 device control

**Responsibilities:**
- Unified device control interface (LED, motor, buzzer)
- Command parsing and execution
- State management
- Configuration via menuconfig

**Dependencies:** ESP-IDF only (minimal)

**Key Files:**
- `firmware/main/blink_main.c` - Device control logic
- `firmware/main/commands.c` - Command handlers
- `firmware/main/idf_component.yml` - Component dependencies

### serial-interface (Communication Layer)

**Purpose:** Python tool for serial communication with ESP32

**Responsibilities:**
- Serial port communication
- Command sending and response handling
- Device auto-discovery
- Interactive and programmatic interfaces

**Dependencies:** pyserial (required), colorama (optional)

**Key Files:**
- `esp32_device_control.py` - Main control script
- `requirements.txt` - Python dependencies
- `tests/pytest_blink.py` - Unit tests

### ai-status-lights (Integration Layer)

**Purpose:** AI tool lifecycle integration

**Responsibilities:**
- Codex/Claude Code lifecycle hooks
- Status mapping (running→chase, complete→green, etc.)
- Global installation and configuration
- Port caching for multi-project use

**Dependencies:** serial-interface

**Key Files:**
- `codex_hooks.py` - Codex integration
- `claude_hooks.py` - Claude Code integration
- `install.py` - Installation script

### examples (Learning Resources)

**Purpose:** Demonstrate module usage at different complexity levels

**Examples:**
- `basic-led-blink/` - Simple GPIO LED control
- `motor-control/` - Motor control patterns
- `ai-status-integration/` - Full integration example

Each example is independently runnable and documented.

## Code Quality Standards

### Python Code
- Type annotations (Python 3.8+)
- Docstrings for all public functions
- Unit tests with pytest
- Minimal dependencies
- PEP 8 compliance

### C/C++ Firmware
- Clear function comments
- Modular design (one responsibility per file)
- Configuration via menuconfig
- Integration tests

### Documentation
- Independent README for each module
- API documentation (auto-generated where applicable)
- Quick start guide
- Troubleshooting section
- Architecture overview

## Dependency Management

### esp32-device-control
- **Required:** ESP-IDF (official)
- **Optional:** led_strip component (via component manager)

### serial-interface
- **Required:** pyserial
- **Optional:** colorama (colored output)

### ai-status-lights
- **Required:** serial-interface
- **Optional:** Hooks for other AI tools

### Principle
Minimize external dependencies. Each module should be usable independently.

## Open Source Cleanup Checklist

- [ ] Remove personal VSCode settings from `.vscode/settings.json`
- [ ] Clean git history (remove large files, sensitive data)
- [ ] Add LICENSE file (recommend MIT or Apache 2.0)
- [ ] Add CONTRIBUTING.md with guidelines
- [ ] Standardize commit messages
- [ ] Complete `.gitignore` (build artifacts, secrets, IDE files)
- [ ] Add CI/CD configuration (GitHub Actions)
- [ ] Add SECURITY.md for vulnerability reporting
- [ ] Verify all documentation is complete and accurate
- [ ] Test installation from scratch on clean environment

## Documentation Organization

### Project Level (`docs/`)
- **ARCHITECTURE.md** - System design and module interactions
- **GETTING_STARTED.md** - Installation and first steps
- **CONTRIBUTING.md** - Development guidelines
- **SECURITY.md** - Vulnerability reporting

### Module Level (each module's README)
- Purpose and use cases
- Installation instructions
- Quick start example
- API reference
- Troubleshooting

### Examples
- Each example has its own README
- Step-by-step instructions
- Expected output
- Common issues and solutions

## Success Criteria

1. **Modularity:** Each module can be understood and used independently
2. **Documentation:** Clear enough for beginners, detailed enough for advanced users
3. **Quality:** Type-safe Python, well-commented C code, comprehensive tests
4. **Minimal Dependencies:** No unnecessary external packages
5. **Easy Installation:** Both global (ai-status-lights) and local (libraries) installation work smoothly
6. **Examples:** At least 3 working examples covering different use cases

## Implementation Phases

1. **Phase 1:** Restructure directories and separate concerns
2. **Phase 2:** Add type annotations and improve Python code quality
3. **Phase 3:** Write comprehensive documentation
4. **Phase 4:** Add tests and CI/CD
5. **Phase 5:** Clean git history and prepare for release
6. **Phase 6:** Final review and open source release

## Notes

- Preserve all existing functionality during refactoring
- Maintain backward compatibility where possible
- Use this as a template for future open source projects
