// ============================================================
// led_status.h — Non-blocking LED status indicator
// ============================================================
// Uses the built-in LED (GPIO2 on most ESP32 DevKits) to show
// system state via blink patterns. No delay() calls — pure
// millis()-based state machine that runs in loop().
//
// Patterns:
//   FAST blink  (100ms) — WiFi connecting
//   SLOW blink  (500ms) — WiFi OK, MQTT connecting
//   SOLID ON            — Fully connected, healthy
//   DOUBLE flash        — Sensor error detected
//   OFF                 — Deep sleep or LED disabled
// ============================================================

#ifndef LED_STATUS_H
#define LED_STATUS_H

#include <Arduino.h>
#include "config.h"

// System states for the LED indicator.
enum LedState {
  LED_STATE_WIFI_CONNECTING,   // Fast blink
  LED_STATE_MQTT_CONNECTING,   // Slow blink
  LED_STATE_CONNECTED,         // Solid ON
  LED_STATE_SENSOR_ERROR,      // Double flash
  LED_STATE_OFF                // Off (deep sleep prep)
};

#if LED_STATUS_ENABLED

static LedState _currentLedState = LED_STATE_WIFI_CONNECTING;
static unsigned long _ledLastToggleMs = 0;
static bool _ledCurrentlyOn = false;
static uint8_t _ledFlashStep = 0;  // For double-flash pattern

void ledStatusInit() {
  pinMode(PIN_STATUS_LED, OUTPUT);
  digitalWrite(PIN_STATUS_LED, LOW);
  _ledCurrentlyOn = false;
  Serial.println("[LED] Status indicator enabled on GPIO" + String(PIN_STATUS_LED));
}

void ledStatusSet(LedState state) {
  if (state != _currentLedState) {
    _currentLedState = state;
    _ledFlashStep = 0;
    _ledLastToggleMs = millis();
  }
}

// Non-blocking LED update — call every loop() iteration.
void ledStatusLoop() {
  unsigned long now = millis();

  switch (_currentLedState) {

    case LED_STATE_WIFI_CONNECTING: {
      // Fast blink: 100ms on, 100ms off
      if (now - _ledLastToggleMs >= 100) {
        _ledLastToggleMs = now;
        _ledCurrentlyOn = !_ledCurrentlyOn;
        digitalWrite(PIN_STATUS_LED, _ledCurrentlyOn ? HIGH : LOW);
      }
      break;
    }

    case LED_STATE_MQTT_CONNECTING: {
      // Slow blink: 500ms on, 500ms off
      if (now - _ledLastToggleMs >= 500) {
        _ledLastToggleMs = now;
        _ledCurrentlyOn = !_ledCurrentlyOn;
        digitalWrite(PIN_STATUS_LED, _ledCurrentlyOn ? HIGH : LOW);
      }
      break;
    }

    case LED_STATE_CONNECTED: {
      // Solid ON
      if (!_ledCurrentlyOn) {
        digitalWrite(PIN_STATUS_LED, HIGH);
        _ledCurrentlyOn = true;
      }
      break;
    }

    case LED_STATE_SENSOR_ERROR: {
      // Double-flash pattern: ON(100) OFF(100) ON(100) OFF(700)
      // Steps: 0=ON, 1=OFF, 2=ON, 3=long-OFF
      unsigned long durations[] = {100, 100, 100, 700};
      if (now - _ledLastToggleMs >= durations[_ledFlashStep]) {
        _ledLastToggleMs = now;
        _ledFlashStep = (_ledFlashStep + 1) % 4;
        bool on = (_ledFlashStep == 0 || _ledFlashStep == 2);
        digitalWrite(PIN_STATUS_LED, on ? HIGH : LOW);
        _ledCurrentlyOn = on;
      }
      break;
    }

    case LED_STATE_OFF: {
      if (_ledCurrentlyOn) {
        digitalWrite(PIN_STATUS_LED, LOW);
        _ledCurrentlyOn = false;
      }
      break;
    }
  }
}

#else  // LED_STATUS_ENABLED == false

void ledStatusInit() {}
void ledStatusSet(LedState) {}
void ledStatusLoop() {}

#endif  // LED_STATUS_ENABLED

#endif  // LED_STATUS_H
