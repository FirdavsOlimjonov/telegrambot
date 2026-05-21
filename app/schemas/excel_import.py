from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ExcelRowData(BaseModel):
    code: str
    direction: str
    specialty: str
    name: str | None = None
    description: str | None = None


class ExcelRowError(BaseModel):
    row_number: int
    raw_data: dict[str, Any]
    error: str


class SeedResult(BaseModel):
    total_rows: int
    inserted: int
    duplicates: int
    errors: list[ExcelRowError] = Field(default_factory=list)

    def print_summary(self) -> None:
        print(f"\n{'─' * 40}")
        print(f"  Total rows : {self.total_rows}")
        print(f"  Inserted   : {self.inserted} ✅")
        print(f"  Duplicates : {self.duplicates} ⚠️")
        print(f"  Errors     : {len(self.errors)} ❌")
        if self.errors:
            print("\n  Error details:")
            for e in self.errors:
                print(f"    Row {e.row_number}: {e.error}")
        print(f"{'─' * 40}\n")
