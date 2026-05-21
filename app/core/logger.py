from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger as _logger

from app.core.config import settings

_LOG_DIR = Path("logs")
_LOG_DIR.mkdir(exist_ok=True)


def _configure_logger() -> None:
    _logger.remove()  # Remove default stderr handler

    # ── Console handler ───────────────────────────────────────────────────────
    _logger.add(
        sys.stdout,
        level=settings.log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        colorize=True,
        backtrace=True,
        diagnose=settings.debug,
    )

    # ── Rotating file handler (info+) ─────────────────────────────────────────
    _logger.add(
        _LOG_DIR / "bot_{time:YYYY-MM-DD}.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="00:00",       # New file at midnight
        retention="30 days",    # Keep 30 days of logs
        compression="gz",       # Compress old logs
        backtrace=True,
        diagnose=False,         # No sensitive data in file logs
        enqueue=True,           # Thread-safe async logging
    )

    # ── Error-only file (easy alerting integration) ───────────────────────────
    _logger.add(
        _LOG_DIR / "errors.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="100 MB",
        retention="90 days",
        compression="gz",
        backtrace=True,
        diagnose=False,
        enqueue=True,
    )


_configure_logger()

logger = _logger
