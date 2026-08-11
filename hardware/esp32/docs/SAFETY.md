# Pump & Relay Safety

## General Rules

- Keep all relay-controlled devices disconnected while compiling and sensor-testing.
- Use a low-voltage test load (LED or small lamp) before connecting a real pump, valve, or fan.
- Keep a manual power disconnect or emergency switch for every relay-controlled load.

## Firmware Safety Features

The firmware enforces multiple layers of safety:

| Feature | Description |
|---|---|
| **Default OFF** | All relays start logically OFF on boot |
| **Command validation** | Only well-formed JSON commands are accepted; malformed commands are rejected and logged |
| **Max runtime** | Each relay channel has a configurable max continuous runtime (`MAX_RELAY_RUNTIME_MS`, default 5 minutes). After this time, the relay is forced OFF regardless of MQTT state |
| **MQTT disconnect** | All active relays are forced OFF when MQTT connection is lost (configurable via `RELAY_OFF_ON_MQTT_DISCONNECT`) |
| **OTA safety** | All relays are forced OFF when an OTA firmware update begins |
| **Deep sleep guard** | Deep sleep is skipped if any relay is currently ON — the firmware never sleeps while a pump is running |
| **Watchdog** | If the firmware hangs, the watchdog auto-resets the ESP32, which then reinitializes all relays to OFF |

## Hardware Safety

Software cannot guarantee an active-low relay is OFF before ESP32 GPIO initialization. Use hardware pull-up/driver circuitry and test boot/reset behavior with each relay channel.

## Pre-Connection Checklist

Before connecting any real load to a relay channel, verify the following via Serial Monitor:

1. Sensor values and validity flags display correctly
2. `[WIFI]` connection messages appear
3. `[MQTT]` connection messages appear
4. `[RELAY] Initialized N channel(s), all OFF` appears
5. Send a malformed MQTT command and confirm it is rejected
6. Test a valid ON command with a low-voltage test load only
7. Test OFF command
8. Wait for max runtime timeout and confirm auto-OFF
9. Disconnect WiFi (unplug router or change SSID) and confirm all relays turn OFF
10. Disconnect MQTT broker and confirm all relays turn OFF
11. Only then connect the real load

## Multi-Relay Notes

- Channel 0 (pump) is the most safety-critical — test it most thoroughly
- Channels 1-3 have the same safety enforcement (max runtime, MQTT disconnect, etc.)
- Each channel operates independently — one channel timing out does not affect others
- The backend currently only controls the pump (channel 0). Channels 1-3 require backend updates for remote control.

## Deep Sleep Limitations

When deep sleep is enabled (`DEEP_SLEEP_ENABLED true`):
- The ESP32 is completely powered off during sleep — it cannot receive MQTT commands
- Relay/pump remote control is effectively disabled in this mode
- Use deep sleep ONLY for battery-powered sensor-only nodes (no relays)
