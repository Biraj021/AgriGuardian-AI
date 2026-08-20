from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1.routers import (
    alerts,
    analytics,
    auth,
    dashboard,
    device,
    farm,
    health,
    market,
    recommendation,
    sensor,
    weather,
)
from src.infrastructure.external_apis.mqtt_bridge import MqttTelemetrySubscriber
from src.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    subscriber = MqttTelemetrySubscriber()
    app.state.mqtt_subscriber_started = subscriber.start()
    try:
        yield
    finally:
        subscriber.stop()


app = FastAPI(title="AgriGuardian AI", version="0.1.0", lifespan=lifespan)

# Enable CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register routers
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(farm.router, prefix="/api/v1/farm", tags=["farm"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(recommendation.router, prefix="/api/v1/recommendation", tags=["recommendation"])
app.include_router(weather.router, prefix="/api/v1/weather", tags=["weather"])
app.include_router(market.router, prefix="/api/v1/market", tags=["market"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(sensor.router, prefix="/api/v1/sensor", tags=["sensor"])
app.include_router(device.router, prefix="/api/v1/device", tags=["device"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

@app.get("/health")
def root_health():
    return {"status": "ok", "app": "AgriGuardian AI"}

