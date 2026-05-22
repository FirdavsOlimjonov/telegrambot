from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class BotUser(Base, TimestampMixin):
    """Tracks every Telegram user who has interacted with the bot."""

    __tablename__ = "bot_users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, index=True
    )
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    search_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_active_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    def __repr__(self) -> str:
        return f"<BotUser tg_id={self.telegram_id} name={self.full_name!r}>"
