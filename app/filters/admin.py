from __future__ import annotations

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from app.core.config import settings


class IsAdmin(BaseFilter):
    """
    Passes if the sender's Telegram ID is in the ADMIN_IDS config list.
    Works on both Message and CallbackQuery update types.
    """

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user = event.from_user
        if user is None:
            return False
        return user.id in settings.admin_ids
