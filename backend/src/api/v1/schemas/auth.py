from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str

class TokenPayload(BaseModel):
    sub: str | None = None
    role: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "farmer"

import uuid

class UserResponse(BaseModel):
    id: uuid.UUID | str
    email: EmailStr
    role: str
    is_active: bool

    class Config:
        from_attributes = True
