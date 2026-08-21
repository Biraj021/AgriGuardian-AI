"""
Crop Image Analysis API router.

Endpoints
---------
POST /api/v1/crop-analysis/analyze
  - Multipart upload for crop/leaf image.
  - Protected by JWT authentication (farmer ownership check).
  - Performs validation (MIME, file size, readability, extension, security).
  - Invokes PrototypeVisionAnalyzer.
  - Persists result to database.
  - Returns structured observations with mandatory prototype disclaimers.

GET /api/v1/crop-analysis/history
  - Returns past analyses for the authenticated farmer''s active farm.

GET /api/v1/crop-analysis/model/status
  - Returns status/metadata about the current vision engine.
"""

from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db_session
from src.api.v1.schemas.crop_analysis import (
    CropAnalysisHistoryItem,
    CropAnalysisHistoryResponse,
    CropAnalysisResponse,
)
from src.core.domain.entities import UserEntity
from src.infrastructure.ai_engine.vision_service import (
    analyze_crop_image,
    get_vision_model_status,
)
from src.infrastructure.database.models import CropAnalysis, Farm

logger = logging.getLogger(__name__)

router = APIRouter()

# Max allowed image size (10 MB)
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/x-png", "application/octet-stream"}

# Safe upload storage directory (internal to backend, never exposed directly)
UPLOAD_DIR = Path(__file__).resolve().parents[4] / "uploads" / "crop_analysis"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def _get_owned_farm(db: AsyncSession, user: UserEntity) -> Farm:
    result = await db.execute(
        select(Farm).where(Farm.user_id == user.id, Farm.is_active == True).limit(1)
    )
    farm = result.scalars().first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active farm found for current user",
        )
    return farm


@router.get("/model/status")
async def vision_model_status():
    """Return status and transparency info for the vision engine."""
    return get_vision_model_status()


@router.post(
    "/analyze",
    response_model=CropAnalysisResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_crop(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),
    current_user: UserEntity = Depends(get_current_user),
):
    """
    Validate and analyze a crop/leaf image.

    Validates:
    - File extension (.jpg, .jpeg, .png, .webp)
    - Content-Type / MIME type
    - File size (<= 10MB)
    - Image format & readability with Pillow
    - Traversal/malicious filenames
    """
    farm = await _get_owned_farm(db, current_user)

    filename = file.filename or "unknown.jpg"
    # Basic path traversal guard
    clean_filename = os.path.basename(filename)
    ext = Path(clean_filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file extension '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # Some browsers/clients send application/octet-stream or image/x-png; we validate extension & MIME
    if file.content_type and file.content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported MIME type '{file.content_type}'. Allowed: image/jpeg, image/png, image/webp",
        )

    try:
        content = await file.read()
    except Exception as exc:
        logger.error(f"Failed to read uploaded file {clean_filename}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file: {exc}",
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file is empty (0 bytes).",
        )

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB.",
        )

    # Run analysis through VisionAnalyzer
    try:
        analysis_data = analyze_crop_image(content)
    except Exception as exc:
        logger.exception(f"Vision analysis internal exception for {clean_filename}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vision analysis error: {exc}",
        )

    if not analysis_data.get("image_valid"):
        notes = "; ".join(analysis_data.get("quality_notes", []))
        logger.warning(f"Image validation failed for {clean_filename}: {notes}")
        detail_msg = f"The uploaded file is corrupt or not a recognized image format: {notes}" if notes else "The uploaded file is corrupt or not a recognized image format."
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail_msg,
        )

    # Double check recognized format matches supported formats
    detected_format = (analysis_data.get("image_format") or "").upper()
    if detected_format not in {"JPEG", "PNG", "WEBP"}:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Image data format '{detected_format}' is not supported. Please use JPEG, PNG, or WEBP.",
        )

    # Save to safe internal storage using UUID key
    image_uuid = str(uuid.uuid4())
    stored_file_key = f"{image_uuid}{ext}"
    destination = UPLOAD_DIR / stored_file_key
    try:
        with open(destination, "wb") as f:
            f.write(content)
    except Exception as exc:
        logger.warning(f"Failed to persist image to disk {destination}: {exc}")

    # Persist to database
    record = CropAnalysis(
        farm_id=farm.id,
        image_key=stored_file_key,
        original_filename=clean_filename,
        analysis_type=analysis_data["analysis_type"],
        model_status=analysis_data["model_status"],
        model_name=analysis_data["model"]["name"],
        model_version=analysis_data["model"]["version"],
        image_valid=analysis_data["image_valid"],
        image_format=analysis_data.get("image_format"),
        image_width=analysis_data.get("width"),
        image_height=analysis_data.get("height"),
        image_relevant=analysis_data.get("image_relevant", True),
        relevance_reason=analysis_data.get("relevance_reason"),
        image_quality=analysis_data.get("image_quality"),
        image_quality_issues=analysis_data.get("image_quality_issues"),
        crop=analysis_data.get("crop"),
        plant_part=analysis_data.get("plant_part"),
        overall_condition=analysis_data.get("overall_condition"),
        possible_issues=analysis_data.get("possible_issues"),
        severity=analysis_data.get("severity"),
        recommendations=analysis_data.get("recommendations"),
        next_photo_tip=analysis_data.get("next_photo_tip"),
        uncertainties=analysis_data.get("uncertainties"),
        quality_notes=analysis_data.get("quality_notes"),
        vegetation_proxy=analysis_data.get("vegetation_proxy"),
        observations=analysis_data.get("observations"),
        raw_metrics=analysis_data.get("raw_metrics"),
        disclaimer=analysis_data["disclaimer"],
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return CropAnalysisResponse(
        analysis_id=str(record.id),
        analysis_type=record.analysis_type,
        model_status=record.model_status,
        model=analysis_data["model"],
        image_valid=bool(record.image_valid),
        image_format=record.image_format,
        width=record.image_width,
        height=record.image_height,
        image_relevant=record.image_relevant if record.image_relevant is not None else True,
        relevance_reason=record.relevance_reason,
        image_quality=record.image_quality or "Acceptable",
        image_quality_issues=record.image_quality_issues or [],
        crop=record.crop or "Unknown",
        plant_part=record.plant_part,
        overall_condition=record.overall_condition or "Analyzed",
        observations=record.observations or [],
        possible_issues=record.possible_issues or [],
        severity=record.severity or "Unknown",
        recommendations=record.recommendations or [],
        next_photo_tip=record.next_photo_tip,
        uncertainties=record.uncertainties or [],
        quality_notes=record.quality_notes or [],
        vegetation_proxy=record.vegetation_proxy or {},
        raw_metrics=record.raw_metrics or {},
        disclaimer=record.disclaimer,
        created_at=record.created_at.isoformat(),
    )


@router.get(
    "/history",
    response_model=CropAnalysisHistoryResponse,
    status_code=status.HTTP_200_OK,
)
async def get_crop_analysis_history(
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
    current_user: UserEntity = Depends(get_current_user),
):
    """
    Get past crop image analyses for the authenticated user's farm.
    """
    farm = await _get_owned_farm(db, current_user)

    result = await db.execute(
        select(CropAnalysis)
        .where(CropAnalysis.farm_id == farm.id)
        .order_by(CropAnalysis.created_at.desc())
        .limit(limit)
    )
    records = result.scalars().all()

    items = [
        CropAnalysisHistoryItem(
            id=str(r.id),
            created_at=r.created_at.isoformat() if r.created_at else None,
            analysis_type=r.analysis_type,
            model_status=r.model_status,
            model_name=r.model_name,
            model_version=r.model_version,
            image_valid=r.image_valid,
            image_format=r.image_format,
            image_width=r.image_width,
            image_height=r.image_height,
            image_relevant=r.image_relevant if r.image_relevant is not None else True,
            relevance_reason=r.relevance_reason,
            image_quality=r.image_quality,
            image_quality_issues=r.image_quality_issues,
            crop=r.crop,
            plant_part=r.plant_part,
            overall_condition=r.overall_condition,
            observations=r.observations,
            possible_issues=r.possible_issues,
            severity=r.severity,
            recommendations=r.recommendations,
            next_photo_tip=r.next_photo_tip,
            uncertainties=r.uncertainties,
            quality_notes=r.quality_notes,
            vegetation_proxy=r.vegetation_proxy,
            raw_metrics=r.raw_metrics,
            disclaimer=r.disclaimer,
        )
        for r in records
    ]

    return CropAnalysisHistoryResponse(source="database", analyses=items)
