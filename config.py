"""
Configuration file for AI Overtaking Safety System
Edit these values according to your setup
"""

# ============================================
# ESP32-CAM Configuration
# ============================================

# Server IP address (change to your Python server IP)
# To find your IP: ipconfig (Windows) or ifconfig (Mac/Linux)
ESP32_SERVER_IP = "192.168.1.100"
ESP32_SERVER_PORT = 5000

# WiFi Credentials (update with your WiFi details)
WIFI_SSID = "YOUR_SSID"
WIFI_PASSWORD = "YOUR_PASSWORD"

# Frame capture settings
FRAME_CAPTURE_INTERVAL_MS = 1000  # 1 second between frames
FRAME_SIZE = "QVGA"  # 320x240 (options: QVGA, VGA, SVGA)
JPEG_QUALITY = 10    # 1-63 (lower = smaller file, higher = better quality)

# LED Settings
LED_PIN = 4  # GPIO4 on ESP32-CAM

# ============================================
# Python Server Configuration
# ============================================

# Server listening settings
SERVER_HOST = "0.0.0.0"  # Listen on all interfaces
SERVER_PORT = 5000
SERVER_DEBUG = False  # Set to True for development only

# Detection method
USE_YOLO = True  # True: YOLO vehicle detection, False: Edge detection fallback

# YOLO Settings
YOLO_MODEL = "yolov8n.pt"  # nano (fast), small, medium, large
YOLO_CONFIDENCE = 0.5      # 0-1 (higher = stricter detection)

# Vehicle detection classes (COCO dataset)
VEHICLE_CLASSES = [2, 5, 7]  # car, bus, truck

# Safety Decision Logic
SAFE_VEHICLE_THRESHOLD = 1   # If vehicles <= this, SAFE. Else NOT_SAFE
VEHICLE_DETECTION_CLASSES = {
    2: "car",
    5: "bus",
    7: "truck",
    3: "motorcycle"  # Optional: add motorcycles
}

# Image Processing
IMAGE_RESIZE_WIDTH = 320
IMAGE_RESIZE_HEIGHT = 240
EDGE_DETECT_THRESHOLD1 = 50
EDGE_DETECT_THRESHOLD2 = 150
HOUGH_THRESHOLD = 50

# Performance
MAX_WORKERS = 4  # Thread pool size for Flask
REQUEST_TIMEOUT = 10  # seconds

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "safety_system.log"

# ============================================
# Network Settings
# ============================================

# Firewall ports (these must be open for communication)
REQUIRED_PORTS = [5000]

# ============================================
# Advanced Settings
# ============================================

# Statistics tracking
ENABLE_STATS = True
STATS_UPDATE_INTERVAL = 60  # seconds

# Save analyzed frames (for debugging)
SAVE_DEBUG_FRAMES = False
DEBUG_FRAMES_FOLDER = "debug_frames"

# Performance monitoring
ENABLE_PROFILING = False
