"""
Automated validation tests for AgriGuardian AI Irrigation Model.
"""

from pathlib import Path
import numpy as np
import pytest

from ai.inference.irrigation_predictor import IrrigationPredictor


@pytest.fixture
def predictor():
    repo_root = Path(__file__).resolve().parents[2]
    model_dir = repo_root / "ai" / "models" / "irrigation"
    return IrrigationPredictor(model_dir=model_dir)


def test_model_loads_successfully(predictor):
    assert predictor._model is not None, "Model failed to load"
    assert predictor.model_type == "XGBClassifier"
    assert predictor.version == "irrigation-xgboost-v1"


def test_case_a_dry_soil(predictor):
    """CASE A: dry soil => IRRIGATE"""
    result = predictor.predict(
        temperature=35.0,
        humidity=40.0,
        soil_moisture=15.0,
        rainfall_prev_day=0.0,
    )
    assert result["prediction"] == 1
    assert result["action"] == "IRRIGATE NOW"
    assert result["recommendation"] == "IRRIGATE NOW"
    assert result["confidence"] is not None
    assert 0.5 <= result["confidence"] <= 1.0
    assert "Soil moisture is low" in result["reason"]


def test_case_b_wet_soil(predictor):
    """CASE B: wet soil => SKIP"""
    result = predictor.predict(
        temperature=22.0,
        humidity=80.0,
        soil_moisture=75.0,
        rainfall_prev_day=25.0,
    )
    assert result["prediction"] == 0
    assert result["action"] == "SKIP IRRIGATION"
    assert result["recommendation"] == "SKIP IRRIGATION"
    assert result["confidence"] is not None
    assert 0.5 <= result["confidence"] <= 1.0
    assert "Soil moisture is adequate" in result["reason"]


def test_feature_order_and_normalized_inputs(predictor):
    result = predictor.predict(
        temperature=30.0,
        humidity=50.0,
        soil_moisture=25.0,  # given as percent
        rainfall_prev_day=2.0,
    )
    assert result["feature_order"] == ["temperature", "humidity", "soil_moisture", "rainfall_prev_day"]
    assert result["normalized_inputs"]["soil_moisture"] == 0.25
    assert result["inputs"]["soil_moisture"] == 25.0


def test_output_schema_stability(predictor):
    result = predictor.predict(
        temperature=28.0,
        humidity=60.0,
        soil_moisture=0.4,
        rainfall_prev_day=0.0,
    )
    expected_keys = {
        "prediction",
        "action",
        "recommendation",
        "confidence",
        "confidence_available",
        "inputs",
        "normalized_inputs",
        "feature_order",
        "reason",
        "model_version",
        "model_type",
    }
    assert expected_keys.issubset(result.keys())
    assert isinstance(result["prediction"], int)
    assert isinstance(result["confidence"], float)
    assert isinstance(result["reason"], str)


def test_invalid_nan_input(predictor):
    with pytest.raises(ValueError, match="cannot be NaN"):
        predictor.predict(
            temperature=float("nan"),
            humidity=50.0,
            soil_moisture=30.0,
            rainfall_prev_day=0.0,
        )


def test_invalid_out_of_bounds_input(predictor):
    with pytest.raises(ValueError, match="Humidity out of realistic bounds"):
        predictor.predict(
            temperature=25.0,
            humidity=150.0,
            soil_moisture=30.0,
            rainfall_prev_day=0.0,
        )

    with pytest.raises(ValueError, match="Rainfall cannot be negative"):
        predictor.predict(
            temperature=25.0,
            humidity=50.0,
            soil_moisture=30.0,
            rainfall_prev_day=-10.0,
        )
