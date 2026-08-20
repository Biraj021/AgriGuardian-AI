"""
PrototypeVisionAnalyzer — Honest Image-Level Analysis (No Disease Detection)

STATUS: PROTOTYPE
  - This is NOT a trained crop-disease machine-learning model.
  - It does NOT diagnose plant diseases.
  - It performs only legitimate, measurable image-level analysis using Pillow.
  - Every result carries an explicit disclaimer.

What it DOES measure (honestly):
  - Image validity (readable, not corrupt)
  - Image dimensions (width x height)
  - Image format (JPEG, PNG, WEBP)
  - Overall mean brightness (0-255 scale)
  - Green-pixel ratio: fraction of pixels where green channel dominates
    This is a simple vegetation proxy, NOT a disease indicator.
  - Resolution quality flag (below 100x100 is low quality)

What it does NOT do:
  - Identify plant species
  - Diagnose crop diseases
  - Produce disease confidence scores
  - Generate treatment recommendations
  - Predict yield impact

How to replace this with a real model:
  - Subclass VisionAnalyzer, implement analyze()
  - Set model_status = "trained_model_active"
  - Update vision_service.py to use your new class
  - API, schema, database, frontend: no changes required
"""

from __future__ import annotations

import io
import statistics
from typing import Any

from ai.vision.vision_analyzer import VisionAnalyzer, VisionResult

try:
    from PIL import Image, ImageStat
    _PILLOW_AVAILABLE = True
except ImportError:
    _PILLOW_AVAILABLE = False


_DISCLAIMER = (
    "PROTOTYPE VISUAL ANALYSIS — This feature does not currently use a trained "
    "crop-disease machine-learning model. The measurements below (dimensions, "
    "green-pixel ratio, brightness) are basic image observations only. "
    "They are NOT a crop-disease diagnosis and should NOT be used as the basis "
    "for agricultural treatment decisions. Consult a qualified local agricultural "
    "expert for accurate disease identification and treatment advice."
)

_MODEL_NAME = "PrototypeVisionAnalyzer"
_MODEL_VERSION = "prototype-v1"


class PrototypeVisionAnalyzer(VisionAnalyzer):
    """
    Prototype image analyzer that performs only objective, measurable
    image-level analysis. Does not diagnose crop disease.

    All outputs are heuristic observations clearly labeled as such.
    """

    @property
    def name(self) -> str:
        return _MODEL_NAME

    @property
    def version(self) -> str:
        return _MODEL_VERSION

    def analyze(self, image_bytes: bytes) -> VisionResult:
        """
        Perform honest image-level analysis.

        Returns dimensions, format, green-pixel ratio, and brightness.
        Never returns disease names, disease confidence, or treatment advice.
        """
        result = VisionResult(
            analysis_type="prototype_visual_analysis",
            model_status="no_trained_crop_disease_model",
            model_name=_MODEL_NAME,
            model_version=_MODEL_VERSION,
            disclaimer=_DISCLAIMER,
        )

        if not _PILLOW_AVAILABLE:
            result.image_valid = False
            result.quality_notes.append(
                "Pillow library not installed — image measurement unavailable."
            )
            result.observations.append(
                "Image could not be measured. Install Pillow to enable basic image analysis."
            )
            return result

        try:
            img = Image.open(io.BytesIO(image_bytes))
            img.verify()  # Detects corrupt files
            # Re-open after verify() (verify() closes the file pointer)
            img = Image.open(io.BytesIO(image_bytes))
            img.load()
        except Exception as exc:
            result.image_valid = False
            result.quality_notes.append(f"Image could not be read: {exc}")
            result.observations.append("The uploaded file does not appear to be a valid image.")
            return result

        result.image_valid = True
        result.image_format = img.format or "Unknown"
        result.width, result.height = img.size

        # --- Quality notes ---
        pixel_count = result.width * result.height
        if pixel_count < 10_000:  # < 100x100
            result.quality_notes.append(
                f"Image resolution is very low ({result.width}x{result.height}). "
                "A higher-resolution image improves any future AI analysis."
            )
        elif pixel_count < 160_000:  # < ~400x400
            result.quality_notes.append(
                f"Image resolution is moderate ({result.width}x{result.height})."
            )
        else:
            result.quality_notes.append(
                f"Image resolution is adequate ({result.width}x{result.height})."
            )

        # --- Brightness measurement ---
        rgb_img = img.convert("RGB")
        stat = ImageStat.Stat(rgb_img)
        mean_r, mean_g, mean_b = stat.mean[:3]
        mean_brightness = (mean_r + mean_g + mean_b) / 3

        result.raw_metrics["mean_brightness"] = round(mean_brightness, 2)
        result.raw_metrics["mean_red"] = round(mean_r, 2)
        result.raw_metrics["mean_green"] = round(mean_g, 2)
        result.raw_metrics["mean_blue"] = round(mean_b, 2)

        if mean_brightness < 50:
            result.quality_notes.append(
                "Image appears dark (mean brightness: "
                f"{mean_brightness:.0f}/255). Better lighting helps analysis."
            )
        elif mean_brightness > 220:
            result.quality_notes.append(
                "Image appears overexposed (mean brightness: "
                f"{mean_brightness:.0f}/255). Reduce glare for better results."
            )
        else:
            result.quality_notes.append(
                f"Image brightness is acceptable (mean: {mean_brightness:.0f}/255)."
            )

        # --- Green-pixel ratio (vegetation proxy) ---
        # A pixel is "green-dominant" when green channel is strictly greater
        # than both red and blue channels. This is a simple, honest heuristic.
        # It is NOT a vegetation index and NOT a disease indicator.
        pixels = list(rgb_img.getdata())
        green_count = sum(
            1 for r, g, b in pixels if g > r and g > b
        )
        total_pixels = len(pixels)
        green_ratio = green_count / total_pixels if total_pixels > 0 else 0.0

        result.vegetation_proxy = {
            "green_dominant_pixel_ratio": round(green_ratio, 4),
            "description": (
                "Fraction of pixels where the green channel exceeds both "
                "red and blue channels. This is a basic image heuristic — "
                "NOT a vegetation health score or disease indicator."
            ),
            "note": "A higher ratio generally suggests more green material is visible in the image.",
        }
        result.raw_metrics["green_dominant_pixel_ratio"] = round(green_ratio, 4)
        result.raw_metrics["total_pixels_sampled"] = total_pixels

        # --- Plain-language observations (clearly labeled as heuristic) ---
        result.observations.append(
            f"[Image measurement] The image is {result.width}x{result.height} pixels "
            f"in {result.image_format} format."
        )
        result.observations.append(
            f"[Image measurement] Green-dominant pixel ratio: {green_ratio:.1%}. "
            "This is a basic image statistic — not a vegetation health assessment."
        )
        if green_ratio > 0.30:
            result.observations.append(
                "[Heuristic observation] A significant portion of the image appears green. "
                "This may indicate leafy/vegetative content. "
                "No disease conclusion can be drawn from this measurement."
            )
        else:
            result.observations.append(
                "[Heuristic observation] Less than 30% of the image shows green-dominant pixels. "
                "The image may contain soil, stems, or non-vegetative material. "
                "No disease conclusion can be drawn from this measurement."
            )

        result.observations.append(
            "[Reminder] A trained crop-disease model is NOT currently active. "
            "These are image measurements only, not medical or agricultural diagnoses."
        )

        return result


def get_prototype_analyzer() -> PrototypeVisionAnalyzer:
    """Return a singleton-style instance of the prototype analyzer."""
    return PrototypeVisionAnalyzer()
