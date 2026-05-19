#include "vibration_motor.h"

#include "driver/gpio.h"
#include "esp_check.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/timers.h"
#include "sdkconfig.h"

#ifdef CONFIG_VIBRATION_MOTOR_ENABLE

static const char *TAG = "vibration_motor";
static TimerHandle_t s_vibration_timer;

#define MS_TO_TICKS_MIN_ONE(ms) ({            \
    TickType_t ticks = pdMS_TO_TICKS(ms);     \
    ticks > 0 ? ticks : 1;                    \
})

static void vibration_motor_timer_callback(TimerHandle_t timer)
{
    (void)timer;
    gpio_set_level(CONFIG_VIBRATION_MOTOR_GPIO, 0);
}

esp_err_t vibration_motor_init(void)
{
    gpio_config_t config = {
        .pin_bit_mask = 1ULL << CONFIG_VIBRATION_MOTOR_GPIO,
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    ESP_RETURN_ON_ERROR(gpio_config(&config), TAG, "configure vibration motor GPIO");

    s_vibration_timer = xTimerCreate("vibration_off",
                                     MS_TO_TICKS_MIN_ONE(1),
                                     pdFALSE,
                                     NULL,
                                     vibration_motor_timer_callback);
    if (s_vibration_timer == NULL) {
        return ESP_ERR_NO_MEM;
    }

    ESP_RETURN_ON_ERROR(vibration_motor_off(), TAG, "turn vibration motor off");

    ESP_LOGI(TAG, "Vibration motor configured on GPIO %d", CONFIG_VIBRATION_MOTOR_GPIO);
    return ESP_OK;
}

esp_err_t vibration_motor_vibrate(uint32_t duration_ms)
{
    if (duration_ms < 1 || duration_ms > 60000) {
        return ESP_ERR_INVALID_ARG;
    }

    if (s_vibration_timer == NULL) {
        return ESP_ERR_INVALID_STATE;
    }

    ESP_RETURN_ON_ERROR(gpio_set_level(CONFIG_VIBRATION_MOTOR_GPIO, 1),
                        TAG, "start vibration motor");
    if (xTimerChangePeriod(s_vibration_timer, MS_TO_TICKS_MIN_ONE(duration_ms), 0) != pdPASS ||
        xTimerStart(s_vibration_timer, 0) != pdPASS) {
        ESP_RETURN_ON_ERROR(vibration_motor_off(), TAG, "stop vibration motor after timer failure");
        return ESP_FAIL;
    }

    return ESP_OK;
}

esp_err_t vibration_motor_off(void)
{
    if (s_vibration_timer != NULL) {
        xTimerStop(s_vibration_timer, 0);
    }
    return gpio_set_level(CONFIG_VIBRATION_MOTOR_GPIO, 0);
}

#else

esp_err_t vibration_motor_init(void)
{
    return ESP_OK;
}

esp_err_t vibration_motor_vibrate(uint32_t duration_ms)
{
    (void)duration_ms;
    return ESP_ERR_NOT_SUPPORTED;
}

esp_err_t vibration_motor_off(void)
{
    return ESP_ERR_NOT_SUPPORTED;
}

#endif
