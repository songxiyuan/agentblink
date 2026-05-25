# agentblink

Visual feedback for AI coding assistants through ESP32-based status lights.

[English](#agentblink) | [中文](#agentblink-中文)

---

## agentblink 中文

为 AI 编程助手提供 ESP32 状态灯视觉反馈。

### 功能特性

- **AI 工具集成** - 自动为 Codex 和 Claude Code 提供状态灯
- **多种 LED 效果** - 追逐、彩虹、呼吸、纯色等多种效果
- **音频和触觉反馈** - 支持蜂鸣器和振动马达
- **易于安装** - 全局钩子实现与 AI 工具的无缝集成
- **跨平台支持** - 支持 macOS、Linux 和 Windows (WSL)
- **模块化设计** - 可独立使用或组合使用各个组件

### 快速开始

#### 对于 AI 工具用户（5 分钟）

```bash
# 1. 刷写固件到 ESP32
cd esp32-device-control/firmware
idf.py set-target esp32
idf.py flash

# 2. 安装串口接口
cd ../../serial-interface
python3 install.py

# 3. 安装 AI 工具钩子
cd ../ai-status-lights
python3 scripts/install_claude_hooks.py

# 4. 测试状态灯
python3 ../serial-interface/esp32_light_control.py rainbow
```

#### 对于开发者

详见 [快速开始指南](docs/GETTING_STARTED.md)

### 模块

agentblink 由三个独立模块组成：

#### ESP32 设备控制
ESP32 状态灯的硬件抽象层。提供支持可寻址 LED 灯条、GPIO LED、蜂鸣器和振动马达的固件。

**位置:** `esp32-device-control/`  
**详见:** [README](esp32-device-control/README.md)

#### 串口接口
用于与 ESP32 设备通信的 Python 库。包括命令行工具和 Python API，用于设备控制和自动检测。

**位置:** `serial-interface/`  
**详见:** [README](serial-interface/README.md)

#### AI 状态灯
AI 编程助手的集成层。将 AI 工具生命周期事件映射到通过钩子脚本的视觉反馈。

**位置:** `ai-status-lights/`  
**详见:** [README](ai-status-lights/README.md)

### 文档

- **[快速开始](docs/GETTING_STARTED.md)** - 不同用户的设置指南
- **[架构设计](docs/ARCHITECTURE.md)** - 系统设计和模块交互
- **[贡献指南](docs/CONTRIBUTING.md)** - 开发指南和贡献流程

### 支持的硬件

| 支持的目标 | ESP32 | ESP32-C2 | ESP32-C3 | ESP32-C5 | ESP32-C6 | ESP32-C61 | ESP32-H2 | ESP32-H21 | ESP32-H4 | ESP32-P4 | ESP32-S2 | ESP32-S3 |
| --------- | ----- | -------- | -------- | -------- | -------- | --------- | -------- | --------- | -------- | -------- | -------- | -------- |

**可选组件:**
- 可寻址 LED 灯条 (WS2812B/NeoPixel)
- 无源蜂鸣器模块
- 振动马达

### 示例

查看 `examples/` 目录获取完整的工作示例：
- 基础 LED 控制
- 串口通信模式
- 钩子集成示例

### 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

### 支持

- **问题反馈**: [GitHub Issues](https://github.com/yourusername/agentblink/issues)
- **讨论**: [GitHub Discussions](https://github.com/yourusername/agentblink/discussions)
- **文档**: 查看 `docs/` 目录

---

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
