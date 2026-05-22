from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.core.config import settings
from app.core.logger import logger
from app.handlers.common.start import router as start_router
from app.handlers.user.search import router as search_router
from app.handlers.user.code_search import router as code_search_router
from app.handlers.admin.stats import router as stats_router
from app.middlewares.db import DatabaseMiddleware
from app.middlewares.logging import LoggingMiddleware
from app.middlewares.user_tracking import UserTrackingMiddleware


def create_bot() -> Bot:
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    """
    Storage: MemoryStorage for development.
    Production recommendation: RedisStorage for multi-instance deployments.
    """
    dp = Dispatcher(storage=MemoryStorage())

    # ── Global middlewares ────────────────────────────────────────────────────
    dp.update.outer_middleware(LoggingMiddleware())
    dp.update.middleware(DatabaseMiddleware())
    dp.update.middleware(UserTrackingMiddleware())

    # ── Register routers (order matters — more specific before generic) ───────
    dp.include_router(start_router)
    dp.include_router(stats_router)
    dp.include_router(code_search_router)  # before search_router — has FSM states
    dp.include_router(search_router)

    return dp
