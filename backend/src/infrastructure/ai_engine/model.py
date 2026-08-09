from pathlib import Path
import joblib
import numpy as np
import os

MODEL = None


def train_demo_model(path: str):
    # Deterministic synthetic data
    import xgboost as xgb
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score

    rng = np.random.RandomState(42)
    n = 1000
    # features: temp, humidity, soil_moisture, rainfall_prev_day
    X = rng.uniform(low=[10, 20, 0.0, 0.0], high=[40, 100, 1.0, 100.0], size=(n, 4))
    # simple rule-based label: need_irrigation if soil_moisture < 0.3 and temp>25
    y = ((X[:, 2] < 0.3) & (X[:, 0] > 25)).astype(int)

    model = xgb.XGBClassifier(n_estimators=50, use_label_encoder=False, eval_metric="logloss", random_state=42)
    model.fit(X, y)

    os.makedirs(Path(path).parent, exist_ok=True)
    joblib.dump(model, path)
    return model


def get_model(path: str):
    global MODEL
    if MODEL is not None:
        return MODEL
    p = Path(path)
    if not p.exists():
        try:
            MODEL = train_demo_model(str(p))
        except Exception:
            MODEL = None
            raise
    else:
        MODEL = joblib.load(str(p))
    return MODEL


def predict(inputs: dict, model_path: str):
    m = get_model(model_path)
    X = np.array([[
        float(inputs.get("temperature", 25.0)),
        float(inputs.get("humidity", 50.0)),
        float(inputs.get("soil_moisture", 0.5)),
        float(inputs.get("rainfall_prev_day", 0.0)),
    ]])
    proba = m.predict_proba(X)[0][1]
    pred = int(proba > 0.5)

    # Try SHAP explanation if available
    try:
        import shap
        explainer = shap.Explainer(m)
        shap_values = explainer(X)
        explanation = {"shap_values": shap_values.values.tolist(), "features": ["temperature","humidity","soil_moisture","rainfall_prev_day"]}
    except Exception:
        # fallback: feature importances
        try:
            import numpy as _np
            imp = m.feature_importances_.tolist()
            explanation = {"feature_importances": imp, "features": ["temperature","humidity","soil_moisture","rainfall_prev_day"]}
        except Exception:
            explanation = {"note": "no explanation available"}

    return {"prediction": pred, "confidence": float(proba), "explanation": explanation}
