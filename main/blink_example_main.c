/* Blink Example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_log.h"
#include "led_strip.h"
#include "sdkconfig.h"

static const char *TAG = "example";

/* Use project configuration menu (idf.py menuconfig) to choose the GPIO to blink,
   or you can edit the following line and set a number here.
*/
#define BLINK_GPIO CONFIG_BLINK_GPIO
#define LED_COUNT 8

#ifdef CONFIG_BLINK_LED_STRIP
static uint8_t s_led_index = 0;
static uint8_t s_effect_mode = 0;
static uint8_t s_effect_phase = 0;
static const uint8_t s_led_reverse_order = 0; // 如果灯带线序反向，改成 1
#else
static uint8_t s_led_state = 0;
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

static void blink_led(void)
{
    led_strip_clear(led_strip);
    uint8_t display_index;
    uint8_t r = 0, g = 0, b = 0;

    switch (s_effect_mode) {
    case 0: // 单点追逐+渐变尾巴
        for (uint8_t i = 0; i < LED_COUNT; i++) {
            display_index = s_led_reverse_order ? (LED_COUNT - 1 - i) : i;
            int16_t distance = (int16_t)i - s_led_index;
            if (distance < 0) {
                distance += LED_COUNT;
            }
            if (distance < 3) {
                uint8_t intensity = 255 - distance * 80;
                wheel((s_effect_phase * 32 + i * 16) % 256, &r, &g, &b);
                led_strip_set_pixel(led_strip, display_index,
                                    (r * intensity) / 255,
                                    (g * intensity) / 255,
                                    (b * intensity) / 255);
            }
        }
        break;

    case 1: // 两色闪烁交替
        for (uint8_t i = 0; i < LED_COUNT; i++) {
            display_index = s_led_reverse_order ? (LED_COUNT - 1 - i) : i;
            if (((i + s_led_index) % 2) == 0) {
                led_strip_set_pixel(led_strip, display_index, 255, 80, 0);
            } else {
                led_strip_set_pixel(led_strip, display_index, 0, 80, 255);
            }
        }
        break;

    default: // 彩虹流动
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

static void blink_led(void)
{
    /* Set the GPIO level according to the state (LOW or HIGH)*/
    gpio_set_level(BLINK_GPIO, s_led_state);
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

void app_main(void)
{

    /* Configure the peripheral according to the LED type */
    configure_led();

    while (1) {
#ifdef CONFIG_BLINK_LED_STRIP
        ESP_LOGI(TAG, "Effect %d step %d", s_effect_mode, s_led_index);
        blink_led();
        s_led_index = (s_led_index + 1) % LED_COUNT;
        if (s_led_index == 0) {
            s_effect_phase = (s_effect_phase + 1) % 8;
            s_effect_mode = (s_effect_mode + 1) % 3;
        }
#else
        ESP_LOGI(TAG, "Turning the LED %s!", s_led_state == true ? "ON" : "OFF");
        blink_led();
        /* Toggle the LED state */
        s_led_state = !s_led_state;
#endif
        vTaskDelay(pdMS_TO_TICKS(80));
    }
}
