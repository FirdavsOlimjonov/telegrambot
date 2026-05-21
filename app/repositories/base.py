from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """
    Generic async repository providing standard CRUD operations.
    Subclass and set `model` to use. All methods are type-safe.
    """

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, pk: int) -> ModelT | None:
        return await self.session.get(self.model, pk)

    async def get_all(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        order_by=None,
    ) -> list[ModelT]:
        stmt = select(self.model)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()

    async def create(self, **kwargs: Any) -> ModelT:
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()  # Get ID without full commit
        await self.session.refresh(obj)
        return obj

    async def update_by_id(self, pk: int, **kwargs: Any) -> ModelT | None:
        stmt = (
            update(self.model)
            .where(self.model.id == pk)  # type: ignore[attr-defined]
            .values(**kwargs)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_by_id(self, pk: int) -> bool:
        stmt = delete(self.model).where(
            self.model.id == pk  # type: ignore[attr-defined]
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def exists(self, **kwargs: Any) -> bool:
        stmt = select(func.count()).select_from(self.model)
        for key, value in kwargs.items():
            stmt = stmt.where(
                getattr(self.model, key) == value
            )
        result = await self.session.execute(stmt)
        return (result.scalar_one() or 0) > 0
