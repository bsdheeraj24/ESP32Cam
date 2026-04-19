/*
 * AI-Based Overtaking Safety System - ESP32-CAM (AI Thinker)
 * Captures images and sends to Python server for AI analysis
 * Controls LED based on overtaking safety status
 * 
 * Board: ESP32 Wrover Module
 * Camera: OV2640
 * LED Pin: 4 (GPIO4)
 * 
 * Author: AI Safety System
 * Version: 1.0
 */

#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include "esp_http_server.h"
#include "freertos/task.h"

// ============================================
// WiFi Configuration
// ============================================
const char* WIFI_SSID = "Techyguide2";
const char* WIFI_PASSWORD = "12345678";

// ============================================
// Server Configuration
// ============================================
const char* SERVER_URL = "http://172.23.29.253:5000/analyze";  // Change IP if PC IP changes
const int REQUEST_TIMEOUT = 10000;  // 10 seconds

// ============================================
// ESP32 Camera Interface Configuration
// ============================================
const int CAMERA_WEB_PORT = 80;
WebServer cameraWebServer(CAMERA_WEB_PORT);
bool cameraWebStarted = false;
extern httpd_handle_t stream_httpd;
volatile bool stream_client_connected = false;

// ============================================
// Camera Pin Configuration (AI Thinker Board)
// ============================================
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// ============================================
// LED Pin Configuration
// ============================================
#define LED_PIN 4           // GPIO4 for LED control
#define LED_ON  LOW         // LED active LOW
#define LED_OFF HIGH        // LED inactive HIGH

// ============================================
// System Variables
// ============================================
int frame_count = 0;
unsigned long last_request_time = 0;
const int REQUEST_INTERVAL = 1000;  // 1 second between requests
String last_status = "INIT";
String last_server_response = "";
int last_http_code = 0;
int last_frame_bytes = 0;
unsigned long last_capture_ms = 0;
unsigned long last_http_ms = 0;

// ============================================
// Function: Print runtime diagnostics to terminal
// ============================================
void print_runtime_diagnostics(int frameBytes, unsigned long captureMs, unsigned long requestMs, const String& status) {
  last_frame_bytes = frameBytes;
  last_capture_ms = captureMs;
  last_http_ms = requestMs;
  last_status = status;
  Serial.print("[DIAG] FrameBytes=");
  Serial.print(frameBytes);
  Serial.print(", CaptureMs=");
  Serial.print(captureMs);
  Serial.print(", HttpMs=");
  Serial.print(requestMs);
  Serial.print(", RSSI=");
  Serial.print(WiFi.RSSI());
  Serial.print(" dBm, Heap=");
  Serial.print(ESP.getFreeHeap());
  Serial.print(" bytes, Status=");
  Serial.println(status);
}

// ============================================
// Function: Live browser status JSON
// ============================================
String json_escape(String value) {
  value.replace("\\", "\\\\");
  value.replace("\"", "\\\"");
  return value;
}

String build_status_json() {
  String json = "{";
  json += "\"frame_count\":" + String(frame_count) + ",";
  json += "\"status\":\"" + last_status + "\",";
  json += "\"http_code\":" + String(last_http_code) + ",";
  json += "\"frame_bytes\":" + String(last_frame_bytes) + ",";
  json += "\"capture_ms\":" + String(last_capture_ms) + ",";
  json += "\"http_ms\":" + String(last_http_ms) + ",";
  json += "\"rssi\":" + String(WiFi.RSSI()) + ",";
  json += "\"heap\":" + String(ESP.getFreeHeap()) + ",";
  json += "\"wifi_ip\":\"" + WiFi.localIP().toString() + "\",";
  json += "\"server_url\":\"" + String(SERVER_URL) + "\",";
  json += "\"server_response\":\"" + json_escape(last_server_response) + "\"";
  json += "}";
  return json;
}

// ============================================
// Function: Camera web handlers
// ============================================
void handle_camera_home() {
  String html =
    "<!DOCTYPE html><html><head><meta charset='utf-8'>"
    "<meta name='viewport' content='width=device-width, initial-scale=1'>"
    "<meta http-equiv='Cache-Control' content='no-cache, no-store, must-revalidate'>"
    "<meta http-equiv='Pragma' content='no-cache'>"
    "<meta http-equiv='Expires' content='0'>"
    "<title>ESP32-CAM Live Interface</title>"
    "<style>body{font-family:Arial;margin:0;background:#0f172a;color:#e2e8f0;}"
    ".wrap{max-width:1100px;margin:0 auto;padding:20px;}"
    ".card{background:#111827;border:1px solid #334155;border-radius:14px;padding:18px;box-shadow:0 12px 30px rgba(0,0,0,.25);}"
    ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-top:12px;}"
    ".item{background:#0b1220;border:1px solid #243043;border-radius:12px;padding:12px;}"
    ".label{color:#94a3b8;font-size:.9rem;}.value{font-size:1.05rem;font-weight:700;margin-top:4px;}"
    "img{width:100%;max-width:100%;border-radius:12px;border:1px solid #334155;background:#000;}"
    "a{color:#60a5fa;text-decoration:none;} button{padding:10px 14px;border:0;border-radius:8px;background:#2563eb;color:#fff;cursor:pointer;}"
    "pre{white-space:pre-wrap;word-break:break-word;background:#0b1220;padding:12px;border-radius:10px;border:1px solid #243043;}</style>"
    "</head><body><div class='wrap'><div class='card'>"
    "<h1>ESP32-CAM Live Interface</h1>"
    "<p>Live camera stream and real-time status from the running ESP32-CAM firmware.</p>"
    "<div class='grid'>"
    "<div class='item'><div class='label'>Device IP</div><div class='value' id='wifi_ip'>" + WiFi.localIP().toString() + "</div></div>"
    "<div class='item'><div class='label'>WiFi RSSI</div><div class='value' id='rssi'>" + String(WiFi.RSSI()) + " dBm</div></div>"
    "<div class='item'><div class='label'>Frame Count</div><div class='value' id='frame_count'>" + String(frame_count) + "</div></div>"
    "<div class='item'><div class='label'>Safety Status</div><div class='value' id='status'>" + last_status + "</div></div>"
    "<div class='item'><div class='label'>Last HTTP Code</div><div class='value' id='http_code'>" + String(last_http_code) + "</div></div>"
    "<div class='item'><div class='label'>Free Heap</div><div class='value' id='heap'>" + String(ESP.getFreeHeap()) + " bytes</div></div>"
    "</div>"
    "<h3 style='margin-top:18px;'>Live Camera Preview</h3>"
    "<img id='cam' src='' alt='Camera Preview'>"
    "<div style='margin-top:14px;display:flex;gap:10px;flex-wrap:wrap;'>"
    "<button onclick='refreshStatus()'>Refresh Status</button>"
    "<a href='/capture' target='_blank'>Open Snapshot</a>"
    "<a href='/status' target='_blank'>Open Status JSON</a>"
    "<a href='http://" + WiFi.localIP().toString() + ":81/stream' target='_blank'>Open Stream</a>"
    "</div>"
    "<h3 style='margin-top:18px;'>Last Server Response</h3>"
    "<pre id='server_response'>" + last_server_response + "</pre>"
    "</div></div>"
    "<script>const streamUrl='http://" + WiFi.localIP().toString() + ":81/stream'; document.getElementById('cam').src=streamUrl; async function refreshStatus(){try{const r=await fetch('/status?t='+Date.now(),{cache:'no-store'});const d=await r.json();document.getElementById('wifi_ip').textContent=d.wifi_ip;document.getElementById('rssi').textContent=d.rssi+' dBm';document.getElementById('frame_count').textContent=d.frame_count;document.getElementById('status').textContent=d.status;document.getElementById('http_code').textContent=d.http_code;document.getElementById('heap').textContent=d.heap+' bytes';document.getElementById('server_response').textContent=d.server_response||'';}catch(e){console.log(e);}} setInterval(refreshStatus, 1000); refreshStatus();</script>"
    "</body></html>";

  cameraWebServer.send(200, "text/html", html);
}

void handle_status() {
  cameraWebServer.send(200, "application/json", build_status_json());
}

static esp_err_t stream_handler(httpd_req_t *req) {
  static const char* _STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=frame";
  static const char* _STREAM_BOUNDARY = "\r\n--frame\r\n";
  static const char* _STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";
  char part_buf[64];
  camera_fb_t *fb = NULL;
  esp_err_t res = ESP_OK;

  stream_client_connected = true;
  res = httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);
  if (res != ESP_OK) {
    stream_client_connected = false;
    return res;
  }

  while (true) {
    fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("[STREAM] Frame capture failed");
      res = ESP_FAIL;
    } else {
      size_t hlen = snprintf(part_buf, sizeof(part_buf), _STREAM_PART, fb->len);
      res = httpd_resp_send_chunk(req, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));
      if (res == ESP_OK) res = httpd_resp_send_chunk(req, part_buf, hlen);
      if (res == ESP_OK) res = httpd_resp_send_chunk(req, (const char *)fb->buf, fb->len);
      esp_camera_fb_return(fb);
    }

    if (res != ESP_OK) {
      break;
    }
    delay(30);
  }

  stream_client_connected = false;
  return res;
}

void start_stream_server() {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port = 81;
  config.ctrl_port = 32768;
  config.stack_size = 8192;

  httpd_uri_t stream_uri = {
    .uri = "/stream",
    .method = HTTP_GET,
    .handler = stream_handler,
    .user_ctx = NULL
  };

  if (httpd_start(&stream_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(stream_httpd, &stream_uri);
    Serial.print("[WEB] MJPEG stream started at http://");
    Serial.print(WiFi.localIP());
    Serial.println(":81/stream");
  } else {
    Serial.println("[WEB] Failed to start MJPEG stream server");
  }
}

void handle_camera_capture() {
  camera_fb_t* fb = esp_camera_fb_get();
  if (!fb) {
    cameraWebServer.send(500, "text/plain", "Camera capture failed");
    return;
  }

  cameraWebServer.setContentLength(fb->len);
  cameraWebServer.send(200, "image/jpeg", "");
  WiFiClient client = cameraWebServer.client();
  client.write(fb->buf, fb->len);
  esp_camera_fb_return(fb);
}

void start_camera_interface() {
  if (cameraWebStarted) {
    return;
  }

  cameraWebServer.on("/", HTTP_GET, handle_camera_home);
  cameraWebServer.on("/capture", HTTP_GET, handle_camera_capture);
  cameraWebServer.on("/status", HTTP_GET, handle_status);
  cameraWebServer.onNotFound([]() {
    cameraWebServer.send(404, "text/plain", "Use / for UI or /capture for snapshot");
  });
  cameraWebServer.begin();
  cameraWebStarted = true;
  Serial.print("[WEB] Camera interface started at http://");
  Serial.println(WiFi.localIP());
  Serial.print("[WEB] UI URL: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/");
  Serial.print("[WEB] Snapshot URL: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/capture");

  start_stream_server();
}

// ============================================
// Function: Initialize LED
// ============================================
void init_led() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LED_OFF);
  Serial.println("[LED] LED initialized (GPIO 4)");
}

// ============================================
// Function: Set LED state
// ============================================
void set_led(bool state) {
  if (state) {
    digitalWrite(LED_PIN, LED_ON);
    Serial.println("[LED] -> ON (SAFE to overtake)");
  } else {
    digitalWrite(LED_PIN, LED_OFF);
    Serial.println("[LED] -> OFF (NOT SAFE to overtake)");
  }
}

// ============================================
// Function: Initialize Camera
// ============================================
bool init_camera() {
  Serial.println("[CAMERA] Initializing camera...");
  
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_QVGA;    // 320x240
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 10;
  config.fb_count = psramFound() ? 2 : 1;

  // Initialize camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("[CAMERA] ERROR: Camera init failed with error 0x%x\n", err);
    return false;
  }

  // Adjust sensor settings
  sensor_t * s = esp_camera_sensor_get();
  if (s != NULL) {
    s->set_brightness(s, 0);
    s->set_contrast(s, 0);
    s->set_saturation(s, 0);
    s->set_special_effect(s, 0);
    s->set_whitebal(s, 1);
    s->set_awb_gain(s, 1);
    s->set_wb_mode(s, 0);
    s->set_exposure_ctrl(s, 1);
    s->set_aec_value(s, 300);
    s->set_agc_gain(s, 0);
    s->set_gainceiling(s, (gainceiling_t)0);
    s->set_bpc(s, 0);
    s->set_wpc(s, 1);
    s->set_raw_gma(s, 1);
    s->set_lenc(s, 1);
    s->set_hmirror(s, 0);
    s->set_vflip(s, 0);
    s->set_dcw(s, 1);
    s->set_colorbar(s, 0);
  }

  Serial.println("[CAMERA] Camera initialized successfully");
  return true;
}

// ============================================
// Function: Initialize WiFi
// ============================================
void init_wifi() {
  Serial.println("[WiFi] Connecting to WiFi...");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WiFi] ✓ Connected");
    Serial.print("[WiFi] IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[WiFi] ✗ Failed to connect to WiFi");
  }
}

// ============================================
// Function: Capture Frame
// ============================================
camera_fb_t* capture_frame() {
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("[CAMERA] Failed to capture frame");
    return NULL;
  }
  return fb;
}

// ============================================
// Function: Send Frame to Server and Get Response
// ============================================
String send_frame_to_server(camera_fb_t * fb, unsigned long captureTimeMs) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[HTTP] WiFi not connected");
    return "ERROR";
  }

  HTTPClient http;
  http.setTimeout(REQUEST_TIMEOUT);
  
  Serial.print("[HTTP] Sending frame (" + String(fb->len) + " bytes) to ");
  Serial.println(SERVER_URL);

  // Start connection and send HTTP header
  if (!http.begin(SERVER_URL)) {
    Serial.println("[HTTP] Failed to begin HTTP");
    return "ERROR";
  }

  // Send POST request with image data
  unsigned long requestStart = millis();
  int httpResponseCode = http.POST(fb->buf, fb->len);
  unsigned long requestTimeMs = millis() - requestStart;

  String response = "ERROR";
  
  if (httpResponseCode > 0) {
    last_http_code = httpResponseCode;
    Serial.print("[HTTP] Response code: ");
    Serial.println(httpResponseCode);

    if (httpResponseCode == 200) {
      String payload = http.getString();
      Serial.print("[HTTP] Response: ");
      Serial.println(payload);
      
      // Simple JSON parsing for status
      if (payload.indexOf("\"status\":\"SAFE\"") >= 0) {
        response = "SAFE";
      } else if (payload.indexOf("\"status\":\"NOT_SAFE\"") >= 0) {
        response = "NOT_SAFE";
      }

      last_server_response = payload;

      print_runtime_diagnostics(fb->len, captureTimeMs, requestTimeMs, response);
    }
  } else {
    last_http_code = httpResponseCode;
    Serial.print("[HTTP] Error code: ");
    Serial.println(httpResponseCode);
  }

  http.end();
  return response;
}

// ============================================
// Function: Process Safety Response
// ============================================
void process_response(String response) {
  frame_count++;
  
  Serial.println("\n" + String(40, '='));
  Serial.print("[FRAME #");
  Serial.print(frame_count);
  Serial.println("]");
  
  if (response == "SAFE") {
    Serial.println("[STATUS] ✓ SAFE - Overtaking is allowed");
    set_led(true);  // LED ON
  } else if (response == "NOT_SAFE") {
    Serial.println("[STATUS] ✗ NOT SAFE - Do not overtake");
    set_led(false);  // LED OFF
  } else {
    Serial.println("[STATUS] ? ERROR - Could not determine safety");
    set_led(false);  // LED OFF (fail-safe)
  }
  
  Serial.println(String(40, '=') + "\n");
}

// ============================================
// Function: Main Processing Loop
// ============================================
void process_image() {
  // Rate limiting - send frame every REQUEST_INTERVAL ms
  if (millis() - last_request_time < REQUEST_INTERVAL) {
    return;
  }
  last_request_time = millis();

  // Capture frame from camera
  unsigned long captureStart = millis();
  camera_fb_t * fb = capture_frame();
  unsigned long captureTimeMs = millis() - captureStart;
  if (!fb) {
    Serial.println("[ERROR] Failed to capture frame");
    set_led(false);  // Fail-safe: LED OFF
    return;
  }

  // Send frame to server
  String response = send_frame_to_server(fb, captureTimeMs);
  
  // Release frame buffer
  esp_camera_fb_return(fb);

  // Process response and control LED
  process_response(response);
}

// ============================================
// Setup Function
// ============================================
void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n\n");
  Serial.println("╔════════════════════════════════════════╗");
  Serial.println("║   AI Overtaking Safety System         ║");
  Serial.println("║   ESP32-CAM (AI Thinker)             ║");
  Serial.println("║   Version: 1.0                        ║");
  Serial.println("╚════════════════════════════════════════╝\n");

  // Initialize LED
  init_led();
  
  // Initialize Camera
  if (!init_camera()) {
    Serial.println("[SYSTEM] Fatal error: Camera initialization failed");
    while (1) {
      set_led(false);
      delay(500);
    }
  }

  // Initialize WiFi
  init_wifi();

  // Start camera interface in browser
  if (WiFi.status() == WL_CONNECTED) {
    start_camera_interface();
  } else {
    Serial.println("[WEB] Camera interface not started: WiFi not connected.");
    Serial.println("[WEB] Check WIFI_SSID/WIFI_PASSWORD and ensure 2.4GHz network.");
  }

  Serial.println("\n[SYSTEM] Initialization complete. Ready to capture and analyze frames.\n");
}

// ============================================
// Main Loop
// ============================================
void loop() {
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WiFi] Connection lost, attempting to reconnect...");
    init_wifi();
    if (WiFi.status() == WL_CONNECTED) {
      start_camera_interface();
    }
    delay(5000);
    return;
  }

  // Handle browser requests for camera interface
  cameraWebServer.handleClient();

  // Capture and process frame
  if (!stream_client_connected) {
    process_image();
  }

  // Small delay to prevent watchdog timeout
  delay(100);
}
