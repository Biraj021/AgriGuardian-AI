from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_alerts():
    return {
        "source": "demo",
        "is_live": False,
        "message": "Demo alert feed — configure DISASTER_ALERT_API_KEY for live alerts",
        "alerts": [
            {
                "id": "ALT-101",
                "title": "Heavy Rain & Flash Flood Alert",
                "severity": "high",
                "category": "Weather",
                "region": "Northern Agricultural Zone",
                "issued_at": "2026-08-20T10:30:00Z",
                "description": "Heavy rainfall exceeding 85mm expected over the next 24 hours. High risk of waterlogging in low-lying crop fields.",
                "recommendation": "Ensure drainage channels are clear. Postpone fertilizer application and delay irrigation cycles."
            },
            {
                "id": "ALT-102",
                "title": "Locust & Pest Outbreak Advisory",
                "severity": "medium",
                "category": "Pest Control",
                "region": "District 4 & Neighboring Belts",
                "issued_at": "2026-08-19T14:15:00Z",
                "description": "Increased swarming activity reported nearby. Risk of leaf damage on cotton and paddy fields.",
                "recommendation": "Inspect crop undersides daily. Prepare recommended biopesticides or neem-oil spray."
            },
            {
                "id": "ALT-103",
                "title": "Heatwave & High Evapotranspiration",
                "severity": "low",
                "category": "Temperature",
                "region": "Central Plains",
                "issued_at": "2026-08-18T09:00:00Z",
                "description": "Day temperatures projected to hit 39°C with low humidity.",
                "recommendation": "Schedule early morning drip irrigation to prevent crop wilting."
            }
        ],
    }
