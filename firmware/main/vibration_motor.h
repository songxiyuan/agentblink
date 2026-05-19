#pragma once

#include <stdint.h>

#include "esp_err.h"

esp_err_t vibration_motor_init(void);
esp_err_t vibration_motor_vibrate(uint32_t duration_ms);
esp_err_t vibration_motor_off(void);
