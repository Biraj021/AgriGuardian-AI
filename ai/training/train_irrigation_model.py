"""
AgriGuardian AI — Irrigation Model Training Pipeline

Trains an XGBoost classifier for crop irrigation recommendations based on
environmental and soil sensor signals. Saves the model and metadata artifact.
"""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
import xgboost as xgb

FEATURE_NAMES = ["temperature", "humidity", "soil_moisture", "rainfall_prev_day"]
MODEL_VERSION = "irrigation-xgboost-v1"


def generate_synthetic_agronomic_dataset(n_samples: int = 2500, random_state: int = 42) -> pd.DataFrame:
    """
    Generate realistic synthetic agricultural sensor data based on agronomic rules.
    - temperature: 10 - 45 °C
    - humidity: 15 - 95 %
    - soil_moisture: 0.05 - 0.95 (normalized fraction)
    - rainfall_prev_day: 0.0 - 50.0 mm
    """
    rng = np.random.RandomState(random_state)

    temperature = rng.uniform(10.0, 45.0, n_samples)
    humidity = rng.uniform(15.0, 95.0, n_samples)
    soil_moisture = rng.uniform(0.05, 0.95, n_samples)
    rainfall_prev_day = rng.exponential(scale=5.0, size=n_samples)
    rainfall_prev_day = np.clip(rainfall_prev_day, 0.0, 80.0)

    # Agronomic target classification logic: 1 = IRRIGATE, 0 = SKIP
    # Dry soil (< 35%), low rainfall (< 5mm) => IRRIGATE
    # High temp (> 30C), low humidity (< 50%), soil < 45%, rainfall < 10mm => IRRIGATE
    # High soil moisture (>= 50%) or heavy rain (>= 15mm) => SKIP
    irrigate_score = (
        (soil_moisture < 0.35) * 2.5 +
        ((temperature > 30.0) & (humidity < 50.0) & (soil_moisture < 0.45)) * 2.0 -
        (soil_moisture >= 0.50) * 3.0 -
        (rainfall_prev_day >= 12.0) * 4.0 -
        (rainfall_prev_day >= 5.0) * 1.5 +
        (temperature > 35.0) * 1.0
    )

    # Add small noise for smooth probability transition near boundaries
    noise = rng.normal(0.0, 0.3, n_samples)
    target = (irrigate_score + noise > 0.0).astype(int)

    df = pd.DataFrame({
        "temperature": np.round(temperature, 2),
        "humidity": np.round(humidity, 2),
        "soil_moisture": np.round(soil_moisture, 4),
        "rainfall_prev_day": np.round(rainfall_prev_day, 2),
        "target": target,
    })
    return df


def train_and_evaluate():
    print("Generating synthetic agronomic training dataset...")
    df = generate_synthetic_agronomic_dataset(n_samples=3000, random_state=42)

    # Save raw/processed dataset samples if folders exist
    repo_root = Path(__file__).resolve().parents[2]
    data_raw_dir = repo_root / "ai" / "data" / "raw"
    data_processed_dir = repo_root / "ai" / "data" / "processed"
    os.makedirs(data_raw_dir, exist_ok=True)
    os.makedirs(data_processed_dir, exist_ok=True)

    df.to_csv(data_raw_dir / "irrigation_synthetic_data.csv", index=False)
    df.to_csv(data_processed_dir / "irrigation_processed_features.csv", index=False)

    X = df[FEATURE_NAMES]
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training XGBoost Classifier on {len(X_train)} samples...")
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        random_state=42,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    cm = confusion_matrix(y_test, y_pred).tolist()

    print("=== Model Evaluation ===")
    print(f"Accuracy : {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall   : {rec:.4f}")
    print(f"F1 Score : {f1:.4f}")
    print(f"Confusion Matrix: {cm}")

    # Artifact paths
    model_dir = repo_root / "ai" / "models" / "irrigation"
    os.makedirs(model_dir, exist_ok=True)
    model_path = model_dir / "model.joblib"
    meta_path = model_dir / "metadata.json"

    joblib.dump(model, model_path)
    print(f"Saved trained model to {model_path}")

    metadata = {
        "model_name": "irrigation-xgboost",
        "version": MODEL_VERSION,
        "features": FEATURE_NAMES,
        "classes": [0, 1],
        "class_labels": {
            "0": "SKIP IRRIGATION",
            "1": "IRRIGATE NOW"
        },
        "training_date": datetime.now(timezone.utc).isoformat(),
        "dataset_source": "Synthetic Agronomic Rules Dataset (MVP Demonstration)",
        "evaluation_metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "confusion_matrix": cm,
            "test_samples": len(y_test),
        },
        "model_libraries": {
            "xgboost": xgb.__version__,
            "joblib": joblib.__version__,
        },
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Saved metadata to {meta_path}")

    # Case A validation
    case_a = np.array([[35.0, 40.0, 0.15, 0.0]])
    pred_a = int(model.predict(case_a)[0])
    prob_a = float(model.predict_proba(case_a)[0][pred_a])
    print(f"Sanity Check Case A (Dry Soil): Pred={pred_a} ({'IRRIGATE' if pred_a==1 else 'SKIP'}), Conf={prob_a:.3f}")
    assert pred_a == 1, "Case A (dry soil) failed sanity check!"

    # Case B validation
    case_b = np.array([[22.0, 80.0, 0.75, 25.0]])
    pred_b = int(model.predict(case_b)[0])
    prob_b = float(model.predict_proba(case_b)[0][pred_b])
    print(f"Sanity Check Case B (Wet Soil): Pred={pred_b} ({'IRRIGATE' if pred_b==1 else 'SKIP'}), Conf={prob_b:.3f}")
    assert pred_b == 0, "Case B (wet soil) failed sanity check!"

    return model, metadata


if __name__ == "__main__":
    train_and_evaluate()
