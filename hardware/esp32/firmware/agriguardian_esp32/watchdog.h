// ============================================================
// watchdog.h — Hardware watchdog timer for crash recovery
// ============================================================
// Enables the ESP32 Task Watchdog Timer (TWDT). If the main
// loop() hangs for longer than WATCHDOG_TIMEOUT_S seconds,
// the chip auto-resets. This covers infinite loops, deadlocks,
// and sensor drivers that block unexpectedly.
//
// The watchdog is fed (reset) every loop() iteration via
// watchdogFeed(). If loop() completes within the timeout,
// nothing happens. If it doesn't, the ESP32 reboots.
// ============================================================

#ifndef WATCHDOG_H
#define WATCHDOG_H

#include "config.h"

#if WATCHDOG_ENABLED

#include <esp_task_wdt.h>

bool _watchdogInitialized = false;

void watchdogInit() {
  // Configure the Task Watchdog Timer.
  // ESP32 Arduino Core 3.x (ESP-IDF 5.x) changed the init signature to use a config struct.
#if defined(ESP_ARDUINO_VERSION_MAJOR) && ESP_ARDUINO_VERSION_MAJOR >= 3
  esp_task_wdt_config_t config = {
    .timeout_ms = WATCHDOG_TIMEOUT_S * 1000,
    .idle_core_mask = 0,
    .trigger_panic = true
  };
  esp_err_t err = esp_task_wdt_init(&config);
#else
  // Core 2.x legacy signature: timeout in seconds, panic on timeout
  esp_err_t err = esp_task_wdt_init(WATCHDOG_TIMEOUT_S, true);
#endif
  if (err != ESP_OK && err != ESP_ERR_INVALID_STATE) {
    // ESP_ERR_INVALID_STATE means TWDT is already initialized (e.g. by the
    // system). That's fine — we'll just subscribe to it.
    Serial.print("[WDT] Init failed, err=");
    Serial.println(err);
    return;
  }

  // Subscribe the current (loopTask) to the watchdog.
  err = esp_task_wdt_add(NULL);
  if (err != ESP_OK && err != ESP_ERR_INVALID_ARG) {
    Serial.print("[WDT] Add task failed, err=");
    Serial.println(err);
    return;
  }

  _watchdogInitialized = true;
  Serial.print("[WDT] Watchdog enabled, timeout=");
  Serial.print(WATCHDOG_TIMEOUT_S);
  Serial.println("s");
}

void watchdogFeed() {
  if (_watchdogInitialized) {
    esp_task_wdt_reset();
  }
}

#else  // WATCHDOG_ENABLED == false

void watchdogInit() {
  Serial.println("[WDT] Watchdog disabled in config");
}

void watchdogFeed() {
  // No-op when watchdog is disabled.
}

#endif  // WATCHDOG_ENABLED

#endif  // WATCHDOG_H
