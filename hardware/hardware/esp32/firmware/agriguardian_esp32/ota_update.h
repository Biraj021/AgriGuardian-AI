// ============================================================
// ota_update.h — Over-the-Air firmware update support
// ============================================================
// Uses the built-in ArduinoOTA library (part of ESP32 Arduino
// core — no extra install needed). Password-protected.
//
// When an OTA upload starts, all relays are forced OFF as a
// safety measure (the firmware is being replaced — we can't
// guarantee relay state during the flash process).
//
// OTA is only active while WiFi is connected. The hostname
// is set to DEVICE_ID for easy network discovery.
// ============================================================

#ifndef OTA_UPDATE_H
#define OTA_UPDATE_H

#include <Arduino.h>
#include "config.h"

#if OTA_ENABLED

#include <ArduinoOTA.h>

// Forward declaration — relayAllOff() is defined in relay_control.h
// and will be linked at compile time since the .ino includes both.
extern void relayAllOff();

static bool _otaInProgress = false;

bool otaIsInProgress() {
  return _otaInProgress;
}

void otaInit() {
  ArduinoOTA.setHostname(DEVICE_ID);
  ArduinoOTA.setPassword(OTA_PASSWORD);

  ArduinoOTA.onStart([]() {
    _otaInProgress = true;
    // SAFETY: Force all relays OFF before firmware replacement.
    relayAllOff();

    String type = (ArduinoOTA.getCommand() == U_FLASH) ? "sketch" : "filesystem";
    Serial.println("[OTA] Update starting (" + type + ")");
    Serial.println("[OTA] SAFETY: All relays forced OFF");
  });

  ArduinoOTA.onEnd([]() {
    _otaInProgress = false;
    Serial.println("\n[OTA] Update complete — rebooting");
  });

  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    static int lastPercent = -1;
    int percent = (progress * 100) / total;
    // Log every 10% to avoid flooding serial.
    if (percent / 10 != lastPercent / 10) {
      lastPercent = percent;
      Serial.printf("[OTA] Progress: %u%%\r\n", percent);
    }
  });

  ArduinoOTA.onError([](ota_error_t error) {
    _otaInProgress = false;
    Serial.printf("[OTA] Error[%u]: ", error);
    switch (error) {
      case OTA_AUTH_ERROR:    Serial.println("Auth Failed");    break;
      case OTA_BEGIN_ERROR:   Serial.println("Begin Failed");   break;
      case OTA_CONNECT_ERROR: Serial.println("Connect Failed"); break;
      case OTA_RECEIVE_ERROR: Serial.println("Receive Failed"); break;
      case OTA_END_ERROR:     Serial.println("End Failed");     break;
      default:                Serial.println("Unknown");        break;
    }
  });

  ArduinoOTA.begin();
  Serial.print("[OTA] Enabled, hostname=");
  Serial.print(DEVICE_ID);
  Serial.println(", port=3232");
}

// Call every loop() iteration while WiFi is connected.
void otaLoop() {
  ArduinoOTA.handle();
}

#else  // OTA_ENABLED == false

bool otaIsInProgress() { return false; }
void otaInit() {
  Serial.println("[OTA] Disabled in config");
}
void otaLoop() {}

#endif  // OTA_ENABLED

#endif  // OTA_UPDATE_H
