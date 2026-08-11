# Hardware Libraries — AgriGuardian AI

## Required Arduino Libraries

Install these libraries via **Arduino IDE → Sketch → Include Library → Manage Libraries**

| Library | Version | Installed Via | Purpose |
|---|---|---|---|
| `DHT sensor library` | 1.4.6+ | Library Manager | DHT22 temperature + humidity |
| `Adafruit Unified Sensor` | 1.1.14+ | Library Manager | Dependency for DHT library |
| `PubSubClient` | 2.8.0+ | Library Manager | MQTT publish/subscribe for ESP32 |
| `ArduinoJson` | 7.x | Library Manager | Build JSON payloads for MQTT messages |
| `WiFi` | Built-in | ESP32 Core | WiFi connection (included with ESP32 board package) |

## Step-by-Step Library Installation

### 1. DHT Sensor Library

1. Open Arduino IDE
2. Go to **Sketch → Include Library → Manage Libraries**
3. Search for `DHT sensor library` by **Adafruit**
4. Click **Install** — when prompted to install dependencies, click **Install All**

### 2. PubSubClient (MQTT)

1. In Library Manager, search for `PubSubClient` by **Nick O'Leary**
2. Click **Install**

> ⚠️ **Important**: PubSubClient has a default MQTT message size limit of 256 bytes.
> Our JSON payloads may exceed this. You must increase the buffer size.
> See [SETUP_GUIDE.md](SETUP_GUIDE.md#mqtt-buffer-fix) for the fix.

### 3. ArduinoJson

1. In Library Manager, search for `ArduinoJson` by **Benoit Blanchon**
2. Install version **7.x** (NOT 5.x — the API is completely different)

## Verifying Installation

After installing all libraries, open:

**File → Examples → DHT sensor library → DHTtester**

If it compiles without errors, your libraries are correctly installed.

## ESP32 Board Package

Before installing libraries, you need the ESP32 board support package.
See [SETUP_GUIDE.md](SETUP_GUIDE.md) for installation instructions.

## Library Files Location

On Windows:
```
C:\Users\<YourUsername>\Documents\Arduino\libraries\
```

On Mac:
```
~/Documents/Arduino/libraries/
```
