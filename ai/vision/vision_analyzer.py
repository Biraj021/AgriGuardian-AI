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

    Fields
    ------
    analysis_type : str
        Always "prototype_visual_analysis" until a trained model replaces this.
    model_status : str
        "no_trained_crop_disease_model" for the prototype.
        Set to "trained_model_active" when a real model is used.
    image_valid : bool
        Whether the image was readable and well-formed.
    image_format : str | None
        Detected image format (JPEG, PNG, WEBP, …).
    width : int | None
        Image width in pixels.
    height : int | None
        Image height in pixels.
    quality_notes : list[str]
        Objective quality observations (resolution, brightness, etc.).
    vegetation_proxy : dict[str, Any]
        Heuristic green-pixel ratio and related measurements.
        Labeled as a proxy observation — NOT a diagnostic result.
    observations : list[str]
        Plain-language heuristic observations labeled as such.
    disclaimer : str
        Mandatory disclaimer that must appear in every API response.
    model_name : str
        Name of the analyzer used.
    model_version : str
        Version string of the analyzer.
    raw_metrics : dict[str, Any]
        Any additional raw numeric measurements.
    """
    analysis_type: str = "prototype_visual_analysis"
    model_status: str = "no_trained_crop_disease_model"
    image_valid: bool = False
    image_format: str | None = None
    width: int | None = None
    height: int | None = None
    quality_notes: list[str] = field(default_factory=list)
    vegetation_proxy: dict[str, Any] = field(default_factory=dict)
    observations: list[str] = field(default_factory=list)
    disclaimer: str = (
        "PROTOTYPE — This analysis uses only basic image measurements. "
        "No trained crop-disease machine-learning model is currently active. "
        "These observations are NOT a crop-disease diagnosis. "
        "Consult a qualified agricultural expert for disease identification."
    )
    model_name: str = "PrototypeVisionAnalyzer"
    model_version: str = "prototype-v1"
    raw_metrics: dict[str, Any] = field(default_factory=dict)


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
