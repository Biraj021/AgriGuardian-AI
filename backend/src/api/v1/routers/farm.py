from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db_session
from src.core.domain.entities import UserEntity
from src.infrastructure.database.models import Farm

router = APIRouter()

@router.get("/")
async def list_farms(
    db: AsyncSession = Depends(get_db_session),
    current_user: UserEntity = Depends(get_current_user)
):
    """
    Get all active farms for the authenticated user.
    """
    result = await db.execute(select(Farm).where(Farm.user_id == current_user.id, Farm.is_active == True))
    farms = result.scalars().all()
    return {
        "status": "success",
        "farms": [
            {
                "id": str(f.id),
                "name": f.name,
                "location_lat": f.location_lat,
                "location_lon": f.location_lon,
                "primary_crop": f.primary_crop,
                "is_active": f.is_active
            }
            for f in farms
        ]
    }

