from __future__ import annotations

import asyncio

from app.bot import create_bot, create_dispatcher
from app.core.config import settings
from app.core.database import engine
from app.core.logger import logger
from app.models import Base  # Ensures all models are registered with metadata


async def on_startup(bot, dispatcher) -> None:
    me = await bot.get_me()
    logger.info(f"Bot started: @{me.username} (id={me.id})")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Admin IDs: {settings.admin_ids}")


async def on_shutdown(bot, dispatcher) -> None:
    logger.info("Bot shutting down...")
    await engine.dispose()
    logger.info("Database connections closed.")


async def main() -> None:
    bot = create_bot()
    dp = create_dispatcher()

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logger.info("Starting bot in polling mode...")
    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    asyncio.run(main())
