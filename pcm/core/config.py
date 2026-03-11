from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = "PCM"
    app_env: str = "development"
    app_debug: bool = True
    app_version: str = "1.0.0"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4

    # Database
    database_url: str = "postgresql+asyncpg://postgres:2020Tra@localhost:5432/pcmdata"
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_db: int = 1
    redis_celery_db: int = 2

    # Security
    secret_key: str = "change-this-to-a-secure-random-key"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    cors_credentials: bool = True

    # Proxmox
    proxmox_verify_ssl: bool = False
    proxmox_timeout: int = 30

    # Observability
    otel_enabled: bool = True
    otel_endpoint: str = "http://localhost:4317"
    prometheus_port: int = 9090

    # Celery
    celery_broker_url: str = "redis://localhost:6379/2"
    celery_result_backend: str = "redis://localhost:6379/3"

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"


settings = Settings()
