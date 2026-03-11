"""
FoodScout AI — Application Configuration
Loads and validates all environment variables via pydantic-settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_host: str = Field(default="0.0.0.0", env="APP_HOST")
    app_port: int = Field(default=8000, env="APP_PORT")
    debug: bool = Field(default=False, env="DEBUG")
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000", env="CORS_ORIGINS"
    )

    # Database
    database_url: str = Field(
        default="postgresql://postgres:password@localhost:5432/foodscout",
        env="DATABASE_URL",
    )

    # Redis / Celery
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0", env="CELERY_BROKER_URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/1", env="CELERY_RESULT_BACKEND"
    )

    # API keys
    youtube_api_key: str = Field(default="", env="YOUTUBE_API_KEY")
    google_maps_api_key: str = Field(default="", env="GOOGLE_MAPS_API_KEY")
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_base_url: str = Field(
        default="https://api.groq.com/openai/v1", env="OPENAI_BASE_URL"
    )
    openai_model: str = Field(default="llama3-8b-8192", env="OPENAI_MODEL")

    # Google Sheets
    google_sheets_credentials_file: str = Field(
        default="credentials.json", env="GOOGLE_SHEETS_CREDENTIALS_FILE"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
