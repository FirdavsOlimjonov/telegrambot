from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bot_user import BotUser
from app.repositories.base import BaseRepository


class BotUserRepository(BaseRepository[BotUser]):
    model = BotUser

    async def get_by_telegram_id(self, telegram_id: int) -> BotUser | None:
        stmt = select(BotUser).where(BotUser.telegram_id == telegram_id)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def upsert(
        self,
        telegram_id: int,
        username: str | None,
        full_name: str | None,
    ) -> BotUser:
        """Create user on first visit, update name/activity on subsequent visits."""
        now = datetime.now(timezone.utc)
        user = await self.get_by_telegram_id(telegram_id)

        if user is None:
            user = BotUser(
                telegram_id=telegram_id,
                username=username,
                full_name=full_name,
                last_active_at=now,
            )
            self.session.add(user)
        else:
            user.username = username
            user.full_name = full_name
            user.last_active_at = now

        await self.session.flush()
        return user

    async def increment_search(self, telegram_id: int) -> None:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            user.search_count += 1
            await self.session.flush()

    async def get_stats(self) -> dict:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)

        total = (
            await self.session.execute(select(func.count()).select_from(BotUser))
        ).scalar_one()

        new_today = (
            await self.session.execute(
                select(func.count()).select_from(BotUser)
                .where(BotUser.created_at >= today_start)
            )
        ).scalar_one()

        active_today = (
            await self.session.execute(
                select(func.count()).select_from(BotUser)
                .where(BotUser.last_active_at >= today_start)
            )
        ).scalar_one()

        active_week = (
            await self.session.execute(
                select(func.count()).select_from(BotUser)
                .where(BotUser.last_active_at >= week_ago)
            )
        ).scalar_one()

        total_searches = (
            await self.session.execute(
                select(func.sum(BotUser.search_count)).select_from(BotUser)
            )
        ).scalar_one() or 0

        return {
            "total": total,
            "new_today": new_today,
            "active_today": active_today,
            "active_week": active_week,
            "total_searches": total_searches,
        }
