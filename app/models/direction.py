from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.specialty import Specialty
    from app.models.position_code import PositionCode


class Direction(Base, TimestampMixin, SoftDeleteMixin):
    """
    Top-level classification. Example: 'Umumiy qurilish' (General Construction).
    """

    __tablename__ = "directions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_uz: Mapped[str] = mapped_column(Text, nullable=False)
    name_ru: Mapped[str] = mapped_column(Text, nullable=False)
    name_en: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon_emoji: Mapped[str | None] = mapped_column(String(10), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)

    specialties: Mapped[list["Specialty"]] = relationship(
        back_populates="direction", lazy="selectin"
    )
    codes: Mapped[list["PositionCode"]] = relationship(
        back_populates="direction", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Direction id={self.id} slug={self.slug!r}>"
