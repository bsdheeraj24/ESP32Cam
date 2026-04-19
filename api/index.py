from flask import Flask, request, jsonify
import numpy as np
import cv2
from datetime import datetime

app = Flask(__name__)

stats = {
    "total_frames": 0,
    "safe_count": 0,
    "unsafe_count": 0,
}


def analyze_frame_edge_detection(image):
    image = cv2.resize(image, (320, 240))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        50,
        minLineLength=40,
        maxLineGap=20,
    )

    line_count = 0 if lines is None else len(lines)
    status = "NOT_SAFE" if line_count > 25 else "SAFE"
    return status, line_count


@app.route("/", methods=["GET"])
def home():
    html = """<!DOCTYPE html>
<html>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>AI Overtaking Safety API</title>
  <style>
    body { font-family: Segoe UI, Arial, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; }
    .wrap { max-width: 920px; margin: 0 auto; padding: 24px; }
    .card { background: #111827; border: 1px solid #334155; border-radius: 14px; padding: 18px; }
    a { color: #60a5fa; text-decoration: none; }
    code { background: #0b1220; padding: 2px 6px; border-radius: 6px; }
  </style>
</head>
<body>
  <div class='wrap'>
    <div class='card'>
      <h1>AI Overtaking Safety API</h1>
      <p>Vercel deployment endpoint for ESP32-CAM image analysis.</p>
      <p>Use <code>POST /analyze</code> with JPEG bytes from ESP32-CAM.</p>
      <p><a href='/health'>Open health</a> | <a href='/stats'>Open stats</a> | <a href='/analyze'>Analyze help</a></p>
    </div>
  </div>
</body>
</html>"""
    return html, 200, {"Content-Type": "text/html; charset=utf-8"}


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "OK",
        "method": "Edge Detection",
        "stats": stats,
        "platform": "Vercel",
    })


@app.route("/stats", methods=["GET"])
def get_stats():
    total = stats["total_frames"]
    safe_pct = (stats["safe_count"] / total * 100) if total > 0 else 0
    return jsonify({
        "total_frames": total,
        "safe_count": stats["safe_count"],
        "unsafe_count": stats["unsafe_count"],
        "safe_percentage": round(safe_pct, 2),
        "detection_method": "Edge Detection",
    })


@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    if request.method == "GET":
        return jsonify({
            "status": "OK",
            "message": "Use POST with raw JPEG bytes from ESP32-CAM.",
            "content_type": "application/octet-stream",
        })

    if not request.data:
        return jsonify({"status": "ERROR", "message": "No image data"}), 400

    try:
        file_bytes = np.frombuffer(request.data, np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if image is None:
            return jsonify({"status": "ERROR", "message": "Invalid image format"}), 400

        stats["total_frames"] += 1
        status, line_count = analyze_frame_edge_detection(image)

        if status == "SAFE":
            stats["safe_count"] += 1
        else:
            stats["unsafe_count"] += 1

        return jsonify({
            "status": status,
            "line_count": line_count,
            "frames_processed": stats["total_frames"],
            "timestamp": datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500
