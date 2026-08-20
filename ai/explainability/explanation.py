"""
Explainable AI utility for AgriGuardian AI irrigation recommendations.
Provides deterministic, human-readable explanations based on model feature inputs.
"""

from typing import Dict, Any


def generate_irrigation_explanation(
    prediction: int,
    temperature: float,
    humidity: float,
    soil_moisture: float,
    rainfall_prev_day: float,
) -> str:
    """
    Generate clear human-readable explanation from model inputs and prediction.
    soil_moisture is expected as fraction (0-1) or percentage (0-100).
    """
    moisture_pct = soil_moisture * 100.0 if soil_moisture <= 1.0 else soil_moisture

    if humidity < 40:
        humidity_desc = "low"
    elif humidity > 75:
        humidity_desc = "high"
    else:
        humidity_desc = "moderate"

    if rainfall_prev_day < 2.0:
        rain_desc = "no recent rainfall"
    else:
        rain_desc = f"{rainfall_prev_day:.1f} mm rainfall yesterday"

    if prediction == 1:
        return (
            f"Soil moisture is low at {moisture_pct:.1f}% (optimal: 45–70%). "
            f"Temperature is {temperature:.1f}°C with {humidity_desc} humidity ({humidity:.0f}%) and {rain_desc}. "
            "XGBoost model recommends irrigation to prevent crop stress."
        )
    else:
        return (
            f"Soil moisture is adequate at {moisture_pct:.1f}%. "
            f"Temperature is {temperature:.1f}°C with {humidity_desc} humidity ({humidity:.0f}%) and {rain_desc}. "
            "XGBoost model indicates sufficient moisture — irrigation not required."
        )
