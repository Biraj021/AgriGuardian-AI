"""
VisionAnalyzer — Abstract Base Class for Crop Image Analysis.

This interface allows AgriGuardian to swap in a real trained crop-disease
computer-vision model (e.g. ResNet, EfficientNet fine-tuned on PlantVillage)
without changing the API, database schema, or frontend.

Current Implementation: PrototypeVisionAnalyzer
  - Performs legitimate image-level observations only.
  - Does NOT diagnose crop disease.
  - analysis_type = "prototype_visual_analysis"
  - model_status = "no_trained_crop_disease_model"

Future Implementation: RealCropDiseaseAnalyzer (not yet built)
  - Replace PrototypeVisionAnalyzer with a trained model.
  - Must populate all VisionResult fields with real measured values.
  - Must include model name, version, dataset, and evaluation metrics.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class VisionResult:
    """
    Structured output of a crop image analysis.
    """
    analysis_type: str = "multimodal_vision_ai"
    model_status: str = "trained_model_active"
    image_valid: bool = False
    image_format: str | None = None
    width: int | None = None
    height: int | None = None
    
    # Multimodal Vision AI fields
    image_relevant: bool = True
    relevance_reason: str | None = None
    image_quality: str = "Acceptable"  # "Good" | "Acceptable" | "Poor"
    image_quality_issues: list[str] = field(default_factory=list)
    crop: str = "Unknown"
    plant_part: str | None = None
    overall_condition: str = "Unknown"
    observations: list[str] = field(default_factory=list)
    possible_issues: list[dict[str, Any]] = field(default_factory=list)
    severity: str = "Unknown"  # "Healthy / No obvious issue" | "Low" | "Moderate" | "High" | "Unknown"
    recommendations: list[str] = field(default_factory=list)
    next_photo_tip: str | None = None
    uncertainties: list[str] = field(default_factory=list)

    # Legacy/Prototype telemetry fields (kept for backward compatibility)
    quality_notes: list[str] = field(default_factory=list)
    vegetation_proxy: dict[str, Any] = field(default_factory=dict)
    raw_metrics: dict[str, Any] = field(default_factory=dict)
    
    disclaimer: str = (
        "This is AI-based visual guidance, not a confirmed agricultural or laboratory diagnosis. "
        "Always inspect surrounding crops and consult local agricultural experts before applying treatments."
    )
    model_name: str = "GeminiVisionAnalyzer"
    model_version: str = "gemini-2.5-flash"



class VisionAnalyzer(ABC):
    """
    Abstract base class for all crop image analyzers.

    To integrate a real trained model:
    1. Subclass VisionAnalyzer.
    2. Implement analyze().
    3. Return a VisionResult with model_status = "trained_model_active".
    4. Update vision_service.py to instantiate your new class.
    5. No changes needed to the API router, schema, database, or frontend.
    """

    @abstractmethod
    def analyze(self, image_bytes: bytes) -> VisionResult:
        """
        Analyze crop image bytes and return a VisionResult.

        Parameters
        ----------
        image_bytes : bytes
            Raw image bytes (JPEG, PNG, or WEBP).

        Returns
        -------
        VisionResult
            Structured analysis result. Must never contain fabricated
            disease names, fabricated confidence scores, or invented
            diagnostic conclusions.
        """
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this analyzer."""
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        """Version string of this analyzer."""
        ...
