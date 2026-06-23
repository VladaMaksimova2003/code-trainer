from __future__ import annotations

from pydantic import BaseModel, Field


class StructureHintResponse(BaseModel):
    type: str
    subtype: str
    difficulty: int
    title: str
    explanation: str
    examples: dict[str, str] = Field(default_factory=dict)


class StructureCatalogResponse(BaseModel):
    structures: dict[str, list[str]]
