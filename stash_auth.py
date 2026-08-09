from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.api.dependencies import get_auth_use_cases, get_current_user
from src.api.v1.schemas.auth import Token, UserCreate, UserLogin, UserResponse
from src.core.domain.entities import UserEntity
from src.core.domain.exceptions import UnauthorizedActionError, ValidationFailedError
from src.core.use_cases.auth_use_cases import AuthUseCases

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases)
):
    """Register a new user."""
    try:
        user_entity = await auth_use_cases.register_user(user_in)
        return user_entity
    except ValidationFailedError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    Swagger UI will use this endpoint.
    """
    try:
        user_login = UserLogin(email=form_data.username, password=form_data.password)
        token = await auth_use_cases.authenticate_user(user_login)
        return token
    except UnauthorizedActionError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserEntity = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return current_user
