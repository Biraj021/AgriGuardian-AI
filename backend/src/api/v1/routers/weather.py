from fastapi import APIRouter

router = APIRouter()


@router.get("/current")
def current_weather():
    """Return explicit demo data until a live weather client is implemented."""
    return {
        "source": "demo",
        "is_live": False,
        "message": "Demo weather data: a live weather provider is not implemented in this MVP.",
        "temperature": 26.5,
        "humidity": 62,
        "rainfall": 0,
        "condition": "Partly Cloudy",
    }
