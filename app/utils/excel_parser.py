from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import ValidationError

from app.core.logger import logger
from app.schemas.excel_import import ExcelRowData, ExcelRowError

# Maps Excel column headers (lowercase) → ExcelRowData field names.
# Supports Uzbek, Russian, and English headers.
COLUMN_ALIASES: dict[str, str] = {
    # code
    "kod": "code",
    "code": "code",
    "код": "code",
    "pozitsiya kodi": "code",
    "position code": "code",
    # direction
    "yo'nalish": "direction",
    "йуналиш": "direction",
    "direction": "direction",
    "направление": "direction",
    "yunalish": "direction",
    # specialty
    "mutaxassislik": "specialty",
    "специальность": "specialty",
    "specialty": "specialty",
    "speciality": "specialty",
    # name
    "nomi": "name",
    "name": "name",
    "название": "name",
    "наименование": "name",
    # description
    "tavsif": "description",
    "description": "description",
    "описание": "description",
    "izoh": "description",
}

REQUIRED_FIELDS = {"code", "direction", "specialty"}


def _normalize_headers(df: pd.DataFrame) -> pd.DataFrame:
    renamed = {}
    for col in df.columns:
        key = col.strip().lower()
        if key in COLUMN_ALIASES:
            renamed[col] = COLUMN_ALIASES[key]
    return df.rename(columns=renamed)


def _check_required_columns(df: pd.DataFrame) -> list[str]:
    return sorted(REQUIRED_FIELDS - set(df.columns))


def parse_excel_file(
    file_path: str | Path,
) -> tuple[list[ExcelRowData], list[ExcelRowError]]:
    """
    Read an Excel file and return (valid_rows, error_rows).
    Each valid row represents one position code to be inserted.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    engine = "openpyxl" if path.suffix.lower() == ".xlsx" else "xlrd"

    try:
        df = pd.read_excel(path, engine=engine, dtype=str)
    except Exception as exc:
        raise ValueError(f"Cannot read Excel file: {exc}") from exc

    df = df.dropna(how="all").fillna("")
    df = _normalize_headers(df)

    missing = _check_required_columns(df)
    if missing:
        raise ValueError(
            f"Missing required columns: {missing}. Found: {list(df.columns)}"
        )

    logger.info(f"Parsing {len(df)} rows from {path.name}")

    valid: list[ExcelRowData] = []
    errors: list[ExcelRowError] = []

    for i, row in enumerate(df.to_dict("records"), start=2):
        raw: dict[str, Any] = {k: str(v).strip() for k, v in row.items()}
        try:
            validated = ExcelRowData(
                code=raw.get("code", ""),
                direction=raw.get("direction", ""),
                specialty=raw.get("specialty", ""),
                name=raw.get("name") or None,
                description=raw.get("description") or None,
            )
            if not validated.code:
                raise ValueError("code field is empty")
            valid.append(validated)
        except (ValidationError, ValueError) as exc:
            errors.append(ExcelRowError(row_number=i, raw_data=raw, error=str(exc)))

    logger.info(f"Parsed: {len(valid)} valid, {len(errors)} errors from {path.name}")
    return valid, errors
