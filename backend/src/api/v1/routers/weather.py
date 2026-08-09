from fastapi import APIRouter
from src.core.config import settings

router = APIRouter()


@router.get("/current")
def current_weather():
    """Weather data with explicit demo fallback when no API key is configured."""
    if settings.OPENWEATHER_API_KEY:
        # TODO: integrate OpenWeatherMap when key is available
        pass

    return {
        "source": "demo",
        "is_live": False,
        "message": "Demo weather data — configure OPENWEATHER_API_KEY for live forecasts",
        "temperature": 26.5,
        "humidity": 62,
        "rainfall": 0,
        "condition": "Partly Cloudy",
    }
