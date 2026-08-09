from pydantic import BaseModel, Field
from uuid import UUID

class FarmCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    primary_crop: str | None = None
    location_lat: float | None = None
    location_lon: float | None = None

class FarmUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    primary_crop: str | None = None
    location_lat: float | None = None
    location_lon: float | None = None
    is_active: bool | None = None

class FarmResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    primary_crop: str | None = None
    location_lat: float | None = None
    location_lon: float | None = None
    is_active: bool
    created_at: str | None = None
    updated_at: str | None = None

    class Config:
        from_attributes = True
