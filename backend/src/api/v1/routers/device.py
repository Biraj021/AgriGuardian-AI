from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_devices():
    return {"source": "demo", "devices": [{"id": "dev-1", "status": "online"}]}
