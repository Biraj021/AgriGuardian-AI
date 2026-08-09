import uuid
from abc import ABC, abstractmethod

from src.core.domain.entities import FarmEntity, UserEntity

class IFarmRepository(ABC):
    @abstractmethod
    async def get_by_id(self, farm_id: uuid.UUID) -> FarmEntity | None:
        pass

    @abstractmethod
    async def get_all_for_user(self, user_id: uuid.UUID) -> list[FarmEntity]:
        pass

    @abstractmethod
    async def save(self, farm: FarmEntity) -> FarmEntity:
        pass

    @abstractmethod
    async def delete(self, farm_id: uuid.UUID) -> None:
        pass

class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> UserEntity | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> UserEntity | None:
        pass
