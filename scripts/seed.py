"""
One-time database seeder.

Usage:
    python scripts/seed.py path/to/data.xlsx

The Excel file must have columns (Uzbek, Russian, or English headers are all accepted):
    kod | yo'nalish | mutaxassislik | nomi (optional) | tavsif (optional)

Directions and specialties that don't exist yet are created automatically.
Duplicate codes (same direction + specialty + code) are silently skipped.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Allow running from project root: python scripts/seed.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.core.database import AsyncSessionFactory
from app.core.logger import logger
from app.models import Direction, Specialty, PositionCode
from app.schemas.excel_import import ExcelRowError, SeedResult
from app.utils.excel_parser import parse_excel_file


async def _get_or_create_direction(session, name: str) -> Direction:
    name_clean = name.strip()
    slug = name_clean.lower().replace(" ", "-")

    stmt = select(Direction).where(Direction.slug == slug)
    direction = (await session.execute(stmt)).scalar_one_or_none()

    if direction is None:
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

    return direction


async def _get_or_create_specialty(
    session, name: str, direction_id: int
) -> Specialty:
    name_clean = name.strip()
    slug = f"{direction_id}-{name_clean.lower().replace(' ', '-')}"

    stmt = select(Specialty).where(
        Specialty.direction_id == direction_id,
        Specialty.slug == slug,
    )
    specialty = (await session.execute(stmt)).scalar_one_or_none()

    if specialty is None:
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
    duplicates = 0
    resolution_errors: list[ExcelRowError] = []

    async with AsyncSessionFactory() as session:
        # Cache direction/specialty objects within this session to avoid N+1
        direction_cache: dict[str, Direction] = {}
        specialty_cache: dict[tuple[int, str], Specialty] = {}

        for i, row in enumerate(valid_rows, start=2):
            dir_key = row.direction.strip().lower()
            if dir_key not in direction_cache:
                direction_cache[dir_key] = await _get_or_create_direction(
                    session, row.direction
                )
            direction = direction_cache[dir_key]

            spec_key = (direction.id, row.specialty.strip().lower())
            if spec_key not in specialty_cache:
                specialty_cache[spec_key] = await _get_or_create_specialty(
                    session, row.specialty, direction.id
                )
            specialty = specialty_cache[spec_key]

            # Check for duplicate
            exists_stmt = select(PositionCode).where(
                PositionCode.direction_id == direction.id,
                PositionCode.specialty_id == specialty.id,
                PositionCode.code == row.code,
            )
            existing = (await session.execute(exists_stmt)).scalar_one_or_none()

            if existing:
                duplicates += 1
                continue

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
        duplicates=duplicates,
        errors=all_errors,
    )
    result.print_summary()
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/seed.py path/to/data.xlsx")
        sys.exit(1)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"File not found: {path}")
        sys.exit(1)

    asyncio.run(seed(path))
