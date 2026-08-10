// ============================================================
// wifi_manager.h — WiFi connection with non-blocking reconnect
// ============================================================

#ifndef WIFI_MANAGER_H
#define WIFI_MANAGER_H

#include <WiFi.h>
#include "config.h"

void wifiInit() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("[WIFI] Connecting");

  // This initial connect blocks — that's acceptable ONLY in setup(),
  // once, before the sensing loop starts. loop() itself never blocks
  // waiting for WiFi (see wifiLoop() below).
  unsigned long startAttempt = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startAttempt < 15000) {
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println(" connected.");
    Serial.print("[WIFI] IP address: ");
    Serial.println(WiFi.localIP().toString());
  } else {
    Serial.println(" not connected yet — will keep retrying in background.");
  }
}

// Call every loop() iteration. Non-blocking: only attempts a reconnect
// every 10 seconds if currently disconnected, never delay()-blocks.
void wifiLoop() {
  if (WiFi.status() != WL_CONNECTED) {
    static unsigned long lastAttemptMs = 0;
    if (millis() - lastAttemptMs > 10000) {
      lastAttemptMs = millis();
      Serial.println("[WIFI] Disconnected — attempting reconnect...");
      WiFi.disconnect();
      WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    }
  }
}

bool wifiConnected() {
  return WiFi.status() == WL_CONNECTED;
}

#endif
