from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.position_code import PositionCodeRepository
from app.schemas.position_code import PositionCodeFilter, PositionCodeRead
from app.core.logger import logger


class CodeService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = PositionCodeRepository(session)

    async def find_codes(
        self, filters: PositionCodeFilter
    ) -> tuple[list[PositionCodeRead], int, int]:
        """
        Returns (codes, total_count, total_pages).
        """
        codes, total = await self._repo.get_by_direction_and_specialty(filters)
        total_pages = max(1, -(-total // filters.page_size))

        results = []
        for c in codes:
            dto = PositionCodeRead.model_validate(c)
            if c.direction:
                dto.direction_name = c.direction.name_uz
            if c.specialty:
                dto.specialty_name = c.specialty.name_uz
            results.append(dto)

        logger.debug(
            f"Found {len(results)}/{total} codes for "
            f"direction={filters.direction_id} specialty={filters.specialty_id}"
        )
        return results, total, total_pages

    async def search_by_code(
        self, query: str, page: int = 1, page_size: int = 10
    ) -> tuple[list[PositionCodeRead], int, int]:
        """
        Free-text search on the code field (partial match).
        Returns (results, total_count, total_pages).
        """
        codes, total = await self._repo.search_by_code(
            query.strip(), page=page, page_size=page_size
        )
        total_pages = max(1, -(-total // page_size))

        results = []
        for c in codes:
            dto = PositionCodeRead.model_validate(c)
            if c.direction:
                dto.direction_name = c.direction.name_uz
            if c.specialty:
                dto.specialty_name = c.specialty.name_uz
            results.append(dto)

        logger.debug(f"Code search '{query}': {len(results)}/{total} results")
        return results, total, total_pages

    async def get_statistics(self) -> dict:
        by_dir = await self._repo.stats_by_direction()
        total = await self._repo.count()
        return {"total_codes": total, "by_direction": by_dir}
