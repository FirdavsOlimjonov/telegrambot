from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.handlers.states import CodeSearchStates
from app.keyboards.inline import code_search_result_keyboard
from app.repositories.bot_user import BotUserRepository
from app.schemas.position_code import PositionCodeRead
from app.services.code_service import CodeService

router = Router(name="user:code_search")

_PAGE_SIZE = 5


def _format_result(code: PositionCodeRead, index: int) -> str:
    lines = [f"<b>{index}. {code.code}</b>"]
    if code.direction_name:
        lines.append(f"{code.direction_name}")
    if code.specialty_name:
        lines.append(f"<b>{code.specialty_name}</b>")
    if code.name:
        lines.append(f"{code.name}")
    if code.description:
        lines.append(f"ℹ️ {code.description}")
    return "\n".join(lines)


@router.callback_query(F.data == "search:by_code")
async def on_search_by_code(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    await state.set_state(CodeSearchStates.waiting_for_code)
    await callback.message.answer(
        "🔍 Qidirmoqchi bo'lgan lavozim kodni kiriting.\n"
        "To'liq yoki qisman kiritishingiz mumkin.\n\n"
        "Masalan: <code>11200004</code> yoki <code>1120</code>",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(StateFilter(CodeSearchStates.waiting_for_code))
async def on_code_input(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    query = (message.text or "").strip()

    if len(query) < 1:
        await message.answer("Iltimos, kamida 1 ta belgi kiriting.")
        return

    if message.from_user:
        await BotUserRepository(session).increment_search(message.from_user.id)

    service = CodeService(session)
    results, total, total_pages = await service.search_by_code(
        query, page=1, page_size=_PAGE_SIZE
    )

    if not results:
        await message.answer(
            f"❌ <b>{query}</b> bo'yicha hech narsa topilmadi.\n\n"
            "Boshqa lavozim kodini kiriting:",
            parse_mode="HTML",
        )
        return

    # Save query in FSM state so pagination callbacks can reuse it
    await state.set_state(CodeSearchStates.viewing_results)
    await state.update_data(query=query)

    text = _build_result_text(query, results, total, page=1, total_pages=total_pages)
    await message.answer(
        text,
        reply_markup=code_search_result_keyboard(1, total_pages),
        parse_mode="HTML",
    )


@router.callback_query(
    StateFilter(CodeSearchStates.viewing_results),
    F.data.startswith("scode_page:"),
)
async def on_search_pagination(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    page = int(callback.data.split(":")[1])
    data = await state.get_data()
    query: str = data.get("query", "")

    service = CodeService(session)
    results, total, total_pages = await service.search_by_code(
        query, page=page, page_size=_PAGE_SIZE
    )

    text = _build_result_text(query, results, total, page=page, total_pages=total_pages)
    await callback.message.edit_text(
        text,
        reply_markup=code_search_result_keyboard(page, total_pages),
        parse_mode="HTML",
    )
    await callback.answer()


def _build_result_text(
    query: str,
    results: list[PositionCodeRead],
    total: int,
    page: int,
    total_pages: int,
) -> str:
    header = (
        f"🔍 <b>{query}</b> bo'yicha qidiruv\n"
        f"Topildi: <b>{total}</b> ta natija\n\n"
    )
    cards = "\n\n".join(
        _format_result(r, i + (page - 1) * _PAGE_SIZE + 1)
        for i, r in enumerate(results)
    )
    return header + cards
