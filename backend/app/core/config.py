"""Application configuration."""

import os

from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    DATABASE_URL: str = "sqlite:///./data/app.db"
    APP_ENV: str = "development"
    TZ: str = "UTC"
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Calendar Backend"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Backend API for AI Calendar Application"

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://frontend:5173",
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        """Parse CORS origins."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list | str):
            return v
        raise ValueError(v)

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = True


settings = Settings()


def get_database_url() -> str:
    """Get database URL with proper path resolution."""
    if settings.DATABASE_URL.startswith("sqlite:///"):
        # Make sure the data directory exists
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return settings.DATABASE_URL
