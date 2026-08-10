from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.api.dependencies import get_current_user, get_db_session
from src.core.domain.entities import UserEntity
from src.infrastructure.database.models import Farm, Recommendation, Device, SensorReading

router = APIRouter()


@router.get("/")
async def get_dashboard(
    db: AsyncSession = Depends(get_db_session),
    current_user: UserEntity = Depends(get_current_user),
):
    """Aggregated dashboard payload backed by SQLite."""
    farms_result = await db.execute(
        select(Farm).where(Farm.user_id == current_user.id, Farm.is_active == True)
    )
    farms = farms_result.scalars().all()

    farm_payload = None
    latest_recommendation = None
    latest_sensor = None

    if farms:
        farm = farms[0]
        farm_payload = {
            "id": str(farm.id),
            "name": farm.name,
            "location_lat": farm.location_lat,
            "location_lon": farm.location_lon,
            "primary_crop": farm.primary_crop,
            "is_active": farm.is_active,
        }

        rec_result = await db.execute(
            select(Recommendation)
            .where(Recommendation.farm_id == farm.id)
            .order_by(Recommendation.created_at.desc())
            .limit(1)
        )
        rec = rec_result.scalars().first()
        if rec:
            latest_recommendation = {
                "type": rec.type,
                "decision": rec.decision,
                "confidence": rec.confidence,
                "priority": rec.priority,
                "reason": rec.reason,
                "created_at": rec.created_at.isoformat() if rec.created_at else None,
            }

        device_result = await db.execute(
            select(Device).where(Device.farm_id == farm.id, Device.is_active == True).limit(1)
        )
        device = device_result.scalars().first()
        if device:
            sensor_result = await db.execute(
                select(SensorReading)
                .where(SensorReading.device_id == device.id)
                .order_by(SensorReading.recorded_at.desc())
                .limit(1)
            )
            reading = sensor_result.scalars().first()
            if reading:
                latest_sensor = {
                    "temperature": reading.temperature,
                    "humidity": reading.humidity,
                    "soil_moisture": reading.soil_moisture,
                    "recorded_at": reading.recorded_at.isoformat() if reading.recorded_at else None,
                }

    device_payload = None
    if farms:
        device_result = await db.execute(
            select(Device).where(Device.farm_id == farms[0].id, Device.is_active == True).limit(1)
        )
        device = device_result.scalars().first()
        if device:
            device_payload = {
                "id": str(device.id), "mac_address": device.mac_address, "status": device.status,
                "last_seen_at": device.last_seen_at.isoformat() if device.last_seen_at else None,
            }

    return {
        "status": "success",
        "source": "database",
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "role": current_user.role,
        },
        "farm": farm_payload,
        "latest_recommendation": latest_recommendation,
        "latest_sensor": latest_sensor,
        "device": device_payload,
        "farms_count": len(farms),
    }
