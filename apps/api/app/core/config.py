from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    log_level: str = "INFO"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    api_rate_limit_per_minute: int = 120

    database_url: str = "******localhost:5432/stockmind"
    redis_url: str = "redis://localhost:6379/0"

    twelve_data_api_key: str | None = None


settings = Settings()
