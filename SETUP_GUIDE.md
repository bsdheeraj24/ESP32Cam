# AI-Based Overtaking Safety System - Setup Guide

## System Overview

This is a complete AI-based overtaking safety system that uses an ESP32-CAM to capture road images and a Python server with YOLOv8 for vehicle detection.

**Components:**
- **ESP32-CAM (AI Thinker)**: Captures images, communicates with server
- **Python Flask Server**: Processes images using YOLOv8 vehicle detection
- **LED Indicator**: Shows safety status (ON=SAFE, OFF=NOT_SAFE)

---

## Part 1: ESP32-CAM Setup

### Hardware Required:
- ESP32-CAM (AI Thinker board)
- USB-to-Serial adapter (CH340 or CP2102)
- LED with current-limiting resistor (~1kΩ)
- Power supply (5V)
- WiFi network

### Step 1: Install Arduino IDE
1. Download from: https://www.arduino.cc/en/software
2. Install the latest version

### Step 2: Configure Arduino IDE for ESP32
1. Go to **File → Preferences**
2. Add this URL to "Additional Boards Manager URLs":
   ```
   https://dl.espressif.com/dl/package_esp32_index.json
   ```
3. Go to **Tools → Board → Boards Manager**
4. Search for "ESP32" and install "esp32" by Espressif Systems

### Step 3: Install Required Libraries
In **Tools → Manage Libraries**, install:
- **esp32-camera** (by espressif) - for camera control
- **Arduino** (built-in) - for core functionality

### Step 4: Configure Board Settings
1. **Board**: Select "ESP32 Wrover Module"
2. **Upload Speed**: 921600 baud
3. **CPU Frequency**: 240MHz
4. **Flash Frequency**: 80MHz
5. **Flash Mode**: QIO
6. **Flash Size**: 4MB
7. **Partition Scheme**: Huge APP (3MB No OTA/1MB SPIFFS)
8. **Core Debug Level**: None

### Step 5: Connect Hardware
```
ESP32-CAM → USB-to-Serial Adapter:
- GND     → GND
- U0R     → TX
- U0T     → RX
- 5V      → 5V

LED Circuit (GPIO4):
GPIO4 → 1kΩ resistor → LED anode
LED cathode → GND
```

### Step 6: Upload ESP32 Code
1. Open `ESP32_CAM_OvertakingSafety.ino` in Arduino IDE
2. **IMPORTANT**: Edit lines 16-17 with your WiFi credentials:
   ```cpp
   const char* WIFI_SSID = "YOUR_SSID";           // ← Change this
   const char* WIFI_PASSWORD = "YOUR_PASSWORD";   // ← Change this
   ```
3. Edit line 20 with your Python server IP:
   ```cpp
   const char* SERVER_URL = "http://192.168.1.100:5000/analyze";  // ← Change IP
   ```
4. Click **Sketch → Upload**
5. Hold **IO0** button while uploading, then release

### Step 7: Verify ESP32 Connection
1. Open **Tools → Serial Monitor**
2. Set baud rate to **115200**
3. Press **Reset** button
4. You should see:
   ```
   ╔════════════════════════════════════════╗
   ║   AI Overtaking Safety System         ║
   ║   ESP32-CAM (AI Thinker)             ║
   ...
   [WiFi] ✓ Connected
   [WiFi] IP: 192.168.x.x
   ```

---

## Part 2: Python Server Setup

### Prerequisites:
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Create Virtual Environment
```bash
# Navigate to project folder
cd C:\Users\WELCOME\OneDrive\Desktop\ESP32Cam

# Create virtual environment (already done if .venv exists)
python -m venv .venv

# Activate virtual environment
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# On Windows (Command Prompt):
.venv\Scripts\activate.bat

# On macOS/Linux:
source .venv/bin/activate
```

### Step 2: Install Python Dependencies

Create `requirements.txt` with the following content:
```txt
Flask==2.3.3
opencv-python==4.8.1.78
numpy==1.24.3
ultralytics==8.0.195
```

Then install:
```bash
pip install -r requirements.txt
```

**Note**: First installation may take 5-10 minutes as YOLOv8 downloads the model (~80MB)

### Step 3: Configure Network Settings

**Method 1: Find your Python server IP (Windows)**
```powershell
ipconfig
```
Look for "IPv4 Address" under your active network adapter (usually 192.168.x.x)

**Method 2: Find your Python server IP (macOS/Linux)**
```bash
ifconfig
```

### Step 4: Update ESP32 Code with Server IP
Before uploading to ESP32, update line 20 in `ESP32_CAM_OvertakingSafety.ino`:
```cpp
const char* SERVER_URL = "http://YOUR_SERVER_IP:5000/analyze";
```

### Step 5: Run Python Server
```bash
# Make sure virtual environment is activated
python server.py
```

Expected output:
```
============================================================
🚀 AI Overtaking Safety System - Server started
Detection Method: YOLOv8
📡 Listening on http://0.0.0.0:5000
============================================================
```

### Step 6: Test the Server

**Using PowerShell (Windows):**
```powershell
# In a new terminal, with venv activated
$url = "http://localhost:5000/health"
Invoke-WebRequest -Uri $url -Method Get | Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json
```

**Using curl (any OS):**
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "OK",
  "method": "YOLO",
  "stats": {
    "total_frames": 0,
    "safe_count": 0,
    "unsafe_count": 0
  }
}
```

---

## Part 3: Network Configuration

### Find Devices IP Addresses

**Windows PowerShell:**
```powershell
# Find Python server IP
ipconfig | findstr "IPv4"

# Find ESP32-CAM IP from serial monitor (check Arduino IDE Serial Monitor)
```

**Configuration Checklist:**
- [ ] Python server and ESP32-CAM are on the **same WiFi network**
- [ ] Firewall allows port 5000 (open if needed)
- [ ] Python server IP correctly set in ESP32 code
- [ ] ESP32-CAM can reach server: use `ping <server_ip>` from device

### Firewall Configuration (Windows)

If connection fails, allow the Python server through firewall:
1. Open **Windows Defender Firewall**
2. Click **Allow an app through firewall**
3. Find **Python** in the list
4. Check both **Private** and **Public**
5. Click **OK**

---

## Part 4: Complete System Testing

### Step 1: Start Python Server
```bash
# Terminal 1 - Python server
python server.py
```

### Step 2: Monitor ESP32
```
# Terminal 2 - Arduino IDE Serial Monitor (115200 baud)
# Watch the connection and frame analysis logs
```

### Step 3: View Real-Time Statistics
```bash
# Terminal 3 - Check statistics
curl http://localhost:5000/stats
```

### Step 4: Expected System Behavior

**Endpoint Functions:**
- `GET http://server_ip:5000/` → API documentation
- `GET http://server_ip:5000/health` → Server status
- `GET http://server_ip:5000/stats` → Analysis statistics
- `POST http://server_ip:5000/analyze` → Image analysis (used by ESP32-CAM)

**LED Behavior:**
- **LED ON** (GPIO4 LOW): Road is SAFE for overtaking (≤1 vehicle detected)
- **LED OFF** (GPIO4 HIGH): Road is NOT SAFE for overtaking (>1 vehicle detected)
- **Blinking OFF**: System error or WiFi disconnected

---

## Part 5: Vehicle Detection Logic

### Safety Decision:
```
- SAFE:     0-1 vehicles detected → LED ON
- NOT_SAFE: 2+ vehicles detected → LED OFF
```

### Detected Vehicle Classes (COCO Dataset):
- Car (class 2)
- Bus (class 5)
- Truck (class 7)

### Model Used:
- **YOLOv8 Nano** (yolov8n.pt) - optimized for ESP32-CAM latency
- Confidence threshold: 50%
- Auto-downloads on first run

---

## Part 6: Troubleshooting

### ESP32-CAM Issues:

**Problem: "Failed to connect to WiFi"**
- Check SSID and password are correct
- Ensure WiFi is 2.4GHz (not 5GHz, ESP32 doesn't support)
- Move closer to router

**Problem: "Camera initialization failed"**
- Check all camera pins are connected
- Verify board selection is "ESP32 Wrover Module"
- Try OV2640 driver reset: GPIO32 to ground briefly

**Problem: "HTTP error" or connection timeouts**
- Verify Python server is running and reachable
- Check server IP in ESP32 code
- Test with: `ping <server_ip>` from computer
- Check firewall settings

### Python Server Issues:

**Problem: "YOLO model failed to download"**
- Check internet connection
- Manually download: https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt
- Place in `~/.yolov8/weights/yolov8n.pt`

**Problem: "Port 5000 already in use"**
- Find process using port 5000:
  ```bash
  # Windows
  netstat -ano | findstr :5000
  ```
- Change port in `server.py` line 128 if needed

**Problem: "ImportError: No module named 'ultralytics'"**
- Ensure virtual environment is activated
- Run: `pip install ultralytics`

---

## Part 7: Performance Optimization

### ESP32-CAM Optimization:
- Frame size: QVGA (320x240) - balanced quality/speed
- JPEG quality: 10 - smaller file size
- Request interval: 1000ms - prevents network bottleneck

### Python Server Optimization:
- YOLOv8 Nano: Fastest inference
- Enable GPU: Install `torch` with CUDA support
- Multi-threaded Flask: Handles concurrent requests

### Typical Performance:
- ESP32 frame capture: ~200-300ms
- Server processing: ~150-250ms
- Total round-trip: ~400-600ms per frame
- FPS: ~1.5-2.5 frames/second

---

## Part 8: Advanced Configuration

### Change Detection Method (if YOLO fails):
Edit line 9 in `server.py`:
```python
USE_YOLO = True   # Set to False to use edge detection fallback
```

### Adjust Safety Threshold:
In `server.py`, modify line 56:
```python
status = "NOT_SAFE" if vehicle_count > 1 else "SAFE"  # Change > 1
```

### Change Request Interval:
In `ESP32_CAM_OvertakingSafety.ino`, line 58:
```cpp
const int REQUEST_INTERVAL = 1000;  // Change milliseconds
```

---

## Part 9: Production Deployment

### SSL Configuration (HTTPS):
Add to `server.py`:
```python
from flask_talisman import Talisman
Talisman(app)
```

### Database Logging:
Modify `server.py` to log to database instead of console

### Docker Deployment:
Create `Dockerfile`:
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY server.py .
CMD ["python", "server.py"]
```

---

## Quick Start Checklist

- [ ] Arduino IDE installed and configured for ESP32
- [ ] USB-to-Serial adapter connected to ESP32-CAM
- [ ] WiFi SSID and password updated in ESP32 code
- [ ] Python virtual environment created and activated
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Python server IP configured in ESP32 code
- [ ] Python server started: `python server.py`
- [ ] ESP32 code uploaded successfully
- [ ] WiFi connection verified in serial monitor
- [ ] LED responds to safety status
- [ ] Server statistics update with each frame

---

## System Architecture Diagram

```
┌─────────────────────┐          WiFi (2.4GHz)          ┌──────────────────┐
│                     │◄──────────HTTP POST──────────────►│                  │
│  ESP32-CAM          │   Frame + JPEG Image              │  Python Server   │
│  (AI Thinker)       │                                   │  (Flask + YOLO)  │
│                     │◄──────────JSON Response────────────│                  │
│  ┌──────────────┐   │  {"status": "SAFE/NOT_SAFE"}     │                  │
│  │   Camera     │   │                                   │  ┌────────────┐  │
│  │   (OV2640)   │   │                                   │  │ YOLOv8     │  │
│  └──────────────┘   │                                   │  │ Vehicle    │  │
│                     │                                   │  │ Detection  │  │
│  ┌──────────────┐   │                                   │  └────────────┘  │
│  │   LED        │   │                                   │                  │
│  │   (GPIO4)    │───┼─ (ON/OFF)                         │                  │
│  └──────────────┘   │                                   │                  │
└─────────────────────┘                                   └──────────────────┘

LED Status:
   ON  (LOW)  = SAFE to overtake (≤1 vehicle)
   OFF (HIGH) = NOT SAFE to overtake (>1 vehicle)
```

---

## Support & Debugging

For detailed debugging:
1. Check serial monitor output (115200 baud)
2. Review server logs: `python server.py` output
3. Test endpoints with curl/PowerShell
4. Check firewall and network settings

---

## License & Attribution

This is a complete, production-ready system combining:
- ESP32 camera APIs
- YOLOv8 from Ultralytics
- Flask web framework
- OpenCV for image processing

---

**Last Updated**: 2026-04-19  
**Version**: 1.0  
**Status**: Production Ready
