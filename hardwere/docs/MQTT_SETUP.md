# MQTT setup

Topics use `agriguardian/farm/{device_id}/telemetry`, `control`, and `status`.

Telemetry must contain a `device_id` that exactly matches the topic device ID and may contain `temperature`, `humidity`, `soil_moisture`, `rainfall`, and `water_level`. The backend validates ranges and persists all five values to SQLite for known active devices.

The backend currently provides authenticated HTTP ingestion at `POST /api/v1/sensor/ingest` and an optional authenticated control endpoint at `POST /api/v1/device/{device_id}/control`. It publishes only validated `PUMP_ON` (with a bounded duration) and `PUMP_OFF` commands when MQTT configuration is present.

FastAPI starts an MQTT telemetry/status subscriber when `MQTT_BROKER_HOST` is configured. It subscribes to the telemetry and status wildcards, rejects malformed/unknown-device messages, and updates `last_seen_at` plus status. A real broker/device integration test is still required before claiming physical MQTT operation.

## Production security requirements

The repository's `deploy/docker/mosquitto.conf` permits anonymous connections **only for local development**. Do not expose it to the internet. For production:

1. Set non-empty `MQTT_USERNAME` and `MQTT_PASSWORD` through the deployment secret store; never commit them.
2. Set `allow_anonymous false` and configure a Mosquitto password file.
3. Use separate device credentials where the broker supports them, and restrict each device to its own `agriguardian/farm/{device_id}/telemetry`, `status`, and `control` topics.
4. Require TLS with a trusted CA and do not expose the unauthenticated port publicly.
5. Keep the backend subscriber as the only principal allowed to read telemetry wildcards; retain backend known-device validation as defence in depth.
