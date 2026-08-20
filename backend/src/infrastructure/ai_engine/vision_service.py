"""
Vision AI service for crop image analysis.

This service loads the VisionAnalyzer implementation and exposes a clean
analyze_crop_image() function consistent with the existing irrigation_service.py pattern.

Current Status
--------------
PROTOTYPE - No trained crop-disease model is active.
  analysis_type  = "prototype_visual_analysis"
  model_status   = "no_trained_crop_disease_model"

To integrate a real model later:
  1. Create a new class that inherits VisionAnalyzer
  2. Update _get_analyzer() to return your new class instance
  3. No other files need to change
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Ensure repo root is on sys.path so ai.vision can be imported
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ai.vision.vision_analyzer import VisionAnalyzer, VisionResult

_ANALYZER: VisionAnalyzer | None = None


def _get_analyzer() -> VisionAnalyzer:
    """
    Return the active VisionAnalyzer singleton.

    Currently returns PrototypeVisionAnalyzer.
    Replace this function body to switch to a trained model.
    """
    global _ANALYZER
    if _ANALYZER is not None:
        return _ANALYZER

    from ai.vision.prototype_analyzer import PrototypeVisionAnalyzer
    _ANALYZER = PrototypeVisionAnalyzer()
    return _ANALYZER


def analyze_crop_image(image_bytes: bytes) -> dict[str, Any]:
    """
    Run image analysis and return a serializable dict for the API layer.

    Parameters
    ----------
    image_bytes : bytes
        Raw image file bytes.

    Returns
    -------
    dict
        Serializable analysis result. Always includes:
        - analysis_type: "prototype_visual_analysis"
        - model_status: "no_trained_crop_disease_model"
        - disclaimer: mandatory warning text
    """
    analyzer = _get_analyzer()
    result: VisionResult = analyzer.analyze(image_bytes)

    return {
        "analysis_type": result.analysis_type,
        "model_status": result.model_status,
        "model": {
            "name": result.model_name,
            "version": result.model_version,
        },
        "image_valid": result.image_valid,
        "image_format": result.image_format,
        "width": result.width,
        "height": result.height,
        "quality_notes": result.quality_notes,
        "vegetation_proxy": result.vegetation_proxy,
        "observations": result.observations,
        "raw_metrics": result.raw_metrics,
        "disclaimer": result.disclaimer,
    }


def get_vision_model_status() -> dict[str, Any]:
    """Return status information about the current vision analyzer."""
    analyzer = _get_analyzer()
    return {
        "analyzer": analyzer.name,
        "version": analyzer.version,
        "analysis_type": "prototype_visual_analysis",
        "model_status": "no_trained_crop_disease_model",
        "capabilities": [
            "image_validation",
            "image_dimensions",
            "image_format_detection",
            "brightness_measurement",
            "green_pixel_ratio_estimation",
        ],
        "not_capable_of": [
            "crop_disease_diagnosis",
            "disease_confidence_scoring",
            "treatment_recommendation",
            "species_identification",
        ],
        "note": (
            "A trained crop-disease computer-vision model is a planned future extension. "
            "The VisionAnalyzer interface is ready to accept it."
        ),
    }
