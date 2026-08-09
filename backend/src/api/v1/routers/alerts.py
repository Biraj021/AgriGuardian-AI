from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_alerts():
    return {
        "source": "demo",
        "is_live": False,
        "message": "Demo alert feed — configure DISASTER_ALERT_API_KEY for live alerts",
        "alerts": [],
    }
