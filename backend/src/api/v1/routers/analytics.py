from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db_session
from src.core.domain.entities import UserEntity
from src.infrastructure.database.models import Device, Farm, Recommendation, SensorReading

router = APIRouter()


@router.get("/overview")
async def analytics_overview(
    db: AsyncSession = Depends(get_db_session),
    current_user: UserEntity = Depends(get_current_user),
):
    """Return calculated, farm-owned sensor and recommendation summary data."""
    readings_result = await db.execute(
        select(SensorReading)
        .join(Device, SensorReading.device_id == Device.id)
        .join(Farm, Device.farm_id == Farm.id)
        .where(Farm.user_id == current_user.id, Farm.is_active == True)
        .order_by(SensorReading.recorded_at.asc())
    )
    readings = readings_result.scalars().all()
    recommendation_result = await db.execute(
        select(Recommendation)
        .join(Farm, Recommendation.farm_id == Farm.id)
        .where(Farm.user_id == current_user.id, Farm.is_active == True)
        .order_by(Recommendation.created_at.desc())
    )
    recommendations = recommendation_result.scalars().all()

    return {
        "source": "database",
        "data_limited": len(readings) < 2,
        "sensor_readings_count": len(readings),
        "recommendations_count": len(recommendations),
        "latest_sensor_at": readings[-1].recorded_at.isoformat() if readings else None,
        "series": {
            "labels": [item.recorded_at.isoformat() for item in readings],
            "temperature": [item.temperature for item in readings],
            "soil_moisture": [item.soil_moisture for item in readings],
            "humidity": [item.humidity for item in readings],
        },
    }
