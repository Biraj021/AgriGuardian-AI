from datetime import datetime, timezone
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db_session
from src.core.domain.entities import UserEntity
from src.infrastructure.database.models import Device, Farm, SensorReading

router = APIRouter()


class TelemetryPayload(BaseModel):
    """Transport-neutral telemetry contract for HTTP and future MQTT consumers."""
    device_id: str = Field(..., min_length=1)
    timestamp: datetime | None = None
    temperature: float | None = Field(default=None, ge=-50, le=100)
    humidity: float | None = Field(default=None, ge=0, le=100)
    soil_moisture: float | None = Field(default=None, ge=0, le=100)
    rainfall: float | None = Field(default=None, ge=0)
    water_level: float | None = Field(default=None, ge=0, le=100)


async def _owned_device(db: AsyncSession, user: UserEntity, device_id: str) -> Device:
    statement = (
        select(Device)
        .join(Farm, Device.farm_id == Farm.id)
        .where(Farm.user_id == user.id, Farm.is_active == True)
    )
    try:
        statement = statement.where(Device.id == uuid.UUID(device_id))
    except ValueError:
        statement = statement.where(Device.mac_address == device_id)
    result = await db.execute(statement)
    device = result.scalars().first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found for current user")
    return device


@router.get("/recent")
async def recent_readings(
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
    current_user: UserEntity = Depends(get_current_user),
):
    """Return recent readings only from devices belonging to the current user."""
    statement = (
        select(SensorReading, Device)
        .join(Device, SensorReading.device_id == Device.id)
        .join(Farm, Device.farm_id == Farm.id)
        .where(Farm.user_id == current_user.id, Farm.is_active == True, Device.is_active == True)
        .order_by(SensorReading.recorded_at.desc())
        .limit(limit)
    )
    result = await db.execute(statement)
    rows = result.all()
    return {
        "source": "database",
        "readings": [
            {
                "id": str(reading.id), "device_id": str(device.id), "device_mac": device.mac_address,
                "temperature": reading.temperature, "humidity": reading.humidity,
                "soil_moisture": reading.soil_moisture, "rainfall": reading.rainfall,
                "water_level": reading.water_level,
                "recorded_at": reading.recorded_at.isoformat(),
            }
            for reading, device in rows
        ],
        "count": len(rows),
    }


@router.post("/ingest", status_code=status.HTTP_201_CREATED)
async def ingest_reading(
    payload: TelemetryPayload,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserEntity = Depends(get_current_user),
):
    """Persist validated telemetry for a device owned by the authenticated user.

    MQTT consumers can use this payload contract and call the same persistence
    logic once broker credentials and device authentication are configured.
    """
    device = await _owned_device(db, current_user, payload.device_id)
    if payload.temperature is None and payload.humidity is None and payload.soil_moisture is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="At least one stored sensor value is required")
    reading = SensorReading(
        device_id=device.id,
        temperature=payload.temperature,
        humidity=payload.humidity,
        soil_moisture=payload.soil_moisture,
        rainfall=payload.rainfall,
        water_level=payload.water_level,
        recorded_at=payload.timestamp or datetime.now(timezone.utc),
    )
    device.status = "active"
    device.last_seen_at = datetime.now(timezone.utc)
    db.add(reading)
    await db.commit()
    await db.refresh(reading)
    return {
        "status": "stored", "reading_id": str(reading.id), "device_id": str(device.id),
        "recorded_at": reading.recorded_at.isoformat(),
    }
