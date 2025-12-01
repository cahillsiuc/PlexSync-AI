"""
PlexSync AI - Configuration Management
Clean, type-safe configuration using Pydantic Settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = "PlexSync AI"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True

    # Security
    secret_key: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440

    # Database
    database_url: str
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_pool_timeout: int = 30

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 3600

    # Plex ERP
    plex_api_url: str
    plex_api_key: str
    plex_timeout: int = 30
    plex_retry_attempts: int = 3
    plex_po_endpoint: str = "/purchase-orders"
    plex_invoice_endpoint: str = "/ap-invoices"
    plex_vendor_endpoint: str = "/vendors"

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4-vision-preview"
    openai_max_tokens: int = 2000
    openai_temperature: float = 0.1

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # File Storage
    storage_type: str = "local"
    storage_path: str = "./storage/invoices"
    max_file_size_mb: int = 16
    allowed_file_types: List[str] = ["pdf", "png", "jpg", "jpeg", "tiff"]

    # Processing
    high_confidence_threshold: float = 90.0
    auto_approve_threshold: float = 95.0
    low_confidence_threshold: float = 70.0
    max_concurrent_jobs: int = 5
    ai_retry_attempts: int = 2
    ai_timeout_seconds: int = 60

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/plexsync.log"
    log_max_bytes: int = 10485760
    log_backup_count: int = 5

    # Sentry
    sentry_enabled: bool = False
    sentry_dsn: Optional[str] = None

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000

    # Feature Flags
    feature_email_integration: bool = True
    feature_auto_approval: bool = False
    feature_bulk_upload: bool = True
    feature_analytics: bool = True
    feature_api_access: bool = True

    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4

    # Docs
    docs_enabled: bool = True
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
