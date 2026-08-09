"""
IoT device ingestion placeholder for tomorrow's ESP32 integration.

Expected flow:
  ESP32 sensors → POST /api/v1/sensor/readings → SQLite sensor_readings table
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class SensorReadingPayload(BaseModel):
    """Payload shape for future IoT device submissions."""
    device_mac: str = Field(..., description="Device MAC address")
    temperature: Optional[float] = Field(None, ge=-50, le=100)
    humidity: Optional[float] = Field(None, ge=0, le=100)
    soil_moisture: Optional[float] = Field(None, ge=0, le=100)
    rainfall_mm: Optional[float] = Field(None, ge=0)
    recorded_at: Optional[datetime] = None


class IoTIngestionService:
    """Placeholder service — implement device lookup and DB persistence tomorrow."""

    async def ingest_reading(self, payload: SensorReadingPayload) -> dict:
        recorded_at = payload.recorded_at or datetime.now(timezone.utc)
        return {
            "status": "placeholder",
            "message": "IoT ingestion not yet implemented — wire ESP32 firmware tomorrow",
            "received": {
                "device_mac": payload.device_mac,
                "temperature": payload.temperature,
                "humidity": payload.humidity,
                "soil_moisture": payload.soil_moisture,
                "rainfall_mm": payload.rainfall_mm,
                "recorded_at": recorded_at.isoformat(),
            },
        }
