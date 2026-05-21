from __future__ import annotations

from pydantic import BaseModel


class DirectionRead(BaseModel):
    id: int
    name_uz: str
    name_ru: str
    name_en: str
    slug: str
    icon_emoji: str | None
    is_active: bool

    model_config = {"from_attributes": True}

    def localized_name(self, lang: str = "uz") -> str:
        return getattr(self, f"name_{lang}", self.name_uz)


class SpecialtyRead(BaseModel):
    id: int
    direction_id: int
    name_uz: str
    name_ru: str
    name_en: str
    slug: str
    is_active: bool

    model_config = {"from_attributes": True}

    def localized_name(self, lang: str = "uz") -> str:
        return getattr(self, f"name_{lang}", self.name_uz)
