import uuid
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings
from ...core.domain.entities import UserEntity
from ...core.interfaces.repositories import IFarmRepository, IUserRepository
from ...core.use_cases.auth_use_cases import AuthUseCases
from ...core.use_cases.farm_use_cases import FarmUseCases
from ...infrastructure.database.base import AsyncSessionLocal
from ...infrastructure.database.repositories.farm_repository import FarmRepository
from ...infrastructure.database.repositories.user_repository import UserRepository

# OAuth2 scheme for Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# --- Database Session ---

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yields an async database session for the request lifecycle."""
    async with AsyncSessionLocal() as session:
        yield session

# --- Repositories ---

def get_farm_repository(session: AsyncSession = Depends(get_db_session)) -> IFarmRepository:
    return FarmRepository(session=session)

def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> IUserRepository:
    return UserRepository(session=session)

# --- Use Cases ---

def get_farm_use_cases(farm_repo: IFarmRepository = Depends(get_farm_repository)) -> FarmUseCases:
    return FarmUseCases(farm_repo=farm_repo)

def get_auth_use_cases(user_repo: IUserRepository = Depends(get_user_repository)) -> AuthUseCases:
    return AuthUseCases(user_repo=user_repo)

# --- Authentication Dependencies ---

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: IUserRepository = Depends(get_user_repository)
) -> UserEntity:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.APP_SECRET_KEY, algorithms=["HS256"])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = uuid.UUID(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception
    
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user

async def get_current_active_admin(
    current_user: UserEntity = Depends(get_current_user)
) -> UserEntity:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user
