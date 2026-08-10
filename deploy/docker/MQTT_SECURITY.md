# MQTT deployment security

The included `mosquitto.conf` is intentionally development-only and allows
anonymous local connections so that the ESP32 sample configuration can be used
on a trusted local network. It is not a production broker configuration.

Before deployment, configure Mosquitto with `allow_anonymous false`, a password
file stored outside the repository, TLS certificates supplied by the deployment
platform, and ACLs equivalent to:

```text
device:<device_id> publish agriguardian/farm/<device_id>/telemetry
device:<device_id> publish agriguardian/farm/<device_id>/status
device:<device_id> subscribe agriguardian/farm/<device_id>/control
backend             read    agriguardian/farm/+/telemetry
backend             read    agriguardian/farm/+/status
backend             write   agriguardian/farm/+/control
```

Backend database validation remains required: a topic/device ID must map to an
active registered device before telemetry is persisted.
