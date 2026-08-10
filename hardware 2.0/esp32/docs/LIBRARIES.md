# ESP32 Libraries

## Required Arduino Libraries

Install from Arduino IDE Library Manager:

- **DHT sensor library** by Adafruit (v1.4.6+)
- **Adafruit Unified Sensor** by Adafruit (v1.1.14+)
- **PubSubClient** by Nick O'Leary (v2.8.0+)

## Built-in (No Install Needed)

These come with the ESP32 Arduino board package or the C++ toolchain:

- `WiFi.h` — WiFi connection
- `Arduino.h` — Core Arduino API
- `ctype.h` — Character classification
- `SPIFFS.h` — SPI Flash File System (for offline telemetry buffering)
- `ArduinoOTA.h` — Over-the-air firmware updates
- `esp_task_wdt.h` — Hardware watchdog timer (ESP-IDF)
- `esp_sleep.h` — Deep sleep management (ESP-IDF)

## Board Package

Install the **ESP32 by Espressif Systems** board package. See [SETUP_GUIDE.md](../../docs/SETUP_GUIDE.md) for full installation instructions.

## PlatformIO Alternative

If using PlatformIO instead of Arduino IDE, all dependencies are declared in `platformio.ini` and installed automatically on first build:

```bash
pio run          # Compile (auto-installs dependencies)
pio run -t upload  # Flash to ESP32
```

The `platformio.ini` also sets `MQTT_MAX_PACKET_SIZE=1024` via a build flag, eliminating the need to manually patch PubSubClient.h.

## MQTT Buffer Fix (Arduino IDE Only)

If using Arduino IDE, increase the PubSubClient buffer size manually:

1. Find: `C:\Users\<YourName>\Documents\Arduino\libraries\PubSubClient\src\PubSubClient.h`
2. Change: `#define MQTT_MAX_PACKET_SIZE 256` to `#define MQTT_MAX_PACKET_SIZE 1024`
3. Save the file

This is NOT needed if using PlatformIO (the build flag handles it).

## Notes

- ArduinoJson is **not used** by this firmware. JSON is built with String concatenation to avoid the dependency.
