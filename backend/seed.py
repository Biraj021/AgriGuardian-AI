import asyncio
from datetime import datetime, timezone, timedelta
from sqlalchemy.future import select
from src.infrastructure.database.base import AsyncSessionLocal
from src.infrastructure.database.models import User, Farm, Device, Recommendation, SensorReading
from src.core.services.auth_service import AuthService

from src.infrastructure.database.base import engine, Base

async def seed_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Check if demo user already exists
        result = await session.execute(select(User).where(User.email == "demo@agriguardian.com"))
        existing_user = result.scalars().first()
        
        if existing_user:
            print("Demo user already exists.")
            return

        print("Seeding database...")
        # 1. Create Demo User
        hashed = AuthService.get_password_hash("Demo@12345")
        demo_user = User(
            email="demo@agriguardian.com",
            hashed_password=hashed,
            role="farmer",
            is_active=True,
        )
        session.add(demo_user)
        await session.flush()

        # 2. Create Demo Farm
        demo_farm = Farm(
            user_id=demo_user.id,
            name="Green Horizon Farm",
            location_lat=30.9010,
            location_lon=75.8573,
            primary_crop="Wheat",
            is_active=True,
        )
        session.add(demo_farm)
        await session.flush()

        # 3. Create Demo Device (IoT placeholder for tomorrow)
        demo_device = Device(
            farm_id=demo_farm.id,
            mac_address="AA:BB:CC:DD:EE:FF",
            status="active"
        )
        session.add(demo_device)
        await session.flush()

        # 4. Create realistic sensor readings (last 24h)
        now = datetime.now(timezone.utc)
        readings = [
            (28.5, 62.0, 42.0),
            (29.1, 58.0, 40.5),
            (30.2, 55.0, 38.0),
            (31.0, 52.0, 35.5),
            (32.5, 48.0, 33.0),
        ]
        for i, (temp, hum, moisture) in enumerate(readings):
            session.add(SensorReading(
                device_id=demo_device.id,
                temperature=temp,
                humidity=hum,
                soil_moisture=moisture,
                recorded_at=now - timedelta(hours=len(readings) - i),
            ))

        # 5. Create Initial Demo Recommendation
        demo_rec = Recommendation(
            farm_id=demo_farm.id,
            type="irrigation",
            decision="Optimal Soil Moisture Maintained (42%)",
            confidence=0.92,
            priority="normal",
            reason="Calculated using XGBoost Irrigation AI model based on recent moisture and weather indicators.",
            data_sources={"moisture": 42, "temperature": 28},
            top_features={"soil_moisture": 42, "temperature": 28},
            is_implemented=False
        )
        session.add(demo_rec)

        await session.commit()
        print("Database seeded successfully!")
        print("  Demo login: demo@agriguardian.com / Demo@12345")

if __name__ == "__main__":
    asyncio.run(seed_data())
