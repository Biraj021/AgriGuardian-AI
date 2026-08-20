from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db_session
from src.core.domain.entities import UserEntity
from src.infrastructure.ai_engine.irrigation_service import get_model_status_info, predict_irrigation
from src.infrastructure.database.models import Device, Farm, Recommendation, SensorReading

router = APIRouter()


@router.get("/model/status")
async def get_model_status():
    """Return status and metadata of the deployed irrigation AI model."""
    return get_model_status_info()



class IrrigationInput(BaseModel):
    temperature: float = Field(..., ge=-50, le=100)
    humidity: float = Field(..., ge=0, le=100)
    soil_moisture: float = Field(..., ge=0, le=100)
    rainfall_prev_day: float = Field(default=0.0, ge=0)
    rainfall: float | None = Field(default=None, ge=0)

    @field_validator("temperature", "humidity", "soil_moisture", "rainfall_prev_day")
    @classmethod
    def must_be_finite(cls, value: float) -> float:
        if value != value:
            raise ValueError("Value must be a valid number")
        return value


async def _get_owned_farm(db: AsyncSession, user: UserEntity) -> Farm:
    result = await db.execute(
        select(Farm).where(Farm.user_id == user.id, Farm.is_active == True).limit(1)
    )
    farm = result.scalars().first()
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active farm found")
    return farm


@router.post("/irrigation")
@router.post("/generate")
async def get_irrigation_recommendation(
    payload: IrrigationInput,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserEntity = Depends(get_current_user),
):
    """Run the irrigation model and store the resulting farm recommendation."""
    rainfall = payload.rainfall if payload.rainfall is not None else payload.rainfall_prev_day
    farm = await _get_owned_farm(db, current_user)
    try:
        result = predict_irrigation(
            temperature=payload.temperature,
            humidity=payload.humidity,
            soil_moisture=payload.soil_moisture,
            rainfall_prev_day=rainfall,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"AI model inference error: {exc}")

    record = Recommendation(
        farm_id=farm.id,
        type="irrigation",
        decision=result["recommendation"],
        confidence=float(result["confidence"] or 0.0),
        priority="high" if result["prediction"] == 1 else "normal",
        reason=result["reason"],
        data_sources={"inputs": result["inputs"], "normalized_inputs": result["normalized_inputs"]},
        top_features={"feature_order": result["feature_order"], "model_type": result["model_type"]},
        is_implemented=False,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return {"status": "success", **result, "recommendation_id": str(record.id), "created_at": record.created_at.isoformat()}


@router.post("/irrigation/latest")
async def get_latest_sensor_irrigation_recommendation(
    db: AsyncSession = Depends(get_db_session),
    current_user: UserEntity = Depends(get_current_user),
):
    """Generate and persist an irrigation recommendation from the latest owned sensor reading."""
    farm = await _get_owned_farm(db, current_user)
    result = await db.execute(
        select(SensorReading)
        .join(Device, SensorReading.device_id == Device.id)
        .where(Device.farm_id == farm.id, Device.is_active == True)
        .order_by(SensorReading.recorded_at.desc())
        .limit(1)
    )
    reading = result.scalars().first()
    if reading is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No sensor reading found for active farm")
    if None in (reading.temperature, reading.humidity, reading.soil_moisture):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Latest sensor reading lacks temperature, humidity, or soil moisture",
        )
    return await get_irrigation_recommendation(
        IrrigationInput(
            temperature=reading.temperature,
            humidity=reading.humidity,
            soil_moisture=reading.soil_moisture,
            rainfall_prev_day=reading.rainfall or 0.0,
        ),
        db,
        current_user,
    )


@router.get("/history")
async def recommendation_history(
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
    current_user: UserEntity = Depends(get_current_user),
):
    """Return persisted irrigation recommendations for the current user's farm."""
    farm = await _get_owned_farm(db, current_user)
    result = await db.execute(
        select(Recommendation)
        .where(Recommendation.farm_id == farm.id, Recommendation.type == "irrigation")
        .order_by(Recommendation.created_at.desc())
        .limit(limit)
    )
    records = result.scalars().all()
    return {
        "source": "database",
        "recommendations": [
            {
                "id": str(item.id), "decision": item.decision, "confidence": item.confidence,
                "reason": item.reason, "priority": item.priority,
                "inputs": (item.data_sources or {}).get("inputs"),
                "created_at": item.created_at.isoformat() if item.created_at else None,
            }
            for item in records
        ],
    }
