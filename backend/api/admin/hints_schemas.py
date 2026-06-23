from __future__ import annotations

from pydantic import BaseModel, Field


class HintUpsertRequest(BaseModel):
    type: str = Field(description="Core structure id, e.g. function")
    subtype: str
    difficulty: int = Field(ge=1, le=10)
    explanation: str
    examples: dict[str, str] = Field(default_factory=dict)
    title: str | None = None


class HintAdminResponse(BaseModel):
    id: int | None = None
    type: str
    subtype: str
    title: str
    difficulty: int
    explanation: str
    examples: dict[str, str] = Field(default_factory=dict)
    source: str = "yaml"
