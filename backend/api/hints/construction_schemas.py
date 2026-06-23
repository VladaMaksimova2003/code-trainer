from __future__ import annotations

from pydantic import BaseModel, Field


class MpltConstructionResponse(BaseModel):
    id: int
    name: str
    description: str
    category_id: int
    category_name: str
    pitfall_id: str | None = None
    transfer_type: str | None = None
    hint_ru: str | None = None


class MpltConstructionListResponse(BaseModel):
    category_name: str
    items: list[MpltConstructionResponse] = Field(default_factory=list)
