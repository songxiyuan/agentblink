idf_component_register(SRCS "blink_main.c" "buzzer.c" "vibration_motor.c"
                       INCLUDE_DIRS "."
                       PRIV_REQUIRES esp_driver_gpio esp_driver_uart esp_driver_ledc esp_driver_usb_serial_jtag led_strip)
