import uuid
from typing import Any
from sqlalchemy import Boolean, CheckConstraint, Float, ForeignKey, Index, String, Text
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import Base

class Recommendation(Base):
    __tablename__ = "recommendations"

    farm_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    decision: Mapped[str] = mapped_column(String(255), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    priority: Mapped[str | None] = mapped_column(String(20), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_sources: Mapped[list[Any] | dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    top_features: Mapped[list[Any] | dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    is_implemented: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    farm: Mapped["Farm"] = relationship("Farm", back_populates="recommendations")

    # Constraints and Indexes
    __table_args__ = (
        CheckConstraint("confidence BETWEEN 0.0 AND 1.0", name="chk_confidence_range"),
        # Index for querying farm recommendations sorted by creation date
        Index("ix_recommendations_farm_type_date", "farm_id", "type", "created_at"),
    )
