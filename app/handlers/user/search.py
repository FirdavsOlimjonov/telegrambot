from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.inline import code_result_keyboard, directions_keyboard, specialties_keyboard
from app.schemas.position_code import PositionCodeFilter, PositionCodeRead
from app.services.code_service import CodeService
from app.services.direction_service import DirectionService

router = Router(name="user:search")


def _format_code_card(code: PositionCodeRead) -> str:
    lines = [f"🔢 <b>{code.code}</b>"]
    if code.name:
        lines.append(f"📌 {code.name}")
    if code.description:
        lines.append(f"ℹ️ {code.description}")
    return "\n".join(lines)


@router.callback_query(F.data.startswith("dir:"))
async def on_direction_selected(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    direction_id = int(callback.data.split(":")[1])

    service = DirectionService(session)
    specialties = await service.list_specialties(direction_id)
    direction = await service.get_direction(direction_id)

    if not specialties:
        await callback.answer(
            "Bu yo'nalishda mutaxassisliklar mavjud emas.", show_alert=True
        )
        return

    await callback.message.edit_text(
        f"📂 <b>{direction.name_uz if direction else 'Yo\'nalish'}</b>\n\n"
        f"Mutaxassislikni tanlang:",
        reply_markup=specialties_keyboard(specialties, direction_id),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("spec:"))
async def on_specialty_selected(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    _, dir_id_str, spec_id_str = callback.data.split(":")
    direction_id = int(dir_id_str)
    specialty_id = int(spec_id_str)

    await _show_codes(callback, session, direction_id, specialty_id, page=1)


@router.callback_query(F.data.startswith("page:"))
async def on_pagination(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    parts = callback.data.split(":")
    direction_id = int(parts[1])
    specialty_id = int(parts[2])
    page = int(parts[3])

    await _show_codes(callback, session, direction_id, specialty_id, page=page)


@router.callback_query(F.data == "back:directions")
async def on_back_to_directions(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    service = DirectionService(session)
    directions = await service.list_active_directions()

    await callback.message.edit_text(
        "📋 Yo'nalishni tanlang:",
        reply_markup=directions_keyboard(directions),
    )
    await callback.answer()


@router.callback_query(F.data == "noop")
async def on_noop(callback: CallbackQuery) -> None:
    await callback.answer()


async def _show_codes(
    callback: CallbackQuery,
    session: AsyncSession,
    direction_id: int,
    specialty_id: int,
    page: int,
) -> None:
    filters = PositionCodeFilter(
        direction_id=direction_id,
        specialty_id=specialty_id,
        page=page,
    )
    service = CodeService(session)
    codes, total, total_pages = await service.find_codes(filters)

    if not codes:
        await callback.answer(
            "Bu mutaxassislik uchun kodlar topilmadi.", show_alert=True
        )
        return

    cards = "\n\n".join(_format_code_card(c) for c in codes)
    header = f"📊 Jami: <b>{total}</b> ta kod\n\n"

    await callback.message.edit_text(
        header + cards,
        reply_markup=code_result_keyboard(page, total_pages, direction_id, specialty_id),
        parse_mode="HTML",
    )
    await callback.answer()
