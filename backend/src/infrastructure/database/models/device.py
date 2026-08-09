import uuid
from datetime import datetime
from sqlalchemy import Boolean, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import Base

class Device(Base):
    __tablename__ = "devices"

    farm_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("farms.id", ondelete="CASCADE"), index=True, nullable=False)
    mac_address: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="offline")
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    farm: Mapped["Farm"] = relationship("Farm", back_populates="devices")
    sensor_readings: Mapped[list["SensorReading"]] = relationship("SensorReading", back_populates="device", cascade="all, delete-orphan")
