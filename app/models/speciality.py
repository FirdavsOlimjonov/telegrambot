from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.direction import Direction
    from app.models.position_code import PositionCode


class Specialty(Base, TimestampMixin, SoftDeleteMixin):
    """
    Second-level classification under a Direction.
    Example: Direction='General Construction' → Specialty='Chief Engineer'.
    """

    __tablename__ = "specialties"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    direction_id: Mapped[int] = mapped_column(
        ForeignKey("directions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name_uz: Mapped[str] = mapped_column(String(200), nullable=False)
    name_ru: Mapped[str] = mapped_column(String(200), nullable=False)
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)

    direction: Mapped["Direction"] = relationship(back_populates="specialties")
    codes: Mapped[list["PositionCode"]] = relationship(
        back_populates="specialty", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Specialty id={self.id} slug={self.slug!r}>"
