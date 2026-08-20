# AI Engine — AgriGuardian AI

## Overview

The AI Engine is the intelligence core of AgriGuardian AI. It processes real-time sensor telemetry and environmental inputs to generate **explainable, actionable irrigation recommendations** for farmers.

## Verified Models

| Model | Algorithm | Feature Inputs | Output | Model Version |
|---|---|---|---|---|
| Irrigation Planner | XGBoost Classifier (`XGBClassifier`) | `temperature`, `humidity`, `soil_moisture`, `rainfall_prev_day` | `0` (SKIP IRRIGATION) / `1` (IRRIGATE NOW) + Confidence + Reasoning | `irrigation-xgboost-v1` |

## Explainability

The engine generates deterministic, human-readable explanations based on model input signals and decision boundaries (e.g., *"Soil moisture is low at 15.0% (optimal: 45–70%). Temperature is 35.0°C with low humidity (40%) and no recent rainfall. XGBoost model recommends irrigation to prevent crop stress."*). Confidence scores are computed directly from `predict_proba`.

## Folder Structure

```
ai/
├── models/
│   └── irrigation/               ← Model joblib artifact & metadata
│       ├── model.joblib
│       ├── metadata.json
│       └── README.md
├── data/
│   ├── raw/                      ← Synthetic agronomic dataset
│   └── processed/                ← Feature engineered dataset
├── training/
│   └── train_irrigation_model.py ← Reproducible XGBoost training pipeline
├── inference/
│   └── irrigation_predictor.py   ← Production inference engine wrapper
├── evaluation/
│   └── evaluate_irrigation_model.py ← Benchmark evaluation & test suite
├── explainability/
│   └── explanation.py            ← Rule-augmented explanation generator
├── tests/
│   └── test_irrigation_model.py   ← Automated model unit tests
└── README.md
```

## Training & Evaluation

```bash
# Train irrigation model
python ai/training/train_irrigation_model.py

# Evaluate model benchmark suite
python ai/evaluation/evaluate_irrigation_model.py

# Run model unit tests
python -m pytest ai/tests/test_irrigation_model.py -q
```

## Production Inference Usage

```python
from ai.inference.irrigation_predictor import IrrigationPredictor

predictor = IrrigationPredictor()
result = predictor.predict(
    temperature=35.0,
    humidity=40.0,
    soil_moisture=15.0,
    rainfall_prev_day=0.0,
)
# Returns dict with prediction (1), action ("IRRIGATE NOW"), confidence (0.9967), and human-readable reason
```
