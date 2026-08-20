"""
Evaluation script for AgriGuardian AI Irrigation Model.
"""

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import json
import numpy as np
from ai.inference.irrigation_predictor import IrrigationPredictor



def run_evaluation():
    repo_root = Path(__file__).resolve().parents[2]
    model_dir = repo_root / "ai" / "models" / "irrigation"

    predictor = IrrigationPredictor(model_dir=model_dir)

    print(f"Evaluating Model: {predictor.model_type} (Version: {predictor.version})")

    # Benchmark Test Cases
    cases = [
        {"temp": 35.0, "hum": 40.0, "soil": 15.0, "rain": 0.0, "expected": 1, "label": "Case A (Dry Soil)"},
        {"temp": 22.0, "hum": 80.0, "soil": 75.0, "rain": 25.0, "expected": 0, "label": "Case B (Wet Soil)"},
        {"temp": 30.0, "hum": 60.0, "soil": 55.0, "rain": 0.0, "expected": 0, "label": "Normal Moisture"},
        {"temp": 38.0, "hum": 30.0, "soil": 20.0, "rain": 0.0, "expected": 1, "label": "Extreme Heat + Dry"},
    ]

    passed = 0
    results = []

    for case in cases:
        res = predictor.predict(
            temperature=case["temp"],
            humidity=case["hum"],
            soil_moisture=case["soil"],
            rainfall_prev_day=case["rain"],
        )
        is_pass = res["prediction"] == case["expected"]
        if is_pass:
            passed += 1
        print(f"[{'PASS' if is_pass else 'FAIL'}] {case['label']}: Pred={res['prediction']} (Expected={case['expected']}), Conf={res['confidence']:.4f}")
        results.append({
            "label": case["label"],
            "prediction": res["prediction"],
            "expected": case["expected"],
            "passed": is_pass,
            "confidence": res["confidence"],
            "reason": res["reason"],
        })

    print(f"\nEvaluation Benchmark Score: {passed}/{len(cases)} passed.")
    return {
        "model_version": predictor.version,
        "total_cases": len(cases),
        "passed_cases": passed,
        "benchmark_results": results,
    }


if __name__ == "__main__":
    run_evaluation()
