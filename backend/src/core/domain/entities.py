import uuid
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class FarmEntity:
    """Pure domain entity representing a Farm, decoupled from SQLAlchemy."""
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    is_active: bool = True
    location_lat: float | None = None
    location_lon: float | None = None
    primary_crop: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def deactivate(self):
        self.is_active = False

@dataclass
class UserEntity:
    id: uuid.UUID
    email: str
    role: str
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
