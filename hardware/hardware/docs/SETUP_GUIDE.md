# ESP32 Development Environment Setup Guide
# AgriGuardian AI — Hardware Module

## Overview

This guide walks you through setting up a complete ESP32 development environment
on Windows, starting from zero and ending with a blinking LED — proof that
your entire toolchain works.

---

## Prerequisites

| Item | Notes |
|---|---|
| Windows 10/11 computer | 64-bit recommended |
| Internet connection | For downloading IDE + board packages (~400MB total) |
| ESP32 Dev Board | DOIT ESP32 DevKit V1 or similar |
| USB Micro-B data cable | Must carry data — not just power |

---

## Step 1: Install Arduino IDE 2

1. Go to: **https://www.arduino.cc/en/software**
2. Download **Arduino IDE 2.x** for Windows (`.exe` installer)
3. Run the installer:
   - Accept the license agreement
   - Leave default installation path
   - Check all options (drivers, shortcuts)
   - Click "Install"
4. When complete, launch Arduino IDE

---

## Step 2: Install CP210x USB Driver

Most ESP32 boards (DOIT DevKit V1, NodeMCU-32S) use the **Silicon Labs CP2102** USB-to-UART chip. Windows needs a driver to communicate with it.

1. Go to: **https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers**
2. Click "Downloads" tab
3. Download **"CP210x Windows Drivers"**
4. Extract the ZIP file
5. Run `CP210xVCPInstaller_x64.exe` (for 64-bit Windows)
6. Follow the installer prompts
7. **Restart your computer**

### Verify Driver Installation

1. Plug in your ESP32 via USB
2. Open **Device Manager** (right-click Start → Device Manager)
3. Look for **"Ports (COM & LPT)"**
4. You should see **"Silicon Labs CP210x USB to UART Bridge (COM3)"** or similar
5. Note the COM number — you'll need it in Step 4

---

## Step 3: Install ESP32 Board Package

1. Open Arduino IDE
2. Go to **File → Preferences** (Ctrl+,)
3. Find the field: **"Additional boards manager URLs"**
4. Click the icon to the right of the field (or edit directly)
5. Add this URL on a new line:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
6. Click OK
7. Go to **Tools → Board → Boards Manager** (or click the board icon on the left sidebar)
8. In the search box, type: `esp32`
9. Find **"esp32 by Espressif Systems"**
10. Click **Install** — this downloads approximately 300MB
11. Wait for "INSTALLED" to appear (3-10 minutes)

---

## Step 4: Configure Board & Port

1. Go to **Tools → Board → esp32 Arduino → ESP32 Dev Module**
2. Go to **Tools → Port → COM3** (or whichever COM port your ESP32 uses)
3. Verify these settings in the Tools menu:
   - Board: **ESP32 Dev Module**
   - Upload Speed: **921600**
   - CPU Frequency: **240MHz (WiFi/BT)**
   - Flash Frequency: **80MHz**
   - Flash Mode: **QIO**
   - Flash Size: **4MB (32Mb)**
   - Partition Scheme: **Default 4MB with spiffs**
   - Core Debug Level: **None**
   - PSRAM: **Disabled**
   - Port: **COMx** (your port)

---

## Step 5: Upload the Blink Test

1. Open: `hardware/esp32/firmware/01_led_blink/01_led_blink.ino`
2. Click the **Upload button** (→ arrow, top left)
3. Watch the output console at the bottom:
   ```
   Compiling sketch...
   ...
   Linking everything together...
   ...
   Uploading...
   esptool.py v4.x
   Connecting......
   Chip is ESP32-D0WD-V3 ...
   Wrote 234608 bytes ...
   Hash of data verified.
   Hard resetting via RTS pin...
   ```
4. The blue LED starts blinking

> **Upload fails?** Hold the **BOOT** button during upload. See Debugging section.

---

## Step 6: Open Serial Monitor

1. **Tools → Serial Monitor** (Ctrl+Shift+M)
2. Set baud rate to **115200** (bottom right dropdown)
3. Press **EN (reset)** button on ESP32
4. Expected output:
   ```
   ============================================
     AgriGuardian AI — Module 1: ESP32 Setup
     LED Blink Test Starting...
   ============================================
   Setup complete. LED_PIN = 2
   Blink interval = 1000 ms
   Starting blink loop...

   [1034 ms] LED ON
   [2035 ms] LED OFF
   ```

---

## MQTT Buffer Fix

> Required before we add MQTT in Step 6

The `PubSubClient` library has a hard-coded MQTT message buffer of 256 bytes.
Our JSON telemetry payload is ~200 bytes, which is close to the limit.
Increase it to 1024 bytes:

1. Find the library file:
   ```
   C:\Users\<YourName>\Documents\Arduino\libraries\PubSubClient\src\PubSubClient.h
   ```
2. Find this line:
   ```cpp
   #define MQTT_MAX_PACKET_SIZE 256
   ```
3. Change to:
   ```cpp
   #define MQTT_MAX_PACKET_SIZE 1024
   ```
4. Save the file

---

## Quick Reference: Common Commands

```
Upload code:         Ctrl+U
Verify/Compile:      Ctrl+R
Open Serial Monitor: Ctrl+Shift+M
New sketch:          Ctrl+N
Open file:           Ctrl+O
Save:                Ctrl+S
```

---

## Board Pinout Reference

```
                    DOIT ESP32 DevKit V1
                 ┌──────────────────────┐
           3.3V ─┤ 3V3        GND      ├─ GND
            GND ─┤ GND        GPIO23   ├─
            GPIO36─┤ VP         GPIO22  ├─
            GPIO39─┤ VN         GPIO1   ├─ (TXD - DO NOT USE)
            GPIO34─┤ GPIO34 ←SOIL ADC  │
            GPIO35─┤ GPIO35 ←RAIN      │
            GPIO32─┤ GPIO32     GPIO3  ├─ (RXD - DO NOT USE)
            GPIO33─┤ GPIO33     GPIO21 ├─
            GPIO25─┤ GPIO25     GND    ├─ GND
            GPIO26─┤ GPIO26 ←RELAY     │
            GPIO27─┤ GPIO27     GPIO19 ├─
            GPIO14─┤ GPIO14     GPIO18 ├─ ←ULTRASONIC ECHO
            GPIO12─┤ GPIO12     GPIO5  ├─ ←ULTRASONIC TRIG
               GND─┤ GND        GPIO17 ├─
            GPIO13─┤ GPIO13     GPIO16 ├─
            GPIO9 ─┤ SD2        GPIO4  ├─ ←DHT22
            GPIO10─┤ SD3        GPIO0  ├─ (BOOT - careful)
            GPIO11─┤ CMD        GPIO2  ├─ ←LED (built-in)
            GPIO6 ─┤ CLK        GPIO15 ├─
            GPIO7 ─┤ SD0        GPIO8  ├─
            GPIO8 ─┤ SD1        GPIO7  ├─
                 └──────────────────────┘

⚠️ GPIO 6-11 connected to SPI Flash — DO NOT USE for sensors
⚠️ GPIO 1, 3 are UART TX/RX — avoid for sensors
```
