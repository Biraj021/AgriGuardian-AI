// AgriGuardian ESP32 node. Hardware validation is required before field use.
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include "../../config/config.h"

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
DHT dht(DHT_PIN, DHT_TYPE);
unsigned long lastTelemetryAt = 0;
unsigned long pumpStartedAt = 0;
bool pumpOn = false;

String topic(const char *suffix) { return String("agriguardian/farm/") + DEVICE_ID + "/" + suffix; }

void setPump(bool on) {
  // Relay is active LOW on common modules; change only after electrical verification.
  digitalWrite(RELAY_PIN, on ? LOW : HIGH);
  pumpOn = on;
  pumpStartedAt = on ? millis() : 0;
}

void publishStatus(const char *state) {
  StaticJsonDocument<192> doc;
  doc["device_id"] = DEVICE_ID;
  doc["status"] = state;
  doc["pump_on"] = pumpOn;
  char payload[192];
  serializeJson(doc, payload);
  mqttClient.publish(topic("status").c_str(), payload, true);
}

void onMqtt(char *rawTopic, byte *payload, unsigned int length) {
  if (String(rawTopic) != topic("control") || length == 0) return;
  StaticJsonDocument<192> doc;
  if (deserializeJson(doc, payload, length)) return;  // malformed commands fail safe
  const char *command = doc["command"] | "";
  unsigned long duration = doc["duration_seconds"] | 0UL;
  if (String(command) == "PUMP_ON" && duration > 0 && duration <= MAX_PUMP_RUNTIME_SECONDS) {
    setPump(true);
    publishStatus("pump_on");
  } else if (String(command) == "PUMP_OFF") {
    setPump(false);
    publishStatus("pump_off");
  }
}

void ensureWifi() {
  if (WiFi.status() == WL_CONNECTED) return;
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  unsigned long started = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - started < 10000) delay(250);
}

void ensureMqtt() {
  if (mqttClient.connected()) return;
  setPump(false);  // never keep pump on through a broker disconnect
  String clientId = String("agriguardian-") + DEVICE_ID;
  if (mqttClient.connect(clientId.c_str(), MQTT_USERNAME, MQTT_PASSWORD)) {
    mqttClient.subscribe(topic("control").c_str());
    publishStatus("online");
  }
}

float waterLevelPercent() {
  digitalWrite(WATER_TRIG_PIN, LOW); delayMicroseconds(2);
  digitalWrite(WATER_TRIG_PIN, HIGH); delayMicroseconds(10); digitalWrite(WATER_TRIG_PIN, LOW);
  long duration = pulseIn(WATER_ECHO_PIN, HIGH, 30000);
  if (duration == 0) return -1;
  // HC-SR04 distance in cm. Calibrate EMPTY/FULL distances in config.h for
  // the installed tank; the defaults are examples, not sensor calibration.
  float distance = duration * 0.0343f / 2.0f;
  float span = WATER_EMPTY_DISTANCE_CM - WATER_FULL_DISTANCE_CM;
  if (span <= 0) return -1;  // fail safe when calibration is invalid
  return constrain((WATER_EMPTY_DISTANCE_CM - distance) * 100.0f / span, 0, 100);
}

void publishTelemetry() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  int rawSoil = analogRead(SOIL_PIN);
  float soil = constrain(map(rawSoil, SOIL_DRY_VALUE, SOIL_WET_VALUE, 0, 100), 0, 100);
  StaticJsonDocument<320> doc;
  doc["device_id"] = DEVICE_ID;
  doc["temperature"] = isnan(temperature) ? nullptr : temperature;
  doc["humidity"] = isnan(humidity) ? nullptr : humidity;
  doc["soil_moisture"] = soil;
  doc["rainfall"] = digitalRead(RAIN_PIN) == LOW ? 1 : 0;
  float water = waterLevelPercent();
  if (water >= 0) doc["water_level"] = water;
  char payload[320]; serializeJson(doc, payload);
  mqttClient.publish(topic("telemetry").c_str(), payload);
}

void setup() {
  pinMode(RELAY_PIN, OUTPUT); pinMode(RAIN_PIN, INPUT);
  pinMode(WATER_TRIG_PIN, OUTPUT); pinMode(WATER_ECHO_PIN, INPUT);
  setPump(false);  // fail-safe boot default
  dht.begin(); mqttClient.setServer(MQTT_HOST, MQTT_PORT); mqttClient.setCallback(onMqtt);
}

void loop() {
  ensureWifi(); ensureMqtt();
  if (mqttClient.connected()) mqttClient.loop();
  if (pumpOn && millis() - pumpStartedAt >= MAX_PUMP_RUNTIME_SECONDS * 1000UL) { setPump(false); publishStatus("pump_timeout_off"); }
  if (mqttClient.connected() && millis() - lastTelemetryAt >= TELEMETRY_INTERVAL_MS) {
    lastTelemetryAt = millis();
    publishTelemetry();
    publishStatus("online");  // retained heartbeat/status for backend consumers
  }
}
