# MQTT Setup

Set Wi-Fi and MQTT values in the local `config.h`; keep it out of Git. Start from `config.h.example`.

Topics for `DEVICE_ID`:

- Publish telemetry: `agriguardian/farm/{device_id}/telemetry`
- Subscribe control: `agriguardian/farm/{device_id}/control`
- Publish status: `agriguardian/farm/{device_id}/status`

Telemetry includes temperature, humidity, soil percentage/raw ADC, rain raw/boolean, water level, pump state, and `timestamp_ms`. `timestamp_ms` is ESP32 uptime, not UTC time. The backend stores its own UTC receipt time.

Control accepts only `{"pump":true}` and `{"pump":false}`. Never expose broker credentials or permit direct untrusted clients to publish control commands.

## Backend registration and broker setup

Set `MQTT_ENABLED=true`, `MQTT_HOST`, `MQTT_PORT`, `MQTT_CLIENT_ID`, and optional credentials in the backend `.env`. The backend subscribes to telemetry/status and only stores messages from an existing active `devices` record whose `external_id` exactly matches the ESP32 `DEVICE_ID`.

Before powering the node, register a device in the existing SQLite `devices` table for its farm, then set its `external_id` to the exact value from firmware, for example `agriguardian-esp32-001`. Unknown IDs are rejected and logged; the backend never auto-registers devices from MQTT traffic.

For a local Mosquitto broker, use the same host and port in ESP32 `config.h` and backend `.env`. Plain port 1883 is suitable only for a trusted local network. TLS and broker ACLs are required before production deployment.
