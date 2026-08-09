import uuid
from typing import Tuple

from src.core.domain.entities import UserEntity
from src.core.domain.exceptions import EntityNotFoundError, UnauthorizedActionError, ValidationFailedError
from src.core.interfaces.repositories import IUserRepository
from src.core.services.auth_service import AuthService
from src.api.v1.schemas.auth import UserCreate, UserLogin, Token

class AuthUseCases:
    """Orchestrates business logic for user authentication and registration."""
    
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo
        
    async def register_user(self, user_create: UserCreate) -> UserEntity:
        existing_user = await self.user_repo.get_by_email(user_create.email)
        if existing_user:
            raise ValidationFailedError("A user with this email already exists.")
            
        hashed_password = AuthService.get_password_hash(user_create.password)
        
        new_user = UserEntity(
            id=uuid.uuid4(),
            email=user_create.email,
            role=user_create.role,
            is_active=True
        )
        
        return await self.user_repo.save(new_user, hashed_password=hashed_password)

    async def authenticate_user(self, user_login: UserLogin) -> Token:
        # We need the ORM model here specifically to check the hashed password which isn't in the domain entity
        # In a purist approach, we'd add a `verify_password` method to the repository interface.
        orm_user = await getattr(self.user_repo, "get_orm_by_email")(user_login.email)
        
        if not orm_user:
            raise UnauthorizedActionError("Incorrect email or password")
            
        if not AuthService.verify_password(user_login.password, orm_user.hashed_password):
            raise UnauthorizedActionError("Incorrect email or password")
            
        if not orm_user.is_active:
            raise UnauthorizedActionError("Inactive user")

        access_token = AuthService.create_access_token(
            data={"sub": str(orm_user.id), "role": orm_user.role}
        )
        refresh_token = AuthService.create_refresh_token(
            data={"sub": str(orm_user.id)}
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
