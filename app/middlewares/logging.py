from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from app.core.logger import logger


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = getattr(event, "from_user", None)
        user_info = f"user_id={user.id}" if user else "unknown"

        if isinstance(event, Message):
            logger.debug(
                f"[MSG] {user_info} text={event.text!r} "
                f"chat={event.chat.id}"
            )

        try:
            return await handler(event, data)
        except Exception as exc:
            logger.error(
                f"Unhandled exception for {user_info}: {type(exc).__name__}: {exc}",
                exc_info=True,
            )
            raise
