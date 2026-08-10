# Hardware — AgriGuardian AI IoT Node

## Overview

The hardware layer consists of an **ESP32 microcontroller** connected to:
- **DHT22** — Temperature + Humidity sensor
- **Capacitive Soil Moisture Sensor** — Soil water content
- **Rain Sensor** — Rainfall detection
- **HC-SR04 or Float Sensor** — Water level measurement
- **4-Channel Relay Module** — Irrigation pump + 3 spare channels (valves, fans, lights)

## Features (v2.0)

| Feature | Description |
|---|---|
| **Sensor Smoothing** | Median filter (soil, rain) + EMA (water level) for noise reduction |
| **Multi-Relay** | 4-channel relay control with per-channel safety limits |
| **Watchdog Timer** | Auto-resets ESP32 if firmware hangs (30s timeout) |
| **LED Status** | Built-in LED shows WiFi/MQTT/sensor health via blink patterns |
| **Offline Buffering** | Telemetry stored in SPIFFS when MQTT is down, flushed on reconnect |
| **OTA Updates** | Password-protected over-the-air firmware updates |
| **Deep Sleep** | Optional battery-powered mode for sensor-only field nodes |
| **PlatformIO** | Proper build system with pinned dependencies |

## Folder Contents

```
hardware/
├── esp32/
│   ├── firmware/
│   │   └── agriguardian_esp32/
│   │       ├── agriguardian_esp32.ino   ← Main sketch
│   │       ├── config.h                  ← Private config (git-ignored)
│   │       ├── config.h.example          ← Config template
│   │       ├── sensors.h                 ← Sensor reading + smoothing
│   │       ├── wifi_manager.h            ← WiFi connection
│   │       ├── mqtt_client.h             ← MQTT pub/sub + buffer flush
│   │       ├── relay_control.h           ← Multi-channel relay safety
│   │       ├── watchdog.h                ← Hardware watchdog timer
│   │       ├── led_status.h              ← LED status indicator
│   │       ├── telemetry_buffer.h        ← Offline SPIFFS buffer
│   │       ├── ota_update.h              ← OTA firmware updates
│   │       ├── power_manager.h           ← Deep sleep management
│   │       └── platformio.ini            ← PlatformIO build config
│   ├── config/                           ← Legacy pointer only
│   └── docs/
│       ├── WIRING_GUIDE.md
│       ├── LIBRARIES.md
│       ├── SENSOR_CALIBRATION.md
│       ├── MQTT_SETUP.md
│       ├── SAFETY.md
│       └── OTA_GUIDE.md
├── schematics/                           ← Circuit diagrams (future)
├── pcb/                                  ← PCB layout (future)
└── docs/
    ├── SETUP_GUIDE.md
    ├── LIBRARIES.md
    └── SENSOR_CALIBRATION.md
```

## Quick Start

1. See [ESP32 wiring](esp32/docs/WIRING_GUIDE.md) before applying power.
2. Install required libraries listed in [ESP32 libraries](esp32/docs/LIBRARIES.md).
3. Copy `esp32/firmware/agriguardian_esp32/config.h.example` to `config.h` in the same folder
4. Fill in your WiFi and MQTT credentials
5. Flash to ESP32 via Arduino IDE or PlatformIO

## Active Firmware

The only active Arduino sketch is `esp32/firmware/agriguardian_esp32/`.
Its `config.h` sits beside the `.ino` file and is included as `#include "config.h"`.
`esp32/config/config.h.example` is a legacy pointer only; do not use it for builds.

Read the [MQTT setup](esp32/docs/MQTT_SETUP.md), [calibration guide](esp32/docs/SENSOR_CALIBRATION.md), [safety guide](esp32/docs/SAFETY.md), and [OTA guide](esp32/docs/OTA_GUIDE.md) before connecting a relay or pump.

## MQTT Topics

| Topic | Direction | Payload |
|---|---|---|
| `agriguardian/farm/{device_id}/telemetry` | Publish | JSON sensor data |
| `agriguardian/farm/{device_id}/control` | Subscribe | JSON control command |
| `agriguardian/farm/{device_id}/status` | Publish | Device heartbeat |

## Control Commands

| Command | Action |
|---|---|
| `{"pump":true}` | Turn pump (relay ch0) ON |
| `{"pump":false}` | Turn pump (relay ch0) OFF |
| `{"relay":N,"state":true}` | Turn relay channel N ON (0-3) |
| `{"relay":N,"state":false}` | Turn relay channel N OFF (0-3) |

## Sensor Pin Map (Default)

| Sensor | Pin |
|---|---|
| DHT22 Data | GPIO4 |
| Soil Moisture Analog | GPIO34 |
| Rain Sensor Analog | GPIO35 |
| Water Level Trigger | GPIO5 |
| Water Level Echo | GPIO18 |
| Relay 1 (Pump) | GPIO26 |
| Relay 2 (Valve) | GPIO27 |
| Relay 3 (Fan) | GPIO14 |
| Relay 4 (Light) | GPIO12 |
| Status LED | GPIO2 (built-in) |

## LED Status Patterns

| Pattern | Meaning |
|---|---|
| Fast blink (100ms) | WiFi connecting |
| Slow blink (500ms) | WiFi OK, MQTT connecting |
| Solid ON | Fully connected, healthy |
| Double flash | Sensor error detected |
| OFF | Deep sleep or LED disabled |
