// ============================================================
// agriguardian_esp32.ino — AgriGuardian AI ESP32 IoT Node
// ============================================================
// Main firmware entry point. Integrates all hardware modules:
//   - Sensors (DHT22, soil, rain, ultrasonic) with smoothing
//   - WiFi with non-blocking reconnect
//   - MQTT publish/subscribe with offline buffering
//   - Multi-channel relay control with safety enforcement
//   - Watchdog timer for crash recovery
//   - LED status indicators
//   - OTA (over-the-air) firmware updates
//   - Deep sleep power management (optional)
// ============================================================

#include <Arduino.h>
#include "config.h"

// Module includes — order matters: config first, then modules
// that don't depend on each other, then modules that do.
#include "sensors.h"
#include "led_status.h"
#include "watchdog.h"
#include "relay_control.h"       // must be before ota_update.h (relayAllOff)
#include "telemetry_buffer.h"
#include "wifi_manager.h"
#include "mqtt_client.h"         // depends on relay_control.h, telemetry_buffer.h
#include "ota_update.h"          // depends on relay_control.h (relayAllOff)
#include "power_manager.h"       // depends on relay_control.h (relayAnyOn)

// ── Helper: format float or "null" for JSON ───────────────
String jsonFloatOrNull(float value, bool valid, unsigned int decimals = 2) {
  return valid ? String(value, decimals) : "null";
}

// ── Track sensor health for LED indicator ─────────────────
bool _lastSensorHealthy = true;

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("================================");
  Serial.println(" AgriGuardian AI - ESP32 Node");
  Serial.println(" Production Firmware v2.0");
  Serial.println("================================");

  // Initialize subsystems in dependency order.
  ledStatusInit();
  ledStatusSet(LED_STATE_WIFI_CONNECTING);

  watchdogInit();
  sensorsInit();
  relayInit();
  telemetryBufferInit();
  powerManagerInit();

  wifiInit();

  if (wifiConnected()) {
    ledStatusSet(LED_STATE_MQTT_CONNECTING);
    otaInit();
  }

  mqttInit();

  Serial.println("[MAIN] Setup complete");
}

void loop() {
  // ── Watchdog: feed every iteration ──────────────────────
  watchdogFeed();

  // ── LED: update blink pattern ───────────────────────────
  ledStatusLoop();

  // ── Relay safety: enforce max runtime (always, even offline) ──
  relayEnforceSafety();

  // ── OTA: skip all other work during firmware upload ─────
  if (otaIsInProgress()) {
    delay(10);
    return;
  }

  // ── WiFi: handle connection ─────────────────────────────
  static bool wasWifiConnected = false;
  if (!wifiConnected()) {
    if (wasWifiConnected) {
      relayHandleMqttDisconnect();
      ledStatusSet(LED_STATE_WIFI_CONNECTING);
    }
    wasWifiConnected = false;
    wifiLoop();
    delay(10);
    return;
  }

  // WiFi just connected (or still connected).
  if (!wasWifiConnected) {
    // WiFi just came back — initialize OTA.
    otaInit();
    ledStatusSet(LED_STATE_MQTT_CONNECTING);
  }
  wasWifiConnected = true;

  // ── OTA: handle incoming updates ────────────────────────
  otaLoop();

  // ── MQTT: handle connection + incoming messages + buffer flush ──
  mqttLoop();

  // ── LED: update state based on connectivity ─────────────
  if (mqttIsConnected()) {
    if (!_lastSensorHealthy) {
      ledStatusSet(LED_STATE_SENSOR_ERROR);
    } else {
      ledStatusSet(LED_STATE_CONNECTED);
    }
  } else {
    ledStatusSet(LED_STATE_MQTT_CONNECTING);
  }

  // ── Heartbeat: periodic status publish ──────────────────
  static unsigned long lastStatus = 0;
  if (millis() - lastStatus >= STATUS_INTERVAL_MS) {
    lastStatus = millis();
    mqttPublishHeartbeat();
  }

  // ── Telemetry: periodic sensor read + publish ───────────
  static unsigned long lastTelemetry = 0;
  if (millis() - lastTelemetry >= TELEMETRY_INTERVAL_MS) {
    lastTelemetry = millis();

    EnvironmentReading environment = readEnvironment();
    SoilReading soil = readSoilMoisture();
    RainReading rain = readRain();
    WaterLevelReading waterLevel = readWaterLevel();

    // Track sensor health for LED indicator.
    _lastSensorHealthy = environment.valid && soil.valid && rain.valid && waterLevel.valid;

    // Serial debug output.
    Serial.println("---- Sensor Data ----");
    Serial.print("Temperature: ");
    Serial.println(environment.valid ? String(environment.temperature) : "INVALID");
    Serial.print("Humidity: ");
    Serial.println(environment.valid ? String(environment.humidity) : "INVALID");
    Serial.print("Soil Moisture: ");
    Serial.println(soil.valid ? String(soil.percent) + "%" : "INVALID");
    Serial.print("Soil Raw: ");
    Serial.println(soil.raw);
    Serial.print("Rain: ");
    Serial.println(rain.valid ? (rain.isRaining ? "YES" : "NO") : "INVALID");
    Serial.print("Rain Raw: ");
    Serial.println(rain.raw);
    Serial.print("Water Level: ");
    Serial.println(waterLevel.valid ? String(waterLevel.percent) + "%" : "INVALID");

    // Build JSON payload — MUST match the backend's ingest_telemetry() contract.
    // See: backend/src/infrastructure/external_apis/mqtt_iot.py
    String payload = "{";
    payload += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
    payload += "\"temperature_c\":" + jsonFloatOrNull(environment.temperature, environment.valid) + ",";
    payload += "\"temperature_valid\":" + String(environment.valid ? "true" : "false") + ",";
    payload += "\"humidity_percent\":" + jsonFloatOrNull(environment.humidity, environment.valid) + ",";
    payload += "\"humidity_valid\":" + String(environment.valid ? "true" : "false") + ",";
    payload += "\"soil_moisture_percent\":" + jsonFloatOrNull(soil.percent, soil.valid) + ",";
    payload += "\"soil_valid\":" + String(soil.valid ? "true" : "false") + ",";
    payload += "\"soil_moisture_raw\":" + String(soil.raw) + ",";
    payload += "\"rain_raw\":" + String(rain.raw) + ",";
    payload += "\"raining\":" + String(rain.isRaining ? "true" : "false") + ",";
    payload += "\"rain_valid\":" + String(rain.valid ? "true" : "false") + ",";
    payload += "\"water_level_percent\":" + jsonFloatOrNull(waterLevel.percent, waterLevel.valid) + ",";
    payload += "\"water_level_valid\":" + String(waterLevel.valid ? "true" : "false") + ",";
    payload += "\"pump_on\":" + String(pumpIsOn ? "true" : "false") + ",";
    // The device has no RTC. uptime_ms is the explicit timestamp strategy.
    payload += "\"timestamp_ms\":" + String(millis());
    payload += "}";

    // publishTelemetry() handles both MQTT-connected and offline cases.
    // When offline, it auto-buffers to SPIFFS.
    publishTelemetry(payload);

    // ── Deep sleep: enter after publishing (if enabled) ───
    // powerManagerSleep() returns false if sleep is disabled or
    // skipped (relay active). If it returns true, the ESP32 has
    // already reset — execution never reaches past this point.
    if (DEEP_SLEEP_ENABLED) {
      powerManagerSleep();
    }
  }

  delay(10);
}
