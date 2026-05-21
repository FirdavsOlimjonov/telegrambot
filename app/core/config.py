from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    # ── Telegram ──────────────────────────────────────────────────────────────
    bot_token: str = Field(..., min_length=40)
    bot_webhook_url: str | None = None

    # Stored as plain string to avoid pydantic-settings JSON-parsing it.
    # Use settings.admin_ids to get list[int].
    admin_ids_raw: str = Field(default="", alias="admin_ids")

    # ── PostgreSQL ────────────────────────────────────────────────────────────
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "mehnat_bot"
    postgres_user: str = "mehnat_user"
    postgres_password: str = "password"

    # ── App ───────────────────────────────────────────────────────────────────
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "DEBUG"

    # ── Pagination ────────────────────────────────────────────────────────────
    page_size: int = Field(default=5, ge=1, le=50)

    # ── Localization ──────────────────────────────────────────────────────────
    default_language: Literal["uz", "ru", "en"] = "uz"

    # ── Computed properties ───────────────────────────────────────────────────
    @computed_field  # type: ignore[misc]
    @property
    def admin_ids(self) -> list[int]:
        """Parses ADMIN_IDS=123456789,987654321 from .env into a list."""
        return [
            int(x.strip())
            for x in self.admin_ids_raw.split(",")
            if x.strip().isdigit()
        ]

    @computed_field  # type: ignore[misc]
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field  # type: ignore[misc]
    @property
    def database_url_sync(self) -> str:
        """Sync URL used by Alembic only."""
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field  # type: ignore[misc]
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
