# Firmware setup

1. Copy `hardwere/config/config.h.example` to `config.h`; do not commit it.
2. Install ESP32 board support, DHT sensor library, PubSubClient, and ArduinoJson.
3. Open `firmware/08_relay_control/agriguardian_node.ino` in Arduino IDE.
4. Verify relay polarity with no pump attached before connecting a load.

The firmware defaults the relay off at boot, on broker disconnect, on malformed commands, and after the configured maximum runtime. It has not been compiled or tested against physical hardware in this workspace.
