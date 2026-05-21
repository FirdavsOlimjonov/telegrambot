from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PaginationMeta:
    page: int
    page_size: int
    total: int

    @property
    def total_pages(self) -> int:
        return max(1, -(-self.total // self.page_size))

    @property
    def has_previous(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    def __str__(self) -> str:
        return f"Page {self.page}/{self.total_pages} ({self.total} total)"
