"""
AI-Based Overtaking Safety System - Python Server
Flask API for receiving images from ESP32-CAM and performing vehicle detection
Author: AI Safety System
Version: 1.0
"""

from flask import Flask, request, jsonify
import numpy as np
import cv2
import os
import sys
import logging
from datetime import datetime

try:
    from ultralytics import YOLO
except Exception:
    YOLO = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load YOLOv8 model
model = None
if YOLO is None:
    logger.warning("ultralytics is not installed. Falling back to edge detection")
    USE_YOLO = False
else:
    try:
        logger.info("Loading YOLOv8 model...")
        model = YOLO('yolov8n.pt')  # nano model for real-time performance
        logger.info("YOLOv8 model loaded successfully")
        USE_YOLO = True
    except Exception as e:
        logger.warning(f"YOLO model failed to load: {e}. Falling back to edge detection")
        USE_YOLO = False

# Statistics
stats = {
    "total_frames": 0,
    "safe_count": 0,
    "unsafe_count": 0
}


def build_html_page(title, heading, message, endpoints_html):
        return f"""<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='utf-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; background: #0f172a; color: #e2e8f0; }}
        .wrap {{ max-width: 900px; margin: 0 auto; padding: 32px 20px; }}
        .card {{ background: #111827; border: 1px solid #334155; border-radius: 16px; padding: 24px; box-shadow: 0 12px 30px rgba(0,0,0,.25); }}
        h1 {{ margin-top: 0; font-size: 2rem; }}
        p {{ line-height: 1.6; color: #cbd5e1; }}
        code, pre {{ background: #0b1220; color: #93c5fd; border-radius: 8px; }}
        code {{ padding: 2px 6px; }}
        pre {{ padding: 14px; overflow-x: auto; }}
        .grid {{ display: grid; gap: 14px; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); margin-top: 18px; }}
        .item {{ background: #0b1220; border: 1px solid #243043; border-radius: 12px; padding: 14px; }}
        a {{ color: #60a5fa; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .muted {{ color: #94a3b8; font-size: .95rem; }}
    </style>
</head>
<body>
    <div class='wrap'>
        <div class='card'>
            <h1>{heading}</h1>
            <p>{message}</p>
            <div class='grid'>
                {endpoints_html}
            </div>
        </div>
    </div>
</body>
</html>"""


def analyze_frame_yolo(image):
    """
    Analyze frame using YOLOv8 for vehicle detection
    Returns: safety_status, processed_image, vehicle_count
    """
    try:
        # Run YOLOv8 inference
        results = model(image, conf=0.5, verbose=False)
        
        vehicle_classes = [2, 5, 7]  # car, bus, truck (COCO classes)
        vehicle_count = 0
        
        # Parse results
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                
                # Count vehicle-like objects
                if cls in vehicle_classes and conf > 0.5:
                    vehicle_count += 1
                    
                    # Draw bounding box
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(image, f"Vehicle {conf:.2f}", 
                              (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 
                              0.5, (0, 255, 0), 2)
        
        # Decision logic: multiple vehicles = NOT_SAFE
        status = "NOT_SAFE" if vehicle_count > 1 else "SAFE"
        
        logger.info(f"YOLO: Detected {vehicle_count} vehicles - Status: {status}")
        return status, image, vehicle_count
        
    except Exception as e:
        logger.error(f"YOLO analysis error: {e}")
        return "ERROR", image, 0


def analyze_frame_edge_detection(image):
    """
    Fallback: Analyze frame using edge detection and line detection
    Returns: safety_status, processed_image
    """
    try:
        # Resize for faster processing
        original_height = image.shape[0]
        image = cv2.resize(image, (320, 240))
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply GaussianBlur to reduce noise
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection using Canny
        edges = cv2.Canny(blur, 50, 150)
        
        # Detect lines using Hough Transform
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50,
                                minLineLength=40, maxLineGap=20)
        
        line_count = 0 if lines is None else len(lines)
        
        # Draw detected lines on image
        if lines is not None:
            for line in lines[:20]:
                x1, y1, x2, y2 = line[0]
                cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Add text info
        cv2.putText(image, f"Lines: {line_count}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        # Decision logic: high line count indicates obstacles
        status = "NOT_SAFE" if line_count > 25 else "SAFE"
        
        logger.info(f"Edge Detection: Found {line_count} lines - Status: {status}")
        return status, image
        
    except Exception as e:
        logger.error(f"Edge detection error: {e}")
        return "ERROR", image


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "OK",
        "method": "YOLO" if USE_YOLO else "Edge Detection",
        "stats": stats
    }), 200


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    """
    Main endpoint: Receive image from ESP32-CAM and perform analysis
    Returns: JSON with safety status
    """
    try:
        if request.method == 'GET':
            html = build_html_page(
                "AI Overtaking Safety System - Analyze",
                "Analyze Endpoint",
                "This endpoint accepts POST requests from the ESP32-CAM. Open the links below for browser-friendly pages.",
                """
                <div class='item'><b>Status</b><br><span class='muted'>Use POST with raw JPEG bytes</span></div>
                <div class='item'><b>Example</b><pre>POST /analyze\nContent-Type: application/octet-stream</pre></div>
                <div class='item'><b>Browser Pages</b><br><a href='/'>Home</a><br><a href='/health'>Health</a><br><a href='/stats'>Stats</a></div>
                """
            )
            return html, 200, {"Content-Type": "text/html; charset=utf-8"}

        if not request.data:
            logger.warning("Empty image data received")
            return jsonify({"status": "ERROR", "message": "No image data"}), 400
        
        # Decode image from binary data
        file_bytes = np.frombuffer(request.data, np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if image is None:
            logger.warning("Failed to decode image")
            return jsonify({"status": "ERROR", "message": "Invalid image format"}), 400
        
        # Update statistics
        stats["total_frames"] += 1
        
        # Perform analysis
        if USE_YOLO:
            status, processed_image, vehicle_count = analyze_frame_yolo(image)
        else:
            status, processed_image = analyze_frame_edge_detection(image)
            vehicle_count = 0
        
        # Update statistics
        if status == "SAFE":
            stats["safe_count"] += 1
        elif status == "NOT_SAFE":
            stats["unsafe_count"] += 1
        
        # Log response
        logger.info(f"Frame #{stats['total_frames']} - Response: {status}")
        
        return jsonify({
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "frames_processed": stats["total_frames"],
            "vehicle_count": vehicle_count
        }), 200
        
    except Exception as e:
        logger.error(f"Analysis endpoint error: {e}")
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    total = stats["total_frames"]
    safe_percent = (stats["safe_count"] / total * 100) if total > 0 else 0
    
    return jsonify({
        "total_frames": total,
        "safe_count": stats["safe_count"],
        "unsafe_count": stats["unsafe_count"],
        "safe_percentage": round(safe_percent, 2),
        "detection_method": "YOLO" if USE_YOLO else "Edge Detection"
    }), 200


@app.route('/', methods=['GET'])
def home():
        """Interactive dashboard page"""
        html = f"""<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='utf-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <title>AI Overtaking Safety Dashboard</title>
    <style>
        :root {{
            --bg-0: #0b1320;
            --bg-1: #0f1b30;
            --bg-2: #14233d;
            --card: #101a2b;
            --card-border: #2a3d5c;
            --text: #e5edf8;
            --muted: #9ab0cc;
            --accent: #22c55e;
            --warn: #f59e0b;
            --danger: #ef4444;
            --info: #3b82f6;
        }}
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            font-family: "Segoe UI", Tahoma, Verdana, sans-serif;
            color: var(--text);
            background:
                radial-gradient(1200px 400px at 10% -10%, #1f3b66 0%, rgba(31,59,102,0) 70%),
                radial-gradient(1000px 350px at 100% -20%, #214d43 0%, rgba(33,77,67,0) 70%),
                linear-gradient(160deg, var(--bg-0), var(--bg-1) 55%, var(--bg-2));
            min-height: 100vh;
        }}
        .wrap {{ max-width: 1200px; margin: 0 auto; padding: 24px 16px 40px; }}
        .title {{ margin: 0; font-size: 2rem; letter-spacing: .2px; }}
        .sub {{ margin: 6px 0 18px; color: var(--muted); }}
        .status-pill {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            border: 1px solid var(--card-border);
            padding: 6px 12px;
            border-radius: 999px;
            background: rgba(16,26,43,.7);
            font-size: .92rem;
            margin-bottom: 14px;
        }}
        .dot {{ width: 9px; height: 9px; border-radius: 50%; background: var(--danger); }}
        .dot.ok {{ background: var(--accent); box-shadow: 0 0 10px rgba(34,197,94,.7); }}
        .grid {{ display: grid; gap: 14px; }}
        .grid-4 {{ grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }}
        .grid-2 {{ grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); margin-top: 14px; }}
        .card {{
            background: linear-gradient(180deg, rgba(16,26,43,.95), rgba(14,22,35,.95));
            border: 1px solid var(--card-border);
            border-radius: 14px;
            padding: 14px;
            box-shadow: 0 8px 26px rgba(0,0,0,.25);
        }}
        .k {{ color: var(--muted); font-size: .86rem; }}
        .v {{ font-size: 1.4rem; font-weight: 700; margin-top: 6px; }}
        .v.small {{ font-size: 1rem; word-break: break-all; }}
        .row {{ display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }}
        button {{
            border: 1px solid #37527a;
            background: #143056;
            color: var(--text);
            border-radius: 9px;
            padding: 8px 12px;
            cursor: pointer;
        }}
        button:hover {{ background: #1b3f70; }}
        input {{
            width: 100%;
            border: 1px solid #38527a;
            background: #0c1a30;
            color: var(--text);
            border-radius: 9px;
            padding: 9px 10px;
            outline: none;
        }}
        .muted {{ color: var(--muted); font-size: .9rem; }}
        .bar {{ height: 10px; width: 100%; border-radius: 99px; background: #1b2940; overflow: hidden; margin-top: 10px; border: 1px solid #314866; }}
        .bar > span {{ display: block; height: 100%; width: 0%; background: linear-gradient(90deg, #22c55e, #84cc16); transition: width .4s ease; }}
        .json {{
            margin-top: 10px;
            background: #081325;
            border: 1px solid #2a3d5c;
            border-radius: 10px;
            padding: 10px;
            max-height: 260px;
            overflow: auto;
            white-space: pre-wrap;
            font-family: Consolas, monospace;
            font-size: .86rem;
            color: #c7d8f2;
        }}
        img {{ width: 100%; border-radius: 10px; border: 1px solid #2f4465; background: #000; min-height: 220px; object-fit: contain; }}
    </style>
</head>
<body>
    <div class='wrap'>
        <h1 class='title'>AI Overtaking Safety Dashboard</h1>
        <p class='sub'>Live monitoring panel for health, stats, and ESP32 camera stream.</p>
        <div class='status-pill'><span id='serverDot' class='dot'></span><span id='serverState'>Connecting...</span></div>

        <div class='grid grid-4'>
            <div class='card'><div class='k'>Detection Method</div><div class='v' id='method'>-</div></div>
            <div class='card'><div class='k'>Total Frames</div><div class='v' id='totalFrames'>0</div></div>
            <div class='card'><div class='k'>Current Safety</div><div class='v' id='safetyNow'>-</div></div>
            <div class='card'><div class='k'>Safe Percentage</div><div class='v' id='safePct'>0%</div></div>
        </div>

        <div class='grid grid-2'>
            <div class='card'>
                <div class='row'>
                    <div style='flex:1'>
                        <div class='k'>ESP32 Stream URL</div>
                        <input id='streamUrl' value='' placeholder='http://192.168.x.x:81/stream'>
                    </div>
                </div>
                <div class='row' style='margin-top:10px'>
                    <button id='loadStream'>Load Stream</button>
                    <button id='openStream'>Open Stream Tab</button>
                </div>
                <p class='muted' style='margin:10px 0 8px'>Tip: set your ESP32 IP here to view live stream.</p>
                <img id='streamImg' alt='ESP32 Stream'>
            </div>

            <div class='card'>
                <div class='k'>Safety Ratio</div>
                <div class='bar'><span id='ratioBar'></span></div>
                <div class='row' style='margin-top:10px'>
                    <div class='muted'>Safe: <span id='safeCount'>0</span></div>
                    <div class='muted'>Unsafe: <span id='unsafeCount'>0</span></div>
                </div>
                <div class='row' style='margin-top:10px'>
                    <button id='refreshNow'>Refresh Now</button>
                    <button id='toggleAuto'>Pause Auto Refresh</button>
                    <button id='openAnalyze'>Open Analyze Help</button>
                </div>
                <div class='json' id='lastJson'>{{}}</div>
            </div>
        </div>
    </div>

    <script>
        const methodEl = document.getElementById('method');
        const totalFramesEl = document.getElementById('totalFrames');
        const safetyNowEl = document.getElementById('safetyNow');
        const safePctEl = document.getElementById('safePct');
        const safeCountEl = document.getElementById('safeCount');
        const unsafeCountEl = document.getElementById('unsafeCount');
        const ratioBarEl = document.getElementById('ratioBar');
        const serverDot = document.getElementById('serverDot');
        const serverState = document.getElementById('serverState');
        const lastJson = document.getElementById('lastJson');
        const streamUrlInput = document.getElementById('streamUrl');
        const streamImg = document.getElementById('streamImg');

        let auto = true;
        let timer = null;

        async function fetchJson(path) {{
            const res = await fetch(path + '?t=' + Date.now(), {{ cache: 'no-store' }});
            if (!res.ok) throw new Error(path + ' ' + res.status);
            return res.json();
        }}

        function setState(ok, text) {{
            serverDot.classList.toggle('ok', ok);
            serverState.textContent = text;
        }}

        async function refresh() {{
            try {{
                const [health, stats] = await Promise.all([
                    fetchJson('/health'),
                    fetchJson('/stats')
                ]);

                methodEl.textContent = stats.detection_method || health.method || '-';
                totalFramesEl.textContent = String(stats.total_frames ?? 0);
                safePctEl.textContent = String(stats.safe_percentage ?? 0) + '%';
                safeCountEl.textContent = String(stats.safe_count ?? 0);
                unsafeCountEl.textContent = String(stats.unsafe_count ?? 0);
                safetyNowEl.textContent = (stats.unsafe_count > 0 && stats.total_frames === stats.unsafe_count) ? 'NOT_SAFE' : 'SAFE';
                ratioBarEl.style.width = String(Math.max(0, Math.min(100, Number(stats.safe_percentage || 0)))) + '%';
                lastJson.textContent = JSON.stringify({{ health, stats }}, null, 2);
                setState(true, 'Server Online');
            }} catch (e) {{
                setState(false, 'Server Offline / Error');
                lastJson.textContent = String(e);
            }}
        }}

        function applyStream() {{
            const url = streamUrlInput.value.trim();
            if (!url) return;
            streamImg.src = url + (url.includes('?') ? '&' : '?') + 't=' + Date.now();
            localStorage.setItem('esp32StreamUrl', url);
        }}

        function startAuto() {{
            if (timer) clearInterval(timer);
            timer = setInterval(() => {{ if (auto) refresh(); }}, 1200);
        }}

        document.getElementById('refreshNow').onclick = refresh;
        document.getElementById('loadStream').onclick = applyStream;
        document.getElementById('openStream').onclick = () => {{
            const url = streamUrlInput.value.trim();
            if (url) window.open(url, '_blank');
        }};
        document.getElementById('openAnalyze').onclick = () => window.open('/analyze', '_blank');
        document.getElementById('toggleAuto').onclick = (e) => {{
            auto = !auto;
            e.target.textContent = auto ? 'Pause Auto Refresh' : 'Resume Auto Refresh';
        }};

        const saved = localStorage.getItem('esp32StreamUrl');
        streamUrlInput.value = saved || 'http://192.168.137.215:81/stream';
        applyStream();
        refresh();
        startAuto();
    </script>
</body>
</html>"""
        return html, 200, {"Content-Type": "text/html; charset=utf-8"}


@app.route('/ui', methods=['GET'])
def ui_page():
    """Dedicated browser UI page for manual testing."""
    endpoints_html = f"""
    <div class='item'><b>Status</b><br><span class='muted'>Dedicated UI test page</span></div>
    <div class='item'><b>Server</b><br><span class='muted'>AI Overtaking Safety System</span></div>
    <div class='item'><b>Analyze</b><br><a href='/analyze'>Open analyze help</a></div>
    <div class='item'><b>Health</b><br><a href='/health'>Open health check</a></div>
    <div class='item'><b>Stats</b><br><a href='/stats'>Open statistics</a></div>
    """
    html = build_html_page(
        "AI Overtaking Safety System - UI",
        "Camera UI",
        "If you can see this page, the updated server is active.",
        endpoints_html
    )
    return html, 200, {"Content-Type": "text/html; charset=utf-8"}


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"status": "ERROR", "message": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({"status": "ERROR", "message": "Internal server error"}), 500


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🚀 AI Overtaking Safety System - Server started")
    logger.info(f"Detection Method: {'YOLOv8' if USE_YOLO else 'Edge Detection'}")
    logger.info("📡 Listening on http://0.0.0.0:5000")
    logger.info("=" * 60)
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
