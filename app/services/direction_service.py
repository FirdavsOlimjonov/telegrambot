from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.direction import DirectionRepository, SpecialtyRepository
from app.schemas.direction import DirectionRead, SpecialtyRead


class DirectionService:
    def __init__(self, session: AsyncSession) -> None:
        self._dir_repo = DirectionRepository(session)
        self._spec_repo = SpecialtyRepository(session)

    async def list_active_directions(self) -> list[DirectionRead]:
        directions = await self._dir_repo.get_active()
        return [DirectionRead.model_validate(d) for d in directions]

    async def list_specialties(self, direction_id: int) -> list[SpecialtyRead]:
        specialties = await self._spec_repo.get_by_direction(direction_id)
        return [SpecialtyRead.model_validate(s) for s in specialties]

    async def get_direction(self, direction_id: int) -> DirectionRead | None:
        d = await self._dir_repo.get_by_id(direction_id)
        return DirectionRead.model_validate(d) if d else None

    async def get_specialty(self, specialty_id: int) -> SpecialtyRead | None:
        s = await self._spec_repo.get_by_id(specialty_id)
        return SpecialtyRead.model_validate(s) if s else None
