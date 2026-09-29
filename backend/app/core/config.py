"""
Application configuration via environment variables.

Uses pydantic-settings to load and validate all config from .env / environment.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration â€” all values read from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # â”€â”€ Application â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    APP_NAME: str = "UnifiedRx"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # â”€â”€ Database â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    DATABASE_URL: str

    # â”€â”€ Authentication â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # â”€â”€ Admin seed â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    ADMIN_EMAIL: str = "admin@unifiedrx.com"
    ADMIN_PASSWORD: str = "Admin1234"
    ADMIN_FULL_NAME: str = "System Administrator"

    # ── Clinical Intelligence ─────────────────────────────────────────────────
    # Days window for temporal association engine (14–90, per project brief default: 14)
    TEMPORAL_ASSOCIATION_WINDOW_DAYS: int = 14

    # Set False in environments where torch/EasyOCR DLLs are blocked by OS policy.
    # Tests always monkeypatch extract_text_from_file directly, so this is for live runs only.
    ENABLE_REAL_OCR_MODELS: bool = True


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance (read once, reuse everywhere)."""
    return Settings()
