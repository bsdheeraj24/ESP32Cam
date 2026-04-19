#!/usr/bin/env python3
"""
Quick Reference - AI Overtaking Safety System
One-page guide for getting started quickly
"""

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║              🚗 AI OVERTAKING SAFETY SYSTEM - QUICK START 🚗                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 WHAT YOU HAVE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ ESP32 Arduino Code:        ESP32_CAM_OvertakingSafety.ino
✅ Python Flask Server:        server.py (with YOLOv8 support)
✅ Configuration File:          config.py
✅ Test Client:                test_client.py
✅ Dependencies List:           requirements.txt
✅ Full Documentation:          SETUP_GUIDE.md
✅ README:                      README.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ 30-SECOND START (Testing Only - No Hardware Needed)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Activate Python environment:
   .\.venv\Scripts\Activate.ps1

2. Install dependencies:
   pip install -r requirements.txt

3. Start server (Terminal 1):
   python server.py

4. Test system (Terminal 2):
   python test_client.py http://localhost:5000

Expected: All tests PASS ✓

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 PRODUCTION SETUP (With ESP32-CAM Hardware)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 1: Arduino setup
   ├─ Install Arduino IDE
   ├─ Add ESP32 board support
   ├─ Configure for "ESP32 Wrover Module"
   └─ Install arduino-esp32 library

STEP 2: Update Arduino code
   ├─ Edit line 16: WIFI_SSID = "YOUR_SSID"
   ├─ Edit line 17: WIFI_PASSWORD = "PASSWORD"
   └─ Edit line 20: SERVER_URL = "http://192.168.1.XXX:5000/analyze"

STEP 3: Flash ESP32
   ├─ Connect USB-to-Serial adapter
   ├─ Open ESP32_CAM_OvertakingSafety.ino
   ├─ Click Upload
   └─ Watch Serial Monitor (115200 baud) for WiFi connection

STEP 4: Run Python server
   python server.py

STEP 5: Verify connection
   ├─ Check ESP32 Serial Monitor for "WiFi ✓ Connected"
   ├─ Check Python server logs for incoming frames
   └─ LED should respond to safety status

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 SYSTEM COMPONENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────────────┐
│ ESP32-CAM (ESP32_CAM_OvertakingSafety.ino)                      │
├─────────────────────────────────────────────────────────────────┤
│ ✓ Captures video frames from OV2640 camera                      │
│ ✓ Connects to WiFi network (2.4GHz)                             │
│ ✓ Sends images via HTTP POST to server                          │
│ ✓ Controls LED on GPIO4 (Safety indicator)                      │
│ ✓ Auto-reconnect on WiFi disconnect                             │
│ ✓ Serial logging for debugging                                  │
└─────────────────────────────────────────────────────────────────┘
              │
              │ HTTP POST (JPEG image)
              │ Requests every 1 second
              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Python Server (server.py)                                       │
├─────────────────────────────────────────────────────────────────┤
│ ✓ Flask HTTP API (port 5000)                                    │
│ ✓ YOLOv8 vehicle detection (nano model)                         │
│ ✓ Real-time image processing                                    │
│ ✓ Safety decision logic (SAFE/NOT_SAFE)                         │
│ ✓ Statistics tracking                                            │
│ ✓ Fallback edge detection method                                │
│ ✓ Multi-threaded request handling                               │
└─────────────────────────────────────────────────────────────────┘
              │
              │ JSON Response
              │ {"status": "SAFE"/"NOT_SAFE"}
              ▼
┌─────────────────────────────────────────────────────────────────┐
│ ESP32 LED Control                                               │
├─────────────────────────────────────────────────────────────────┤
│ GPIO4 LOW  =  LED ON   = SAFE to overtake (≤1 vehicle)          │
│ GPIO4 HIGH =  LED OFF  = NOT SAFE to overtake (>1 vehicle)      │
└─────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 DECISION LOGIC
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Image Analysis
   │
   ├─ YOLOv8 Detection
   │  ├─ Count vehicles (cars, buses, trucks)
   │  └─ Confidence threshold: 50%
   │
   └─ Decision
      ├─ 0-1 vehicles → SAFE ✓ (LED ON)
      └─ 2+ vehicles  → NOT_SAFE ✗ (LED OFF)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔌 API ENDPOINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GET  /                   → API documentation
GET  /health             → Server health check
GET  /stats              → System statistics
POST /analyze            → Image analysis (used by ESP32-CAM)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 CONFIGURATION FILES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

config.py
├─ ESP32_SERVER_IP = "192.168.1.100"     ← Your server IP
├─ WIFI_SSID = "YOUR_SSID"               ← Your WiFi name
├─ WIFI_PASSWORD = "PASSWORD"            ← Your WiFi password
├─ SAFE_VEHICLE_THRESHOLD = 1            ← Safety threshold
└─ YOLO_MODEL = "yolov8n.pt"             ← Detection model

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧪 TESTING WITHOUT HARDWARE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

python test_client.py [SERVER_URL]

Scenarios tested:
├─ empty              → No vehicles (SAFE)
├─ one_vehicle        → Single vehicle (SAFE)
├─ multiple_vehicles  → Two vehicles (NOT_SAFE)
└─ crowded            → Multiple vehicles (NOT_SAFE)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐛 QUICK TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Problem: "ModuleNotFoundError: No module named 'ultralytics'"
Solution: pip install ultralytics

Problem: "Port 5000 already in use"
Solution: netstat -ano | findstr :5000
         taskkill /PID [PID] /F

Problem: "ESP32 won't connect to WiFi"
Solution: Check SSID/password, must be 2.4GHz (not 5GHz)

Problem: "HTTP timeout from ESP32"
Solution: Check server IP in line 20 of .ino file
         Test: ping 192.168.1.100 (from another device)

Problem: "Camera initialization failed"
Solution: Check USB connection
         Try different USB port
         Verify board is "ESP32 Wrover Module"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 PERFORMANCE METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Frame Capture Time:        200-300ms (ESP32-CAM)
Image Transmission:        50-150ms (WiFi)
Server Processing (YOLO):  150-250ms (Python)
Response Send:             20-50ms
────────────────────────
Total Round-Trip:          400-600ms
Frames Per Second:         1.5-2.5 FPS
Safety Decision Latency:   ~500ms

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 DOCUMENTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

README.md              → Overview and features
SETUP_GUIDE.md         → Detailed setup instructions
ESP32*.ino             → ESP32-CAM firmware with comments
server.py              → Python server with detailed comments
config.py              → Configuration options
test_client.py         → Test harness for development

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 DEPLOYMENT CHECKLIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hardware:
   ☐ ESP32-CAM purchased and tested
   ☐ Camera module installed and working
   ☐ LED with resistor connected to GPIO4
   ☐ USB-to-Serial adapter available
   ☐ 5V power supply ready

Software Setup:
   ☐ Arduino IDE installed
   ☐ ESP32 board support added
   ☐ WiFi credentials updated (lines 16-17 in .ino)
   ☐ Server IP configured (line 20 in .ino)
   ☐ Python 3.8+ installed
   ☐ Virtual environment created
   ☐ Dependencies installed (pip install -r requirements.txt)

Testing:
   ☐ Test server without hardware (python test_client.py)
   ☐ Verify all tests pass
   ☐ Upload ESP32 code
   ☐ Monitor ESP32 Serial output
   ☐ Verify WiFi connection
   ☐ Check LED response
   ☐ Monitor server logs

Deployment:
   ☐ Server running: python server.py
   ☐ ESP32-CAM connected and operational
   ☐ LED indicator responding correctly
   ☐ Statistics updating: curl http://localhost:5000/stats
   ☐ System monitoring ready

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 TIPS & TRICKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Find your computer IP:
  Windows: ipconfig | findstr IPv4
  Mac/Linux: ifconfig | grep "inet "

• Monitor server in real-time:
  while($true) { curl http://localhost:5000/stats; sleep 2 }

• Clear ESP32 settings:
  Hold FLASH button for 10 seconds to reset

• Use development mode:
  Set USE_YOLO = False in server.py for faster testing

• Profile performance:
  Set ENABLE_PROFILING = True in config.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ READY TO START? Run: python server.py

For detailed help, see: SETUP_GUIDE.md

╚══════════════════════════════════════════════════════════════════════════════╝
""")
