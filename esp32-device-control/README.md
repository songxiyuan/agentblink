# ESP32 Device Control

Hardware abstraction library for ESP32-based status lights with LED strips, buzzers, and vibration motors.

[English](#esp32-device-control) | [中文](#esp32-设备控制)

---

## ESP32 设备控制

用于 ESP32 状态灯的硬件抽象库，支持 LED 灯条、蜂鸣器和振动马达。

### 功能特性

- **可寻址 LED 灯条控制**: 支持 WS2812B/NeoPixel LED 灯条的多种效果
  - 纯色
  - 追逐（带衰减尾部的跑马灯）
  - 交替颜色
  - 彩虹流动
  - 黄色呼吸效果
  - 自动循环效果
- **GPIO LED 支持**: 简单的 GPIO LED 开关控制
- **蜂鸣器控制**: 无源蜂鸣器支持，可配置频率和时长
  - 自定义频率和时长的蜂鸣
  - 音调生成
  - 水滴音效
- **振动马达**: 可配置时长的触觉反馈
- **串口命令接口**: UART/USB-Serial 远程控制
- **FreeRTOS 集成**: 支持并发操作的多任务处理

### 前置要求

- ESP-IDF (v5.0 或更高版本)
- ESP32、ESP32-C3 或 ESP32-S3 开发板
- 可选: WS2812B LED 灯条（用于可寻址 LED 效果）
- 可选: 无源蜂鸣器模块
- 可选: 振动马达模块

### 构建和刷写

#### 配置项目

```bash
cd esp32-device-control/firmware
idf.py menuconfig
```

关键配置选项：
- `CONFIG_BLINK_GPIO`: LED GPIO 引脚（默认: GPIO8）
- `CONFIG_BLINK_LED_STRIP`: 启用可寻址 LED 灯条支持
- `CONFIG_BLINK_LED_GPIO`: 启用简单 GPIO LED 支持
- `CONFIG_BUZZER_ENABLE`: 启用蜂鸣器支持
- `CONFIG_VIBRATION_MOTOR_ENABLE`: 启用振动马达支持

#### 构建固件

```bash
idf.py build
```

#### 刷写到设备

```bash
idf.py flash
```

#### 监控串口输出

```bash
idf.py monitor
```

### 串口协议

设备通过 UART 通信（通常在开发板上作为 USB-Serial 暴露）。命令以纯文本形式发送，以换行符结尾。

#### 命令格式

```
COMMAND [ARG1] [ARG2] ...
```

#### LED 命令

- `off` - 关闭所有 LED
- `on` - 打开 LED（仅 GPIO 模式）
- `blink` - 闪烁 LED（GPIO 模式）或循环效果（LED 灯条模式）
- `auto` - 循环追逐、交替和彩虹效果
- `chase` - 带衰减尾部的跑马灯
- `alternate` - 橙蓝交替颜色
- `rainbow` - 流动彩虹效果
- `yellow` - 黄色闪烁呼吸效果
- `solid R G B` - 设置纯色（仅 LED 灯条，值 0-255）
- `speed MS` - 设置动画延迟（毫秒，10-5000）

#### 蜂鸣器命令

- `beep [FREQ] [MS]` - 播放蜂鸣声（默认: 2000 Hz, 200 ms）
- `tone FREQ [DUTY]` - 生成连续音调（占空比 1-90%）
- `drop [COUNT]` - 播放水滴音效（1-10 次重复）
- `buzzer off` - 关闭蜂鸣器

#### 振动马达命令

- `vibrate MS` - 振动指定毫秒数（1-60000）
- `motor MS` - vibrate 的别名

#### 系统命令

- `probe` - 识别设备（响应 "ESP32_LIGHT_OK"）
- `help` - 显示可用命令

### 架构

#### 主要文件

- `firmware/main/blink_main.c` - 主应用逻辑和串口命令处理
- `firmware/main/buzzer.c/h` - 蜂鸣器控制实现
- `firmware/main/vibration_motor.c/h` - 振动马达控制实现
- `firmware/main/led_strip.h` - LED 灯条驱动接口

#### 关键组件

**串口命令任务**: 从 UART/USB-Serial 读取命令并分发到相应处理程序。

**LED 效果引擎**: 管理 LED 状态并使用 FreeRTOS 任务以可配置的间隔渲染效果。

**外设驱动**: 蜂鸣器、马达和 LED 灯条硬件的抽象。

### 贡献

详见主项目 [CONTRIBUTING.md](../docs/CONTRIBUTING.md) 了解提交问题和拉取请求的指南。

---

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
