from setuptools import setup

setup(
    name='esp32-device-control',
    version='0.1.0',
    description='Python serial interface for ESP32 device control',
    py_modules=['esp32_light_control', 'esp32_event_control'],
    install_requires=[
        'pyserial>=3.5',
        'colorama>=0.4.6',
    ],
    python_requires='>=3.8',
)
