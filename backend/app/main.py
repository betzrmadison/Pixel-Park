from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List
import json

app = FastAPI(title="Pixel Park Telemetry Engine")

# Define what a standard ride telemetry packet looks like
class TelemetryData(BaseModel):
    cart_id: str
    x: float
    y: float
    z: float
    timestamp: float

# Manage active browser/dashboard connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.sent_text(message)

manager = ConnectionManager()

@app.get("/")
def read_root():
    return {"status": "Pixel Park Backend Online"}

# Endpoint: receives data from Minecraft
@app.post("/api/telemetry")
async def receive_telemetry(data: TelemetryData):
    # Turn incoming data into JSON string
    payload = json.dumps(data.model_dump())

    # Broadcast instantly to any open web dashboards
    await manager.broadcast(payload)

    # Return success to Minecraft plugin
    return {"status": "Telemetry Received", "broadcasted": True}

# Endpoint: broadcasts live data to the frontend dashboard
@app.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive listening for client messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
