from __future__ import annotations

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.position_code import PositionCode
from app.repositories.base import BaseRepository
from app.schemas.position_code import PositionCodeFilter


class PositionCodeRepository(BaseRepository[PositionCode]):
    model = PositionCode

    async def get_by_direction_and_specialty(
        self, filters: PositionCodeFilter
    ) -> tuple[list[PositionCode], int]:
        """
        Returns (paginated_codes, total_count) for the given direction+specialty.
        """
        where = and_(
            PositionCode.direction_id == filters.direction_id,
            PositionCode.specialty_id == filters.specialty_id,
        )

        total: int = (
            await self.session.execute(
                select(func.count()).select_from(PositionCode).where(where)
            )
        ).scalar_one()

        offset = (filters.page - 1) * filters.page_size
        stmt = (
            select(PositionCode)
            .options(
                selectinload(PositionCode.direction),
                selectinload(PositionCode.specialty),
            )
            .where(where)
            .order_by(PositionCode.code)
            .offset(offset)
            .limit(filters.page_size)
        )
        rows = list((await self.session.execute(stmt)).scalars().all())
        return rows, total

    async def bulk_upsert(
        self,
        records: list[dict],
    ) -> tuple[int, int]:
        """
        Insert new (direction_id, specialty_id, code) combos; skip duplicates.
        Returns (inserted, skipped).
        """
        if not records:
            return 0, 0

        # Collect existing keys in one query
        keys = [(r["direction_id"], r["specialty_id"], r["code"]) for r in records]
        # Build OR conditions for the composite key
        from sqlalchemy import tuple_
        existing_stmt = select(
            PositionCode.direction_id,
            PositionCode.specialty_id,
            PositionCode.code,
        ).where(
            tuple_(
                PositionCode.direction_id,
                PositionCode.specialty_id,
                PositionCode.code,
            ).in_(keys)
        )
        existing_keys: set[tuple] = set(
            (await self.session.execute(existing_stmt)).all()
        )

        new_records = [
            r for r in records
            if (r["direction_id"], r["specialty_id"], r["code"]) not in existing_keys
        ]
        skipped = len(records) - len(new_records)

        if new_records:
            self.session.add_all([PositionCode(**r) for r in new_records])
            await self.session.flush()

        return len(new_records), skipped

    async def search_by_code(
        self, query: str, page: int = 1, page_size: int = 10
    ) -> tuple[list[PositionCode], int]:
        """
        Partial case-insensitive match on the code field.
        Returns results from all directions/specialties.
        """
        where = PositionCode.code.ilike(f"%{query}%")

        total: int = (
            await self.session.execute(
                select(func.count()).select_from(PositionCode).where(where)
            )
        ).scalar_one()

        offset = (page - 1) * page_size
        stmt = (
            select(PositionCode)
            .options(
                selectinload(PositionCode.direction),
                selectinload(PositionCode.specialty),
            )
            .where(where)
            .order_by(PositionCode.code)
            .offset(offset)
            .limit(page_size)
        )
        rows = list((await self.session.execute(stmt)).scalars().all())
        return rows, total

    async def stats_by_direction(self) -> list[dict]:
        stmt = (
            select(
                PositionCode.direction_id,
                func.count(PositionCode.id).label("count"),
            )
            .group_by(PositionCode.direction_id)
        )
        rows = (await self.session.execute(stmt)).all()
        return [{"direction_id": r.direction_id, "count": r.count} for r in rows]
