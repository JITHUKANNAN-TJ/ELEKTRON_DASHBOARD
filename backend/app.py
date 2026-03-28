from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import time
import random
import json
import os

try:
    import cv2
    import numpy as np
    HAS_CV = True
except ImportError:
    HAS_CV = False

try:
    from ultralytics import YOLO
    HAS_YOLO = True
except ImportError:
    HAS_YOLO = False

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from pydantic import BaseModel

# Base Model for logging
class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str
    data: dict | None = None

class CameraConfig(BaseModel):
    url: str

class CameraStatus(BaseModel):
    active: bool

CAMERA_URL = 0
CAMERA_ACTIVE = True  # Always active; camera wakes on request

@app.post("/api/camera_url")
def update_camera_url(config: CameraConfig):
    global CAMERA_URL
    try:
        if config.url.isdigit():
            CAMERA_URL = int(config.url)
        else:
            CAMERA_URL = config.url
        return {"status": "success", "url": CAMERA_URL}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/camera_status")
def update_camera_status(status: CameraStatus):
    global CAMERA_ACTIVE
    print(f"DEBUG: Setting CAMERA_ACTIVE to {status.active}")
    CAMERA_ACTIVE = status.active
    return {"status": "success", "active": CAMERA_ACTIVE}

if HAS_YOLO:
    print("Loading YOLOv26 AI Model... this may take a moment to download weights on first run.")
    try:
        # User specified YOLOv26
        model = YOLO('yolo26n.pt')
        print("YOLOv26 Core loaded successfully.")
    except Exception as e:
        print(f"Could not load yolov26.pt: {e}")
        HAS_YOLO = False

def generate_video_stream():
    global CAMERA_URL
    global CAMERA_ACTIVE
    if not HAS_CV:
        yield b''
        return

    # Connect to the primary system camera
    current_url = CAMERA_URL
    cap = None
    
    try:
        while True:
            if not CAMERA_ACTIVE:
                if cap is not None:
                    print("DEBUG: CAMERA_ACTIVE is False, releasing cap!")
                    cap.release()
                    cap = None
                time.sleep(0.5)
                # Keep stream alive or wait for disconnect
                yield b'--frame\r\n\r\n'
                continue

            if cap is None:
                current_url = CAMERA_URL
                cap = cv2.VideoCapture(current_url)

            # Check if URL was updated
            if CAMERA_URL != current_url:
                if cap is not None:
                    cap.release()
                current_url = CAMERA_URL
                cap = cv2.VideoCapture(current_url)

            if not cap.isOpened() or not HAS_YOLO:
                # Fallback simulated feed if no camera or no YOLO package
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                frame[:] = (random.randint(10,30), random.randint(30,50), random.randint(50,80))
                
                # Artificial bounding box simulations
                if random.random() > 0.5:
                    cv2.rectangle(frame, (200, 150), (350, 300), (0, 0, 255), 2)
                    cv2.putText(frame, "Plastic Waste 92%", (200, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                cv2.putText(frame, "AI DRONE FEED (YOLOv26 ACTIVE)", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                if not HAS_YOLO:
                    cv2.putText(frame, "SIMULATED: YOLOv26 NOT INSTALLED", (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                elif not cap.isOpened():
                    cv2.putText(frame, f"DISCONNECTED: {current_url}", (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                time.sleep(0.5)
                continue
                
            success, frame = cap.read()
            if not success:
                # Video ended or stream dropped. Try to reconnect
                cap.release()
                time.sleep(1)
                cap = cv2.VideoCapture(current_url)
                continue
                
            # Execute YOLO detection inference on the frame
            results = model(frame, stream=False)
            
            # Map common MS COCO objects to simulated river waste categories
            WASTE_MAPPING = {
                'bottle': 'Plastic Debris',
                'wine glass': 'Glass Debris',
                'cup': 'Plastic Cup',
                'fork': 'Metal Waste',
                'knife': 'Metal Waste',
                'spoon': 'Metal Waste',
                'bowl': 'Plastic Container',
                'backpack': 'Submerged Bag',
                'umbrella': 'Debris',
                'handbag': 'Submerged Bag',
                'suitcase': 'Large Debris',
                'sports ball': 'Floating Plastic',
                'cell phone': 'E-Waste',
                'laptop': 'E-Waste',
                'mouse': 'E-Waste',
                'keyboard': 'E-Waste',
                'remote': 'E-Waste',
                'book': 'Paper Waste',
                'clock': 'E-Waste',
                'vase': 'Ceramic Debris',
                'scissors': 'Metal Debris',
                'teddy bear': 'Textile Waste',
                'toothbrush': 'Plastic Waste'
            }
            
            annotated_frame = frame.copy()
            waste_detected = False
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    class_name = model.names[cls_id]
                    
                    # Only highlight classes mapped to Waste
                    if class_name in WASTE_MAPPING:
                        waste_label = WASTE_MAPPING[class_name]
                        conf = float(box.conf[0])
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        # Draw Alert Bounding Box (Red color in BGR is 0,0,255)
                        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                        
                        # Label Background and Text
                        label = f"WASTE: {waste_label} ({int(conf*100)}%)"
                        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                        cv2.rectangle(annotated_frame, (x1, max(0, y1 - 25)), (x1 + w, y1), (0, 0, 255), -1)
                        cv2.putText(annotated_frame, label, (x1, max(20, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                        waste_detected = True
            
            # Add custom telemetry HUD
            cv2.putText(annotated_frame, "HYDRAMETRIC YOLOv26 ENGINE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            if not ret:
                continue
                
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        if cap is not None:
            cap.release()

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_video_stream(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/api/sensors")
def get_sensor_data():
    return {
        "tds_mgl": random.uniform(1500, 1600),
        "bod_mgl": random.uniform(13.0, 16.0),
        "cod_mgl": random.uniform(80.0, 90.0),
        "ph_level": random.uniform(7.8, 8.3)
    }

import urllib.request
import urllib.parse
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"DEBUG: Client connected ({len(self.active_connections)} active).")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"DEBUG: Client disconnected ({len(self.active_connections)} remaining).")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for any client messages
            data = await websocket.receive_text()
            # Echo back or handle commands if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Background task to broadcast sensor data to all connected clients
async def broadcast_sensor_updates():
    while True:
        data = {
            "type": "metricUpdate",
            "payload": {
                "tds_mgl": random.uniform(1500, 1600),
                "bod_mgl": random.uniform(13.0, 16.0),
                "cod_mgl": random.uniform(80.0, 90.0),
                "ph_level": random.uniform(7.8, 8.3)
            }
        }
        await manager.broadcast(json.dumps(data))
        await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(broadcast_sensor_updates())

@app.get("/api/aqi")
def get_aqi_data(city: str = "Delhi", limit: int = 50):
    try:
        import os
        api_key = os.getenv("AQI_API_KEY", "579b464db66ec23bdd0000018b72af4808f444b04705cb177217411e")
        city_enc = urllib.parse.quote(city)
        url = f"https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69?api-key={api_key}&format=json&filters[city]={city_enc}&limit={limit}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read())
    except Exception as e:
        return {"records": [], "error": str(e)}

@app.post("/api/logs")
async def report_log(log: LogEntry):
    print(f"CLIENT LOG [{log.level}]: {log.message} - Data: {log.data}")
    return {"status": "logged"}

# Mount the root directory to serve static files (index.html, js/, etc.)
# Use absolute path so this works regardless of where gunicorn is launched from
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/", StaticFiles(directory=ROOT_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
