"""
Pydantic schemas for Crop Image Analysis endpoints.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    name: str
    version: str


class PossibleIssueItem(BaseModel):
    name: str
    confidence: float | str | None = None
    reason: str


class CropAnalysisResponse(BaseModel):
    analysis_id: str
    analysis_type: str = "multimodal_vision_ai"
    model_status: str = "trained_model_active"
    model: ModelInfo
    image_valid: bool
    image_format: str | None = None
    width: int | None = None
    height: int | None = None
    
    # Multimodal Vision AI Fields
    image_relevant: bool = True
    relevance_reason: str | None = None
    image_quality: str = "Acceptable"
    image_quality_issues: list[str] = Field(default_factory=list)
    crop: str = "Unknown"
    plant_part: str | None = None
    overall_condition: str = "Unknown"
    observations: list[str] = Field(default_factory=list)
    possible_issues: list[PossibleIssueItem] = Field(default_factory=list)
    severity: str = "Unknown"
    recommendations: list[str] = Field(default_factory=list)
    next_photo_tip: str | None = None
    uncertainties: list[str] = Field(default_factory=list)

    # Legacy & telemetry fields
    quality_notes: list[str] = Field(default_factory=list)
    vegetation_proxy: dict[str, Any] = Field(default_factory=dict)
    raw_metrics: dict[str, Any] = Field(default_factory=dict)
    disclaimer: str
    created_at: str


class CropAnalysisHistoryItem(BaseModel):
    id: str
    created_at: str | None
    analysis_type: str
    model_status: str
    model_name: str
    model_version: str
    image_valid: bool | None
    image_format: str | None
    image_width: int | None
    image_height: int | None
    
    # Multimodal Fields
    image_relevant: bool | None = True
    relevance_reason: str | None = None
    image_quality: str | None = None
    image_quality_issues: list[str] | None = None
    crop: str | None = None
    plant_part: str | None = None
    overall_condition: str | None = None
    observations: list[str] | None = None
    possible_issues: list[dict[str, Any]] | list[PossibleIssueItem] | None = None
    severity: str | None = None
    recommendations: list[str] | None = None
    next_photo_tip: str | None = None
    uncertainties: list[str] | None = None

    # Legacy
    quality_notes: list[str] | None = None
    vegetation_proxy: dict[str, Any] | None = None
    raw_metrics: dict[str, Any] | None = None
    disclaimer: str


class CropAnalysisHistoryResponse(BaseModel):
    source: str = "database"
    analyses: list[CropAnalysisHistoryItem]
