#pragma once

#include <stdint.h>

#include "esp_err.h"

esp_err_t buzzer_init(void);
esp_err_t buzzer_tone(uint32_t frequency_hz, uint8_t duty_percent);
esp_err_t buzzer_beep(uint32_t frequency_hz, uint32_t duration_ms);
esp_err_t buzzer_drop(uint8_t count);
esp_err_t buzzer_off(void);

