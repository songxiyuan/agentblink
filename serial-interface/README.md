# Serial Interface

Python serial interface for ESP32 device control. Provides command-line tools and Python APIs for controlling LED patterns, audio output, and event handling on ESP32 microcontrollers.

[English](#serial-interface) | [中文](#串口接口)

---

## 串口接口

用于 ESP32 设备控制的 Python 串口接口。提供命令行工具和 Python API，用于控制 ESP32 微控制器上的 LED 模式、音频输出和事件处理。

### 安装

#### 从源代码安装

```bash
pip install -r requirements.txt
```

或作为包安装：

```bash
pip install -e .
```

#### 要求

- Python 3.8+
- pyserial>=3.5
- colorama>=0.4.6

### 快速开始

#### Python API

```python
from esp32_light_control import ESP32LightControl

# 创建控制器实例
controller = ESP32LightControl()

# 自动检测 ESP32 设备
controller.probe_and_connect()

# 发送命令
controller.send_command("solid 255 0 0")  # 红色灯
controller.send_command("chase")           # 追逐模式
controller.send_command("off")             # 关闭
```

#### 命令行使用

列出可用的串口：
```bash
python esp32_light_control.py --list-ports
```

发送灯光命令：
```bash
python esp32_light_control.py -p /dev/cu.usbserial-0001 solid 255 0 0
```

交互模式：
```bash
python esp32_light_control.py -p /dev/cu.usbserial-0001 interactive
```

常用命令：
- `off` - 关闭灯光
- `solid R G B` - 设置纯色（RGB 值 0-255）
- `chase` - 追逐模式
- `rainbow` - 彩虹模式
- `blink` - 闪烁模式
- `beep FREQ MS` - 蜂鸣声
- `vibrate MS` - 振动时长

### API 参考

#### ESP32LightControl

用于控制 ESP32 设备上 LED 模式和音频的主类。

**方法:**
- `probe_and_connect()` - 自动检测并连接到 ESP32
- `send_command(command)` - 发送命令字符串
- `close()` - 关闭串口连接

#### ESP32EventControl

ESP32 设备的事件处理和配置。

详见 `esp32_event_control.py` 获取详细的 API 文档。

### 测试

运行测试套件：

```bash
pytest tests/
```

运行覆盖率测试：

```bash
pytest --cov=. tests/
```

类型检查：

```bash
mypy esp32_light_control.py esp32_event_control.py
```

---

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
