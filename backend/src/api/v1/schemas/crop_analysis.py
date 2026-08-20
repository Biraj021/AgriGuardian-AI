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


class VegetationProxy(BaseModel):
    green_dominant_pixel_ratio: float = Field(..., ge=0.0, le=1.0)
    description: str
    note: str


class CropAnalysisResponse(BaseModel):
    analysis_id: str
    analysis_type: str = "prototype_visual_analysis"
    model_status: str = "no_trained_crop_disease_model"
    model: ModelInfo
    image_valid: bool
    image_format: str | None = None
    width: int | None = None
    height: int | None = None
    quality_notes: list[str] = Field(default_factory=list)
    vegetation_proxy: dict[str, Any] = Field(default_factory=dict)
    observations: list[str] = Field(default_factory=list)
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
    quality_notes: list[str] | None
    vegetation_proxy: dict[str, Any] | None
    observations: list[str] | None
    raw_metrics: dict[str, Any] | None
    disclaimer: str


class CropAnalysisHistoryResponse(BaseModel):
    source: str = "database"
    analyses: list[CropAnalysisHistoryItem]
