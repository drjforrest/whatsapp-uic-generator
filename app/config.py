"""
Application configuration management using Pydantic Settings.
Loads configuration from environment variables with validation.
"""
from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable loading."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application Settings
    app_name: str = "WhatsApp UIC Generator"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # Security
    uic_salt: str = Field(
        ...,
        description="Secret salt for UIC hashing. Must be kept secure.",
        min_length=16
    )

    # Database
    database_url: str = Field(
        default="sqlite:///./uic_database.db",
        description="SQLAlchemy database URL"
    )

    # Twilio Configuration
    twilio_account_sid: str = Field(
        ...,
        description="Twilio Account SID from console"
    )
    twilio_auth_token: str = Field(
        ...,
        description="Twilio Auth Token from console"
    )
    twilio_whatsapp_number: str = Field(
        default="whatsapp:+14155238886",
        description="Twilio WhatsApp sandbox number"
    )

    # Webhook Configuration
    webhook_path: str = Field(
        default="/whatsapp/webhook",
        description="Path for Twilio webhook"
    )

    # Session Management
    session_timeout_minutes: int = Field(
        default=15,
        ge=1,
        le=60,
        description="Minutes before user session expires"
    )

    # QR Code Feature
    enable_qr_code: bool = Field(
        default=False,
        description="Enable QR code generation and delivery via WhatsApp"
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_json: bool = False

    @field_validator("uic_salt")
    @classmethod
    def validate_salt_complexity(cls, v: str) -> str:
        """Ensure UIC salt meets minimum security requirements."""
        if len(v) < 16:
            raise ValueError("UIC salt must be at least 16 characters long")
        if v.isalpha() or v.isdigit():
            raise ValueError("UIC salt should contain mixed character types")
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def sqlalchemy_database_url(self) -> str:
        """Get SQLAlchemy-compatible database URL."""
        return self.database_url


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure settings are loaded only once.
    """
    return Settings()


# Convenience export
settings = get_settings()
