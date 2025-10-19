import os
from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database settings
    DATABASE_URL: str

    # Local dev docker-compose services - optional in production
    POSTGRES_HOST: str | None = None
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None
    PGADMIN_DEFAULT_EMAIL: str | None = None
    PGADMIN_DEFAULT_PASSWORD: str | None = None

    # Cache - optional (add when needed)
    REDIS_URL: str | None = None

    # Blob Storage - optional (add when needed)
    MINIO_ENDPOINT: str | None = None
    MINIO_ACCESS_KEY: str | None = None
    MINIO_SECRET_KEY: str | None = None
    MINIO_ROOT_USER: str | None = None
    MINIO_ROOT_PASSWORD: str | None = None

    # Application
    APP_NAME: str
    DEBUG: bool
    VERSION: str

    # CORS
    CORS_ORIGINS: list[str]
    CORS_ALLOW_CREDENTIALS: bool
    CORS_ALLOW_METHODS: list[str]
    CORS_ALLOW_HEADERS: list[str]

    # Allowed hosts
    ALLOWED_HOSTS: list[str] = Field(
        default=[
            "localhost",
            "127.0.0.1",
            "productivity-tracker-backend-jp1k.onrender.com",
            "*.onrender.com",
        ],
        description="Allowed hosts for TrustedHostMiddleware",
        validation_alias=AliasChoices("ALLOWED_HOSTS", "allowed_hosts"),
    )

    # Security & Authentication
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # Cookie settings
    COOKIE_NAME: str
    COOKIE_SECURE: bool
    COOKIE_HTTPONLY: bool
    COOKIE_SAMESITE: Literal["lax", "strict", "none"]
    COOKIE_MAX_AGE: int

    model_config = SettingsConfigDict(
        env_file=".env.test" if os.getenv("TESTING") else ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    ENVIRONMENT: str = Field(
        default="development",
        description="Application environment (development, testing, staging, production)",
    )

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.ENVIRONMENT.lower() == "testing"


settings = Settings()  # type: ignore[call-arg]
