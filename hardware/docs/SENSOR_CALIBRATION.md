# Sensor Calibration Guide — AgriGuardian AI

## Why Calibration is Necessary

Every capacitive soil moisture sensor is slightly different — even two sensors from the same manufacturer
will give different raw ADC readings for the same soil moisture level.

The ESP32's ADC (Analog-to-Digital Converter) gives a number from **0 to 4095**:
- **0** = 0V (completely dry / or sensor in air)
- **4095** = 3.3V (fully wet / or sensor in water)

> Note: Most capacitive soil moisture sensors output LOWER voltage when WET
> and HIGHER voltage when DRY. This is counter-intuitive but correct.
> Our code maps this correctly: higher ADC reading = drier soil.

We need to find YOUR sensor's specific dry and wet readings, then map them to 0–100%.

---

## Calibration Procedure

### Step 1: Find the Dry Value

1. Open `01_led_blink.ino` (or any test sketch)
2. Add this to `loop()`:
   ```cpp
   int rawValue = analogRead(34);   // or your soil moisture pin
   Serial.println("Raw: " + String(rawValue));
   delay(500);
   ```
3. Upload and open Serial Monitor (115200 baud)
4. Hold the sensor **in the air** — not touching anything
5. Note the reading. This is your **SOIL_DRY_VALUE**
   - Typical range: **2800 – 3500**

### Step 2: Find the Wet Value

1. Fill a glass with clean water
2. Submerge ONLY the sensor electrodes (the striped part) — do NOT submerge the electronics
3. Note the reading in Serial Monitor. This is your **SOIL_WET_VALUE**
   - Typical range: **1000 – 1500**

### Step 3: Update config.h

```cpp
// In hardware/esp32/config/config.h
#define SOIL_DRY_VALUE    3200    // ← Replace with YOUR dry reading
#define SOIL_WET_VALUE    1200    // ← Replace with YOUR wet reading
```

### Step 4: Verify the Mapping

After updating, run this formula manually to verify:

```
Moisture % = ((DRY - RAW) / (DRY - WET)) × 100

Example:
  DRY = 3200, WET = 1200, RAW = 2200
  Moisture % = ((3200 - 2200) / (3200 - 1200)) × 100
             = (1000 / 2000) × 100
             = 50%  ← makes sense for half-wet soil
```

---

## DHT22 Verification

The DHT22 does not need calibration, but verify it works:

1. Connect DHT22 and run the DHT example sketch
2. Expected ranges:
   - Temperature: -40°C to 80°C (±0.5°C accuracy)
   - Humidity: 0% to 100% RH (±2-5% accuracy)
3. If readings show `nan` (not a number): check wiring, add 10kΩ pull-up resistor on data pin

---

## Rain Sensor Threshold

The rain sensor has an onboard potentiometer (small blue dial).
Turn it with a small screwdriver to set sensitivity:
- Clockwise = less sensitive (only triggers in heavy rain)
- Counter-clockwise = more sensitive (triggers with light mist)

Set it so the LED on the sensor module turns ON when you drip a few drops of water on it.

---

## Water Level Sensor (HC-SR04)

No calibration needed. The formula is:
```
distance_cm = (duration_microseconds × speed_of_sound) / 2
            = (duration × 0.034) / 2
```

Install the sensor above the water tank opening:
- Measure the distance from sensor to the bottom of the EMPTY tank = `TANK_EMPTY_DISTANCE`
- Measure the distance from sensor to water surface when FULL = `TANK_FULL_DISTANCE`

Update config.h:
```cpp
#define TANK_EMPTY_DISTANCE_CM   50   // sensor to empty tank bottom
#define TANK_FULL_DISTANCE_CM    5    // sensor to full water surface
```
