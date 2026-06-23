"""Run fixed structure checks: AST → present / absent (yes/no only)."""
from __future__ import annotations

from functools import lru_cache

from tree_sitter import Tree

from domain.analysis.core_detection import CoreDetectionResult
from infrastructure.analysis.core.detectors import ALL_DETECTORS


class DetectorEngine:
    def detect(self, tree: Tree) -> CoreDetectionResult:
        detected: list[str] = []
        counts: dict[str, int] = {}

        for structure_id, check in ALL_DETECTORS:
            if check(tree):
                detected.append(structure_id)
                counts[structure_id] = 1

        return CoreDetectionResult(
            detected=frozenset(detected),
            counts=counts,
        )


@lru_cache(maxsize=1)
def get_default_engine() -> DetectorEngine:
    return DetectorEngine()
