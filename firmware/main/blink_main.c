/* Blink Example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/uart.h"
#if CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG_ENABLED
#include "driver/usb_serial_jtag.h"
#endif
#include "esp_log.h"
#include "buzzer.h"
#include "vibration_motor.h"
#include "led_strip.h"
#include "sdkconfig.h"

static const char *TAG = "example";

/* Use project configuration menu (idf.py menuconfig) to choose the GPIO to blink,
   or you can edit the following line and set a number here.
*/
#define BLINK_GPIO CONFIG_BLINK_GPIO
#define LED_COUNT 8
#define UART_PORT CONFIG_ESP_CONSOLE_UART_NUM
#define UART_RX_BUF_SIZE 1024
#define UART_CMD_BUF_SIZE 96
#define SERIAL_PROBE_COMMAND "probe"
#define SERIAL_PROBE_RESPONSE "ESP32_LIGHT_OK"

typedef enum {
    LIGHT_EFFECT_OFF = 0,
    LIGHT_EFFECT_SOLID,
    LIGHT_EFFECT_CHASE,
    LIGHT_EFFECT_ALTERNATE,
    LIGHT_EFFECT_RAINBOW,
    LIGHT_EFFECT_YELLOW_BLINK,
    LIGHT_EFFECT_AUTO,
} light_effect_t;

#ifdef CONFIG_BLINK_LED_STRIP
static volatile uint8_t s_led_index = 0;
static volatile float s_led_position = 0.0;
static volatile uint8_t s_effect_phase = 0;
static volatile uint8_t s_solid_r = 255;
static volatile uint8_t s_solid_g = 255;
static volatile uint8_t s_solid_b = 255;
static const uint8_t s_led_reverse_order = 0; // 如果灯带线序反向，改成 1
#else
static volatile uint8_t s_led_state = 0;
#endif
static volatile light_effect_t s_effect = LIGHT_EFFECT_OFF;
#ifdef CONFIG_BLINK_LED_STRIP
static volatile uint32_t s_effect_delay_ms = 160;
#else
static volatile uint32_t s_effect_delay_ms = CONFIG_BLINK_PERIOD;
#endif

#ifdef CONFIG_BLINK_LED_STRIP

static led_strip_handle_t led_strip;

static void wheel(uint8_t pos, uint8_t *r, uint8_t *g, uint8_t *b)
{
    if (pos < 85) {
        *r = pos * 3;
        *g = 255 - pos * 3;
        *b = 0;
    } else if (pos < 170) {
        pos -= 85;
        *r = 255 - pos * 3;
        *g = 0;
        *b = pos * 3;
    } else {
        pos -= 170;
        *r = 0;
        *g = pos * 3;
        *b = 255 - pos * 3;
    }
}

static const char *effect_name(light_effect_t effect)
{
    switch (effect) {
    case LIGHT_EFFECT_OFF:
        return "off";
    case LIGHT_EFFECT_SOLID:
        return "solid";
    case LIGHT_EFFECT_CHASE:
        return "chase";
    case LIGHT_EFFECT_ALTERNATE:
        return "alternate";
    case LIGHT_EFFECT_RAINBOW:
        return "rainbow";
    case LIGHT_EFFECT_YELLOW_BLINK:
        return "yellow";
    case LIGHT_EFFECT_AUTO:
        return "auto";
    default:
        return "unknown";
    }
}

static light_effect_t current_strip_effect(void)
{
    if (s_effect != LIGHT_EFFECT_AUTO) {
        return s_effect;
    }

    switch (s_effect_phase % 3) {
    case 0:
        return LIGHT_EFFECT_CHASE;
    case 1:
        return LIGHT_EFFECT_ALTERNATE;
    default:
        return LIGHT_EFFECT_RAINBOW;
    }
}

static uint32_t current_effect_delay_ms(void)
{
    if (current_strip_effect() == LIGHT_EFFECT_YELLOW_BLINK) {
        return 60;
    }
    if (current_strip_effect() == LIGHT_EFFECT_CHASE) {
        return 100;  // 增加延迟到100ms，使流水灯速度慢一点（约8秒一圈）
    }

    return s_effect_delay_ms;
}

static void blink_led(void)
{
    led_strip_clear(led_strip);
    uint8_t display_index;
    uint8_t r = 0, g = 0, b = 0;
    light_effect_t effect = current_strip_effect();

    switch (effect) {
    case LIGHT_EFFECT_OFF:
        break;

    case LIGHT_EFFECT_SOLID:
        for (uint8_t i = 0; i < LED_COUNT; i++) {
            display_index = s_led_reverse_order ? (LED_COUNT - 1 - i) : i;
            led_strip_set_pixel(led_strip, display_index, s_solid_r, s_solid_g, s_solid_b);
        }
        break;

    case LIGHT_EFFECT_CHASE: // 单点追逐+渐变尾巴，头部渐变亮，尾巴渐变灭
        for (uint8_t i = 0; i < LED_COUNT; i++) {
            display_index = s_led_reverse_order ? (LED_COUNT - 1 - i) : i;
            float distance = (float)i - s_led_position;
            if (distance < 0) {
                distance += LED_COUNT;
            }
            if (distance >= -0.5 && distance <= 3.5) {
                float fade = 1.0;
                if (distance < 1.0) {
                    // 头部渐变亮，从-0.5到1
                    fade = (distance + 0.5) / 1.5;
                } else {
                    // 尾巴渐变灭，从1到3.5
                    fade = (3.5 - distance) / 2.5;
                }
                uint8_t intensity = (uint8_t)(fade * 255);
                wheel((s_effect_phase * 32 + i * 16) % 256, &r, &g, &b);
                led_strip_set_pixel(led_strip, display_index,
                                    (r * intensity) / 255,
                                    (g * intensity) / 255,
                                    (b * intensity) / 255);
            }
        }
        break;

    case LIGHT_EFFECT_ALTERNATE: // 两色闪烁交替
        for (uint8_t i = 0; i < LED_COUNT; i++) {
            display_index = s_led_reverse_order ? (LED_COUNT - 1 - i) : i;
            if (((i + s_led_index) % 2) == 0) {
                led_strip_set_pixel(led_strip, display_index, 255, 80, 0);
            } else {
                led_strip_set_pixel(led_strip, display_index, 0, 80, 255);
            }
        }
        break;

    case LIGHT_EFFECT_RAINBOW: // 彩虹流动
        for (uint8_t i = 0; i < LED_COUNT; i++) {
            display_index = s_led_reverse_order ? (LED_COUNT - 1 - i) : i;
            wheel((s_led_index * 8 + i * 24) % 256, &r, &g, &b);  // 降低颜色更新频率
            led_strip_set_pixel(led_strip, display_index, r, g, b);
        }
        break;

    case LIGHT_EFFECT_YELLOW_BLINK:
        static const uint8_t breathe_steps[] = {
            4, 5, 6, 7, 8, 10, 12, 14,
            16, 19, 22, 26, 30, 35, 40, 46,
            52, 59, 66, 75, 84, 94, 104, 116,
            128, 141, 154, 167, 180, 192, 204, 216,
            226, 234, 242, 248, 252, 255, 255, 252,
            248, 242, 234, 226, 216, 204, 192, 180,
            167, 154, 141, 128, 116, 104, 94, 84,
            75, 66, 59, 52, 46, 40, 35, 30,
            26, 22, 19, 16, 14, 12, 10, 8,
            7, 6, 5, 4
        };
        uint8_t intensity = breathe_steps[s_led_index % (sizeof(breathe_steps) / sizeof(breathe_steps[0]))];
        for (uint8_t i = 0; i < LED_COUNT; i++) {
            display_index = s_led_reverse_order ? (LED_COUNT - 1 - i) : i;
            led_strip_set_pixel(led_strip, display_index,
                                (255 * intensity) / 255,
                                (180 * intensity) / 255,
                                0);
        }
        break;

    case LIGHT_EFFECT_AUTO:
    default:
        for (uint8_t i = 0; i < LED_COUNT; i++) {
            display_index = s_led_reverse_order ? (LED_COUNT - 1 - i) : i;
            wheel((s_led_index * 16 + i * 24) % 256, &r, &g, &b);
            led_strip_set_pixel(led_strip, display_index, r, g, b);
        }
        break;
    }

    led_strip_refresh(led_strip);
}

static void configure_led(void)
{
    ESP_LOGI(TAG, "Example configured to blink addressable LED!");
    /* LED strip initialization with the GPIO and pixels number*/
    led_strip_config_t strip_config = {
        .strip_gpio_num = BLINK_GPIO,
        .max_leds = 8, // use 8 LEDs for running light
    };
#if CONFIG_BLINK_LED_STRIP_BACKEND_RMT
    led_strip_rmt_config_t rmt_config = {
        .resolution_hz = 10 * 1000 * 1000, // 10MHz
        .flags.with_dma = false,
    };
    ESP_ERROR_CHECK(led_strip_new_rmt_device(&strip_config, &rmt_config, &led_strip));
#elif CONFIG_BLINK_LED_STRIP_BACKEND_SPI
    led_strip_spi_config_t spi_config = {
        .spi_bus = SPI2_HOST,
        .flags.with_dma = true,
    };
    ESP_ERROR_CHECK(led_strip_new_spi_device(&strip_config, &spi_config, &led_strip));
#else
#error "unsupported LED strip backend"
#endif
    /* Set all LED off to clear all pixels */
    led_strip_clear(led_strip);
    led_strip_refresh(led_strip);
}

#elif CONFIG_BLINK_LED_GPIO

static const char *effect_name(light_effect_t effect)
{
    switch (effect) {
    case LIGHT_EFFECT_OFF:
        return "off";
    case LIGHT_EFFECT_SOLID:
        return "on";
    case LIGHT_EFFECT_AUTO:
    case LIGHT_EFFECT_CHASE:
    case LIGHT_EFFECT_ALTERNATE:
    case LIGHT_EFFECT_RAINBOW:
    case LIGHT_EFFECT_YELLOW_BLINK:
        return "blink";
    default:
        return "unknown";
    }
}

static void blink_led(void)
{
    /* Set the GPIO level according to the state (LOW or HIGH)*/
    gpio_set_level(BLINK_GPIO, s_led_state);
}

static uint32_t current_effect_delay_ms(void)
{
    return s_effect_delay_ms;
}

static void configure_led(void)
{
    ESP_LOGI(TAG, "Example configured to blink GPIO LED!");
    gpio_reset_pin(BLINK_GPIO);
    /* Set the GPIO as a push/pull output */
    gpio_set_direction(BLINK_GPIO, GPIO_MODE_OUTPUT);
}

#else
#error "unsupported LED type"
#endif

static void print_help(void)
{
#ifdef CONFIG_BLINK_LED_STRIP
    printf("\nCommands:\n");
    printf("  help                 show this help\n");
    printf("  probe                identify this ESP32 controller\n");
    printf("  off                  turn all LEDs off\n");
    printf("  auto                 cycle chase/alternate/rainbow\n");
    printf("  chase                running light with fading tail\n");
    printf("  alternate            alternating orange/blue\n");
    printf("  rainbow              flowing rainbow\n");
    printf("  yellow               blinking yellow light\n");
    printf("  solid R G B          solid color\n");
    printf("  speed MS             animation delay, 10-5000 ms\n\n");
#else
    printf("\nCommands:\n");
    printf("  help                 show this help\n");
    printf("  probe                identify this ESP32 controller\n");
    printf("  off                  turn LED off\n");
    printf("  on                   turn LED on\n");
    printf("  blink                blink LED\n");
    printf("  yellow               blink LED in yellow mode\n");
    printf("  speed MS             blink delay, 10-5000 ms\n\n");
#endif
#ifdef CONFIG_BUZZER_ENABLE
    printf("Buzzer commands:\n");
    printf("  beep [FREQ] [MS]     play a short beep, default 2000 Hz 200 ms\n");
    printf("  tone FREQ [DUTY]     keep passive buzzer on, duty 1-90 percent\n");
    printf("  drop [COUNT]         play water drop sound, optional repeat count 1-10\n");
    printf("  buzzer off           turn passive buzzer off\n\n");
#endif
#ifdef CONFIG_VIBRATION_MOTOR_ENABLE
    printf("Vibration motor commands:\n");
    printf("  vibrate MS           set motor GPIO high for 1-60000 ms\n");
    printf("  motor MS             same as vibrate MS\n\n");
#endif
}

static int parse_long_arg(const char *arg, long min, long max, long *value)
{
    if (arg == NULL) {
        return -1;
    }

    char *endptr = NULL;
    long parsed = strtol(arg, &endptr, 10);
    if (*arg == '\0' || *endptr != '\0' || parsed < min || parsed > max) {
        return -1;
    }

    *value = parsed;
    return 0;
}

#ifdef CONFIG_BLINK_LED_STRIP
static int parse_byte_arg(const char *arg, uint8_t *value)
{
    long parsed = 0;
    if (parse_long_arg(arg, 0, 255, &parsed) != 0) {
        return -1;
    }

    *value = (uint8_t)parsed;
    return 0;
}
#endif

static void handle_serial_command(char *line)
{
    char *cmd = strtok(line, " \t\r\n");
    if (cmd == NULL) {
        return;
    }

    if (strcmp(cmd, SERIAL_PROBE_COMMAND) == 0) {
        printf("%s\n", SERIAL_PROBE_RESPONSE);
        return;
    } else if (strcmp(cmd, "help") == 0 || strcmp(cmd, "?") == 0) {
        print_help();
    }
#ifdef CONFIG_BUZZER_ENABLE
    else if (strcmp(cmd, "beep") == 0) {
        long frequency_hz = 2000;
        long duration_ms = 200;
        char *freq_arg = strtok(NULL, " \t\r\n");
        char *duration_arg = strtok(NULL, " \t\r\n");

        if ((freq_arg != NULL && parse_long_arg(freq_arg, 20, 20000, &frequency_hz) != 0) ||
            (duration_arg != NULL && parse_long_arg(duration_arg, 10, 10000, &duration_ms) != 0)) {
            printf("Invalid beep. Use: beep [20..20000] [10..10000]\n");
            return;
        }

        if (buzzer_beep((uint32_t)frequency_hz, (uint32_t)duration_ms) != ESP_OK) {
            printf("Buzzer is disabled or failed to beep\n");
            return;
        }
        printf("Beep: %ld Hz, %ld ms\n", frequency_hz, duration_ms);
        return;
    } else if (strcmp(cmd, "drop") == 0) {
        long count = 1;
        char *count_arg = strtok(NULL, " \t\r\n");

        if (count_arg != NULL && parse_long_arg(count_arg, 1, 10, &count) != 0) {
            printf("Invalid drop count. Use: drop [1..10]\n");
            return;
        }

        if (buzzer_drop((uint8_t)count) != ESP_OK) {
            printf("Buzzer is disabled or failed to play drop sound\n");
            return;
        }
        printf("Water drop: %ld time(s)\n", count);
        return;
    } else if (strcmp(cmd, "tone") == 0) {
        long frequency_hz = 0;
        long duty_percent = CONFIG_BUZZER_DUTY_PERCENT;
        char *freq_arg = strtok(NULL, " \t\r\n");
        char *duty_arg = strtok(NULL, " \t\r\n");

        if (parse_long_arg(freq_arg, 20, 20000, &frequency_hz) != 0 ||
            (duty_arg != NULL && parse_long_arg(duty_arg, 1, 90, &duty_percent) != 0)) {
            printf("Invalid tone. Use: tone 20..20000 [1..90]\n");
            return;
        }

        if (buzzer_tone((uint32_t)frequency_hz, (uint8_t)duty_percent) != ESP_OK) {
            printf("Buzzer is disabled or failed to start tone\n");
            return;
        }
        printf("Tone: %ld Hz, duty %ld%%\n", frequency_hz, duty_percent);
        return;
    } else if (strcmp(cmd, "buzzer") == 0) {
        char *arg = strtok(NULL, " \t\r\n");
        if (arg != NULL && strcmp(arg, "off") == 0) {
            if (buzzer_off() != ESP_OK) {
                printf("Buzzer is disabled or failed to stop\n");
                return;
            }
            printf("Buzzer off\n");
            return;
        }
        printf("Invalid buzzer command. Use: buzzer off\n");
        return;
    }
#endif
#ifdef CONFIG_VIBRATION_MOTOR_ENABLE
    else if (strcmp(cmd, "vibrate") == 0 || strcmp(cmd, "motor") == 0) {
        long duration_ms = 0;
        char *duration_arg = strtok(NULL, " \t\r\n");

        if (parse_long_arg(duration_arg, 1, 60000, &duration_ms) != 0) {
            printf("Invalid motor duration. Use: vibrate 1..60000\n");
            return;
        }

        if (vibration_motor_vibrate((uint32_t)duration_ms) != ESP_OK) {
            printf("Vibration motor is disabled or failed to vibrate\n");
            return;
        }
        printf("Vibration motor: %ld ms\n", duration_ms);
        return;
    }
#endif
    else if (strcmp(cmd, "off") == 0) {
        s_effect = LIGHT_EFFECT_OFF;
#ifdef CONFIG_BLINK_LED_STRIP
        s_led_index = 0;
#endif
    } else if (strcmp(cmd, "speed") == 0) {
        char *arg = strtok(NULL, " \t\r\n");
        char *endptr = NULL;
        long parsed = arg ? strtol(arg, &endptr, 10) : -1;
        if (arg == NULL || *endptr != '\0' || parsed < 10 || parsed > 5000) {
            printf("Invalid speed. Use: speed 10..5000\n");
            return;
        }
        s_effect_delay_ms = (uint32_t)parsed;
#ifdef CONFIG_BLINK_LED_STRIP
    } else if (strcmp(cmd, "auto") == 0) {
        s_effect = LIGHT_EFFECT_AUTO;
        s_led_index = 0;
        s_effect_phase = 0;
    } else if (strcmp(cmd, "chase") == 0) {
        s_effect = LIGHT_EFFECT_CHASE;
        s_led_position = 0.0;
    } else if (strcmp(cmd, "alternate") == 0 || strcmp(cmd, "blink") == 0) {
        s_effect = LIGHT_EFFECT_ALTERNATE;
        s_led_index = 0;
    } else if (strcmp(cmd, "rainbow") == 0) {
        s_effect = LIGHT_EFFECT_RAINBOW;
        s_led_index = 0;
    } else if (strcmp(cmd, "yellow") == 0) {
        s_effect = LIGHT_EFFECT_YELLOW_BLINK;
        s_led_index = 0;
    } else if (strcmp(cmd, "solid") == 0) {
        uint8_t r, g, b;
        if (parse_byte_arg(strtok(NULL, " \t\r\n"), &r) != 0 ||
            parse_byte_arg(strtok(NULL, " \t\r\n"), &g) != 0 ||
            parse_byte_arg(strtok(NULL, " \t\r\n"), &b) != 0) {
            printf("Invalid color. Use: solid R G B, color values 0-255\n");
            return;
        }
        if (strtok(NULL, " \t\r\n") != NULL) {
            printf("Invalid color. Use: solid R G B, buzzer is controlled separately with beep/tone commands\n");
            return;
        }
        s_solid_r = r;
        s_solid_g = g;
        s_solid_b = b;
        s_effect = LIGHT_EFFECT_SOLID;
#else
    } else if (strcmp(cmd, "on") == 0) {
        s_effect = LIGHT_EFFECT_SOLID;
        s_led_state = 1;
    } else if (strcmp(cmd, "blink") == 0 || strcmp(cmd, "auto") == 0) {
        s_effect = LIGHT_EFFECT_AUTO;
    } else if (strcmp(cmd, "yellow") == 0) {
        s_effect = LIGHT_EFFECT_YELLOW_BLINK;
#endif
    } else {
        printf("Unknown command: %s\n", cmd);
        print_help();
        return;
    }

    printf("Current effect: %s, speed: %lu ms\n",
           effect_name(s_effect),
           (unsigned long)s_effect_delay_ms);
}

static void feed_command_byte(char ch, char *line, size_t *line_len, size_t line_size)
{
    if (ch == '\r' || ch == '\n') {
        if (*line_len > 0) {
            line[*line_len] = '\0';
            handle_serial_command(line);
            *line_len = 0;
        }
    } else if (*line_len < line_size - 1) {
        line[(*line_len)++] = ch;
    } else {
        *line_len = 0;
        printf("Command too long\n");
    }
}

static void serial_command_task(void *arg)
{
    uint8_t data[UART_CMD_BUF_SIZE];
    char line[UART_CMD_BUF_SIZE];
    size_t line_len = 0;

    while (1) {
        // Traditional ESP32 dev boards usually expose USB through CP210x/CH34x
        // chips wired to UART0. Commands from that path arrive here.
        int len = uart_read_bytes(UART_PORT, data, sizeof(data), pdMS_TO_TICKS(50));
        for (int i = 0; i < len; i++) {
            feed_command_byte((char)data[i], line, &line_len, sizeof(line));
        }
    }
}

#if CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG_ENABLED
static void usb_serial_jtag_command_task(void *arg)
{
    uint8_t data[UART_CMD_BUF_SIZE];
    char line[UART_CMD_BUF_SIZE];
    size_t line_len = 0;

    while (1) {
        // ESP32-C3/S3 boards can expose a native USB-Serial/JTAG port. It looks
        // like a serial port on the host, but it is not UART0 inside the chip.
        int len = usb_serial_jtag_read_bytes(data, sizeof(data), pdMS_TO_TICKS(50));
        for (int i = 0; i < len; i++) {
            feed_command_byte((char)data[i], line, &line_len, sizeof(line));
        }
    }
}
#endif

static void configure_serial_commands(void)
{
    uart_config_t uart_config = {
        .baud_rate = CONFIG_ESP_CONSOLE_UART_BAUDRATE,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };

    ESP_ERROR_CHECK(uart_driver_install(UART_PORT, UART_RX_BUF_SIZE, 0, 0, NULL, 0));
    ESP_ERROR_CHECK(uart_param_config(UART_PORT, &uart_config));
    ESP_ERROR_CHECK(uart_set_pin(UART_PORT, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE,
                                 UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE));
    xTaskCreate(serial_command_task, "serial_command", 3072, NULL, 10, NULL);
#if CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG_ENABLED
    // Keep the same command language available on native USB boards while
    // preserving UART0 support for boards with an external USB-UART bridge.
    usb_serial_jtag_driver_config_t usb_serial_jtag_config = {
        .rx_buffer_size = UART_RX_BUF_SIZE,
        .tx_buffer_size = UART_RX_BUF_SIZE,
    };
    ESP_ERROR_CHECK(usb_serial_jtag_driver_install(&usb_serial_jtag_config));
    xTaskCreate(usb_serial_jtag_command_task, "usb_serial_command", 3072, NULL, 10, NULL);
#endif
    print_help();
}

void app_main(void)
{

    /* Configure the peripheral according to the LED type */
    configure_led();
    ESP_ERROR_CHECK(buzzer_init());
    ESP_ERROR_CHECK(vibration_motor_init());
    configure_serial_commands();

    while (1) {
#ifdef CONFIG_BLINK_LED_STRIP
        blink_led();
        if (current_strip_effect() == LIGHT_EFFECT_CHASE) {
            s_led_position += 0.1;
            if (s_led_position >= LED_COUNT) {
                s_led_position -= LED_COUNT;
                s_effect_phase = (s_effect_phase + 1) % 8;
            }
        } else {
            uint8_t effect_steps = current_strip_effect() == LIGHT_EFFECT_YELLOW_BLINK ? 76 : LED_COUNT;
            s_led_index = (s_led_index + 1) % effect_steps;
            if (s_led_index == 0) {
                s_effect_phase = (s_effect_phase + 1) % 8;
            }
        }
#else
        if (s_effect == LIGHT_EFFECT_OFF) {
            s_led_state = 0;
        } else if (s_effect == LIGHT_EFFECT_SOLID) {
            s_led_state = 1;
        } else {
            s_led_state = !s_led_state;
        }
        blink_led();
#endif
        vTaskDelay(pdMS_TO_TICKS(current_effect_delay_ms()));
    }
}
