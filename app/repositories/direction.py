from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.direction import Direction
from app.models.speciality import Specialty
from app.repositories.base import BaseRepository


class DirectionRepository(BaseRepository[Direction]):
    model = Direction

    async def get_active(self) -> list[Direction]:
        stmt = (
            select(Direction)
            .where(Direction.is_active.is_(True), Direction.deleted_at.is_(None))
            .order_by(Direction.sort_order, Direction.name_uz)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_by_slug(self, slug: str) -> Direction | None:
        stmt = select(Direction).where(Direction.slug == slug)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def find_by_name(self, name: str) -> Direction | None:
        """Case-insensitive lookup across all language columns."""
        from sqlalchemy import func, or_
        name_lower = name.strip().lower()
        stmt = (
            select(Direction)
            .where(
                or_(
                    func.lower(Direction.name_uz) == name_lower,
                    func.lower(Direction.name_ru) == name_lower,
                    func.lower(Direction.name_en) == name_lower,
                    func.lower(Direction.slug) == name_lower.replace(" ", "-"),
                )
            )
            .limit(1)
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()


class SpecialtyRepository(BaseRepository[Specialty]):
    model = Specialty

    async def get_by_direction(self, direction_id: int) -> list[Specialty]:
        stmt = (
            select(Specialty)
            .where(
                Specialty.direction_id == direction_id,
                Specialty.is_active.is_(True),
                Specialty.deleted_at.is_(None),
            )
            .order_by(Specialty.sort_order, Specialty.name_uz)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_by_slug(self, slug: str) -> Specialty | None:
        stmt = select(Specialty).where(Specialty.slug == slug)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def find_by_name(self, name: str, direction_id: int | None = None) -> Specialty | None:
        from sqlalchemy import func, or_, and_
        name_lower = name.strip().lower()
        conditions = [
            Specialty.deleted_at.is_(None),
            or_(
                func.lower(Specialty.name_uz) == name_lower,
                func.lower(Specialty.name_ru) == name_lower,
                func.lower(Specialty.name_en) == name_lower,
            ),
        ]
        if direction_id is not None:
            conditions.append(Specialty.direction_id == direction_id)
        stmt = select(Specialty).where(and_(*conditions)).limit(1)
        return (await self.session.execute(stmt)).scalar_one_or_none()
