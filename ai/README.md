# AI Engine — AgriGuardian AI

## Overview

AgriGuardian AI integrates two complementary, decoupled AI pipelines to assist farmers:

1. **Environmental / Sensor AI (Active & Trained)**: Processes real-time sensor telemetry to generate explainable, actionable irrigation decisions.
2. **Crop Image Analysis AI (Prototype Architecture)**: Provides visual quality analysis and vegetation proxy estimation for leaf/crop imagery via a pluggable `VisionAnalyzer` abstraction.

---

## AI Pipelines Comparison

| Attribute | AI Pipeline 1: Sensor Irrigation AI | AI Pipeline 2: Crop Image Analysis |
|---|---|---|
| **Purpose** | Irrigation decision & stress prevention | Crop/leaf visual telemetry & image measurements |
| **Status** | **Production / Trained ML Model** | **Prototype / Replaceable Architecture** |
| **Algorithm / Core** | XGBoost Classifier (`XGBClassifier`) | `VisionAnalyzer` interface (`PrototypeVisionAnalyzer` via Pillow) |
| **Input Modality** | Tabular telemetry: `temp`, `humidity`, `soil_moisture`, `rainfall_prev_day` | Visual image bytes (`JPEG`, `PNG`, `WEBP`) |
| **Output** | Binary decision (`0` = SKIP / `1` = IRRIGATE) + Confidence + Explanation | Dimensions, format, vegetation ratio, brightness, image observations |
| **Model Artifact** | `ai/models/irrigation/model.joblib` | Modular class `ai/vision/prototype_analyzer.py` |
| **Model Version** | `irrigation-xgboost-v1` | `prototype-v1` (`no_trained_crop_disease_model`) |
| **Actuation Safety** | Advisory only -> Farmer confirmation required -> MQTT -> ESP32 | Strictly advisory -> Never actuates pump or devices |

---

## AI Pipeline 1: Environmental / Irrigation AI (XGBoost)

The irrigation model runs deterministic inference on 4 agronomic inputs:
1. `temperature` (Celsius)
2. `humidity` (Percentage)
3. `soil_moisture` (Fraction / Percentage)
4. `rainfall_prev_day` (Millimetres)

```python
from ai.inference.irrigation_predictor import IrrigationPredictor

predictor = IrrigationPredictor()
result = predictor.predict(
    temperature=35.0,
    humidity=40.0,
    soil_moisture=15.0,
    rainfall_prev_day=0.0,
)
# Returns prediction: 1 ("IRRIGATE NOW"), confidence: 0.99+, feature order, and human-readable explanation
```

---

## AI Pipeline 2: Crop Image Analysis (Vision Architecture)

### Current Prototype Capabilities (Honest Assessment)
- Validates file integrity, extension, MIME type, and dimensions.
- Estimates green-dominant pixel ratio as a vegetation presence heuristic.
- Evaluates brightness and exposure quality.
- **Explicit Limitation**: Does NOT diagnose crop diseases or generate chemical treatment plans. No trained crop-disease model is currently deployed in this repository.

### Extensibility & Swapping In a Trained Model
The architecture uses an abstract base class `VisionAnalyzer` (`ai/vision/vision_analyzer.py`):

```python
class VisionAnalyzer(ABC):
    @abstractmethod
    def analyze(self, image_bytes: bytes) -> VisionResult: ...
```

To integrate a fine-tuned crop disease model (e.g., ResNet-50 / EfficientNet-B0 trained on PlantVillage):
1. Subclass `VisionAnalyzer` in `ai/vision/`.
2. Return `VisionResult` with `model_status = "trained_model_active"` and verified evaluation metrics.
3. Update `backend/src/infrastructure/ai_engine/vision_service.py` to instantiate the new class.
4. The database schema, API router, and React UI remain 100% compatible with zero refactoring.

---

## Folder Structure

```
ai/
├── models/
│   └── irrigation/               ← Trained XGBoost model artifact & metadata
│       ├── model.joblib
│       ├── metadata.json
│       └── README.md
├── vision/                       ← Computer vision architecture
│   ├── __init__.py
│   ├── vision_analyzer.py        ← Abstract Base Class (VisionAnalyzer, VisionResult)
│   └── prototype_analyzer.py     ← Prototype implementation (honest image measurements)
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
│   └── test_irrigation_model.py  ← Automated model unit tests
└── README.md
```

---

## Automated Testing

```bash
# Run AI model tests
python -m pytest ai/tests/ -v

# Run full backend suite (including both XGBoost & Vision endpoints)
$env:PYTHONPATH="backend;.backend;."; python -m pytest backend/tests/ -v
```
