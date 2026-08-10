import uuid
from datetime import datetime
from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import Base

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    humidity: Mapped[float | None] = mapped_column(Float, nullable=True)
    soil_moisture: Mapped[float | None] = mapped_column(Float, nullable=True)
    rainfall: Mapped[float | None] = mapped_column(Float, nullable=True)
    water_level: Mapped[float | None] = mapped_column(Float, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    device: Mapped["Device"] = relationship("Device", back_populates="sensor_readings")

    # Constraints and Indexes
    __table_args__ = (
        CheckConstraint("temperature BETWEEN -50 AND 100", name="chk_temperature_range"),
        CheckConstraint("humidity BETWEEN 0 AND 100", name="chk_humidity_range"),
        CheckConstraint("soil_moisture BETWEEN 0 AND 100", name="chk_soil_moisture_range"),
        CheckConstraint("rainfall >= 0", name="chk_rainfall_range"),
        CheckConstraint("water_level BETWEEN 0 AND 100", name="chk_water_level_range"),
        # Optimized index for finding the latest readings for a specific device
        Index("ix_sensor_readings_device_recorded", "device_id", "recorded_at", postgresql_ops={"recorded_at": "DESC"}),
    )
