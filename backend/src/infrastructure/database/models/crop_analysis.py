"""
CropAnalysis database model.

Stores results of crop image analysis requests.
All analyses are linked to a farm (and therefore a user) for ownership isolation.

Note on analysis_type / model_status fields:
  These are stored verbatim from the VisionAnalyzer result.
  Current prototype always stores:
    analysis_type  = "prototype_visual_analysis"
    model_status   = "no_trained_crop_disease_model"
  When a real trained model is integrated, these will change to reflect
  the actual model used. No existing rows are affected.
"""

import uuid
from typing import Any

from sqlalchemy import Float, ForeignKey, Index, String, Text
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import Base


class CropAnalysis(Base):
    __tablename__ = "crop_analyses"

    # Ownership
    farm_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("farms.id", ondelete="CASCADE"), nullable=False
    )

    # Image reference (safe UUID-based key, never the original path)
    image_key: Mapped[str] = mapped_column(String(100), nullable=False)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Analysis identity
    analysis_type: Mapped[str] = mapped_column(
        String(100), nullable=False, default="prototype_visual_analysis"
    )
    model_status: Mapped[str] = mapped_column(
        String(100), nullable=False, default="no_trained_crop_disease_model"
    )
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)

    # Image-level measurements
    image_valid: Mapped[bool | None] = mapped_column(nullable=True)
    image_format: Mapped[str | None] = mapped_column(String(20), nullable=True)
    image_width: Mapped[int | None] = mapped_column(nullable=True)
    image_height: Mapped[int | None] = mapped_column(nullable=True)

    # Analysis output (stored as JSON lists/dicts)
    quality_notes: Mapped[list[Any] | None] = mapped_column(JSON, nullable=True)
    vegetation_proxy: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    observations: Mapped[list[Any] | None] = mapped_column(JSON, nullable=True)
    raw_metrics: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Mandatory disclaimer (stored to ensure it is always returned with history)
    disclaimer: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    farm: Mapped["Farm"] = relationship("Farm", back_populates="crop_analyses")

    # Index for fetching a farm''s analyses by date
    __table_args__ = (
        Index("ix_crop_analyses_farm_created", "farm_id", "created_at"),
    )
