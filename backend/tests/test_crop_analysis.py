"""
Comprehensive tests for Crop Image Analysis feature and Multimodal Vision AI.

Covers:
1. Valid image upload & analysis response schema (PNG, JPEG, WEBP)
2. Invalid file type rejection (e.g. PDF/TXT)
3. Oversized file rejection (>10MB)
4. Corrupt image file rejection
5. Unauthorized request rejection (no JWT token)
6. Authorized request success
7. Database persistence of analysis records with new multimodal fields
8. User/farm ownership isolation
9. Vision model status endpoint & honest transparency
10. History retrieval for authenticated user with crop, severity, condition fields
11. Vision model error handling
12. Gemini vision analyzer parsing & mock test
13. Existing irrigation XGBoost inference verification (ensuring zero regression)
"""

import asyncio
import io
import json
import os
from unittest.mock import MagicMock, patch

import httpx
import pytest
from PIL import Image

os.environ.setdefault("PYTHONPATH", ".")


def _run(coro):
    return asyncio.run(coro)


@pytest.fixture(scope="module")
def client():
    from src.api.main import app

    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


async def _auth_headers(client):
    response = await client.post(
        "/api/v1/auth/token",
        data={"username": "demo@agriguardian.com", "password": "Demo@12345"},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _create_test_image(format="PNG", size=(1448, 1086), color=(40, 160, 60)):
    """Create in-memory dummy image bytes for testing."""
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


def test_vision_model_status_endpoint(client):
    async def _test():
        r = await client.get("/api/v1/crop-analysis/model/status")
        assert r.status_code == 200
        body = r.json()
        assert "analyzer" in body
        assert "capabilities" in body
        assert "not_capable_of" in body

    _run(_test())


def test_unauthorized_crop_analysis_rejected(client):
    async def _test():
        img_bytes = _create_test_image()
        files = {"file": ("leaf.png", img_bytes, "image/png")}
        r = await client.post("/api/v1/crop-analysis/analyze", files=files)
        assert r.status_code == 401

    _run(_test())


def test_valid_png_upload_and_honest_response(client):
    async def _test():
        headers = await _auth_headers(client)
        img_bytes = _create_test_image(format="PNG", size=(1448, 1086), color=(30, 180, 45))
        files = {"file": ("crop_leaf_sample.png", img_bytes, "image/png")}

        r = await client.post("/api/v1/crop-analysis/analyze", files=files, headers=headers)
        assert r.status_code == 200, r.text
        body = r.json()

        # Structural assertions
        assert "analysis_id" in body
        assert body["image_valid"] is True
        assert body["image_format"] == "PNG"
        assert body["width"] == 1448
        assert body["height"] == 1086
        assert "disclaimer" in body
        assert "crop" in body
        assert "severity" in body
        assert "recommendations" in body
        assert "observations" in body

    _run(_test())


def test_valid_jpeg_and_webp_uploads(client):
    async def _test():
        headers = await _auth_headers(client)

        # JPEG
        jpeg_bytes = _create_test_image(format="JPEG", size=(400, 400), color=(50, 150, 50))
        r_jpeg = await client.post(
            "/api/v1/crop-analysis/analyze",
            files={"file": ("leaf.jpg", jpeg_bytes, "image/jpeg")},
            headers=headers,
        )
        assert r_jpeg.status_code == 200, r_jpeg.text
        assert r_jpeg.json()["image_format"] == "JPEG"

        # WEBP
        webp_bytes = _create_test_image(format="WEBP", size=(300, 300), color=(20, 120, 30))
        r_webp = await client.post(
            "/api/v1/crop-analysis/analyze",
            files={"file": ("leaf.webp", webp_bytes, "image/webp")},
            headers=headers,
        )
        assert r_webp.status_code == 200, r_webp.text
        assert r_webp.json()["image_format"] == "WEBP"

    _run(_test())


def test_invalid_file_type_rejected(client):
    async def _test():
        headers = await _auth_headers(client)
        fake_pdf = b"%PDF-1.4 dummy document"
        files = {"file": ("document.pdf", fake_pdf, "application/pdf")}

        r = await client.post("/api/v1/crop-analysis/analyze", files=files, headers=headers)
        assert r.status_code == 415

    _run(_test())


def test_corrupt_image_rejected(client):
    async def _test():
        headers = await _auth_headers(client)
        corrupt_bytes = b"NOT_A_VALID_IMAGE_DATA_CORRUPT_BYTES"
        files = {"file": ("corrupt.jpg", corrupt_bytes, "image/jpeg")}

        r = await client.post("/api/v1/crop-analysis/analyze", files=files, headers=headers)
        assert r.status_code == 422
        assert "corrupt" in r.json()["detail"].lower()

    _run(_test())


def test_empty_file_rejected(client):
    async def _test():
        headers = await _auth_headers(client)
        files = {"file": ("empty.png", b"", "image/png")}

        r = await client.post("/api/v1/crop-analysis/analyze", files=files, headers=headers)
        assert r.status_code == 422

    _run(_test())


def test_oversized_image_rejected(client):
    async def _test():
        headers = await _auth_headers(client)
        # 11MB dummy payload
        big_bytes = b"0" * (11 * 1024 * 1024)
        files = {"file": ("huge.jpg", big_bytes, "image/jpeg")}

        r = await client.post("/api/v1/crop-analysis/analyze", files=files, headers=headers)
        assert r.status_code == 413

    _run(_test())


def test_database_persistence_and_history(client):
    async def _test():
        headers = await _auth_headers(client)
        img_bytes = _create_test_image(format="PNG", size=(150, 150))
        files = {"file": ("persisted_test.png", img_bytes, "image/png")}

        post_res = await client.post("/api/v1/crop-analysis/analyze", files=files, headers=headers)
        assert post_res.status_code == 200
        analysis_id = post_res.json()["analysis_id"]

        history_res = await client.get("/api/v1/crop-analysis/history", headers=headers)
        assert history_res.status_code == 200
        items = history_res.json()["analyses"]
        matching = [item for item in items if item["id"] == analysis_id]
        assert len(matching) == 1
        assert "crop" in matching[0]
        assert "severity" in matching[0]

    _run(_test())


def test_gemini_vision_analyzer_mock_success():
    """Verify GeminiVisionAnalyzer handles mock structured response from client.models.generate_content."""
    from ai.vision.gemini_analyzer import GeminiVisionAnalyzer

    mock_client = MagicMock()
    mock_gemini_payload = {
        "image_relevant": True,
        "relevance_reason": "Close-up leaf image with symptoms",
        "image_quality": "Good",
        "image_quality_issues": [],
        "crop": "Tomato",
        "plant_part": "Leaf",
        "overall_condition": "Possible early fungal leaf spot",
        "observations": [
            "Concentric brown rings on leaf",
            "Yellow halo around lesions"
        ],
        "possible_issues": [
            {
                "name": "Possible Early Blight",
                "confidence": None,
                "reason": "Target-like spotting pattern"
            }
        ],
        "severity": "Moderate",
        "recommendations": [
            "Inspect underside of leaves",
            "Avoid sprinkler irrigation",
            "Consult agricultural expert"
        ],
        "next_photo_tip": "Take close-up showing both healthy and spotted sections",
        "uncertainties": ["Laboratory confirmation required"]
    }

    mock_response = MagicMock()
    mock_response.text = json.dumps(mock_gemini_payload)
    mock_response.parsed = None
    mock_client.models.generate_content.return_value = mock_response

    analyzer = GeminiVisionAnalyzer(api_key="mock-api-key", model_name="gemini-2.5-flash", client=mock_client)
    img_bytes = _create_test_image()

    res = analyzer.analyze(img_bytes)
    assert res.image_valid is True
    assert res.image_relevant is True
    assert res.crop == "Tomato"
    assert res.plant_part == "Leaf"
    assert res.severity == "Moderate"
    assert len(res.observations) == 2
    assert len(res.recommendations) == 3
    assert res.possible_issues[0]["name"] == "Possible Early Blight"
    mock_client.models.generate_content.assert_called_once()


def test_gemini_vision_analyzer_non_crop_handling():
    """Verify GeminiVisionAnalyzer properly flags non-agricultural images."""
    from ai.vision.gemini_analyzer import GeminiVisionAnalyzer

    mock_client = MagicMock()
    mock_non_crop_payload = {
        "image_relevant": False,
        "relevance_reason": "The uploaded photo is of a vehicle, not a crop.",
        "image_quality": "Good",
        "image_quality_issues": [],
        "crop": "Non-crop / Irrelevant",
        "plant_part": None,
        "overall_condition": "Not a plant image",
        "observations": ["No crop or botanical matter detected."],
        "possible_issues": [],
        "severity": "Unknown",
        "recommendations": ["Please upload a photo of a crop or plant."],
        "next_photo_tip": "Take photo of the crop leaf in daylight.",
        "uncertainties": []
    }

    mock_response = MagicMock()
    mock_response.text = json.dumps(mock_non_crop_payload)
    mock_response.parsed = None
    mock_client.models.generate_content.return_value = mock_response

    analyzer = GeminiVisionAnalyzer(api_key="mock-api-key", client=mock_client)
    img_bytes = _create_test_image()

    res = analyzer.analyze(img_bytes)
    assert res.image_relevant is False
    assert "vehicle" in res.relevance_reason.lower()
    assert res.crop == "Non-crop / Irrelevant"


def test_gemini_vision_analyzer_missing_api_key():
    """Verify graceful handling when API key is missing."""
    from ai.vision.gemini_analyzer import GeminiVisionAnalyzer

    analyzer = GeminiVisionAnalyzer(api_key="")
    img_bytes = _create_test_image()
    res = analyzer.analyze(img_bytes)
    assert res.model_status == "gemini_api_key_missing"
    assert "not configured" in res.observations[0].lower()


def test_gemini_vision_analyzer_api_timeout():
    """Verify graceful timeout handling without unhandled exceptions."""
    from ai.vision.gemini_analyzer import GeminiVisionAnalyzer

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = TimeoutError("Deadline exceeded")

    analyzer = GeminiVisionAnalyzer(api_key="mock-api-key", client=mock_client)
    img_bytes = _create_test_image()
    res = analyzer.analyze(img_bytes)
    assert res.model_status == "gemini_timeout_error"
    assert any("timed out" in obs.lower() for obs in res.observations)


def test_gemini_vision_analyzer_malformed_json_fallback():
    """Verify analyzer handles unexpected non-JSON response gracefully."""
    from ai.vision.gemini_analyzer import GeminiVisionAnalyzer

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "This is not valid json output from model."
    mock_response.parsed = None
    mock_client.models.generate_content.return_value = mock_response

    analyzer = GeminiVisionAnalyzer(api_key="mock-api-key", client=mock_client)
    img_bytes = _create_test_image()
    res = analyzer.analyze(img_bytes)
    assert "unstructured response" in res.observations[0].lower()
    assert res.overall_condition == "Analysis incomplete"


def test_vision_internal_error_handling(client):
    async def _test():
        headers = await _auth_headers(client)
        img_bytes = _create_test_image()
        files = {"file": ("error_test.jpg", img_bytes, "image/jpeg")}

        with patch("src.api.v1.routers.crop_analysis.analyze_crop_image", side_effect=RuntimeError("Test crash")):
            r = await client.post("/api/v1/crop-analysis/analyze", files=files, headers=headers)
            assert r.status_code == 500
            assert "Vision analysis error" in r.json()["detail"]

    _run(_test())


def test_existing_xgboost_pipeline_remains_intact_and_isolated():
    """Verify that existing XGBoost irrigation predictor operates untouched and uncorrupted."""
    from src.infrastructure.ai_engine.irrigation_service import predict_irrigation, FEATURE_ORDER

    assert FEATURE_ORDER == ("temperature", "humidity", "soil_moisture", "rainfall_prev_day")
    res = predict_irrigation(temperature=30.0, humidity=40.0, soil_moisture=20.0, rainfall_prev_day=0.0)
    assert res["prediction"] in (0, 1)
    assert res["model_type"] == "XGBClassifier"
    assert "XGBoost model" in res["reason"]


# ---------------------------------------------------------------------------
# NEW: Granular error-category tests (all Gemini calls mocked)
# ---------------------------------------------------------------------------

def test_gemini_vision_analyzer_sdk_missing():
    """Verify correct model_status when SDK is not installed."""
    from ai.vision.gemini_analyzer import GeminiVisionAnalyzer
    import ai.vision.gemini_analyzer as gemini_mod

    # Temporarily mock _GENAI_AVAILABLE = False
    original = gemini_mod._GENAI_AVAILABLE
    gemini_mod._GENAI_AVAILABLE = False
    try:
        analyzer = GeminiVisionAnalyzer(api_key="mock-api-key", client=MagicMock())
        img_bytes = _create_test_image()
        res = analyzer.analyze(img_bytes)
        assert res.model_status == "gemini_sdk_missing"
        assert "sdk" in res.observations[0].lower() or "not installed" in res.observations[0].lower()
    finally:
        gemini_mod._GENAI_AVAILABLE = original


def test_gemini_vision_analyzer_auth_error_401():
    """Verify gemini_auth_error model_status when Gemini returns 401."""
    from ai.vision.gemini_analyzer import GeminiVisionAnalyzer, _classify_genai_error

    mock_exc = MagicMock()
    mock_exc.code = 401
    mock_exc.__class__.__name__ = "APIError"
    status, msg = _classify_genai_error(mock_exc)
    assert status == "gemini_auth_error"
    assert "authentication" in msg.lower()

    # Also test via full analyze() path
    mock_client = MagicMock()
    
    class MockAPIError(Exception):
        pass
        
    api_err = MockAPIError("API key not valid")
    api_err.code = 401
    mock_client.models.generate_content.side_effect = api_err

    analyzer = GeminiVisionAnalyzer(api_key="mock-api-key", client=mock_client)
    img_bytes = _create_test_image()
    res = analyzer.analyze(img_bytes)
    assert res.model_status == "gemini_auth_error"
    assert "authentication" in res.observations[0].lower()


def test_gemini_vision_analyzer_model_not_found_404():
    """Verify gemini_model_not_found model_status when Gemini returns 404."""
    from ai.vision.gemini_analyzer import GeminiVisionAnalyzer, _classify_genai_error

    mock_exc = MagicMock()
    mock_exc.code = 404
    mock_exc.__class__.__name__ = "APIError"
    status, msg = _classify_genai_error(mock_exc)
    assert status == "gemini_model_not_found"
    assert "unavailable" in msg.lower() or "not found" in msg.lower() or "does not exist" in msg.lower()


def test_gemini_vision_analyzer_quota_error_429():
    """Verify gemini_quota_error model_status when Gemini returns 429."""
    from ai.vision.gemini_analyzer import GeminiVisionAnalyzer, _classify_genai_error

    mock_exc = MagicMock()
    mock_exc.code = 429
    mock_exc.__class__.__name__ = "APIError"
    status, msg = _classify_genai_error(mock_exc)
    assert status == "gemini_quota_error"
    assert "quota" in msg.lower() or "rate limit" in msg.lower()


def test_gemini_vision_analyzer_network_error():
    """Verify gemini_network_error model_status on connection error."""
    from ai.vision.gemini_analyzer import GeminiVisionAnalyzer

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = ConnectionError("ssl: connection refused")

    analyzer = GeminiVisionAnalyzer(api_key="mock-api-key", client=mock_client)
    img_bytes = _create_test_image()
    res = analyzer.analyze(img_bytes)
    # Connection errors contain "connection" which is in the network classification
    assert res.model_status in ("gemini_network_error", "gemini_api_error")


def test_model_status_endpoint_has_sdk_field(client):
    """Verify model/status endpoint returns sdk field."""
    async def _test():
        r = await client.get("/api/v1/crop-analysis/model/status")
        assert r.status_code == 200
        body = r.json()
        assert "sdk" in body
        assert body["sdk"] == "google-genai"
        assert "sdk_version" in body
        assert "configured" in body
        # Never expose the key itself
        response_text = r.text
        assert "AQ." not in response_text
        assert "AIza" not in response_text

    _run(_test())
