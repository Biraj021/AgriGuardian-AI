import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db_session
from src.core.domain.entities import UserEntity
from src.infrastructure.database.models import AuditLog, Device, Farm
from src.infrastructure.external_apis.mqtt_bridge import PumpCommand, publish_pump_command

router = APIRouter()


class DeviceControlPayload(BaseModel):
    command: str
    duration_seconds: int | None = Field(default=None, ge=1, le=300)


@router.get("/")
async def list_devices(
    db: AsyncSession = Depends(get_db_session),
    current_user: UserEntity = Depends(get_current_user),
):
    result = await db.execute(
        select(Device, Farm)
        .join(Farm, Device.farm_id == Farm.id)
        .where(Farm.user_id == current_user.id, Farm.is_active == True)
        .order_by(Device.created_at.desc())
    )
    rows = result.all()
    return {"source": "database", "devices": [
        {"id": str(device.id), "farm_id": str(farm.id), "mac_address": device.mac_address,
         "status": device.status, "is_active": device.is_active,
         "last_seen_at": device.last_seen_at.isoformat() if device.last_seen_at else None}
        for device, farm in rows
    ]}


@router.post("/{device_id}/control", status_code=status.HTTP_202_ACCEPTED)
async def control_device(
    device_id: str,
    payload: DeviceControlPayload,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserEntity = Depends(get_current_user),
):
    """Queue a safe pump command for a device owned by the current user."""
    if payload.command not in {"PUMP_ON", "PUMP_OFF"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unsupported command")
    if payload.command == "PUMP_ON" and payload.duration_seconds is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="PUMP_ON requires duration_seconds")
    try:
        device_uuid = uuid.UUID(device_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found for current user")
    result = await db.execute(
        select(Device).join(Farm, Device.farm_id == Farm.id).where(Device.id == device_uuid, Farm.user_id == current_user.id)
    )
    device = result.scalars().first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found for current user")
    try:
        publish_pump_command(PumpCommand(device.mac_address, payload.command, payload.duration_seconds))
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    db.add(AuditLog(
        user_id=current_user.id,
        action="device_control_published",
        entity_type="device",
        entity_id=device.id,
        details={"command": payload.command, "duration_seconds": payload.duration_seconds},
    ))
    await db.commit()
    return {"status": "published", "device_id": str(device.id), "command": payload.command}
