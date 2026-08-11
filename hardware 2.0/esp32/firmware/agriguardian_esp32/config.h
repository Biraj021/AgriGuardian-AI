#ifndef AGRIGUARDIAN_CONFIG_H
#define AGRIGUARDIAN_CONFIG_H

// ======================================================
// AgriGuardian AI - ESP32 Configuration
// ======================================================

// ----------------------
// WiFi
// ----------------------

#define WIFI_SSID "Wifi"
#define WIFI_PASSWORD "Password"

// ----------------------
// MQTT
// ----------------------

// IMPORTANT:
// Replace this with the IP address of the computer/server
// running your MQTT broker.
//
// Example:
// #define MQTT_BROKER_HOST "broker.hivemq.com"

#define MQTT_BROKER_HOST "broker.hivemq.com"
#define MQTT_BROKER_PORT 1883

#define MQTT_USERNAME ""
#define MQTT_PASSWORD ""

// ----------------------
// Device
// ----------------------

#define DEVICE_ID "agriguardian-esp32-001"

// ----------------------
// MQTT Topics
// ----------------------

#define MQTT_TELEMETRY_TOPIC \
  "agriguardian/farm/" DEVICE_ID "/telemetry"

#define MQTT_CONTROL_TOPIC \
  "agriguardian/farm/" DEVICE_ID "/control"

#define MQTT_STATUS_TOPIC \
  "agriguardian/farm/" DEVICE_ID "/status"

// ----------------------
// Sensors
// ----------------------

// DHT22
#define PIN_DHT22 4
#define DHT_TYPE DHT22

// Capacitive soil moisture sensor
#define PIN_SOIL_MOISTURE 34
#define SOIL_DRY_VALUE 3200
#define SOIL_WET_VALUE 1200

// Rain sensor
#define PIN_RAIN_SENSOR 35
// Adjust after testing the module in dry and wet conditions.
#define RAIN_THRESHOLD 2000

// ----------------------
// Sensors — HW-038 Analog Water Level Sensor
// ----------------------

#define PIN_WATER_SENSOR 32
#define WATER_EMPTY_VALUE 10   // ADC value when sensor is dry
#define WATER_FULL_VALUE 2800   // ADC value when sensor is fully submerged

// ----------------------
// Sensor Smoothing
// ----------------------

// Median filter window size for analog sensors (soil, rain, water).
// Must be an odd number. Higher = smoother but slower response.
#define SENSOR_MEDIAN_WINDOW 5

// ----------------------
// Relay — Multi-Channel
// ----------------------

#define RELAY_COUNT 4

#define PIN_RELAY_1 26    // Channel 0: Pump
#define PIN_RELAY_2 27    // Channel 1: Solenoid valve / spare
#define PIN_RELAY_3 14    // Channel 2: Fan / spare
#define PIN_RELAY_4 12    // Channel 3: Light / spare

// Most 4-channel relay boards are active LOW.
#define RELAY_ACTIVE_LOW true

// Local safety limits per channel.
#define MAX_RELAY_RUNTIME_MS 300000UL

// Turn off all relays when MQTT disconnects.
#define RELAY_OFF_ON_MQTT_DISCONNECT true

// Legacy aliases (backward compat)
#define PIN_RELAY_PUMP PIN_RELAY_1
#define MAX_PUMP_RUNTIME_MS MAX_RELAY_RUNTIME_MS
#define PUMP_OFF_ON_MQTT_DISCONNECT RELAY_OFF_ON_MQTT_DISCONNECT

// ----------------------
// LED Status Indicator
// ----------------------

#define LED_STATUS_ENABLED true
#define PIN_STATUS_LED 2

// ----------------------
// Watchdog Timer
// ----------------------

#define WATCHDOG_ENABLED true
#define WATCHDOG_TIMEOUT_S 30

// ----------------------
// OTA (Over-the-Air) Updates
// ----------------------

#define OTA_ENABLED true
#define OTA_PASSWORD "agriguardian-ota"

// ----------------------
// Offline Telemetry Buffer (SPIFFS)
// ----------------------

#define TELEMETRY_BUFFER_ENABLED true
#define TELEMETRY_BUFFER_MAX_ENTRIES 50
#define TELEMETRY_BUFFER_FILE "/telemetry_buffer.jsonl"

// ----------------------
// Deep Sleep / Power Management
// ----------------------

#define DEEP_SLEEP_ENABLED false
#define DEEP_SLEEP_DURATION_US 300000000ULL  // 5 minutes

// ----------------------
// Timing
// ----------------------

#define TELEMETRY_INTERVAL_MS 30000UL
#define STATUS_INTERVAL_MS 60000UL

#define MQTT_RECONNECT_INTERVAL_MS 5000UL
#define MQTT_PACKET_BUFFER_SIZE 512

#endif
