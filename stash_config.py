from pydantic_settings import BaseSettings, SettingsConfigDict

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

    AI_MODEL_PATH: str = "ai/models"
    AI_PREDICTION_THRESHOLD: float = 0.75

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
