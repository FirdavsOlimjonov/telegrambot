from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.direction import Direction
    from app.models.speciality import Specialty


class PositionCode(Base, TimestampMixin):
    """
    The result the user receives.
    Unique on (direction_id, specialty_id, code).

    Example:
        direction = 'Umumiy qurilish'  (General Construction)
        specialty = 'Bosh muhandis'    (Chief Engineer)
        code      = 'BM-001'
    """

    __tablename__ = "position_codes"

    __table_args__ = (
        UniqueConstraint("direction_id", "specialty_id", "code", name="uq_code_per_specialty"),
        Index("ix_position_code_lookup", "direction_id", "specialty_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    direction_id: Mapped[int] = mapped_column(
        ForeignKey("directions.id", ondelete="RESTRICT"), nullable=False
    )
    specialty_id: Mapped[int] = mapped_column(
        ForeignKey("specialties.id", ondelete="RESTRICT"), nullable=False
    )

    name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    direction: Mapped["Direction"] = relationship(back_populates="codes", lazy="selectin")
    specialty: Mapped["Specialty"] = relationship(back_populates="codes", lazy="selectin")

    def __repr__(self) -> str:
        return f"<PositionCode id={self.id} code={self.code!r}>"
