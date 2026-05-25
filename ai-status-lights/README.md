# AI Status Lights

AI tool lifecycle integration for ESP32 status light control. Automatically reflects the state of AI coding assistants (Codex, Claude Code) through visual feedback on an addressable LED.

[English](#ai-status-lights) | [中文](#ai-状态灯)

---

## AI 状态灯

AI 工具生命周期集成，用于 ESP32 状态灯控制。通过可寻址 LED 上的视觉反馈自动反映 AI 编程助手（Codex、Claude Code）的状态。

### 安装

1. 安装 serial-interface 依赖：
   ```sh
   cd ../serial-interface
   python3 install.py
   ```

2. 为你的 AI 工具安装全局钩子：
   ```sh
   # 对于 Codex
   ../scripts/install_codex_hooks.py
   
   # 对于 Claude Code
   ../scripts/install_claude_hooks.py
   
   # 对于两者
   ../scripts/install_codex_hooks.py --target all
   ```

如果 `pyserial` 已在你的 Python 运行时中可用，使用 `--no-deps`。

### 支持的工具

- **Codex** - 安装在全局 `~/.codex/hooks.json`
- **Claude Code** - 安装在全局 `~/.claude/settings.json`

### 工作原理

该模块通过钩子脚本将 AI 工具生命周期事件映射到 LED 状态：

#### 生命周期事件

- **SessionStart** - 灯关闭
- **UserPromptSubmit** - 灯进入追逐模式（跑马灯动画）
- **PreToolUse / PostToolUse / PostToolUseFailure** - 追逐模式（或等待用户输入时为黄色）
- **PermissionRequest / PermissionDenied / Notification** - 黄色呼吸灯
- **SubagentStart / SubagentStop / TaskCreated / TaskCompleted** - 追逐模式
- **Stop / SessionEnd** - 纯绿色（用户恢复输入后空闲监视器关闭）

#### 灯光状态

- **关闭** - 会话空闲或启动
- **追逐** - 任务运行或工具使用中
- **黄色** - 等待用户批准或输入
- **纯绿色** - 任务完成（空闲监视器活跃）

#### 空闲监视器

灯变为纯绿色后，`light_idle_monitor.py` 监视 macOS HIDIdleTime 以检测用户何时恢复键盘/鼠标活动。检测到后，它自动关闭灯并退出。

### 配置

该模块使用 AI 工具传递的钩子事件有效负载。示例有效负载结构：

```json
{
  "hook_event_name": "UserPromptSubmit",
  "tool_name": "example_tool",
  "notification_type": "permission_prompt",
  "transcript_path": "/path/to/transcript",
  "turn_id": "turn_123"
}
```

`status_light.py` 脚本处理这些事件并通过串口控制接口向 ESP32 发送适当的命令。

### 故障排除

- **灯不响应**: 验证 ESP32 已刷写最新固件且串口已检测到
- **钩子未运行**: 检查钩子是否安装在 `~/.codex/hooks.json` 或 `~/.claude/settings.json`
- **权限错误**: 确保钩子脚本有执行权限（`chmod +x`）
- **空闲监视器不工作**: 验证你在 macOS 上（使用 `ioreg` 命令）且监视器进程已成功启动
- **启用日志**: 设置 `STATUS_LIGHT_LOG=true` 环境变量以将调试日志写入 `status_light.log`

---

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
