# Hardware — AgriGuardian AI IoT Node

## Overview

The hardware layer consists of an **ESP32 microcontroller** connected to:
- **DHT22** — Temperature + Humidity sensor
- **Capacitive Soil Moisture Sensor** — Soil water content
- **Rain Sensor** — Rainfall detection
- **HC-SR04 or Float Sensor** — Water level measurement
- **4-Channel Relay Module** — Irrigation pump control

## Folder Contents

```
hardware/
├── esp32/
│   ├── firmware/        ← Main Arduino/PlatformIO firmware
│   ├── config/          ← WiFi/MQTT/pin configuration
│   └── libraries/       ← Custom sensor libraries
├── schematics/          ← Fritzing circuit diagrams
├── pcb/                 ← PCB layout (future)
└── docs/
    ├── WIRING_GUIDE.md  ← Step-by-step setup
    ├── LIBRARIES.md     ← Required Arduino libraries
    └── SENSOR_CALIBRATION.md
```

## Quick Start

1. See [WIRING_GUIDE.md](docs/WIRING_GUIDE.md) for circuit connections
2. Install required libraries listed in [LIBRARIES.md](docs/LIBRARIES.md)
3. Copy `config/config.h.example` to `config/config.h`
4. Fill in your WiFi and MQTT credentials
5. Flash to ESP32 via Arduino IDE or PlatformIO

## MQTT Topics

| Topic | Direction | Payload |
|---|---|---|
| `agriguardian/farm/{device_id}/telemetry` | Publish | JSON sensor data |
| `agriguardian/farm/{device_id}/control` | Subscribe | JSON control command |
| `agriguardian/farm/{device_id}/status` | Publish | Device heartbeat |

## Sensor Pin Map (Default)

| Sensor | Pin |
|---|---|
| DHT22 Data | GPIO4 |
| Soil Moisture Analog | GPIO34 |
| Rain Sensor Digital | GPIO35 |
| Water Level Trigger | GPIO5 |
| Water Level Echo | GPIO18 |
| Relay 1 (Pump) | GPIO26 |
