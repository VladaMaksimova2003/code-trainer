"""Core detection result — shared between domain and detector engine."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CoreDetectionResult:
    detected: frozenset[str]
    counts: dict[str, int]

    def count(self, structure: str) -> int:
        return self.counts.get(structure, 0)

    def has(self, structure: str, min_count: int = 1) -> bool:
        return self.count(structure) >= min_count

    def to_dict(self) -> dict:
        return {
            "detected": sorted(self.detected),
            "counts": dict(self.counts),
        }
