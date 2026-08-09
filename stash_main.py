from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .v1.routers import auth

app = FastAPI(title="AgriGuardian AI", version="0.1.0")

# Enable CORS for all origins (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
