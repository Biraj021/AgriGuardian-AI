// ============================================================
// power_manager.h — Deep sleep / power management
// ============================================================
// Optional feature for battery-powered sensor-only field nodes.
// When enabled, the ESP32 reads sensors once, publishes
// telemetry, then enters deep sleep for DEEP_SLEEP_DURATION_US.
//
// IMPORTANT LIMITATIONS:
//   - Deep sleep resets the ESP32 completely. setup() runs again.
//   - MQTT subscription (relay/pump control) is not possible
//     during sleep — this mode is for sensor-only nodes.
//   - Deep sleep is skipped if any relay is currently ON
//     (safety: can't monitor a running pump while sleeping).
//   - OTA is only possible during the brief wake window.
// ============================================================

#ifndef POWER_MANAGER_H
#define POWER_MANAGER_H

#include <Arduino.h>
#include "config.h"

#if DEEP_SLEEP_ENABLED

#include <esp_sleep.h>

// Forward declaration — relayAnyOn() is defined in relay_control.h.
extern bool relayAnyOn();

void powerManagerInit() {
  // Log the wake reason so we can distinguish first boot from wake.
  esp_sleep_wakeup_cause_t wakeReason = esp_sleep_get_wakeup_cause();
  switch (wakeReason) {
    case ESP_SLEEP_WAKEUP_TIMER:
      Serial.println("[POWER] Woke from deep sleep (timer)");
      break;
    case ESP_SLEEP_WAKEUP_EXT0:
    case ESP_SLEEP_WAKEUP_EXT1:
      Serial.println("[POWER] Woke from deep sleep (external)");
      break;
    default:
      Serial.println("[POWER] Normal boot (not from deep sleep)");
      break;
  }

  Serial.print("[POWER] Deep sleep enabled, duration=");
  Serial.print((unsigned long)(DEEP_SLEEP_DURATION_US / 1000000ULL));
  Serial.println("s");
}

// Call this after telemetry has been published.
// Returns true if deep sleep was entered (caller won't see this — ESP32 resets).
// Returns false if deep sleep was skipped (relay active or other safety reason).
bool powerManagerSleep() {
  // SAFETY: Never sleep while any relay is active.
  if (relayAnyOn()) {
    Serial.println("[POWER] Deep sleep SKIPPED — relay(s) active");
    return false;
  }

  Serial.print("[POWER] Entering deep sleep for ");
  Serial.print((unsigned long)(DEEP_SLEEP_DURATION_US / 1000000ULL));
  Serial.println("s...");
  Serial.flush();  // Ensure all serial output is sent before sleeping.

  esp_sleep_enable_timer_wakeup(DEEP_SLEEP_DURATION_US);
  esp_deep_sleep_start();

  // Execution never reaches here — deep sleep resets the chip.
  return true;
}

#else  // DEEP_SLEEP_ENABLED == false

void powerManagerInit() {
  // No-op — continuous operation mode.
}

bool powerManagerSleep() {
  return false;  // Deep sleep disabled, never enters sleep.
}

#endif  // DEEP_SLEEP_ENABLED

#endif  // POWER_MANAGER_H
