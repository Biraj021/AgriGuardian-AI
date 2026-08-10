// ============================================================
// sensors.h — Sensor reading, conversion, validation & smoothing
// ============================================================
// Every function here returns a value AND a validity flag.
// Nothing downstream (MQTT publish, AI features) should ever
// trust a reading without checking .valid first.
//
// Smoothing:
//   - Soil moisture & rain: median-of-N filter (removes ADC spikes)
//   - Water level (HC-SR04): exponential moving average (reduces jitter)
//   - DHT22: no extra filter (library handles internally, 2s min interval)
// ============================================================

#ifndef SENSORS_H
#define SENSORS_H

#include <DHT.h>
#include "config.h"

DHT dht(PIN_DHT22, DHT_TYPE);

// ── Data structures ───────────────────────────────────────

struct EnvironmentReading {
  float temperature;
  float humidity;
  bool valid;
};

struct SoilReading {
  int raw;
  float percent;
  bool valid;
};

struct RainReading {
  int raw;
  bool isRaining;
  bool valid;
};

struct WaterLevelReading {
  float percent;
  bool valid;
};

// ── Smoothing helpers ─────────────────────────────────────

// Insertion sort for median filter (small N, fast enough in-place).
static void _sortInt(int arr[], int n) {
  for (int i = 1; i < n; i++) {
    int key = arr[i];
    int j = i - 1;
    while (j >= 0 && arr[j] > key) {
      arr[j + 1] = arr[j];
      j--;
    }
    arr[j + 1] = key;
  }
}

// Median filter for integer ADC values.
// Maintains a circular buffer of the last SENSOR_MEDIAN_WINDOW readings
// and returns the median. The buffer and index are stored in the
// caller-provided static arrays (one per sensor).
static int _medianFilter(int newValue, int buffer[], int& count, int& index) {
  buffer[index] = newValue;
  index = (index + 1) % SENSOR_MEDIAN_WINDOW;
  if (count < SENSOR_MEDIAN_WINDOW) count++;

  // Copy to temp array for sorting (don't sort the circular buffer itself).
  int temp[SENSOR_MEDIAN_WINDOW];
  for (int i = 0; i < count; i++) temp[i] = buffer[i];
  _sortInt(temp, count);

  return temp[count / 2];  // Median (middle element of sorted array)
}

// ── Initialization ────────────────────────────────────────

void sensorsInit() {
  dht.begin();
  pinMode(PIN_RAIN_SENSOR, INPUT);
  pinMode(PIN_WATER_SENSOR, INPUT);
}

// ── DHT22: Temperature + Humidity ──────────────────────────
EnvironmentReading readEnvironment() {
  EnvironmentReading r;
  r.temperature = dht.readTemperature();
  r.humidity = dht.readHumidity();

  // DHT22 returns NaN on a failed read — very common if polled too fast
  // (must be at least ~2 seconds since the last read) or on a wiring fault.
  r.valid = !isnan(r.temperature) && !isnan(r.humidity)
            && r.temperature > -40 && r.temperature < 80
            && r.humidity >= 0 && r.humidity <= 100;
  return r;
}

// ── Capacitive Soil Moisture (with median filter) ──────────
SoilReading readSoilMoisture() {
  SoilReading r;

  int rawAdc = analogRead(PIN_SOIL_MOISTURE);

  // Apply median filter to reduce ADC noise/spikes.
  static int soilBuffer[SENSOR_MEDIAN_WINDOW] = {0};
  static int soilCount = 0;
  static int soilIndex = 0;
  r.raw = _medianFilter(rawAdc, soilBuffer, soilCount, soilIndex);

  if (SOIL_DRY_VALUE == SOIL_WET_VALUE) {
    r.percent = 0;
    r.valid = false;
    return r;
  }

  // SOIL_DRY_VALUE and SOIL_WET_VALUE come from config.h — see
  // SENSOR_CALIBRATION.md for how to measure your own two numbers.
  float percent = (float)(SOIL_DRY_VALUE - r.raw) * 100.0
                  / (float)(SOIL_DRY_VALUE - SOIL_WET_VALUE);
  r.percent = constrain(percent, 0.0, 100.0);

  // Raw ADC is always 0-4095 on ESP32; a value outside that range
  // would indicate a hardware-level ADC fault, not a normal reading.
  r.valid = (r.raw >= 0 && r.raw <= 4095);
  return r;
}

// ── Rain Sensor (with median filter) ──────────────────────
RainReading readRain() {
  RainReading r;

  int rawAdc = analogRead(PIN_RAIN_SENSOR);

  // Apply median filter.
  static int rainBuffer[SENSOR_MEDIAN_WINDOW] = {0};
  static int rainCount = 0;
  static int rainIndex = 0;
  r.raw = _medianFilter(rawAdc, rainBuffer, rainCount, rainIndex);

  r.isRaining = r.raw < RAIN_THRESHOLD;
  r.valid = (r.raw >= 0 && r.raw <= 4095);
  return r;
}

// ── HW-038 Water Depth Sensor (Analog with Median filter) ──
WaterLevelReading readWaterLevel() {
  WaterLevelReading r;

  int rawAdc = analogRead(PIN_WATER_SENSOR);

  // Apply median filter to reduce ADC spikes.
  static int waterBuffer[SENSOR_MEDIAN_WINDOW] = {0};
  static int waterCount = 0;
  static int waterIndex = 0;
  int smoothedRaw = _medianFilter(rawAdc, waterBuffer, waterCount, waterIndex);

  if (WATER_EMPTY_VALUE == WATER_FULL_VALUE) {
    r.percent = 0;
    r.valid = false;
    return r;
  }

  // Calculate percentage: empty value maps to 0%, full value maps to 100%.
  float percent = (float)(smoothedRaw - WATER_EMPTY_VALUE) * 100.0
                  / (float)(WATER_FULL_VALUE - WATER_EMPTY_VALUE);
  r.percent = constrain(percent, 0.0, 100.0);

  // Raw ADC is always 0-4095 on ESP32; values outside this range are faults.
  r.valid = (rawAdc >= 0 && rawAdc <= 4095);
  return r;
}

#endif
