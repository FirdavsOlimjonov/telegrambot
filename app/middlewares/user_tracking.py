from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from app.repositories.bot_user import BotUserRepository


class UserTrackingMiddleware(BaseMiddleware):
    """
    Registers new users on first contact and updates last_active_at on every message.
    Runs after DatabaseMiddleware so session is already in data.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = getattr(event, "from_user", None)
        session = data.get("session")

        if user and session and not user.is_bot:
            repo = BotUserRepository(session)
            await repo.upsert(
                telegram_id=user.id,
                username=user.username,
                full_name=user.full_name,
            )

        return await handler(event, data)
