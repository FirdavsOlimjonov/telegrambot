from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.schemas.direction import DirectionRead, SpecialtyRead


def directions_keyboard(
    directions: list[DirectionRead], lang: str = "uz"
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for d in directions:
        label = f"{d.icon_emoji or ''} {d.localized_name(lang)}".strip()
        builder.button(text=label, callback_data=f"dir:{d.id}")
    builder.adjust(2)
    # Search by code button always spans full width at the bottom
    builder.button(text="🔍 Kod bo'yicha qidirish", callback_data="search:by_code")
    builder.adjust(2, 1)
    return builder.as_markup()


def specialties_keyboard(
    specialties: list[SpecialtyRead],
    direction_id: int,
    lang: str = "uz",
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for s in specialties:
        builder.button(
            text=s.localized_name(lang),
            callback_data=f"spec:{direction_id}:{s.id}",
        )
    builder.button(text="⬅️ Orqaga", callback_data="back:directions")
    builder.adjust(2)
    return builder.as_markup()


def code_result_keyboard(
    current_page: int,
    total_pages: int,
    direction_id: int,
    specialty_id: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if current_page > 1:
        builder.button(
            text="◀️ Oldingi",
            callback_data=f"page:{direction_id}:{specialty_id}:{current_page - 1}",
        )

    builder.button(text=f"{current_page}/{total_pages}", callback_data="noop")

    if current_page < total_pages:
        builder.button(
            text="Keyingi ▶️",
            callback_data=f"page:{direction_id}:{specialty_id}:{current_page + 1}",
        )

    builder.button(text="🔄 Yangi qidiruv", callback_data="back:directions")
    builder.adjust(3, 1)
    return builder.as_markup()


def code_search_result_keyboard(
    current_page: int,
    total_pages: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if current_page > 1:
        builder.button(text="◀️ Oldingi", callback_data=f"scode_page:{current_page - 1}")

    builder.button(text=f"{current_page}/{total_pages}", callback_data="noop")

    if current_page < total_pages:
        builder.button(text="Keyingi ▶️", callback_data=f"scode_page:{current_page + 1}")

    builder.button(text="🔍 Yangi qidiruv", callback_data="search:by_code")
    builder.button(text="🏠 Bosh menyu", callback_data="back:directions")
    builder.adjust(3, 1, 1)
    return builder.as_markup()


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Statistika", callback_data="admin:stats")
    builder.adjust(1)
    return builder.as_markup()
