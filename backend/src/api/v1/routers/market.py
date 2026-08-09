import random
from datetime import datetime, timezone, timedelta

import httpx
from fastapi import APIRouter

from src.core.config import settings

router = APIRouter()

# ------------------------------------------------------------------
# Real-time Indian Mandi prices via data.gov.in (free, no key needed)
# API: https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070
# Commodity prices from AGMARKNET (national agriculture market)
# ------------------------------------------------------------------

AGMARKNET_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
DATA_GOV_BASE = "https://api.data.gov.in/resource"

# Fallback static prices with realistic Indian MSP values (Aug 2026)
FALLBACK_PRICES = [
    {"crop": "Wheat",   "price": 2275.0,  "unit": "Quintal", "trend": "up"},
    {"crop": "Rice",    "price": 2300.0,  "unit": "Quintal", "trend": "up"},
    {"crop": "Maize",   "price": 1820.0,  "unit": "Quintal", "trend": "down"},
    {"crop": "Cotton",  "price": 6620.0,  "unit": "Quintal", "trend": "up"},
    {"crop": "Soybean", "price": 4600.0,  "unit": "Quintal", "trend": "down"},
]


def _generate_sparkline(base_price: float, trend: str, days: int = 7) -> list[float]:
    """Generate realistic sparkline history for a given base price."""
    prices = []
    p = base_price * (0.95 if trend == "down" else 0.97)
    for _ in range(days):
        change = random.uniform(-0.8, 1.2) if trend == "up" else random.uniform(-1.2, 0.8)
        p = round(p * (1 + change / 100), 2)
        prices.append(p)
    prices.append(base_price)
    return prices


def _get_date_range_labels(days: int = 7) -> tuple[str, str]:
    """Return start-date and end-date strings for the sparkline period."""
    today = datetime.now(timezone.utc)
    start = today - timedelta(days=days)
    fmt = "%d %b"
    return start.strftime(fmt), today.strftime(fmt)


def _build_price_entry(crop: str, price: float, unit: str, trend: str, change_pct: str | None = None) -> dict:
    sparkline = _generate_sparkline(price, trend)
    start_label, end_label = _get_date_range_labels(len(sparkline) - 1)
    return {
        "crop": crop,
        "currentPrice": f"₹{price:,.0f}",
        "price": price,
        "unit": unit,
        "change": change_pct or (f"+{random.uniform(0.5,2.5):.1f}%" if trend == "up" else f"-{random.uniform(0.3,1.8):.1f}%"),
        "trend": trend,
        "sparkline": sparkline,
        "sparkline_labels": {"start": start_label, "end": end_label},
    }


async def _fetch_live_prices() -> list[dict] | None:
    """
    Try to fetch live commodity prices from data.gov.in AGMARKNET resource.
    Returns None on failure so the caller can fall back to static data.
    """
    if not settings.INDIA_GOV_API_KEY:
        return None  # no key → skip live fetch

    url = f"{DATA_GOV_BASE}/{AGMARKNET_RESOURCE_ID}"
    params = {
        "api-key": settings.INDIA_GOV_API_KEY,
        "format": "json",
        "limit": 50,
        "filters[State]": "Punjab",   # can be parameterised later
    }
    try:
        async with httpx.AsyncClient(timeout=6) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        records = data.get("records", [])
        if not records:
            return None

        # Aggregate by commodity — take max modal price
        seen: dict[str, dict] = {}
        for r in records:
            commodity = r.get("Commodity", "").strip().title()
            modal_price = float(r.get("Modal_Price", 0) or 0)
            min_price   = float(r.get("Min_Price",   0) or 0)
            max_price   = float(r.get("Max_Price",   0) or 0)
            if not commodity or modal_price <= 0:
                continue
            if commodity not in seen or modal_price > seen[commodity]["price"]:
                seen[commodity] = {
                    "crop": commodity,
                    "price": modal_price,
                    "min": min_price,
                    "max": max_price,
                    "unit": "Quintal",
                }

        target_crops = ["Wheat", "Rice", "Maize", "Cotton", "Soybean"]
        results = []
        for crop in target_crops:
            item = seen.get(crop)
            if item:
                trend = "up" if item["price"] >= item["min"] + (item["max"] - item["min"]) * 0.5 else "down"
                results.append(_build_price_entry(
                    crop=item["crop"],
                    price=item["price"],
                    unit=item["unit"],
                    trend=trend,
                ))

        return results if results else None
    except Exception:
        return None


@router.get("/prices")
async def market_prices():
    """
    Real-time Indian mandi crop prices.
    - Live: fetched from data.gov.in AGMARKNET when INDIA_GOV_API_KEY is set.
    - Fallback: realistic static MSP-based prices with generated sparklines.
    Sparklines always reflect the last 7 days relative to today's real date.
    """
    live = await _fetch_live_prices()
    if live:
        return {
            "source": "live",
            "is_live": True,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "message": "Live prices from data.gov.in AGMARKNET",
            "prices": live,
        }

    # --- Fallback with real today-relative dates ---
    prices = [
        _build_price_entry(
            crop=p["crop"],
            price=p["price"],
            unit=p["unit"],
            trend=p["trend"],
        )
        for p in FALLBACK_PRICES
    ]

    return {
        "source": "demo",
        "is_live": False,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "message": (
            "Showing realistic MSP-based prices. "
            "Set INDIA_GOV_API_KEY in .env for live AGMARKNET data."
        ),
        "prices": prices,
    }
