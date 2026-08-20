"""
AgriGuardian AI - Vision Analysis Package

Current Status: PROTOTYPE - No trained crop-disease classification model available.
The PrototypeVisionAnalyzer performs only legitimate image-level observations
(dimensions, format, green-pixel ratio, quality). It does NOT diagnose crop disease.

Future Extension: Replace PrototypeVisionAnalyzer with a trained model
(e.g. PlantVillage ResNet, EfficientNet-B0). Only one class changes.
"""

from ai.vision.vision_analyzer import VisionAnalyzer, VisionResult
from ai.vision.prototype_analyzer import PrototypeVisionAnalyzer

__all__ = ["VisionAnalyzer", "VisionResult", "PrototypeVisionAnalyzer"]
