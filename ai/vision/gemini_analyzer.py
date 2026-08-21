"""
GeminiVisionAnalyzer — Multimodal Vision AI for Crop & Plant Health Analysis.

Powered by Google GenAI SDK (`google-genai`).
Analyzes uploaded crop/plant photos with strict agricultural grounding,
observation vs possibility distinction, structured schema validation, and honesty guarantees.
"""

from __future__ import annotations

import io
import json
import logging
import re
from typing import Any
from pydantic import BaseModel, Field

from ai.vision.vision_analyzer import VisionAnalyzer, VisionResult

try:
    from PIL import Image, ImageStat
    _PILLOW_AVAILABLE = True
except ImportError:
    _PILLOW_AVAILABLE = False

try:
    from google import genai
    from google.genai import types
    _GENAI_AVAILABLE = True
    # Attempt to import APIError — location differs across minor SDK versions
    try:
        from google.genai.errors import APIError as _GenaiAPIError
    except ImportError:
        try:
            from google.api_core.exceptions import GoogleAPICallError as _GenaiAPIError  # type: ignore
        except ImportError:
            _GenaiAPIError = Exception  # fallback

    try:
        _GENAI_VERSION = genai.__version__
    except AttributeError:
        _GENAI_VERSION = "unknown"

except ImportError:
    _GENAI_AVAILABLE = False
    _GenaiAPIError = Exception
    _GENAI_VERSION = "not installed"

logger = logging.getLogger(__name__)

_DEFAULT_MODEL = "gemini-2.5-flash"
_ANALYZER_NAME = "GeminiVisionAnalyzer"

# ---------------------------------------------------------------------------
# Known Gemini API error codes
# ---------------------------------------------------------------------------
_AUTH_CODES = {401, 403}
_NOT_FOUND_CODE = 404
_QUOTA_CODES = {429, 503}


# -------------------------------------------------------------------------
# Pydantic Schemas for Gemini Structured JSON Output
# -------------------------------------------------------------------------
class PossibleIssueSchema(BaseModel):
    name: str = Field(description="Name of the possible disease, pest, nutrient deficiency, stress condition, or health status.")
    confidence: float | None = Field(default=None, description="Optional numerical confidence between 0.0 and 1.0 only if visual symptoms are distinctive, else null.")
    reason: str = Field(description="Objective explanation grounded solely in the visible visual symptoms observed in the image.")


class GeminiAgriculturalAnalysisSchema(BaseModel):
    image_relevant: bool = Field(description="True if image contains a crop, plant, leaf, fruit, stem, flower, seed, field, or agricultural subject. False if non-crop/irrelevant object like vehicle, human portrait, building, device, or non-botanical matter.")
    relevance_reason: str | None = Field(default=None, description="Clear explanation of whether botanical/crop matter is present or why the image is irrelevant.")
    image_quality: str = Field(description="Rating of image quality: 'Good', 'Acceptable', or 'Poor'.")
    image_quality_issues: list[str] = Field(default_factory=list, description="List of visual issues: blurry, underexposed, glare, too distant, partial view, etc.")
    crop: str = Field(default="Unknown", description="Identified crop or plant species (e.g. Tomato, Rice, Wheat, Maize, Potato, Chili, Cotton, or 'Unknown').")
    plant_part: str | None = Field(default=None, description="Primary plant part visible: 'Leaf', 'Fruit', 'Stem', 'Flower', 'Root', 'Whole Plant', 'Field', 'Soil', or 'Other'.")
    overall_condition: str = Field(default="Analyzed", description="Concise summary of overall visible health condition.")
    observations: list[str] = Field(default_factory=list, description="Objective visual symptoms seen directly (e.g. concentric brown spots, yellowing veins, powdery mildew, chewing holes, wilting).")
    possible_issues: list[PossibleIssueSchema] = Field(default_factory=list, description="Possible agricultural causes or conditions consistent with visible signs. Must use tentative language like 'possible' or 'visually consistent with'.")
    severity: str = Field(default="Unknown", description="Assessment of severity: 'Healthy / No obvious issue', 'Low', 'Moderate', 'High', or 'Unknown'.")
    recommendations: list[str] = Field(default_factory=list, description="Practical, safe agronomic next steps for the farmer (e.g. monitor spread, inspect underside of leaves, check irrigation). NEVER prescribe dangerous chemical pesticide dosages.")
    next_photo_tip: str | None = Field(default=None, description="Helpful advice to the farmer for taking a clearer follow-up photo if needed.")
    uncertainties: list[str] = Field(default_factory=list, description="Explicit statement of diagnostic limitations from single photograph alone.")


_GEMINI_AGRICULTURAL_PROMPT = """You are an expert, honest agricultural botanist and plant health computer-vision assistant for farmers.
Analyze the provided crop or plant image carefully and objectively.

Follow these CRITICAL HONESTY AND SAFETY RULES:
1. WHAT IS VISIBLE & RELEVANCE:
   - Determine whether the image contains a plant, crop, leaf, fruit, stem, flower, seed, crop field, soil, pest, or agricultural object.
   - If the image is NOT a crop/plant/agricultural image (e.g. a car, animal, human portrait, electronic device, furniture, random object), set "image_relevant": false and explain clearly in "relevance_reason". Do NOT invent a plant disease or pretend it is a crop.
2. CROP / PLANT IDENTIFICATION:
   - Name the likely crop or plant if visually recognizable (e.g., "Tomato", "Rice", "Wheat", "Maize", "Cotton", "Potato", "Chili", "Apple", "Banana", etc.).
   - If uncertain or if only generic foliage is visible, set "crop": "Unknown". NEVER invent or fabricate a crop name.
3. PLANT PART:
   - Identify the primary plant part visible: "Leaf", "Fruit", "Stem", "Flower", "Root", "Whole Plant", "Field", "Soil", or "Other".
4. VISIBLE SIGNS & OBSERVATIONS:
   - List objective visual symptoms ONLY (e.g., circular brown spots, yellow chlorotic halos, leaf curling, necrosis, pest chew holes, white powdery coating, wilting).
5. POSSIBLE ISSUES (SEPARATE OBSERVATION FROM DIAGNOSIS):
   - Provide possible agricultural explanations based ONLY on visible signs (e.g. "Possible early blight fungal infection", "Possible nitrogen deficiency chlorosis", "Possible water stress", "Visually healthy").
   - Use humble, tentative language ("possible", "may indicate", "visually consistent with").
   - NEVER claim 100% certainty from a photograph alone.
6. SEVERITY:
   - Must be one of: "Healthy / No obvious issue", "Low", "Moderate", "High", "Unknown".
7. RECOMMENDATIONS (FARMER-FRIENDLY & SAFE):
   - Give practical, non-destructive agronomic next steps (e.g., inspect underside of leaves, monitor nearby rows, check soil moisture, isolate infected leaves, consult local agricultural extension officer).
   - NEVER provide dangerous, unverified chemical pesticide dosage formulas or specific brand pesticide application rates.
8. IMAGE QUALITY & RETAKE TIPS:
   - Rate "image_quality": "Good", "Acceptable", or "Poor".
   - Note any issues: blurry, underexposed, glare, too distant.
   - Provide a helpful "next_photo_tip" to help the farmer get better visual clarity.
"""


def _safe_log_error(exc: Exception, model_name: str) -> None:
    """Log Gemini errors safely — never logging the API key."""
    exc_type = type(exc).__name__
    code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    message = getattr(exc, "message", None) or str(exc)
    # Truncate to avoid accidentally leaking sensitive data in long messages
    message_safe = message[:200] if message else "(no message)"
    logger.error(
        "Gemini API error | type=%s | model=%s | code=%s | message=%s",
        exc_type,
        model_name,
        code,
        message_safe,
    )


def _classify_genai_error(exc: Exception) -> tuple[str, str]:
    """
    Classify a Gemini API exception into (model_status, user_message) pair.
    Never inspects the API key or logs secrets.
    Returns a tuple of (model_status_string, user_facing_message).
    """
    code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    exc_str = str(exc).lower()

    # Explicit HTTP status code check (most reliable)
    if code in _AUTH_CODES or code == 401 or code == 403:
        return (
            "gemini_auth_error",
            "Gemini API authentication failed. The server API key may be invalid or expired.",
        )
    if code == _NOT_FOUND_CODE:
        return (
            "gemini_model_not_found",
            "The configured Gemini model is unavailable or does not exist.",
        )
    if code in _QUOTA_CODES or code == 429 or code == 503:
        return (
            "gemini_quota_error",
            "Gemini API quota or rate limit was reached. Please try again later.",
        )

    # Message-based classification (semantics only, no key inspection)
    if "deadline exceeded" in exc_str or "timeout" in exc_str or "timed out" in exc_str:
        return (
            "gemini_timeout_error",
            "Gemini Vision timed out. Please try again.",
        )
    if "api_key_invalid" in exc_str or "invalid api key" in exc_str:
        return (
            "gemini_auth_error",
            "Gemini API authentication failed. The server API key may be invalid.",
        )
    if "not found" in exc_str or "model_not_found" in exc_str:
        return (
            "gemini_model_not_found",
            "The configured Gemini model is unavailable or does not exist.",
        )
    if "quota" in exc_str or "rate limit" in exc_str or "resource exhausted" in exc_str:
        return (
            "gemini_quota_error",
            "Gemini API quota or rate limit was reached. Please try again later.",
        )
    if "permission" in exc_str or "unauthenticated" in exc_str or "forbidden" in exc_str:
        return (
            "gemini_auth_error",
            "Gemini API authentication failed. Check the server API key configuration.",
        )

    code_str = f" (code: {code})" if code else ""
    return (
        "gemini_api_error",
        f"Gemini Vision returned an unexpected error{code_str}. Please try again.",
    )


class GeminiVisionAnalyzer(VisionAnalyzer):
    """
    Multimodal Gemini Vision Analyzer powered by the official google-genai SDK.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = _DEFAULT_MODEL,
        timeout_seconds: float = 25.0,
        client: Any = None,
    ):
        self._api_key = (api_key or "").strip().strip('"').strip("'")
        self._model_name = model_name or _DEFAULT_MODEL
        self._timeout_seconds = timeout_seconds

        # Allow client injection (for tests) or lazy instantiation
        if client is not None:
            self._client = client
        elif _GENAI_AVAILABLE and self._api_key:
            try:
                self._client = genai.Client(api_key=self._api_key)
                logger.info(
                    "GeminiVisionAnalyzer: client initialized (SDK=%s, model=%s)",
                    _GENAI_VERSION,
                    self._model_name,
                )
            except Exception as exc:
                # Log type only — never log the key itself
                logger.error(
                    "GeminiVisionAnalyzer: failed to initialize Client (type=%s): %s",
                    type(exc).__name__,
                    str(exc)[:100],
                )
                self._client = None
        else:
            self._client = None

    @property
    def client(self) -> Any:
        return self._client

    @property
    def name(self) -> str:
        return _ANALYZER_NAME

    @property
    def version(self) -> str:
        return self._model_name

    @property
    def sdk_version(self) -> str:
        return _GENAI_VERSION

    def analyze(self, image_bytes: bytes) -> VisionResult:
        """
        Validate image and perform multimodal analysis via Google GenAI.
        """
        result = VisionResult(
            analysis_type="multimodal_vision_ai",
            model_status="trained_model_active",
            model_name=self.name,
            model_version=self.version,
        )

        if not _PILLOW_AVAILABLE:
            result.image_valid = False
            result.quality_notes.append("Pillow library not installed.")
            result.observations.append("Image processing library is unavailable on the server.")
            result.model_status = "image_processing_unavailable"
            return result

        # ------------------------------------------------------------------
        # Step 1: Image Validation & Measurement
        # ------------------------------------------------------------------
        try:
            pil_img = Image.open(io.BytesIO(image_bytes))
            pil_img.verify()
            pil_img = Image.open(io.BytesIO(image_bytes))
            pil_img.load()
        except Exception as exc:
            result.image_valid = False
            result.model_status = "gemini_image_error"
            result.quality_notes.append(f"Image could not be read: {type(exc).__name__}")
            result.observations.append("The uploaded file is not a valid or readable image.")
            return result

        result.image_valid = True
        result.image_format = (pil_img.format or "JPEG").upper()
        result.width, result.height = pil_img.size

        # Compute secondary image telemetry metrics (not used as diagnosis)
        try:
            rgb_img = pil_img.convert("RGB")
            stat = ImageStat.Stat(rgb_img)
            mean_brightness = sum(stat.mean[:3]) / 3
            result.raw_metrics["mean_brightness"] = round(mean_brightness, 2)

            pixels = list(rgb_img.getdata())
            green_count = sum(1 for r, g, b in pixels if g > r and g > b)
            green_ratio = green_count / len(pixels) if pixels else 0.0
            result.vegetation_proxy = {
                "green_dominant_pixel_ratio": round(green_ratio, 4),
                "description": "Green-pixel proxy telemetry metric.",
            }
            result.raw_metrics["green_dominant_pixel_ratio"] = round(green_ratio, 4)
        except Exception as exc:
            logger.debug("Telemetry metric computation error: %s", type(exc).__name__)

        # ------------------------------------------------------------------
        # Step 2: Check SDK & Client Availability
        # ------------------------------------------------------------------
        if not _GENAI_AVAILABLE:
            result.model_status = "gemini_sdk_missing"
            result.observations.append(
                "Gemini Vision SDK (google-genai) is not installed on the server."
            )
            result.recommendations.append(
                "The backend administrator must install the google-genai package."
            )
            return result

        if not self._api_key:
            result.model_status = "gemini_api_key_missing"
            result.observations.append(
                "Gemini Vision is not configured on the server (GEMINI_API_KEY is missing)."
            )
            result.recommendations.append(
                "Add GEMINI_API_KEY to your environment variables."
            )
            return result

        if self._client is None:
            result.model_status = "gemini_client_init_error"
            result.observations.append(
                "Gemini Vision client failed to initialize. Check the server configuration."
            )
            result.recommendations.append(
                "Check the server logs for Gemini client initialization errors."
            )
            return result

        # ------------------------------------------------------------------
        # Step 3: Prepare Image Part & MIME Type for Gemini
        # ------------------------------------------------------------------
        try:
            buffered = io.BytesIO()
            img_fmt = result.image_format
            if img_fmt in ("JPEG", "JPG"):
                mime_type = "image/jpeg"
                if pil_img.mode in ("RGBA", "P"):
                    pil_img.convert("RGB").save(buffered, format="JPEG", quality=90)
                else:
                    pil_img.save(buffered, format="JPEG", quality=90)
            elif img_fmt == "PNG":
                mime_type = "image/png"
                pil_img.save(buffered, format="PNG")
            elif img_fmt == "WEBP":
                mime_type = "image/webp"
                pil_img.save(buffered, format="WEBP")
            else:
                mime_type = "image/jpeg"
                pil_img.convert("RGB").save(buffered, format="JPEG", quality=90)

            image_data = buffered.getvalue()

        except Exception as exc:
            logger.error("Image re-encoding failed: %s", type(exc).__name__)
            result.model_status = "gemini_image_error"
            result.observations.append(
                "The uploaded image could not be prepared for analysis."
            )
            return result

        # ------------------------------------------------------------------
        # Step 4: Call Gemini API
        # ------------------------------------------------------------------
        try:
            contents = [
                types.Part.from_text(text=_GEMINI_AGRICULTURAL_PROMPT),
                types.Part.from_bytes(data=image_data, mime_type=mime_type),
            ]

            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GeminiAgriculturalAnalysisSchema,
                temperature=0.1,
                max_output_tokens=1500,
            )

            logger.info(
                "GeminiVisionAnalyzer: calling model=%s mime=%s size=%d bytes",
                self._model_name,
                mime_type,
                len(image_data),
            )

            response = self._client.models.generate_content(
                model=self._model_name,
                contents=contents,
                config=config,
            )

            response_text = ""
            if hasattr(response, "text") and response.text:
                response_text = response.text
            elif hasattr(response, "parsed") and response.parsed:
                # SDK returned pre-parsed pydantic object
                if isinstance(response.parsed, GeminiAgriculturalAnalysisSchema):
                    self._apply_parsed_schema(result, response.parsed)
                    return result

            # Parse and validate with Pydantic
            parsed_data = self._parse_and_validate(response_text)
            if parsed_data:
                self._apply_parsed_schema(result, parsed_data)
            else:
                logger.warning(
                    "GeminiVisionAnalyzer: could not parse response as structured JSON. "
                    "First 300 chars: %s",
                    response_text[:300],
                )
                result.model_status = "gemini_response_error"
                result.observations = [
                    "The AI returned an unstructured response. Please try again.",
                ]
                if response_text:
                    result.observations.append(response_text[:200])
                result.overall_condition = "Analysis incomplete"

        except _GenaiAPIError as exc:
            _safe_log_error(exc, self._model_name)
            status, message = _classify_genai_error(exc)
            result.model_status = status
            result.observations.append(message)
            result.recommendations.append(
                "Check server configuration if the problem persists."
            )

        except TimeoutError as exc:
            logger.error(
                "GeminiVisionAnalyzer: timeout calling model=%s (type=%s)",
                self._model_name,
                type(exc).__name__,
            )
            result.model_status = "gemini_timeout_error"
            result.observations.append(
                "Gemini Vision timed out. Please try again in a moment."
            )
            result.recommendations.append("Try again. If the issue persists, check network connectivity.")

        except Exception as exc:
            # Classify by exception TYPE and semantics — NOT by string-matching the key value
            exc_type = type(exc).__name__
            exc_str = str(exc).lower()
            logger.error(
                "GeminiVisionAnalyzer: unexpected error (type=%s) calling model=%s",
                exc_type,
                self._model_name,
                exc_info=True,
            )

            if "deadline" in exc_str or "timeout" in exc_str or "timed out" in exc_str:
                result.model_status = "gemini_timeout_error"
                result.observations.append(
                    "Gemini Vision timed out. Please try again."
                )
            elif any(k in exc_str for k in ("ssl", "connection", "network", "socket", "unreachable")):
                result.model_status = "gemini_network_error"
                result.observations.append(
                    "Could not reach Gemini Vision. Please check network connectivity and try again."
                )
            elif "quota" in exc_str or "rate limit" in exc_str or "resource_exhausted" in exc_str:
                result.model_status = "gemini_quota_error"
                result.observations.append(
                    "Gemini API quota or rate limit was reached. Please try again later."
                )
            elif "api_key_invalid" in exc_str or "invalid api key" in exc_str:
                result.model_status = "gemini_auth_error"
                result.observations.append(
                    "Gemini API authentication failed. Check the server API key configuration."
                )
            elif "not found" in exc_str or "model_not_found" in exc_str:
                result.model_status = "gemini_model_not_found"
                result.observations.append(
                    "The configured Gemini model is unavailable."
                )
            else:
                result.model_status = "gemini_api_error"
                result.observations.append(
                    f"Gemini Vision returned an unexpected error ({exc_type}). Please try again."
                )

            result.recommendations.append(
                "If this error persists, check the server logs for details."
            )

        return result

    def _apply_parsed_schema(self, result: VisionResult, schema: GeminiAgriculturalAnalysisSchema) -> None:
        """Apply validated schema fields onto VisionResult."""
        result.image_relevant = bool(schema.image_relevant)
        result.relevance_reason = schema.relevance_reason
        result.image_quality = schema.image_quality or "Acceptable"
        result.image_quality_issues = schema.image_quality_issues or []
        result.crop = schema.crop or "Unknown"
        result.plant_part = schema.plant_part
        result.overall_condition = schema.overall_condition or "Analyzed"
        result.observations = schema.observations or []
        result.possible_issues = [
            {"name": item.name, "confidence": item.confidence, "reason": item.reason}
            for item in schema.possible_issues
        ]
        result.severity = schema.severity or "Unknown"
        result.recommendations = schema.recommendations or []
        result.next_photo_tip = schema.next_photo_tip
        result.uncertainties = schema.uncertainties or []

    def _parse_and_validate(self, text: str) -> GeminiAgriculturalAnalysisSchema | None:
        """Parse raw text string into GeminiAgriculturalAnalysisSchema."""
        if not text:
            return None

        cleaned = text.strip()
        if "```" in cleaned:
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
            if match:
                cleaned = match.group(1)
            else:
                cleaned = re.sub(r"^```[a-zA-Z]*\n", "", cleaned)
                cleaned = re.sub(r"\n```$", "", cleaned)

        # Attempt direct JSON deserialization and Pydantic validation
        try:
            raw_dict = json.loads(cleaned)
            return GeminiAgriculturalAnalysisSchema.model_validate(raw_dict)
        except Exception:
            # Try to find outermost braces
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    raw_dict = json.loads(cleaned[start : end + 1])
                    return GeminiAgriculturalAnalysisSchema.model_validate(raw_dict)
                except Exception as inner_exc:
                    logger.debug("Pydantic validation fallback failed: %s", type(inner_exc).__name__)
        return None
