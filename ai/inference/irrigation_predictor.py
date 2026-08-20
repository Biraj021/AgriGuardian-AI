"""
Inference wrapper for AgriGuardian AI Irrigation Predictor.
Loads trained XGBoost model and provides safe, validated predictions with explanations.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from typing import Any

import joblib
import numpy as np

from ai.explainability.explanation import generate_irrigation_explanation


FEATURE_ORDER = ["temperature", "humidity", "soil_moisture", "rainfall_prev_day"]
MODEL_VERSION = "irrigation-xgboost-v1"


class IrrigationPredictor:
    """Production inference interface for Irrigation XGBoost model."""

    def __init__(self, model_dir: Path | str | None = None):
        if model_dir is None:
            model_dir = Path(__file__).resolve().parents[1] / "models" / "irrigation"
        else:
            model_dir = Path(model_dir)

        self.model_dir = model_dir
        self.model_path = model_dir / "model.joblib"
        self.metadata_path = model_dir / "metadata.json"

        self._model = None
        self._metadata = None
        self.load_model()

    def load_model(self):
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Irrigation model not found. Expected {self.model_path}"
            )
        self._model = joblib.load(self.model_path)

        if self.metadata_path.exists():
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self._metadata = json.load(f)

    @property
    def model_type(self) -> str:
        return type(self._model).__name__ if self._model else "Unknown"

    @property
    def version(self) -> str:
        if self._metadata and "version" in self._metadata:
            return self._metadata["version"]
        return MODEL_VERSION

    def normalize_soil_moisture(self, value: float) -> float:
        """Ensure soil moisture is normalized to a 0.0 - 1.0 fraction."""
        if value > 1.0:
            return value / 100.0
        return value

    def validate_inputs(
        self,
        temperature: float,
        humidity: float,
        soil_moisture: float,
        rainfall_prev_day: float,
    ) -> tuple[float, float, float, float]:
        """Validate input ranges and types. Raises ValueError for invalid inputs."""
        for name, val in [
            ("temperature", temperature),
            ("humidity", humidity),
            ("soil_moisture", soil_moisture),
            ("rainfall_prev_day", rainfall_prev_day),
        ]:
            if val is None or not isinstance(val, (int, float)):
                raise ValueError(f"Input '{name}' must be a valid numeric value.")
            if np.isnan(val) or np.isinf(val):
                raise ValueError(f"Input '{name}' cannot be NaN or Infinite.")

        if not (-50.0 <= temperature <= 100.0):
            raise ValueError(f"Temperature out of realistic bounds (-50 to 100 C): {temperature}")
        if not (0.0 <= humidity <= 100.0):
            raise ValueError(f"Humidity out of realistic bounds (0 to 100 %): {humidity}")
        if soil_moisture < 0.0 or soil_moisture > 100.0:
            raise ValueError(f"Soil moisture out of realistic bounds (0 to 100): {soil_moisture}")
        if rainfall_prev_day < 0.0:
            raise ValueError(f"Rainfall cannot be negative: {rainfall_prev_day}")

        norm_moisture = self.normalize_soil_moisture(soil_moisture)
        return float(temperature), float(humidity), norm_moisture, float(rainfall_prev_day)

    def predict(
        self,
        temperature: float,
        humidity: float,
        soil_moisture: float,
        rainfall_prev_day: float = 0.0,
    ) -> dict[str, Any]:
        """
        Execute prediction pipeline.
        Returns result schema compatible with AgriGuardian backend API.
        """
        temp_val, hum_val, moist_norm, rain_val = self.validate_inputs(
            temperature, humidity, soil_moisture, rainfall_prev_day
        )

        if self._model is None:
            self.load_model()

        X = np.array([[temp_val, hum_val, moist_norm, rain_val]])

        prediction = int(self._model.predict(X)[0])

        confidence: float | None = None
        if hasattr(self._model, "predict_proba"):
            proba = self._model.predict_proba(X)[0]
            confidence = float(proba[prediction])

        action = "IRRIGATE NOW" if prediction == 1 else "SKIP IRRIGATION"
        reason = generate_irrigation_explanation(
            prediction=prediction,
            temperature=temp_val,
            humidity=hum_val,
            soil_moisture=moist_norm,
            rainfall_prev_day=rain_val,
        )

        return {
            "prediction": prediction,
            "action": action,
            "recommendation": action,
            "confidence": confidence,
            "confidence_available": confidence is not None,
            "inputs": {
                "temperature": temperature,
                "humidity": humidity,
                "soil_moisture": soil_moisture,
                "rainfall_prev_day": rainfall_prev_day,
            },
            "normalized_inputs": {
                "temperature": temp_val,
                "humidity": hum_val,
                "soil_moisture": moist_norm,
                "rainfall_prev_day": rain_val,
            },
            "feature_order": FEATURE_ORDER,
            "reason": reason,
            "model_version": self.version,
            "model_type": self.model_type,
        }
