import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.domain.entities import FarmEntity
from src.core.interfaces.repositories import IFarmRepository
from src.infrastructure.database.models.farm import Farm

class FarmRepository(IFarmRepository):
    """
    SQLAlchemy implementation of IFarmRepository.
    Translates between SQLAlchemy ORM models (Farm) and pure Domain Entities (FarmEntity).
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, orm_model: Farm) -> FarmEntity:
        return FarmEntity(
            id=orm_model.id,
            user_id=orm_model.user_id,
            name=orm_model.name,
            is_active=orm_model.is_active,
            location_lat=orm_model.location_lat,
            location_lon=orm_model.location_lon,
            primary_crop=orm_model.primary_crop,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def _to_orm(self, entity: FarmEntity) -> Farm:
        return Farm(
            id=entity.id,
            user_id=entity.user_id,
            name=entity.name,
            is_active=entity.is_active,
            location_lat=entity.location_lat,
            location_lon=entity.location_lon,
            primary_crop=entity.primary_crop,
        )

    async def get_by_id(self, farm_id: uuid.UUID) -> FarmEntity | None:
        stmt = select(Farm).where(Farm.id == farm_id)
        result = await self.session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        return self._to_entity(orm_model) if orm_model else None

    async def get_all_for_user(self, user_id: uuid.UUID) -> list[FarmEntity]:
        stmt = select(Farm).where(Farm.user_id == user_id, Farm.is_active == True)
        result = await self.session.execute(stmt)
        orm_models = result.scalars().all()
        return [self._to_entity(m) for m in orm_models]

    async def save(self, farm: FarmEntity) -> FarmEntity:
        # Check if exists to update, else insert
        stmt = select(Farm).where(Farm.id == farm.id)
        result = await self.session.execute(stmt)
        existing_orm = result.scalar_one_or_none()
        
        if existing_orm:
            # Update fields
            existing_orm.name = farm.name
            existing_orm.is_active = farm.is_active
            existing_orm.primary_crop = farm.primary_crop
            existing_orm.location_lat = farm.location_lat
            existing_orm.location_lon = farm.location_lon
            await self.session.commit()
            await self.session.refresh(existing_orm)
            return self._to_entity(existing_orm)
        else:
            # Insert
            new_orm = self._to_orm(farm)
            self.session.add(new_orm)
            await self.session.commit()
            await self.session.refresh(new_orm)
            return self._to_entity(new_orm)

    async def delete(self, farm_id: uuid.UUID) -> None:
        stmt = select(Farm).where(Farm.id == farm_id)
        result = await self.session.execute(stmt)
        existing_orm = result.scalar_one_or_none()
        if existing_orm:
            await self.session.delete(existing_orm)
            await self.session.commit()
