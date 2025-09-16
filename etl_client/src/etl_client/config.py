"""Configuration management for the Animal ETL client."""
import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_base_url: str = Field(default="http://localhost:3123", env="API_BASE_URL")
    api_timeout: int = Field(default=30, env="API_TIMEOUT")
    api_max_retries: int = Field(default=5, env="API_MAX_RETRIES")
    api_retry_delay: float = Field(default=1.0, env="API_RETRY_DELAY")
    api_backoff_multiplier: float = Field(default=2.0, env="API_BACKOFF_MULTIPLIER")

    # Processing Configuration
    batch_size: int = Field(default=100, env="BATCH_SIZE")
    max_workers: int = Field(default=4, env="MAX_WORKERS")

    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
