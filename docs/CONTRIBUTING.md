# Contributing

Thank you for your interest in contributing to agentblink! This guide covers how to set up your development environment, follow our code style, and submit changes.

## Development Setup

### Prerequisites

- Python 3.8+
- ESP-IDF v5.0 or later
- Git
- macOS, Linux, or WSL on Windows

### Clone and Setup

```bash
git clone https://github.com/yourusername/agentblink.git
cd agentblink

# Install serial interface in development mode
cd serial-interface
pip install -e .
pip install -r requirements-dev.txt

# Install AI status lights dependencies
cd ../ai-status-lights
pip install -r requirements.txt
```

### ESP-IDF Setup

For firmware development:

```bash
# Install ESP-IDF (if not already installed)
git clone https://github.com/espressif/esp-idf.git
cd esp-idf
./install.sh

# Activate ESP-IDF environment
source export.sh
```

## Code Style

### Python

We follow PEP 8 with these conventions:

- **Line length**: 100 characters
- **Indentation**: 4 spaces
- **Imports**: Organized in groups (stdlib, third-party, local)
- **Type hints**: Use type hints for function signatures
- **Docstrings**: Use Google-style docstrings

Example:
```python
def send_command(self, command: str) -> bool:
    """Send a command to the ESP32 device.
    
    Args:
        command: The command string to send.
        
    Returns:
        True if successful, False otherwise.
    """
    pass
```

### C/Firmware

For ESP32 firmware code:

- **Style**: Follow ESP-IDF coding style
- **Comments**: Use `//` for single-line comments
- **Functions**: Keep functions focused and under 50 lines when possible
- **Error handling**: Always check return values from IDF functions

### Commit Messages

Use clear, descriptive commit messages:

```
type(scope): brief description

Longer explanation if needed. Explain the why, not the what.

Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
- `feat(serial): add device auto-detection`
- `fix(firmware): correct LED timing issue`
- `docs: update getting started guide`

## Testing Requirements

### Python Tests

All Python code must have tests. Run the test suite:

```bash
cd serial-interface
pytest tests/

# With coverage
pytest --cov=. tests/

# Type checking
mypy esp32_light_control.py esp32_event_control.py
```

### Firmware Tests

For firmware changes, verify:

1. **Compilation**: `idf.py build` completes without errors
2. **Flashing**: `idf.py flash` succeeds
3. **Serial commands**: Test commands manually via serial monitor
4. **Hardware**: Test on actual hardware if possible

### Test Coverage

- Aim for 80%+ code coverage
- Test both success and error cases
- Include integration tests for module interactions

## Pull Request Process

### Before Submitting

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and commit with clear messages

3. **Run tests**:
   ```bash
   pytest tests/
   mypy *.py
   ```

4. **Update documentation** if needed

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

### PR Description

Include:
- **Summary**: What does this PR do?
- **Changes**: List of specific changes
- **Testing**: How was this tested?
- **Checklist**:
  - [ ] Tests pass
  - [ ] Code follows style guidelines
  - [ ] Documentation updated
  - [ ] No breaking changes (or documented)

Example:
```markdown
## Summary
Add device auto-detection to serial interface

## Changes
- Implement `probe_and_connect()` method
- Add port scanning logic
- Cache detected port for future use

## Testing
- Unit tests for port detection
- Integration test with real ESP32
- Manual testing on macOS and Linux

## Checklist
- [x] Tests pass
- [x] Code follows style guidelines
- [x] Documentation updated
```

### Review Process

1. At least one maintainer review required
2. All tests must pass
3. No merge conflicts
4. Address feedback and push updates

## Reporting Issues

### Bug Reports

Include:
- **Description**: What's the problem?
- **Steps to reproduce**: How to trigger the bug
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: OS, Python version, hardware, etc.
- **Logs**: Error messages or debug output

Example:
```markdown
## Description
Light doesn't respond to commands after 5 minutes of inactivity

## Steps to Reproduce
1. Flash firmware
2. Send command: `solid 255 0 0`
3. Wait 5 minutes without sending commands
4. Send command: `chase`

## Expected Behavior
Light should enter chase mode

## Actual Behavior
No response, light remains off

## Environment
- OS: macOS 12.6
- Python: 3.10
- Hardware: ESP32-S3-DevKitC
```

### Feature Requests

Include:
- **Description**: What feature would you like?
- **Use case**: Why do you need it?
- **Proposed solution**: How should it work?
- **Alternatives**: Other approaches considered

## Module-Specific Guidelines

### ESP32 Device Control (Firmware)

- Changes to `blink_main.c` require testing on hardware
- New commands must be documented in README
- Serial protocol changes need backward compatibility consideration
- Use FreeRTOS best practices for task management

### Serial Interface (Python)

- All public methods must have type hints
- New commands must include CLI support
- API changes require documentation updates
- Maintain Python 3.8+ compatibility

### AI Status Lights (Integration)

- Hook scripts must handle missing dependencies gracefully
- Event processing must be fast (< 100ms)
- Logging should be optional (controlled by environment variable)
- Support both Codex and Claude Code

## Getting Help

- **Questions**: Open a discussion or issue
- **Documentation**: Check [ARCHITECTURE.md](ARCHITECTURE.md) and [GETTING_STARTED.md](GETTING_STARTED.md)
- **Examples**: See the `examples/` directory
- **Community**: Join our discussions

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

Thank you for contributing to agentblink!
