"""Hint domain records — isolated from educational core grading."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

HintSource = Literal["db", "yaml"]


@dataclass(frozen=True)
class StructureHintRecord:
    structure_type: str
    subtype: str
    difficulty: int
    explanation: str
    examples: dict[str, str]
    title: str | None = None
    id: int | None = None
    source: HintSource = "yaml"

    def to_api_dict(self) -> dict[str, Any]:
        """Fixed public contract for GET /hints/structure/{type}/{subtype}."""
        title = self.title or f"{self.structure_type.title()} ({self.subtype})"
        return {
            "type": self.structure_type,
            "subtype": self.subtype,
            "difficulty": self.difficulty,
            "title": title,
            "explanation": self.explanation,
            "examples": dict(self.examples),
        }

    def to_admin_dict(self) -> dict[str, Any]:
        payload = self.to_api_dict()
        payload["id"] = self.id
        payload["source"] = self.source
        return payload
