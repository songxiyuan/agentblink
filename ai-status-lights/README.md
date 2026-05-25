# AI Status Lights

AI tool lifecycle integration for ESP32 status light control. Automatically reflects the state of AI coding assistants (Codex, Claude Code) through visual feedback on an addressable LED.

## Installation

1. Install the serial-interface dependency:
   ```sh
   cd ../serial-interface
   python3 install.py
   ```

2. Install global hooks for your AI tool:
   ```sh
   # For Codex
   ../scripts/install_codex_hooks.py
   
   # For Claude Code
   ../scripts/install_claude_hooks.py
   
   # For both
   ../scripts/install_codex_hooks.py --target all
   ```

Use `--no-deps` if `pyserial` is already available to your Python runtime.

## Supported Tools

- **Codex** - Installed globally in `~/.codex/hooks.json`
- **Claude Code** - Installed globally in `~/.claude/settings.json`

## How It Works

The module maps AI tool lifecycle events to LED states through hook scripts:

### Lifecycle Events

- **SessionStart** - Light turns off
- **UserPromptSubmit** - Light enters chase mode (running animation)
- **PreToolUse / PostToolUse / PostToolUseFailure** - Chase mode (or yellow if waiting for user input)
- **PermissionRequest / PermissionDenied / Notification** - Yellow breathing light
- **SubagentStart / SubagentStop / TaskCreated / TaskCompleted** - Chase mode
- **Stop / SessionEnd** - Solid green (then idle monitor turns off after user input resumes)

### Light States

- **Off** - Session idle or starting
- **Chase** - Task running or tool in use
- **Yellow** - Waiting for user approval or input
- **Solid Green** - Task complete (with idle monitor active)

### Idle Monitor

After the light turns solid green, `light_idle_monitor.py` monitors macOS HIDIdleTime to detect when the user resumes keyboard/mouse activity. Once detected, it automatically turns the light off and exits.

## Configuration

The module uses hook event payloads passed from the AI tool. Example payload structure:

```json
{
  "hook_event_name": "UserPromptSubmit",
  "tool_name": "example_tool",
  "notification_type": "permission_prompt",
  "transcript_path": "/path/to/transcript",
  "turn_id": "turn_123"
}
```

The `status_light.py` script processes these events and sends appropriate commands to the ESP32 via the serial control interface.

## Troubleshooting

- **Light not responding**: Verify the ESP32 is flashed with the latest firmware and the serial port is detected
- **Hooks not running**: Check that hooks are installed in `~/.codex/hooks.json` or `~/.claude/settings.json`
- **Permission errors**: Ensure the hook scripts have execute permissions (`chmod +x`)
- **Idle monitor not working**: Verify you're on macOS (uses `ioreg` command) and the monitor process started successfully
- **Enable logging**: Set `STATUS_LIGHT_LOG=true` environment variable to write debug logs to `status_light.log`
