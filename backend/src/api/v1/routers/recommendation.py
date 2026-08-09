from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from src.infrastructure.ai_engine.irrigation_service import predict_irrigation

router = APIRouter()


class IrrigationInput(BaseModel):
    temperature: float = Field(..., ge=-50, le=100, description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity percentage")
    soil_moisture: float = Field(..., ge=0, le=100, description="Soil moisture percentage (0-100)")
    rainfall_prev_day: float = Field(default=0.0, ge=0, description="Rainfall in mm from previous day")

    # Alias for simpler client payloads
    rainfall: float | None = Field(default=None, ge=0, description="Alias for rainfall_prev_day")

    @field_validator("temperature", "humidity", "soil_moisture", "rainfall_prev_day")
    @classmethod
    def must_be_finite(cls, v: float) -> float:
        if v != v:  # NaN check
            raise ValueError("Value must be a valid number")
        return v


@router.post("/irrigation")
@router.post("/generate")
def get_irrigation_recommendation(payload: IrrigationInput):
    """Run XGBoost irrigation model (model.joblib) for irrigate/skip decision."""
    rainfall = payload.rainfall if payload.rainfall is not None else payload.rainfall_prev_day

    try:
        result = predict_irrigation(
            temperature=payload.temperature,
            humidity=payload.humidity,
            soil_moisture=payload.soil_moisture,
            rainfall_prev_day=rainfall,
        )
        return {"status": "success", **result}
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI model inference error: {str(e)}",
        )
