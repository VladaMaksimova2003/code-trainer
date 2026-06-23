"""Core bool detection + optional subtype metadata (hints / UI only)."""
from __future__ import annotations

from functools import lru_cache

from tree_sitter import Tree

from domain.analysis.core_detection import CoreDetectionResult
from domain.analysis.structure_enrichment import StructureEnrichmentResult
from infrastructure.analysis.core.detector_engine import get_default_engine
from infrastructure.analysis.metadata.subtype_detector import detect_subtypes


class StructureEnrichmentEngine:
    def detect_core(self, tree: Tree) -> CoreDetectionResult:
        return get_default_engine().detect(tree)

    def detect_subtypes(self, tree: Tree, language_id: str) -> StructureEnrichmentResult:
        raw = detect_subtypes(tree, language_id)
        return StructureEnrichmentResult(
            subtypes={k: tuple(sorted(v)) for k, v in raw.items()},
        )

    def enrich(self, tree: Tree, language_id: str) -> tuple[CoreDetectionResult, StructureEnrichmentResult]:
        return self.detect_core(tree), self.detect_subtypes(tree, language_id)


@lru_cache(maxsize=1)
def get_default_enrichment_engine() -> StructureEnrichmentEngine:
    return StructureEnrichmentEngine()
