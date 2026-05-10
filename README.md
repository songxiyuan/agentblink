| Supported Targets | ESP32 | ESP32-C2 | ESP32-C3 | ESP32-C5 | ESP32-C6 | ESP32-C61 | ESP32-H2 | ESP32-H21 | ESP32-H4 | ESP32-P4 | ESP32-S2 | ESP32-S3 |
| ----------------- | ----- | -------- | -------- | -------- | -------- | --------- | -------- | --------- | -------- | -------- | -------- | -------- |

# Blink Example

(See the README.md file in the upper level 'examples' directory for more information about examples.)

This example demonstrates how to blink a LED by using the GPIO driver or using the [led_strip](https://components.espressif.com/component/espressif/led_strip) library if the LED is addressable e.g. [WS2812](https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf). The `led_strip` library is installed via [component manager](main/idf_component.yml).

## How to Use Example

Before project configuration and build, be sure to set the correct chip target using `idf.py set-target <chip_name>`.

### Hardware Required

* A development board with normal LED or addressable LED on-board (e.g., ESP32-S3-DevKitC, ESP32-C6-DevKitC etc.)
* A USB cable for Power supply and programming

See [Development Boards](https://www.espressif.com/en/products/devkits) for more information about it.

### Configure the Project

Open the project configuration menu (`idf.py menuconfig`).

In the `Example Configuration` menu:

* Select the LED type in the `Blink LED type` option.
  * Use `GPIO` for regular LED
  * Use `LED strip` for addressable LED
* If the LED type is `LED strip`, select the backend peripheral
  * `RMT` is only available for ESP targets with RMT peripheral supported
  * `SPI` is available for all ESP targets
* Set the GPIO number used for the signal in the `Blink GPIO number` option.
* Set the blinking period in the `Blink period in ms` option.

### Build and Flash

Run `idf.py -p PORT flash monitor` to build, flash and monitor the project.

(To exit the serial monitor, type ``Ctrl-]``.)

### Serial Commands

After flashing, type a command in the serial monitor and press Enter.

For LED strip mode:

* `help` - show available commands
* `probe` - identify this ESP32 controller for the Python script
* `off` - turn all LEDs off
* `auto` - cycle through chase, alternate, and rainbow effects
* `chase` - running light with a fading tail
* `alternate` - alternating orange/blue LEDs
* `rainbow` - flowing rainbow effect
* `yellow` - blinking yellow alert
* `solid R G B` - solid color, for example `solid 255 0 0`
* `speed MS` - animation delay from 10 to 5000 ms, for example `speed 120`

For GPIO LED mode:

* `help`
* `probe`
* `off`
* `on`
* `blink`
* `yellow`
* `speed MS`

### Python Serial Control

Install the Python serial dependency:

```sh
python3 -m pip install pyserial
```

Find the ESP32 serial port:

```sh
python3 esp32_light_control.py --list-ports
```

Send commands from Python:

```sh
python3 esp32_light_control.py rainbow
python3 esp32_light_control.py solid 255 0 0
python3 esp32_light_control.py speed 120
python3 esp32_light_control.py off
```

The script probes each serial port and selects the one that responds with the ESP32 light controller signature. Flash the latest firmware first so the `probe` command is available. If needed, specify the port manually:

```sh
python3 esp32_light_control.py -p /dev/cu.usbserial-0001 chase
```

For a manual prompt:

```sh
python3 esp32_light_control.py interactive
```

### Codex Status Lights

Codex status lights are installed globally in `~/.codex/hooks.json` and call scripts in `~/.codex/hooks/`:

* Task running: `chase`
* Task finished: solid green
* Approval or input needed: yellow breathing light
* Session start or other idle state: off

The global hook caches the detected serial port in `~/.codex/hooks/light_port`, so it works from any Codex project after the first successful probe.

See the [Getting Started Guide](https://docs.espressif.com/projects/esp-idf/en/latest/get-started/index.html) for full steps to configure and use ESP-IDF to build projects.

## Example Output

As you run the example, you will see the LED blinking, according to the previously defined period. For the addressable LED, you can also change the LED color by setting the `led_strip_set_pixel(led_strip, 0, 16, 16, 16);` (LED Strip, Pixel Number, Red, Green, Blue) with values from 0 to 255 in the [source file](main/blink_example_main.c).

```text
I (315) example: Example configured to blink addressable LED!
I (325) example: Turning the LED OFF!
I (1325) example: Turning the LED ON!
I (2325) example: Turning the LED OFF!
I (3325) example: Turning the LED ON!
I (4325) example: Turning the LED OFF!
I (5325) example: Turning the LED ON!
I (6325) example: Turning the LED OFF!
I (7325) example: Turning the LED ON!
I (8325) example: Turning the LED OFF!
```

Note: The color order could be different according to the LED model.

The pixel number indicates the pixel position in the LED strip. For a single LED, use 0.

## Troubleshooting

* If the LED isn't blinking, check the GPIO or the LED type selection in the `Example Configuration` menu.

For any technical queries, please open an [issue](https://github.com/espressif/esp-idf/issues) on GitHub. We will get back to you soon.
