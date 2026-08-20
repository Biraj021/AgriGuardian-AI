# Irrigation AI Model Artifacts

This directory contains the trained XGBoost model artifact, metadata, and schema for AgriGuardian AI irrigation recommendation.

## Artifacts

- `model.joblib`: Serialized XGBoost model (`XGBClassifier`)
- `metadata.json`: Model version, training metrics, feature list, and evaluation metrics
- `README.md`: This documentation file

## Features Order

1. `temperature` (Celsius)
2. `humidity` (Percentage 0–100%)
3. `soil_moisture` (Normalized fraction 0.0–1.0)
4. `rainfall_prev_day` (Millimetres 24h accumulated)

## Outputs

- `prediction`: `0` (SKIP IRRIGATION) or `1` (IRRIGATE NOW)
- `confidence`: Probability float [0.0 - 1.0]
- `reason`: Human-readable explanation text
