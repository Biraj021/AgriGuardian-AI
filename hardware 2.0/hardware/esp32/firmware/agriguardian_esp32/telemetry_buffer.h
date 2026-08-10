// ============================================================
// telemetry_buffer.h — Offline telemetry buffering via LittleFS
// ============================================================
// When MQTT is disconnected, telemetry JSON payloads are
// appended to a LittleFS file. On reconnect, buffered payloads
// are flushed one-per-loop-iteration (non-blocking drain).
//
// Max buffer size is capped (TELEMETRY_BUFFER_MAX_ENTRIES).
// Oldest entries are dropped on overflow by truncating the file.
//
// File format: one JSON object per line (JSONL), which is the
// same format the backend's ingest_telemetry() expects.
// ============================================================

#ifndef TELEMETRY_BUFFER_H
#define TELEMETRY_BUFFER_H

#include <Arduino.h>
#include "config.h"

#if TELEMETRY_BUFFER_ENABLED

#include <LittleFS.h>

static bool _fsReady = false;
static bool _bufferHasData = false;

void telemetryBufferInit() {
  // LittleFS is much more stable than SPIFFS on ESP32 Core 3.x
  if (!LittleFS.begin(true)) {  // true = format on first mount
    Serial.println("[BUFFER] LittleFS mount failed — buffering disabled");
    _fsReady = false;
    return;
  }
  _fsReady = true;

  // Check if there's leftover data from a previous session.
  if (LittleFS.exists(TELEMETRY_BUFFER_FILE)) {
    File f = LittleFS.open(TELEMETRY_BUFFER_FILE, FILE_READ);
    if (f && f.size() > 0) {
      _bufferHasData = true;
      Serial.print("[BUFFER] Found ");
      Serial.print(f.size());
      Serial.println(" bytes of buffered telemetry from previous session");
    }
    if (f) f.close();
  }

  Serial.print("[BUFFER] LittleFS ready, max entries=");
  Serial.println(TELEMETRY_BUFFER_MAX_ENTRIES);
}

// Count lines in the buffer file (each line = one telemetry entry).
static int _bufferCountLines() {
  if (!_fsReady) return 0;
  File f = LittleFS.open(TELEMETRY_BUFFER_FILE, FILE_READ);
  if (!f) return 0;
  int count = 0;
  while (f.available()) {
    String line = f.readStringUntil('\n');
    if (line.length() > 0) count++;
  }
  f.close();
  return count;
}

// Trim the buffer to keep only the newest entries when it overflows.
// Removes the oldest (first) lines to make room.
static void _bufferTrimOldest() {
  if (!_fsReady) return;

  File f = LittleFS.open(TELEMETRY_BUFFER_FILE, FILE_READ);
  if (!f) return;

  // Read all lines into memory. On ESP32 with max 50 entries of ~250 bytes
  // each, this is ~12.5KB which fits comfortably in the 320KB SRAM.
  String lines[TELEMETRY_BUFFER_MAX_ENTRIES];
  int count = 0;
  while (f.available() && count < TELEMETRY_BUFFER_MAX_ENTRIES) {
    String line = f.readStringUntil('\n');
    if (line.length() > 0) {
      lines[count++] = line;
    }
  }
  f.close();

  // Keep only the newest half when full (aggressive trim to avoid
  // frequent trim operations).
  int keepFrom = count / 2;

  File out = LittleFS.open(TELEMETRY_BUFFER_FILE, FILE_WRITE);  // truncates
  if (!out) return;
  for (int i = keepFrom; i < count; i++) {
    out.println(lines[i]);
  }
  out.close();

  Serial.print("[BUFFER] Trimmed oldest ");
  Serial.print(keepFrom);
  Serial.println(" entries");
}

// Store a telemetry payload to the buffer file.
void telemetryBufferStore(const String& json) {
  if (!_fsReady) return;

  // Check if we need to trim.
  int lineCount = _bufferCountLines();
  if (lineCount >= TELEMETRY_BUFFER_MAX_ENTRIES) {
    _bufferTrimOldest();
  }

  File f = LittleFS.open(TELEMETRY_BUFFER_FILE, FILE_APPEND);
  if (!f) {
    Serial.println("[BUFFER] Failed to open buffer file for writing");
    return;
  }
  f.println(json);
  f.close();
  _bufferHasData = true;

  Serial.print("[BUFFER] Stored telemetry (");
  Serial.print(lineCount + 1);
  Serial.println(" buffered)");
}

// Check if there are buffered entries waiting to be flushed.
bool telemetryBufferHasData() {
  return _bufferHasData;
}

// Read and remove the oldest buffered entry (FIFO).
// Returns empty string if no data. Non-blocking: reads one entry per call.
String telemetryBufferPop() {
  if (!_fsReady || !_bufferHasData) return "";

  File f = LittleFS.open(TELEMETRY_BUFFER_FILE, FILE_READ);
  if (!f || f.size() == 0) {
    if (f) f.close();
    _bufferHasData = false;
    return "";
  }

  // Read the first line (oldest entry).
  String firstLine = f.readStringUntil('\n');
  firstLine.trim();

  // Read remaining lines.
  String remaining = "";
  bool hasMore = false;
  while (f.available()) {
    String line = f.readStringUntil('\n');
    line.trim();
    if (line.length() > 0) {
      remaining += line + "\n";
      hasMore = true;
    }
  }
  f.close();

  // Rewrite the file without the first line.
  if (hasMore) {
    File out = LittleFS.open(TELEMETRY_BUFFER_FILE, FILE_WRITE);
    if (out) {
      out.print(remaining);
      out.close();
    }
  } else {
    // Last entry — remove the file entirely.
    LittleFS.remove(TELEMETRY_BUFFER_FILE);
    _bufferHasData = false;
  }

  if (firstLine.length() > 0) {
    Serial.println("[BUFFER] Flushing 1 buffered entry");
  }
  return firstLine;
}

// Clear the entire buffer (e.g., on user request or catastrophic error).
void telemetryBufferClear() {
  if (_fsReady && LittleFS.exists(TELEMETRY_BUFFER_FILE)) {
    LittleFS.remove(TELEMETRY_BUFFER_FILE);
  }
  _bufferHasData = false;
  Serial.println("[BUFFER] Cleared");
}

#else  // TELEMETRY_BUFFER_ENABLED == false

void telemetryBufferInit() {}
void telemetryBufferStore(const String&) {}
bool telemetryBufferHasData() { return false; }
String telemetryBufferPop() { return ""; }
void telemetryBufferClear() {}

#endif  // TELEMETRY_BUFFER_ENABLED

#endif  // TELEMETRY_BUFFER_H
