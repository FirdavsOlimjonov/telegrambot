from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Telegram ──────────────────────────────────────────────────────────────
    bot_token: str = Field(..., min_length=40)
    bot_webhook_url: str | None = None
    admin_ids: list[int] = Field(default_factory=list)

    # ── PostgreSQL (individual components) ───────────────────────────────────
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

    # ── File Upload ───────────────────────────────────────────────────────────
    max_file_size_mb: int = Field(default=10, ge=1, le=100)
    upload_dir: str = "uploads/"

    # ── Localization ──────────────────────────────────────────────────────────
    default_language: Literal["uz", "ru", "en"] = "uz"

    # ── Computed properties ───────────────────────────────────────────────────
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
        """Sync URL used by Alembic migrations only."""
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field  # type: ignore[misc]
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @model_validator(mode="after")
    def validate_admin_ids(self) -> "Settings":
        if not self.admin_ids:
            import warnings
            warnings.warn(
                "ADMIN_IDS is empty — no admin commands will be accessible.",
                stacklevel=2,
            )
        return self

    @model_validator(mode="before")
    @classmethod
    def parse_admin_ids(cls, values: dict) -> dict:
        """Allow ADMIN_IDS as comma-separated string in .env"""
        raw = values.get("admin_ids")
        if isinstance(raw, str):
            values["admin_ids"] = [
                int(x.strip()) for x in raw.split(",") if x.strip().isdigit()
            ]
        return values


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
