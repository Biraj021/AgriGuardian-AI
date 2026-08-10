from pathlib import Path
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve absolute paths relative to backend directory
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_NAME: str = "AgriGuardian AI"
    APP_VERSION: str = "0.1.0"
    APP_PORT: int = 8000
    APP_SECRET_KEY: str
    
    DATABASE_URL: str
    
    # External APIs
    OPENWEATHER_API_KEY: str | None = None
    AGMARKET_API_KEY: str | None = None
    INDIA_GOV_API_KEY: str | None = None
    DISASTER_ALERT_API_KEY: str | None = None

    MQTT_BROKER_HOST: str | None = None
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: str | None = None
    MQTT_PASSWORD: str | None = None
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    AI_MODEL_PATH: str = str(BACKEND_DIR.parent / "ai" / "models")
    AI_PREDICTION_THRESHOLD: float = 0.75

    model_config = SettingsConfigDict(
        env_file=[
            str(BACKEND_DIR / ".env"),
            str(BACKEND_DIR.parent / ".env")
        ],
        extra="ignore"
    )

    @model_validator(mode="after")
    def resolve_sqlite_db_path(self) -> "Settings":
        if self.DATABASE_URL.startswith("sqlite"):
            # e.g., sqlite+aiosqlite:///./agri_guardian.db or sqlite:///./agri_guardian.db
            parts = self.DATABASE_URL.split(":///")
            if len(parts) == 2:
                db_path_str = parts[1]
                # If it's a relative path, resolve it relative to the backend directory
                db_path = Path(db_path_str)
                if not db_path.is_absolute():
                    resolved_path = (BACKEND_DIR / db_path).resolve()
                    self.DATABASE_URL = f"{parts[0]}:///{resolved_path.as_posix()}"
        return self

    @property
    def cors_origins(self) -> list[str]:
        """Return the explicitly configured browser origins."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()

