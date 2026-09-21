from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel, Field
from typing import List, Union
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("telemetry")

# Database setup (SQLite file inside container/volume)
DATABASE_URL = "sqlite:///./telemetry.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TelemetryModel(Base):
    __tablename__ = "telemetry_logs"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(String, index=True)
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)
    timestamp = Column(Float)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Remaining clients: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

# Pydantic request model
class TelemetryData(BaseModel):
    cart_id: str = Field(..., example="minecart_1")
    x: float
    y: float
    z: float
    timestamp: Union[int, float]

app = FastAPI(title="Pixel Park Telemetry Service")

# REST endpoint (save to DB & broadcast)
@app.post("/api/telemetry")
async def receive_telemetry(data: TelemetryData, db: Session = Depends(get_db)):
    # Save record to relational database
    db_record = TelemetryModel(
        cart_id=data.cart_id,
        x=data.x,
        y=data.y,
        z=data.z,
        timestamp=float(data.timestamp)
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    payload = data.model_dump()

    # Broadcast immediately to WebSocket subscribers
    await manager.broadcast(payload)

    return {"status": "success", "id": db_record.id, "data": payload}

# WebSocket endpoint
@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)