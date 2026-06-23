"""Subtype metadata — separate from core PASS/FAIL detection."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class StructureEnrichmentResult:
    """Optional detail for teacher UI; never used in grade()."""

    subtypes: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "subtypes": {
                structure: list(names)
                for structure, names in sorted(self.subtypes.items())
            },
        }
