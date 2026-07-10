"""
Application configuration using pydantic-settings.

All configuration values must come from this module.
Never call os.getenv() outside of this file.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central settings class.

    Values are read (in priority order) from:
      1. Environment variables
      2. .env file
      3. Field defaults below

    Usage in FastAPI routes:
        from app.core.config import get_settings
        settings: Settings = Depends(get_settings)

    Usage outside FastAPI DI:
        from app.core.config import get_settings
        settings = get_settings()
    """

    # ── Application ───────────────────────────────────────────────────────────
    APP_NAME: str = "Elevator Configuration Engine"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"  # development | staging | production
    DEBUG: bool = True

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"
    LOG_MAX_BYTES: int = 10_485_760  # 10 MB per file
    LOG_BACKUP_COUNT: int = 5

    # ── API ───────────────────────────────────────────────────────────────────
    API_V1_PREFIX: str = "/api/v1"

    # ── CORS ──────────────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # ── Data ──────────────────────────────────────────────────────────────────
    DATA_DIR: str = "app/data"

    # ── Database (SQLite via SQLAlchemy async) ────────────────────────────────
    # Override in .env:  SQLITE_DATABASE_URL=sqlite+aiosqlite:///./my.db
    SQLITE_DATABASE_URL: str = "sqlite+aiosqlite:///./elevator_config.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def data_dir_path(self) -> Path:
        """Resolved Path object for the data directory."""
        return Path(self.DATA_DIR)

    @property
    def is_production(self) -> bool:
        """True when running in the production environment."""
        return self.ENVIRONMENT == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return a cached singleton Settings instance.

    The lru_cache ensures settings are loaded only once.
    Call get_settings.cache_clear() in tests to reset between runs.
    """
    return Settings()
