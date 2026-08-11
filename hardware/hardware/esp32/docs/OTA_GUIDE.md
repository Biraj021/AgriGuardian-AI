# OTA (Over-the-Air) Firmware Update Guide

## Overview

OTA allows you to update the ESP32 firmware over WiFi without a USB cable. This is essential for deployed field nodes that are physically hard to reach.

## Prerequisites

- ESP32 and your computer must be on the **same WiFi network**
- `OTA_ENABLED true` in `config.h` (enabled by default)
- `OTA_PASSWORD` set in `config.h`

## Uploading via Arduino IDE

1. Ensure the ESP32 is powered on and connected to WiFi
2. In Arduino IDE, go to **Tools → Port**
3. Look for a network port: `agriguardian-esp32-001 at 192.168.1.xxx`
4. Select it instead of the USB COM port
5. Click **Upload** (→ arrow)
6. When prompted, enter the OTA password from `config.h`
7. Wait for the upload to complete (~30 seconds)
8. The ESP32 auto-reboots with the new firmware

## Uploading via PlatformIO

Edit `platformio.ini` and uncomment the OTA section:

```ini
upload_protocol = espota
upload_port = 192.168.1.xxx    ; ← Your ESP32's IP
upload_flags =
    --auth=agriguardian-ota    ; ← Your OTA password
```

Then run:

```bash
pio run -t upload
```

## Uploading via Command Line

```bash
python -m esptool --chip esp32 ota \
  --host 192.168.1.xxx \
  --port 3232 \
  --auth agriguardian-ota \
  firmware.bin
```

Or using Arduino's `espota.py`:

```bash
python espota.py -i 192.168.1.xxx -p 3232 -a agriguardian-ota -f firmware.bin
```

## Safety During OTA

When an OTA update starts:

1. **All relays are immediately forced OFF** — this is a safety measure since the firmware is being replaced and relay state cannot be guaranteed during the flash process.
2. The update progress is logged to Serial (if connected).
3. On success, the ESP32 reboots automatically.
4. On failure, the ESP32 continues running the previous firmware (no brick risk).

## Finding the ESP32's IP Address

### Option 1: Serial Monitor
Connect via USB and open Serial Monitor at 115200 baud. The IP is printed on boot:
```
[WIFI] IP address: 192.168.1.xxx
```

### Option 2: Router Admin Panel
Check your router's connected devices list for a device named `agriguardian-esp32-001`.

### Option 3: mDNS (if supported)
The OTA hostname is set to `DEVICE_ID`. On some networks, you can use:
```
agriguardian-esp32-001.local
```

## Security Notes

- Change `OTA_PASSWORD` from the default before deploying to the field
- OTA is only active while WiFi is connected — it's not exposed to the internet unless you port-forward (don't)
- The OTA port (3232) only accepts authenticated connections
- Failed authentication attempts are logged to Serial
- Consider disabling OTA in production (`OTA_ENABLED false`) if remote updates are not needed
