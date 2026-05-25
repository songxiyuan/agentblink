#include "buzzer.h"

#include "driver/ledc.h"
#include "esp_check.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/timers.h"
#include "sdkconfig.h"

#ifdef CONFIG_BUZZER_ENABLE

static const char *TAG = "buzzer";

#define BUZZER_LEDC_MODE LEDC_LOW_SPEED_MODE
#define BUZZER_LEDC_TIMER LEDC_TIMER_1
#define BUZZER_LEDC_CHANNEL LEDC_CHANNEL_0
#define BUZZER_DUTY_RESOLUTION LEDC_TIMER_10_BIT
#define BUZZER_MAX_DUTY ((1 << 10) - 1)
#define MS_TO_TICKS_MIN_ONE(ms) ({            \
    TickType_t ticks = pdMS_TO_TICKS(ms);     \
    ticks > 0 ? ticks : 1;                    \
})

static TimerHandle_t s_beep_timer;
static TaskHandle_t s_drop_task;

static uint32_t duty_from_percent(uint8_t duty_percent)
{
    if (duty_percent > 100) {
        duty_percent = 100;
    }

    return (BUZZER_MAX_DUTY * duty_percent) / 100;
}

static esp_err_t buzzer_tone_raw(uint32_t frequency_hz, uint8_t duty_percent)
{
    ESP_RETURN_ON_ERROR(ledc_set_freq(BUZZER_LEDC_MODE, BUZZER_LEDC_TIMER, frequency_hz),
                        TAG, "set buzzer frequency");
    ESP_RETURN_ON_ERROR(ledc_set_duty(BUZZER_LEDC_MODE, BUZZER_LEDC_CHANNEL,
                                      duty_from_percent(duty_percent)),
                        TAG, "set buzzer duty");
    return ledc_update_duty(BUZZER_LEDC_MODE, BUZZER_LEDC_CHANNEL);
}

static esp_err_t buzzer_off_raw(void)
{
    ESP_RETURN_ON_ERROR(ledc_set_duty(BUZZER_LEDC_MODE, BUZZER_LEDC_CHANNEL, 0),
                        TAG, "clear buzzer duty");
    return ledc_update_duty(BUZZER_LEDC_MODE, BUZZER_LEDC_CHANNEL);
}

static void beep_timer_callback(TimerHandle_t timer)
{
    (void)timer;
    buzzer_off_raw();
}

static void buzzer_stop_drop_task(void)
{
    if (s_drop_task != NULL && s_drop_task != xTaskGetCurrentTaskHandle()) {
        vTaskDelete(s_drop_task);
        s_drop_task = NULL;
    }
}

static void buzzer_drop_task(void *arg)
{
    uint8_t count = (uint8_t)(uintptr_t)arg;
    static const uint32_t frequencies[] = {1400, 1000, 800, 600};
    static const uint32_t durations[] = {30, 30, 40, 60};
    const size_t pattern_length = sizeof(frequencies) / sizeof(frequencies[0]);

    for (uint8_t c = 0; c < count; c++) {
        for (size_t i = 0; i < pattern_length; i++) {
            if (buzzer_tone_raw(frequencies[i], 80) != ESP_OK) {
                buzzer_off_raw();
                s_drop_task = NULL;
                vTaskDelete(NULL);
                return;
            }
            vTaskDelay(pdMS_TO_TICKS(durations[i]));
        }
        buzzer_off_raw();
        if (c + 1 < count) {
            vTaskDelay(pdMS_TO_TICKS(120));
        }
    }

    s_drop_task = NULL;
    vTaskDelete(NULL);
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

    s_beep_timer = xTimerCreate("buzzer_beep_off",
                                MS_TO_TICKS_MIN_ONE(1),
                                pdFALSE,
                                NULL,
                                beep_timer_callback);
    if (s_beep_timer == NULL) {
        return ESP_ERR_NO_MEM;
    }

    ESP_LOGI(TAG, "Passive buzzer configured on GPIO %d", CONFIG_BUZZER_GPIO);
    return ESP_OK;
}

esp_err_t buzzer_tone(uint32_t frequency_hz, uint8_t duty_percent)
{
    if (frequency_hz < 20 || frequency_hz > 20000) {
        return ESP_ERR_INVALID_ARG;
    }

    if (s_beep_timer != NULL) {
        xTimerStop(s_beep_timer, 0);
    }
    buzzer_stop_drop_task();

    return buzzer_tone_raw(frequency_hz, duty_percent);
}

esp_err_t buzzer_beep(uint32_t frequency_hz, uint32_t duration_ms)
{
    if (duration_ms < 10 || duration_ms > 10000) {
        return ESP_ERR_INVALID_ARG;
    }

    if (s_beep_timer == NULL) {
        return ESP_ERR_INVALID_STATE;
    }

    buzzer_stop_drop_task();

    ESP_RETURN_ON_ERROR(buzzer_tone_raw(frequency_hz, CONFIG_BUZZER_DUTY_PERCENT),
                        TAG, "start beep");
    if (xTimerChangePeriod(s_beep_timer, pdMS_TO_TICKS(duration_ms), 0) != pdPASS ||
        xTimerStart(s_beep_timer, 0) != pdPASS) {
        ESP_RETURN_ON_ERROR(buzzer_off(), TAG, "stop buzzer after timer failure");
        return ESP_FAIL;
    }

    return ESP_OK;
}

esp_err_t buzzer_drop(uint8_t count)
{
    if (count == 0) {
        return ESP_ERR_INVALID_ARG;
    }

    if (s_beep_timer != NULL) {
        xTimerStop(s_beep_timer, 0);
    }
    buzzer_stop_drop_task();

    if (xTaskCreate(buzzer_drop_task, "buzzer_drop", 2048,
                    (void *)(uintptr_t)count, 10, &s_drop_task) != pdPASS) {
        s_drop_task = NULL;
        return ESP_ERR_NO_MEM;
    }

    return ESP_OK;
}

esp_err_t buzzer_off(void)
{
    if (s_beep_timer != NULL) {
        xTimerStop(s_beep_timer, 0);
    }
    buzzer_stop_drop_task();

    return buzzer_off_raw();
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

esp_err_t buzzer_drop(uint8_t count)
{
    (void)count;
    return ESP_ERR_NOT_SUPPORTED;
}

esp_err_t buzzer_off(void)
{
    return ESP_ERR_NOT_SUPPORTED;
}

#endif
