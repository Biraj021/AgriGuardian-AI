import uuid
from typing import List

from src.core.domain.entities import FarmEntity
from src.core.domain.exceptions import EntityNotFoundError, ValidationFailedError
from src.core.interfaces.repositories import IFarmRepository

class FarmUseCases:
    """
    Orchestrates business logic for Farms.
    Relies purely on abstractions (IFarmRepository), making it 100% testable without a DB.
    """
    def __init__(self, farm_repo: IFarmRepository):
        self.farm_repo = farm_repo

    async def create_farm(self, user_id: uuid.UUID, name: str, crop: str | None = None) -> FarmEntity:
        if not name or len(name.strip()) == 0:
            raise ValidationFailedError("Farm name cannot be empty.")
            
        new_farm = FarmEntity(
            id=uuid.uuid4(),
            user_id=user_id,
            name=name,
            primary_crop=crop,
        )
        return await self.farm_repo.save(new_farm)

    async def get_farm_details(self, farm_id: uuid.UUID) -> FarmEntity:
        farm = await self.farm_repo.get_by_id(farm_id)
        if not farm:
            raise EntityNotFoundError("Farm", str(farm_id))
        return farm

    async def list_user_farms(self, user_id: uuid.UUID) -> List[FarmEntity]:
        return await self.farm_repo.get_all_for_user(user_id)

    async def deactivate_farm(self, farm_id: uuid.UUID) -> FarmEntity:
        farm = await self.farm_repo.get_by_id(farm_id)
        if not farm:
            raise EntityNotFoundError("Farm", str(farm_id))
        
        farm.deactivate()
        return await self.farm_repo.save(farm)
