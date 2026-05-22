from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.filters.admin import IsAdmin
from app.repositories.bot_user import BotUserRepository
from app.repositories.position_code import PositionCodeRepository
from app.services.code_service import CodeService
from app.services.direction_service import DirectionService

router = Router(name="admin:stats")
router.callback_query.filter(IsAdmin())


@router.callback_query(F.data == "admin:stats")
async def on_admin_stats(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    user_repo = BotUserRepository(session)
    code_service = CodeService(session)
    direction_service = DirectionService(session)

    user_stats = await user_repo.get_stats()
    code_stats = await code_service.get_statistics()
    directions = await direction_service.list_active_directions()
    dir_map = {d.id: d.name_uz for d in directions}

    lines = [
        "📊 <b>Statistika</b>",
        "",
        "👥 <b>Foydalanuvchilar:</b>",
        f"  • Jami: <b>{user_stats['total']}</b>",
        f"  • Bugun yangi: <b>{user_stats['new_today']}</b>",
        f"  • Bugun faol: <b>{user_stats['active_today']}</b>",
        f"  • Haftalik faol (7 kun): <b>{user_stats['active_week']}</b>",
        f"  • Jami qidiruvlar: <b>{user_stats['total_searches']}</b>",
        "",
        f"🔢 <b>Kodlar bazasi:</b>",
        f"  • Jami kodlar: <b>{code_stats['total_codes']}</b>",
        f"  • Yo'nalishlar: <b>{len(directions)}</b>",
        "",
        "📂 <b>Yo'nalishlar bo'yicha:</b>",
    ]

    for row in sorted(code_stats["by_direction"], key=lambda x: -x["count"]):
        name = dir_map.get(row["direction_id"], f"ID:{row['direction_id']}")
        lines.append(f"  • {name}: {row['count']} ta kod")

    await callback.message.answer("\n".join(lines), parse_mode="HTML")
    await callback.answer()
