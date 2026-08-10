// ============================================================
// mqtt_client.h — MQTT connection, telemetry, and control intake
// ============================================================
// Uses PubSubClient (the standard, widely-used MQTT library for
// Arduino/ESP32). Install via Library Manager: "PubSubClient" by
// Nick O'Leary — see LIBRARIES.md for exact version.
//
// Command surface:
//   {"pump":true}            — backward compat, relay channel 0
//   {"pump":false}           — backward compat, relay channel 0
//   {"relay":N,"state":bool} — extended multi-relay (channels 0-3)
//
// Anything else is rejected and logged.
// ============================================================

#ifndef MQTT_CLIENT_H
#define MQTT_CLIENT_H

#include <WiFi.h>
#include <PubSubClient.h>
#include <ctype.h>
#include "config.h"
#include "relay_control.h"
#include "telemetry_buffer.h"

WiFiClient espWifiClient;
PubSubClient mqttClient(espWifiClient);

String topicTelemetry;
String topicControl;
String topicStatus;

bool mqttWasConnected = false;   // tracks transitions, for disconnect handling

void buildTopics() {
  topicTelemetry = "agriguardian/farm/" + String(DEVICE_ID) + "/telemetry";
  topicControl   = "agriguardian/farm/" + String(DEVICE_ID) + "/control";
  topicStatus    = "agriguardian/farm/" + String(DEVICE_ID) + "/status";
}

// ── Helper: strip whitespace from a string ────────────────
static String _compactJson(const char* payload, unsigned int length) {
  String compact;
  compact.reserve(length);
  for (unsigned int i = 0; i < length; i++) {
    if (!isspace(static_cast<unsigned char>(payload[i]))) {
      compact += payload[i];
    }
  }
  return compact;
}

// ── Helper: extract integer from JSON key in compact string ──
// Minimal parser for {"relay":N,"state":bool} — no ArduinoJson dependency.
// Returns -1 if key not found or value is not a valid small integer.
static int _extractInt(const String& json, const String& key) {
  String search = "\"" + key + "\":";
  int pos = json.indexOf(search);
  if (pos < 0) return -1;
  pos += search.length();
  // Read digits
  String numStr;
  while (pos < (int)json.length() && isdigit(static_cast<unsigned char>(json[pos]))) {
    numStr += json[pos++];
  }
  if (numStr.length() == 0) return -1;
  return numStr.toInt();
}

// ── Helper: extract boolean from JSON key in compact string ──
static int _extractBool(const String& json, const String& key) {
  String searchTrue = "\"" + key + "\":true";
  String searchFalse = "\"" + key + "\":false";
  if (json.indexOf(searchTrue) >= 0) return 1;
  if (json.indexOf(searchFalse) >= 0) return 0;
  return -1;  // not found
}

// ── Incoming control command handling ──────────────────────
// Deliberately strict: anything that isn't EXACTLY a well-formed
// command is rejected and logged, never guessed at.
void handleControlMessage(char* payload, unsigned int length) {
  // Reject absurdly long payloads outright rather than parsing them
  if (length == 0 || length > 128) {
    Serial.println("[MQTT] Control message rejected: invalid length");
    return;
  }

  String compact = _compactJson(payload, length);

  // ── Legacy pump command: {"pump":true} / {"pump":false} ──
  if (compact == "{\"pump\":true}") {
    Serial.println("[MQTT] Valid command: PUMP ON");
    pumpOn();
    return;
  }
  if (compact == "{\"pump\":false}") {
    Serial.println("[MQTT] Valid command: PUMP OFF");
    pumpOff();
    return;
  }

  // ── Extended multi-relay command: {"relay":N,"state":true/false} ──
  int relayChannel = _extractInt(compact, "relay");
  int relayState = _extractBool(compact, "state");

  if (relayChannel >= 0 && relayChannel < RELAY_COUNT && relayState >= 0) {
    Serial.print("[MQTT] Valid command: RELAY Ch");
    Serial.print(relayChannel);
    Serial.println(relayState ? " ON" : " OFF");
    if (relayState) {
      relayOn((uint8_t)relayChannel);
    } else {
      relayOff((uint8_t)relayChannel);
    }
    return;
  }

  // ── Unrecognized command ──
  // Covers: malformed JSON, missing keys, ambiguous payloads,
  // or any other unexpected shape.
  char buf[129];
  memcpy(buf, payload, length);
  buf[length] = '\0';
  Serial.print("[MQTT] Control message REJECTED (unrecognized): ");
  Serial.println(buf);
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  if (String(topic) == topicControl) {
    handleControlMessage((char*)payload, length);
  }
}

void publishStatus(bool online) {
  String status = "{";
  status += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
  status += "\"status\":\"" + String(online ? "online" : "offline") + "\",";
  status += "\"pump_status\":\"" + String(pumpIsOn ? "on" : "off") + "\",";
  status += "\"relay_count\":" + String(RELAY_COUNT) + ",";
  status += "\"uptime_ms\":" + String(millis());
  status += "}";
  mqttClient.publish(topicStatus.c_str(), status.c_str(), true);  // retained
}

void mqttReconnect() {
  if (mqttClient.connected()) return;

  if (mqttWasConnected) {
    // We just transitioned from connected -> disconnected.
    relayHandleMqttDisconnect();
    mqttWasConnected = false;
  }

  Serial.print("[MQTT] Connecting to broker...");
  // Last Will and Testament: if this device drops off ungracefully,
  // the broker announces it offline automatically — the backend/dashboard
  // doesn't have to guess based on a stale heartbeat timeout alone.
  String willTopic = topicStatus;
  String willPayload = "{\"device_id\":\"" + String(DEVICE_ID) + "\",\"status\":\"offline\"}";

  bool connected;
  if (strlen(MQTT_USERNAME) > 0) {
    connected = mqttClient.connect(DEVICE_ID, MQTT_USERNAME, MQTT_PASSWORD,
                                    willTopic.c_str(), 1, true, willPayload.c_str());
  } else {
    connected = mqttClient.connect(DEVICE_ID, willTopic.c_str(), 1, true, willPayload.c_str());
  }

  if (connected) {
    Serial.println(" connected.");
    mqttClient.subscribe(topicControl.c_str());
    publishStatus(true);
    mqttWasConnected = true;
  } else {
    Serial.print(" failed, rc=");
    Serial.print(mqttClient.state());
    Serial.println(" — will retry");
  }
}

void mqttInit() {
  buildTopics();
  mqttClient.setServer(MQTT_BROKER_HOST, MQTT_BROKER_PORT);
  mqttClient.setBufferSize(MQTT_PACKET_BUFFER_SIZE);
  mqttClient.setCallback(mqttCallback);
}

// Call every loop() iteration. Non-blocking: mqttReconnect() only
// attempts a connection when not already connected, and mqttClient.loop()
// handles keepalive + incoming messages without blocking delay().
void mqttLoop() {
  if (!mqttClient.connected()) {
    if (mqttWasConnected) {
      relayHandleMqttDisconnect();
      mqttWasConnected = false;
    }
    static unsigned long lastAttemptMs = 0;
    // Retry every 5s rather than hammering the broker continuously
    if (millis() - lastAttemptMs >= MQTT_RECONNECT_INTERVAL_MS) {
      lastAttemptMs = millis();
      mqttReconnect();
    }
  }
  mqttClient.loop();

  // ── Flush offline buffer on reconnect ──────────────────
  // Drain one buffered entry per loop iteration (non-blocking).
  if (mqttClient.connected() && telemetryBufferHasData()) {
    String buffered = telemetryBufferPop();
    if (buffered.length() > 0) {
      mqttClient.publish(topicTelemetry.c_str(), buffered.c_str());
    }
  }
}

void mqttPublishHeartbeat() {
  if (mqttClient.connected()) publishStatus(true);
}

void publishTelemetry(const String& json) {
  if (mqttClient.connected()) {
    mqttClient.publish(topicTelemetry.c_str(), json.c_str());
  } else {
    Serial.println("[MQTT] Not connected — buffering telemetry");
    telemetryBufferStore(json);
  }
}

// Expose connectivity check for the main sketch.
bool mqttIsConnected() {
  return mqttClient.connected();
}

#endif
