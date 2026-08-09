import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.domain.entities import UserEntity
from src.core.interfaces.repositories import IUserRepository
from src.infrastructure.database.models.user import User

class UserRepository(IUserRepository):
    """Concrete implementation of the user repository using SQLAlchemy."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, orm_model: User) -> UserEntity:
        return UserEntity(
            id=orm_model.id,
            email=orm_model.email,
            role=orm_model.role,
            is_active=orm_model.is_active,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    async def get_by_id(self, user_id: uuid.UUID) -> UserEntity | None:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        return self._to_entity(orm_model) if orm_model else None

    async def get_by_email(self, email: str) -> UserEntity | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        return self._to_entity(orm_model) if orm_model else None

    async def get_orm_by_email(self, email: str) -> User | None:
        """Internal helper to get the ORM model to access the hashed_password, which is NOT in the domain entity."""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
        
    async def save(self, user: UserEntity, hashed_password: str | None = None) -> UserEntity:
        stmt = select(User).where(User.id == user.id)
        result = await self.session.execute(stmt)
        existing_orm = result.scalar_one_or_none()
        
        if existing_orm:
            existing_orm.email = user.email
            existing_orm.role = user.role
            existing_orm.is_active = user.is_active
            if hashed_password:
                existing_orm.hashed_password = hashed_password
            await self.session.commit()
            await self.session.refresh(existing_orm)
            return self._to_entity(existing_orm)
        else:
            if not hashed_password:
                raise ValueError("hashed_password is required when creating a new user.")
            new_orm = User(
                id=user.id,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                hashed_password=hashed_password
            )
            self.session.add(new_orm)
            await self.session.commit()
            await self.session.refresh(new_orm)
            return self._to_entity(new_orm)
