"""
Irrigation AI inference service.

Loads the persisted XGBoost classifier from ai/models/irrigation/model.joblib.
Feature order (from training code in model.py / synthetic data generator):
  1. temperature        — Celsius
  2. humidity           — percent (0-100)
  3. soil_moisture      — fraction (0-1); values > 1 are treated as percent
  4. rainfall_prev_day  — millimetres
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np

# Confirmed by inspecting model.joblib: XGBClassifier, n_features_in_=4, classes_=[0,1]
# No feature_names_in_ on the saved artifact; order comes from project training code.
FEATURE_ORDER = ("temperature", "humidity", "soil_moisture", "rainfall_prev_day")

_MODEL = None
_MODEL_PATH: Path | None = None


def _resolve_model_path() -> Path:
    """Locate model.joblib relative to repo root or backend cwd."""
    candidates = [
        Path("ai/models/irrigation/model.joblib"),
        Path("../ai/models/irrigation/model.joblib"),
        Path(__file__).resolve().parents[4] / "ai" / "models" / "irrigation" / "model.joblib",
    ]
    for path in candidates:
        if path.exists():
            return path.resolve()
    raise FileNotFoundError(
        "Irrigation model not found. Expected ai/models/irrigation/model.joblib"
    )


def get_irrigation_model():
    """Load and cache the irrigation model singleton."""
    global _MODEL, _MODEL_PATH
    if _MODEL is not None:
        return _MODEL
    _MODEL_PATH = _resolve_model_path()
    _MODEL = joblib.load(_MODEL_PATH)
    return _MODEL


def _normalize_soil_moisture(value: float) -> float:
    """Accept 0-1 fraction or 0-100 percent."""
    if value > 1.0:
        return value / 100.0
    return value


def _build_feature_vector(inputs: dict[str, float]) -> np.ndarray:
    return np.array([[
        float(inputs["temperature"]),
        float(inputs["humidity"]),
        float(inputs["soil_moisture"]),
        float(inputs["rainfall_prev_day"]),
    ]])


def predict_irrigation(
    *,
    temperature: float,
    humidity: float,
    soil_moisture: float,
    rainfall_prev_day: float = 0.0,
) -> dict[str, Any]:
    """
    Run irrigation inference.

    Returns prediction (0=skip, 1=irrigate), optional confidence from predict_proba,
    human-readable recommendation, and echo of normalized inputs.
    """
    moisture_norm = _normalize_soil_moisture(soil_moisture)
    normalized = {
        "temperature": float(temperature),
        "humidity": float(humidity),
        "soil_moisture": moisture_norm,
        "rainfall_prev_day": float(rainfall_prev_day),
    }

    model = get_irrigation_model()
    X = _build_feature_vector(normalized)

    prediction = int(model.predict(X)[0])

    confidence: float | None = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0]
        # Probability of the predicted class
        confidence = float(proba[prediction])

    moisture_display = soil_moisture if soil_moisture > 1.0 else moisture_norm * 100.0
    rain_label = "no recent rainfall" if rainfall_prev_day < 2 else f"{rainfall_prev_day:.1f} mm rainfall yesterday"
    humidity_label = "low" if humidity < 40 else ("high" if humidity > 75 else "moderate")

    if prediction == 1:
        recommendation = "IRRIGATE NOW"
        reason = (
            f"Soil moisture is low at {moisture_display:.1f}% (optimal: 45–70%). "
            f"Temperature is {temperature:.1f}°C with {humidity_label} humidity ({humidity:.0f}%) and {rain_label}. "
            "XGBoost model recommends irrigation to prevent crop stress."
        )
    else:
        recommendation = "SKIP IRRIGATION"
        reason = (
            f"Soil moisture is adequate at {moisture_display:.1f}%. "
            f"Temperature is {temperature:.1f}°C with {humidity_label} humidity ({humidity:.0f}%) and {rain_label}. "
            "XGBoost model indicates sufficient moisture — irrigation not required."
        )

    return {
        "prediction": prediction,
        "recommendation": recommendation,
        "confidence": confidence,
        "confidence_available": confidence is not None,
        "inputs": {
            "temperature": temperature,
            "humidity": humidity,
            "soil_moisture": soil_moisture,
            "rainfall_prev_day": rainfall_prev_day,
        },
        "normalized_inputs": normalized,
        "feature_order": list(FEATURE_ORDER),
        "reason": reason,
        "model_type": type(model).__name__,
    }
