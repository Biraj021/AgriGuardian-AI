from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1.routers import auth, farm, recommendation, health, weather, market, alerts, dashboard

app = FastAPI(title="AgriGuardian AI", version="0.1.0")

# Enable CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
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

@app.get("/health")
def root_health():
    return {"status": "ok", "app": "AgriGuardian AI"}

