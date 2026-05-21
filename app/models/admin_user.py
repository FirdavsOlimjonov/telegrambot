from __future__ import annotations

from typing import Literal

from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, SoftDeleteMixin


AdminRole = Literal["superadmin", "admin", "moderator"]


class AdminUser(Base, TimestampMixin, SoftDeleteMixin):
    """
    Persists admin identities separately from the config ADMIN_IDS list.
    This enables role-based access control and audit trails.
    ADMIN_IDS in .env grants initial bootstrap access only.
    """

    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, index=True
    )
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    role: Mapped[AdminRole] = mapped_column(
        String(20), default="admin", nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Track last activity for audit
    last_seen_at: Mapped[str | None] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        return f"<AdminUser tg_id={self.telegram_id} role={self.role!r}>"
