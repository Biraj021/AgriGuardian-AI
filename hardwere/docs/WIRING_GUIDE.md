# Wiring guide

Default pins are DHT22 GPIO4, soil ADC GPIO34, rain digital GPIO35, HC-SR04 trigger GPIO5, HC-SR04 echo GPIO18, and relay GPIO26.

Use a common ground. ESP32 GPIO is 3.3V only: the HC-SR04 echo line requires a suitable level shifter or voltage divider before GPIO18. Do not power a pump from the ESP32. Use a correctly rated isolated relay/driver, supply, fuse, enclosure, and qualified electrical installation. Verify relay polarity and pump safety without a connected pump first.

For the water-level percentage, measure the ultrasonic-sensor distance when the tank is empty and full, then set `WATER_EMPTY_DISTANCE_CM` and `WATER_FULL_DISTANCE_CM` in the local `config.h`. These two values are installation-specific calibration values.
