import uuid
from sqlalchemy import Boolean, Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import Base

class Farm(Base):
    __tablename__ = "farms"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    primary_crop: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="farms")
    devices: Mapped[list["Device"]] = relationship("Device", back_populates="farm", cascade="all, delete-orphan")
    recommendations: Mapped[list["Recommendation"]] = relationship("Recommendation", back_populates="farm", cascade="all, delete-orphan")
    crop_analyses: Mapped[list["CropAnalysis"]] = relationship("CropAnalysis", back_populates="farm", cascade="all, delete-orphan")

    # Composite Index for finding active farms of a user
    __table_args__ = (
        Index("ix_farms_user_id_is_active", "user_id", "is_active"),
    )
