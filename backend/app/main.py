from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from typing import Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("telemetry")

app = FastAPI(title="Pixel Park Telemetry Service")

class TelemetryData(BaseModel):
    cart_id: str = Field(..., example="minecart_1")
    x: float
    y: float
    z: float
    timestamp: Union[int, float]  # Accepts integer seconds or float Unix timestamps

@app.post("/api/telemetry")
async def receive_telemetry(data: TelemetryData):
    logger.info(f"Received telemetry: {data.dict()}")
    return {"status": "success", "received": data}

# Debug middleware to log raw body if parsing fails
@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    body = await request.body()
    logger.error(f"Error handling request! Raw body: {body.decode('utf-8', errors='ignore')}")
    return {"detail": str(exc), "raw_body": body.decode('utf-8', errors='ignore')}