from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    api_base_url: str = Field(default="http://localhost:3123")
    api_timeout: int = Field(default=30)
    api_max_retries: int = Field(default=5)
    api_retry_delay: float = Field(default=1.0)
    api_backoff_multiplier: float = Field(default=2.0)

    batch_size: int = Field(default=100)
    max_workers: int = Field(default=8)

    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
