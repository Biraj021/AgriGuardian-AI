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
    
    Instantiates GeminiVisionAnalyzer if GEMINI_API_KEY is present,
    otherwise falls back to PrototypeVisionAnalyzer for honest offline operation.
    """
    global _ANALYZER
    if _ANALYZER is not None:
        return _ANALYZER

    from src.core.config import settings

    if settings.GEMINI_API_KEY:
        from ai.vision.gemini_analyzer import GeminiVisionAnalyzer
        _ANALYZER = GeminiVisionAnalyzer(
            api_key=settings.GEMINI_API_KEY,
            model_name=settings.GEMINI_VISION_MODEL,
            timeout_seconds=settings.GEMINI_TIMEOUT_SECONDS,
        )
    else:
        from ai.vision.prototype_analyzer import PrototypeVisionAnalyzer
        _ANALYZER = PrototypeVisionAnalyzer()

    return _ANALYZER


def analyze_crop_image(image_bytes: bytes) -> dict[str, Any]:
    """
    Run image analysis and return a serializable dict for the API layer.
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
        "image_relevant": result.image_relevant,
        "relevance_reason": result.relevance_reason,
        "image_quality": result.image_quality,
        "image_quality_issues": result.image_quality_issues,
        "crop": result.crop,
        "plant_part": result.plant_part,
        "overall_condition": result.overall_condition,
        "observations": result.observations,
        "possible_issues": result.possible_issues,
        "severity": result.severity,
        "recommendations": result.recommendations,
        "next_photo_tip": result.next_photo_tip,
        "uncertainties": result.uncertainties,
        "quality_notes": result.quality_notes,
        "vegetation_proxy": result.vegetation_proxy,
        "raw_metrics": result.raw_metrics,
        "disclaimer": result.disclaimer,
    }


def get_vision_model_status() -> dict[str, Any]:
    """Return status information about the current vision analyzer."""
    from src.core.config import settings
    analyzer = _get_analyzer()
    is_gemini = "Gemini" in analyzer.name
    configured = bool(settings.GEMINI_API_KEY)

    sdk_version = "not installed"
    sdk_installed = False
    try:
        from google import genai
        sdk_installed = True
        try:
            sdk_version = genai.__version__
        except AttributeError:
            sdk_version = "unknown"
    except ImportError:
        pass

    available = bool(
        is_gemini
        and configured
        and sdk_installed
        and getattr(analyzer, "_client", None) is not None
    )

    if is_gemini and available:
        model_status = "trained_model_active"
    elif is_gemini and not sdk_installed:
        model_status = "gemini_sdk_missing"
    elif is_gemini and not configured:
        model_status = "gemini_api_key_missing"
    elif is_gemini and getattr(analyzer, "_client", None) is None:
        model_status = "gemini_client_init_error"
    else:
        model_status = "no_trained_crop_disease_model"

    return {
        "provider": "Google Gemini" if is_gemini else "AgriGuardian Prototype Heuristic",
        "analyzer": analyzer.name,
        "model": analyzer.version,
        "version": analyzer.version,
        "sdk": "google-genai",
        "sdk_version": sdk_version if is_gemini else "N/A",
        "configured": configured,
        "available": available,
        "analysis_type": "multimodal_crop_visual_analysis" if is_gemini else "prototype_visual_analysis",
        "model_status": model_status,
        "capabilities": [
            "image_validation",
            "image_dimensions",
            "crop_species_identification",
            "plant_part_detection",
            "visual_symptom_observation",
            "possible_issue_estimation",
            "severity_assessment",
            "farmer_friendly_recommendations",
            "image_quality_and_retake_tips",
            "non_crop_rejection",
        ] if is_gemini else [
            "image_validation",
            "image_dimensions",
            "image_format_detection",
            "brightness_measurement",
            "green_pixel_ratio_estimation",
        ],
        "not_capable_of": [
            "guaranteed_laboratory_diagnosis",
            "unverified_chemical_dosage_instructions",
        ],
        "note": (
            "Multimodal Vision AI active via Google Gemini."
            if (is_gemini and available)
            else "Gemini API key is not configured or SDK is unavailable. Running in prototype heuristic mode."
        ),
    }


def reset_analyzer() -> None:
    """Reset the cached analyzer singleton. Used in tests to force re-initialization."""
    global _ANALYZER
    _ANALYZER = None
