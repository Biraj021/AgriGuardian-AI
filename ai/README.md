# AI Engine — AgriGuardian AI

## Overview

The AI Engine is the intelligence core of AgriGuardian AI. It takes real-time sensor data combined with external signals and produces **explainable, actionable recommendations** for farmers.

## Models

| Model | Algorithm | Input | Output |
|---|---|---|---|
| Crop Advisor | XGBoost Classifier | Soil, weather, location | Crop recommendation + confidence |
| Irrigation Planner | XGBoost Classifier | Soil moisture, weather forecast | Irrigate/Skip + duration |
| Market Analyst | XGBoost Regressor | Price history, crop type, season | Sell/Hold recommendation |

## Explainability

All models use **SHAP (SHapley Additive exPlanations)** to generate:
- Feature importance for each prediction
- Human-readable reason text (e.g., "Soil moisture at 38% — below optimal 45% threshold")
- Confidence score (0–1)

## Folder Structure

```
ai/
├── models/           ← Model code (training + inference)
├── data/             ← Datasets (raw/processed/external)
├── notebooks/        ← EDA and prototyping notebooks
├── pipelines/        ← Training pipeline scripts
├── evaluation/       ← Model evaluation reports
├── explainability/   ← SHAP explainer utilities
├── registry/         ← Saved trained model files (.joblib)
└── tests/            ← Model unit tests
```

## Training Models

```bash
# Train crop advisory model
python pipelines/train_crop_advisor.py

# Train irrigation model
python pipelines/train_irrigation_model.py

# Evaluate all models
python evaluation/evaluate_models.py
```

## Inference Contract

```python
from ai.engine.decision_engine import DecisionEngine

engine = DecisionEngine()
result = engine.predict({
    "soil_moisture": 42.5,
    "temperature": 28.3,
    "humidity": 67.1,
    "rain_detected": False,
    "water_level_cm": 15.2,
    "weather_forecast": {...},
    "current_crop": "wheat",
    "soil_type": "loamy",
})
# Returns: crop_advisory, irrigation, market, schemes — all with reasons
```
