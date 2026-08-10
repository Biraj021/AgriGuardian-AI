# AgriGuardian AI IoT Node

`hardwere/` is the current hardware directory name used by this repository.

## Contents

- `firmware/08_relay_control/agriguardian_node.ino`: ESP32 firmware.
- `config/config.h.example`: Wi-Fi, MQTT, device-ID, pin, and calibration template.
- `docs/`: wiring, library, firmware setup, calibration, and MQTT guides.

## MQTT contract

| Topic | ESP32 direction | Purpose |
|---|---|---|
| `agriguardian/farm/{device_id}/telemetry` | Publish | Temperature, humidity, soil moisture, rainfall, water level |
| `agriguardian/farm/{device_id}/status` | Publish | Online/pump heartbeat status |
| `agriguardian/farm/{device_id}/control` | Subscribe | Validated `PUMP_ON` / `PUMP_OFF` commands |

The backend validates that `{device_id}` matches a known active device MAC address before persisting telemetry. Hardware, broker, and relay behavior still require field verification.

## Quick start

1. Copy `config/config.h.example` to a local `config.h`.
2. Set Wi-Fi, MQTT, and the device MAC/ID to the value registered in the backend.
3. Follow [WIRING_GUIDE.md](docs/WIRING_GUIDE.md) and [FIRMWARE_SETUP.md](docs/FIRMWARE_SETUP.md).
4. Compile/upload with Arduino IDE or PlatformIO.
