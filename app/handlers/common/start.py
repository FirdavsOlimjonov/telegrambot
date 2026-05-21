from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.keyboards.inline import admin_panel_keyboard, directions_keyboard
from app.services.direction_service import DirectionService

router = Router(name="common:start")


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    await state.clear()

    user_id = message.from_user.id if message.from_user else 0
    is_admin = user_id in settings.admin_ids

    if is_admin:
        await message.answer(
            "👋 Xush kelibsiz, Admin!\n\nQuyidagilardan birini tanlang:",
            reply_markup=admin_panel_keyboard(),
        )
        return

    service = DirectionService(session)
    directions = await service.list_active_directions()

    if not directions:
        await message.answer(
            "📭 Hozircha yo'nalishlar mavjud emas.\n"
            "Iltimos, keyinroq urinib ko'ring."
        )
        return

    await message.answer(
        "Yo'nalishni tanlang:",
        reply_markup=directions_keyboard(directions),
    )
