"""Development-only, idempotent seed data for the local SQLite MVP."""
import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select

from src.core.services.auth_service import AuthService
from src.infrastructure.database.base import AsyncSessionLocal
from src.infrastructure.database.models import Device, Farm, Recommendation, SensorReading, User

DEMO_EMAIL = "demo@agriguardian.com"
DEMO_DEVICE_MAC = "AA:BB:CC:DD:EE:FF"


async def seed_data() -> None:
    """Create missing demo records without overwriting existing user data."""
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.email == DEMO_EMAIL))).scalars().first()
        if user is None:
            user = User(
                email=DEMO_EMAIL,
                hashed_password=AuthService.get_password_hash("Demo@12345"),
                role="farmer",
                is_active=True,
            )
            session.add(user)
            await session.flush()

        farm = (
            await session.execute(select(Farm).where(Farm.user_id == user.id, Farm.is_active == True).limit(1))
        ).scalars().first()
        if farm is None:
            farm = Farm(
                user_id=user.id,
                name="Green Horizon Farm",
                location_lat=30.9010,
                location_lon=75.8573,
                primary_crop="Wheat",
                is_active=True,
            )
            session.add(farm)
            await session.flush()

        device = (await session.execute(select(Device).where(Device.mac_address == DEMO_DEVICE_MAC))).scalars().first()
        if device is None:
            device = Device(farm_id=farm.id, mac_address=DEMO_DEVICE_MAC, status="active")
            session.add(device)
            await session.flush()
        elif device.farm_id != farm.id:
            raise RuntimeError("Demo device MAC is already assigned to a different farm")

        reading_count = await session.scalar(select(func.count()).select_from(SensorReading).where(SensorReading.device_id == device.id))
        if reading_count == 0:
            now = datetime.now(timezone.utc)
            readings = ((28.5, 62.0, 42.0), (29.1, 58.0, 40.5), (30.2, 55.0, 38.0), (31.0, 52.0, 35.5), (32.5, 48.0, 33.0))
            for index, (temperature, humidity, soil_moisture) in enumerate(readings):
                session.add(SensorReading(
                    device_id=device.id,
                    temperature=temperature,
                    humidity=humidity,
                    soil_moisture=soil_moisture,
                    rainfall=0.0,
                    recorded_at=now - timedelta(hours=5 - index),
                ))

        recommendation = await session.scalar(
            select(Recommendation).where(Recommendation.farm_id == farm.id, Recommendation.type == "irrigation").limit(1)
        )
        if recommendation is None:
            session.add(Recommendation(
                farm_id=farm.id,
                type="irrigation",
                decision="Optimal Soil Moisture Maintained (42%)",
                confidence=0.92,
                priority="normal",
                reason="Development-only initial recommendation.",
                data_sources={"moisture": 42, "temperature": 28},
                top_features={"soil_moisture": 42, "temperature": 28},
                is_implemented=False,
            ))
        await session.commit()
        print("Demo seed checked: existing data was preserved and missing records were repaired.")


if __name__ == "__main__":
    asyncio.run(seed_data())
