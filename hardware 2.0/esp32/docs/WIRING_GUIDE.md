# AgriGuardian ESP32 Wiring Guide

Use a common ground between ESP32, sensors, relay control supply, and the low-voltage pump test supply.

## Sensor Connections

| Device | ESP32 Connection | Notes |
|---|---|---|
| DHT22 data | GPIO4 | Add a 10 kΩ pull-up to 3.3V if the module does not include one |
| Soil sensor analog out | GPIO34 | Power the sensor from 3.3V so its output never exceeds 3.3V |
| Rain sensor analog out | GPIO35 | Ensure output is at most 3.3V |
| HC-SR04 Trigger | GPIO5 | |
| HC-SR04 Echo | GPIO18 | **Through a voltage divider or level shifter** |

⚠️ Standard HC-SR04 Echo is 5V. A direct Echo-to-GPIO18 connection can damage the ESP32. Use a divider, for example 1 kΩ from Echo to GPIO18 and 2 kΩ from GPIO18 to GND.

## Relay Module Connections

| Relay Channel | ESP32 Pin | Default Function |
|---|---|---|
| Relay IN1 | GPIO26 | Pump |
| Relay IN2 | GPIO27 | Solenoid valve / spare |
| Relay IN3 | GPIO14 | Fan / spare |
| Relay IN4 | GPIO12 | Light / spare |

The relay module needs its own power supply (VCC/JD-VCC and GND). Do not power the relay coils from the ESP32 3.3V pin.

## Status LED

The built-in LED on GPIO2 is used for status indication. No external wiring needed. If your board does not have a built-in LED on GPIO2, connect an LED with a 220Ω resistor from GPIO2 to GND.

## Safety Notes

- Do not power a pump from the ESP32. Use an appropriately rated separate supply and relay/driver.
- Test first with a low-voltage lamp or LED load.
- An active-low relay also needs external pull-up/driver circuitry so it remains OFF during ESP32 boot/reset.
- When using multiple relay channels, ensure each controlled device has its own appropriately rated power supply.
- Keep a manual power disconnect or emergency switch for each relay-controlled load.
