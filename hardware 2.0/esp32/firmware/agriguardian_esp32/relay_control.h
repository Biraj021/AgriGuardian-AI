// ============================================================
// relay_control.h — Multi-channel relay control with safety
// ============================================================
// Every safety rule from the spec lives in this one file, so it
// can be audited in one place:
//   - all relays default OFF on boot
//   - MQTT disconnect -> all relays forced OFF (configurable)
//   - maximum continuous runtime per channel, hardware-enforced
//   - only this file is allowed to write to relay pins
//
// Channel 0 is always the pump. pumpOn()/pumpOff()/pumpIsOn
// remain available for backward compatibility with the existing
// MQTT command contract {"pump":true/false}.
// ============================================================

#ifndef RELAY_CONTROL_H
#define RELAY_CONTROL_H

#include <Arduino.h>
#include "config.h"

// ── Relay pin table ───────────────────────────────────────
// Built from config.h defines. Only the first RELAY_COUNT entries are used.
static const uint8_t _relayPins[] = {
#if RELAY_COUNT >= 1
  PIN_RELAY_1,
#endif
#if RELAY_COUNT >= 2
  PIN_RELAY_2,
#endif
#if RELAY_COUNT >= 3
  PIN_RELAY_3,
#endif
#if RELAY_COUNT >= 4
  PIN_RELAY_4,
#endif
};

static const char* _relayNames[] = {
  "pump", "valve", "fan", "light"
};

// ── Per-channel state ─────────────────────────────────────
bool relayIsOn[RELAY_COUNT] = {false};
unsigned long relayStartedAtMs[RELAY_COUNT] = {0};

// Legacy alias for backward compatibility (used in mqtt_client.h, .ino).
#define pumpIsOn relayIsOn[0]

// ── Low-level pin control ─────────────────────────────────
// Translates a logical "on/off" into the correct physical signal,
// accounting for active-low relay modules (RELAY_ACTIVE_LOW in config.h).
static void _relayWrite(uint8_t channel, bool energize) {
  if (channel >= RELAY_COUNT) return;
  if (RELAY_ACTIVE_LOW) {
    digitalWrite(_relayPins[channel], energize ? LOW : HIGH);
  } else {
    digitalWrite(_relayPins[channel], energize ? HIGH : LOW);
  }
}

// ── Initialization ────────────────────────────────────────
void relayInit() {
  for (uint8_t i = 0; i < RELAY_COUNT; i++) {
    // Preload the inactive level before enabling output. This reduces
    // the transition risk, but external pull-up/driver circuitry is still
    // required to guarantee an active-low relay stays OFF while booting.
    digitalWrite(_relayPins[i], RELAY_ACTIVE_LOW ? HIGH : LOW);
    pinMode(_relayPins[i], OUTPUT);
    _relayWrite(i, false);
    relayIsOn[i] = false;
    relayStartedAtMs[i] = 0;
  }
  Serial.print("[RELAY] Initialized ");
  Serial.print(RELAY_COUNT);
  Serial.println(" channel(s), all OFF (default safe state)");
}

// ── Channel control ───────────────────────────────────────

void relayOn(uint8_t channel) {
  if (channel >= RELAY_COUNT) {
    Serial.print("[RELAY] Invalid channel ");
    Serial.println(channel);
    return;
  }
  if (relayIsOn[channel]) {
    Serial.print("[RELAY] Ch");
    Serial.print(channel);
    Serial.print(" (");
    Serial.print(_relayNames[channel]);
    Serial.println(") already ON; runtime timer not reset");
    return;
  }
  _relayWrite(channel, true);
  relayIsOn[channel] = true;
  relayStartedAtMs[channel] = millis();
  Serial.print("[RELAY] Ch");
  Serial.print(channel);
  Serial.print(" (");
  Serial.print(_relayNames[channel]);
  Serial.println(") ON");
}

void relayOff(uint8_t channel) {
  if (channel >= RELAY_COUNT) return;
  _relayWrite(channel, false);
  relayIsOn[channel] = false;
  Serial.print("[RELAY] Ch");
  Serial.print(channel);
  Serial.print(" (");
  Serial.print(_relayNames[channel]);
  Serial.println(") OFF");
}

// Turn all relays OFF (used by OTA safety and shutdown).
void relayAllOff() {
  for (uint8_t i = 0; i < RELAY_COUNT; i++) {
    _relayWrite(i, false);
    relayIsOn[i] = false;
  }
  Serial.println("[RELAY] All channels OFF");
}

// Check if any relay is currently ON (used by deep sleep guard).
bool relayAnyOn() {
  for (uint8_t i = 0; i < RELAY_COUNT; i++) {
    if (relayIsOn[i]) return true;
  }
  return false;
}

// ── Backward-compatible pump shortcuts ────────────────────
// These map directly to channel 0 for existing code and the
// backend's {"pump":true/false} command.
void pumpOn()  { relayOn(0); }
void pumpOff() { relayOff(0); }

// ── Safety enforcement ────────────────────────────────────
// Call this every loop() iteration, unconditionally.
// Enforces MAX_RELAY_RUNTIME_MS per channel — fires even if the backend
// never sends an OFF command, and even if MQTT itself has dropped,
// because it depends only on local time (millis()).
void relayEnforceSafety() {
  for (uint8_t i = 0; i < RELAY_COUNT; i++) {
    if (relayIsOn[i] && (millis() - relayStartedAtMs[i] > MAX_RELAY_RUNTIME_MS)) {
      Serial.print("[RELAY] SAFETY: Ch");
      Serial.print(i);
      Serial.println(" max runtime exceeded, forcing OFF");
      relayOff(i);
    }
  }
}

// Called when the MQTT connection is lost, if RELAY_OFF_ON_MQTT_DISCONNECT
// is enabled in config.h — no MQTT means no way to receive a stop command,
// so we don't take the risk of leaving relays running unattended.
void relayHandleMqttDisconnect() {
  if (RELAY_OFF_ON_MQTT_DISCONNECT) {
    bool anyWasOn = false;
    for (uint8_t i = 0; i < RELAY_COUNT; i++) {
      if (relayIsOn[i]) {
        anyWasOn = true;
        relayOff(i);
      }
    }
    if (anyWasOn) {
      Serial.println("[RELAY] SAFETY: MQTT disconnected, all active relays forced OFF");
    }
  }
}

#endif
