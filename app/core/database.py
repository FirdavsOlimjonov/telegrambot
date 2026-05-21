from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool

from app.core.config import settings
from app.core.logger import logger


def _build_engine():
    """
    NullPool in testing to avoid connection leaks between test cases.
    AsyncAdaptedQueuePool in production for connection reuse.
    """
    pool_class = NullPool if settings.app_env == "development" else AsyncAdaptedQueuePool

    return create_async_engine(
        settings.database_url,
        echo=settings.debug,           # SQL query logging in debug mode
        pool_pre_ping=True,            # Detect stale connections before using
        pool_size=10,                  # Max persistent connections
        max_overflow=20,               # Connections beyond pool_size (burst)
        pool_recycle=3600,             # Recycle connections after 1 hour
        pool_class=pool_class if pool_class is AsyncAdaptedQueuePool else NullPool,
    )


engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

AsyncSessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,     # Prevent lazy-loading after commit in async context
    autoflush=False,
    autocommit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency-injection style session provider.
    Used in handlers via middleware injection.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def transaction(session: AsyncSession):
    """
    Explicit transaction context manager for multi-step operations.
    Use in services that need atomic multi-table writes.
    """
    async with session.begin():
        try:
            yield session
        except Exception as exc:
            logger.error(f"Transaction rolled back: {exc}")
            raise
