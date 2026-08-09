from fastapi import APIRouter

router = APIRouter()


@router.get("/overview")
def analytics_overview():
    return {"source": "demo", "analytics": {"uptime_hours": 12}}
