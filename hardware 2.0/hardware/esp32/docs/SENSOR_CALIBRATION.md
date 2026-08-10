# Sensor Calibration

Set `SOIL_DRY_VALUE` using the sensor in air and `SOIL_WET_VALUE` using the sensor's sensing section in water. The firmware maps dry to 0% and wet to 100%.

Set `RAIN_THRESHOLD` from observed dry/wet raw values. The firmware reports both `rain_raw` and `raining`; rain detection is not rainfall in millimetres.

Set `TANK_HEIGHT_CM` to the distance from the HC-SR04 face to the tank bottom. Mount the ultrasonic sensor at the tank top, facing down. Verify readings with an empty and full tank.
