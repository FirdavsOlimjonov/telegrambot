"""
Database seeder.

Usage:
    python scripts/seed.py path/to/data.xlsx

Clears position_codes, specialties, and directions before inserting,
so re-running always produces a clean state matching the Excel file.

The Excel file must have columns (Uzbek, Russian, or English headers accepted):
    kod | yo'nalish | mutaxassislik | nomi (optional) | tavsif (optional)
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import delete, text

from app.core.database import AsyncSessionFactory
from app.core.logger import logger
from app.models import Direction, Specialty, PositionCode
from app.schemas.excel_import import ExcelRowError, SeedResult
from app.utils.excel_parser import parse_excel_file


async def _clear_tables(session) -> None:
    """Delete all data in dependency order (child → parent)."""
    await session.execute(delete(PositionCode))
    await session.execute(delete(Specialty))
    await session.execute(delete(Direction))
    await session.flush()
    logger.info("Tables cleared: position_codes, specialties, directions")


async def _get_or_create_direction(session, name: str, cache: dict) -> Direction:
    key = name.strip().lower()
    if key in cache:
        return cache[key]

    name_clean = name.strip()
    slug = key.replace(" ", "-")

    direction = Direction(
        name_uz=name_clean,
        name_ru=name_clean,
        name_en=name_clean,
        slug=slug,
        is_active=True,
    )
    session.add(direction)
    await session.flush()
    logger.info(f"Created direction: {name_clean!r}")
    cache[key] = direction
    return direction


async def _get_or_create_specialty(
    session, name: str, direction_id: int, cache: dict
) -> Specialty:
    key = (direction_id, name.strip().lower())
    if key in cache:
        return cache[key]

    name_clean = name.strip()
    slug = f"{direction_id}-{name_clean.lower().replace(' ', '-')}"

    specialty = Specialty(
        direction_id=direction_id,
        name_uz=name_clean,
        name_ru=name_clean,
        name_en=name_clean,
        slug=slug,
        is_active=True,
    )
    session.add(specialty)
    await session.flush()
    logger.info(f"Created specialty: {name_clean!r} (direction_id={direction_id})")
    cache[key] = specialty
    return specialty


async def seed(file_path: str) -> SeedResult:
    valid_rows, parse_errors = parse_excel_file(file_path)

    if not valid_rows and parse_errors:
        result = SeedResult(
            total_rows=len(parse_errors),
            inserted=0,
            duplicates=0,
            errors=parse_errors,
        )
        result.print_summary()
        return result

    inserted = 0
    resolution_errors: list[ExcelRowError] = []

    async with AsyncSessionFactory() as session:
        await _clear_tables(session)

        direction_cache: dict[str, Direction] = {}
        specialty_cache: dict[tuple, Specialty] = {}

        for i, row in enumerate(valid_rows, start=2):
            direction = await _get_or_create_direction(
                session, row.direction, direction_cache
            )
            specialty = await _get_or_create_specialty(
                session, row.specialty, direction.id, specialty_cache
            )

            session.add(PositionCode(
                code=row.code,
                direction_id=direction.id,
                specialty_id=specialty.id,
                name=row.name,
                description=row.description,
            ))
            inserted += 1

        await session.commit()

    all_errors = parse_errors + resolution_errors
    result = SeedResult(
        total_rows=len(valid_rows) + len(parse_errors),
        inserted=inserted,
        duplicates=0,
        errors=all_errors,
    )
    result.print_summary()
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/seed.py path\\to\\data.xlsx")
        sys.exit(1)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"File not found: {path}")
        sys.exit(1)

    asyncio.run(seed(path))
