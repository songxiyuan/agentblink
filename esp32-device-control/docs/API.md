# ESP32 Device Control API Reference

## Command Protocol

All commands are sent via UART/USB-Serial as ASCII text, terminated with a newline character (`\n` or `\r\n`).

### Response Format

- **Success**: `Current effect: [EFFECT_NAME], speed: [MS] ms`
- **Error**: `[ERROR_MESSAGE]`
- **Probe Response**: `ESP32_LIGHT_OK`

## LED Commands

### LED_OFF

Turn all LEDs off.

**Command**: `off`

**Response**: `Current effect: off, speed: 160 ms`

**Example**:
```
> off
Current effect: off, speed: 160 ms
```

### LED_ON

Turn LED on (GPIO mode only).

**Command**: `on`

**Response**: `Current effect: on, speed: 160 ms`

**Example**:
```
> on
Current effect: on, speed: 160 ms
```

### LED_BLINK

Blink LED (GPIO mode) or cycle through effects (LED strip mode).

**Command**: `blink` or `alternate`

**Response**: `Current effect: blink, speed: 160 ms`

**Example**:
```
> blink
Current effect: blink, speed: 160 ms
```

### LED_CHASE

Running light effect with fading tail (LED strip only).

**Command**: `chase`

**Response**: `Current effect: chase, speed: 100 ms`

**Example**:
```
> chase
Current effect: chase, speed: 100 ms
```

### LED_PULSE

Blinking yellow breathing effect.

**Command**: `yellow`

**Response**: `Current effect: yellow, speed: 60 ms`

**Example**:
```
> yellow
Current effect: yellow, speed: 60 ms
```

### LED_ALTERNATE

Alternating orange and blue colors (LED strip only).

**Command**: `alternate`

**Response**: `Current effect: alternate, speed: 160 ms`

**Example**:
```
> alternate
Current effect: alternate, speed: 160 ms
```

### LED_RAINBOW

Flowing rainbow effect (LED strip only).

**Command**: `rainbow`

**Response**: `Current effect: rainbow, speed: 160 ms`

**Example**:
```
> rainbow
Current effect: rainbow, speed: 160 ms
```

### LED_AUTO

Cycle through chase, alternate, and rainbow effects (LED strip only).

**Command**: `auto`

**Response**: `Current effect: auto, speed: 160 ms`

**Example**:
```
> auto
Current effect: auto, speed: 160 ms
```

### LED_SOLID

Set solid color (LED strip only).

**Command**: `solid R G B`

**Parameters**:
- `R`: Red component (0-255)
- `G`: Green component (0-255)
- `B`: Blue component (0-255)

**Response**: `Current effect: solid, speed: 160 ms`

**Example**:
```
> solid 255 0 0
Current effect: solid, speed: 160 ms
```

### LED_SPEED

Set animation delay in milliseconds.

**Command**: `speed MS`

**Parameters**:
- `MS`: Delay in milliseconds (10-5000)

**Response**: `Current effect: [CURRENT_EFFECT], speed: [MS] ms`

**Example**:
```
> speed 200
Current effect: chase, speed: 200 ms
```

## Buzzer Commands

### BUZZER_BEEP

Play a beep sound.

**Command**: `beep [FREQ] [MS]`

**Parameters**:
- `FREQ`: Frequency in Hz (20-20000, default: 2000)
- `MS`: Duration in milliseconds (10-10000, default: 200)

**Response**: `Beep: [FREQ] Hz, [MS] ms`

**Example**:
```
> beep 2000 200
Beep: 2000 Hz, 200 ms
```

### BUZZER_ALARM

Play water drop sound effect.

**Command**: `drop [COUNT]`

**Parameters**:
- `COUNT`: Number of repetitions (1-10, default: 1)

**Response**: `Water drop: [COUNT] time(s)`

**Example**:
```
> drop 3
Water drop: 3 time(s)
```

### BUZZER_TONE

Generate continuous tone.

**Command**: `tone FREQ [DUTY]`

**Parameters**:
- `FREQ`: Frequency in Hz (20-20000, required)
- `DUTY`: Duty cycle percentage (1-90, default: 50)

**Response**: `Tone: [FREQ] Hz, duty [DUTY]%`

**Example**:
```
> tone 1000 50
Tone: 1000 Hz, duty 50%
```

### BUZZER_OFF

Turn off buzzer.

**Command**: `buzzer off`

**Response**: `Buzzer off`

**Example**:
```
> buzzer off
Buzzer off
```

## Motor Commands

### MOTOR_VIBRATE

Vibrate motor for specified duration.

**Command**: `vibrate MS` or `motor MS`

**Parameters**:
- `MS`: Duration in milliseconds (1-60000)

**Response**: `Vibration motor: [MS] ms`

**Example**:
```
> vibrate 500
Vibration motor: 500 ms
```

## System Commands

### PROBE

Identify the device.

**Command**: `probe`

**Response**: `ESP32_LIGHT_OK`

**Example**:
```
> probe
ESP32_LIGHT_OK
```

### HELP

Display available commands.

**Command**: `help` or `?`

**Response**: Prints help text with all available commands

**Example**:
```
> help
Commands:
  help                 show this help
  probe                identify this ESP32 controller
  off                  turn all LEDs off
  auto                 cycle chase/alternate/rainbow
  chase                running light with fading tail
  ...
```

## Error Responses

### Invalid Command

```
Unknown command: [COMMAND]
```

### Invalid Arguments

```
Invalid [COMMAND]. Use: [USAGE]
```

Examples:
- `Invalid beep. Use: beep [20..20000] [10..10000]`
- `Invalid speed. Use: speed 10..5000`
- `Invalid color. Use: solid R G B, color values 0-255`

### Disabled Features

```
[FEATURE] is disabled or failed to [ACTION]
```

Examples:
- `Buzzer is disabled or failed to beep`
- `Vibration motor is disabled or failed to vibrate`
