from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.filters.admin import IsAdmin
from app.services.code_service import CodeService
from app.services.direction_service import DirectionService

router = Router(name="admin:stats")
router.callback_query.filter(IsAdmin())


@router.callback_query(F.data == "admin:stats")
async def on_admin_stats(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    code_service = CodeService(session)
    direction_service = DirectionService(session)

    stats = await code_service.get_statistics()
    directions = await direction_service.list_active_directions()
    dir_map = {d.id: d.name_uz for d in directions}

    lines = [
        "📊 <b>Statistika</b>\n",
        f"Jami kodlar: <b>{stats['total_codes']}</b>\n",
        "📂 <b>Yo'nalishlar bo'yicha:</b>",
    ]
    for row in stats["by_direction"]:
        name = dir_map.get(row["direction_id"], f"ID:{row['direction_id']}")
        lines.append(f"  • {name}: {row['count']} ta kod")

    await callback.message.answer("\n".join(lines), parse_mode="HTML")
    await callback.answer()
