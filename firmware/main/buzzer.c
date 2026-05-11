#include "buzzer.h"

#include "driver/ledc.h"
#include "esp_check.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sdkconfig.h"

#ifdef CONFIG_BUZZER_ENABLE

static const char *TAG = "buzzer";

#define BUZZER_LEDC_MODE LEDC_LOW_SPEED_MODE
#define BUZZER_LEDC_TIMER LEDC_TIMER_1
#define BUZZER_LEDC_CHANNEL LEDC_CHANNEL_0
#define BUZZER_DUTY_RESOLUTION LEDC_TIMER_10_BIT
#define BUZZER_MAX_DUTY ((1 << 10) - 1)

static uint32_t duty_from_percent(uint8_t duty_percent)
{
    if (duty_percent > 100) {
        duty_percent = 100;
    }

    return (BUZZER_MAX_DUTY * duty_percent) / 100;
}

esp_err_t buzzer_init(void)
{
    ledc_timer_config_t timer_config = {
        .speed_mode = BUZZER_LEDC_MODE,
        .duty_resolution = BUZZER_DUTY_RESOLUTION,
        .timer_num = BUZZER_LEDC_TIMER,
        .freq_hz = 2000,
        .clk_cfg = LEDC_AUTO_CLK,
    };
    ESP_RETURN_ON_ERROR(ledc_timer_config(&timer_config), TAG, "configure LEDC timer");

    ledc_channel_config_t channel_config = {
        .gpio_num = CONFIG_BUZZER_GPIO,
        .speed_mode = BUZZER_LEDC_MODE,
        .channel = BUZZER_LEDC_CHANNEL,
        .intr_type = LEDC_INTR_DISABLE,
        .timer_sel = BUZZER_LEDC_TIMER,
        .duty = 0,
        .hpoint = 0,
    };
    ESP_RETURN_ON_ERROR(ledc_channel_config(&channel_config), TAG, "configure LEDC channel");

    ESP_LOGI(TAG, "Passive buzzer configured on GPIO %d", CONFIG_BUZZER_GPIO);
    return ESP_OK;
}

esp_err_t buzzer_tone(uint32_t frequency_hz, uint8_t duty_percent)
{
    if (frequency_hz < 20 || frequency_hz > 20000) {
        return ESP_ERR_INVALID_ARG;
    }

    ESP_RETURN_ON_ERROR(ledc_set_freq(BUZZER_LEDC_MODE, BUZZER_LEDC_TIMER, frequency_hz),
                        TAG, "set buzzer frequency");
    ESP_RETURN_ON_ERROR(ledc_set_duty(BUZZER_LEDC_MODE, BUZZER_LEDC_CHANNEL,
                                      duty_from_percent(duty_percent)),
                        TAG, "set buzzer duty");
    return ledc_update_duty(BUZZER_LEDC_MODE, BUZZER_LEDC_CHANNEL);
}

esp_err_t buzzer_beep(uint32_t frequency_hz, uint32_t duration_ms)
{
    if (duration_ms < 10 || duration_ms > 10000) {
        return ESP_ERR_INVALID_ARG;
    }

    ESP_RETURN_ON_ERROR(buzzer_tone(frequency_hz, CONFIG_BUZZER_DUTY_PERCENT),
                        TAG, "start beep");
    vTaskDelay(pdMS_TO_TICKS(duration_ms));
    return buzzer_off();
}

esp_err_t buzzer_off(void)
{
    ESP_RETURN_ON_ERROR(ledc_set_duty(BUZZER_LEDC_MODE, BUZZER_LEDC_CHANNEL, 0),
                        TAG, "clear buzzer duty");
    return ledc_update_duty(BUZZER_LEDC_MODE, BUZZER_LEDC_CHANNEL);
}

#else

esp_err_t buzzer_init(void)
{
    return ESP_OK;
}

esp_err_t buzzer_tone(uint32_t frequency_hz, uint8_t duty_percent)
{
    (void)frequency_hz;
    (void)duty_percent;
    return ESP_ERR_NOT_SUPPORTED;
}

esp_err_t buzzer_beep(uint32_t frequency_hz, uint32_t duration_ms)
{
    (void)frequency_hz;
    (void)duration_ms;
    return ESP_ERR_NOT_SUPPORTED;
}

esp_err_t buzzer_off(void)
{
    return ESP_ERR_NOT_SUPPORTED;
}

#endif
