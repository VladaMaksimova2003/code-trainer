from __future__ import annotations

from pydantic import BaseModel, Field


class CurriculumLevelResponse(BaseModel):
    level: int
    allowed_structures: list[str] = Field(default_factory=list)
    next_unlock: list[str] = Field(default_factory=list)
