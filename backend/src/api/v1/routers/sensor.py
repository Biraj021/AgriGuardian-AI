from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/recent")
def recent_readings():
    # demo deterministic readings
    return {
        "source": "demo",
        "readings": [
            {"timestamp": datetime.utcnow().isoformat(), "temperature": 26.5, "humidity": 60, "soil_moisture": 0.4}
        ],
    }
