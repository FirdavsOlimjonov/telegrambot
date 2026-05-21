from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PositionCodeRead(BaseModel):
    id: int
    code: str
    name: str | None
    description: str | None
    direction_id: int
    specialty_id: int
    direction_name: str | None = None
    specialty_name: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PositionCodeFilter(BaseModel):
    direction_id: int
    specialty_id: int
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=50)
