"""Detect concept ids from reference/student code (concepts.yml ast_nodes)."""
from __future__ import annotations

from dataclasses import dataclass

from infrastructure.analysis.concept_ast_detector import concept_label, detect_concepts
from infrastructure.analysis.concept_registry import list_concept_ids
from infrastructure.analysis.tree_sitter_gateway import parse_code


@dataclass(frozen=True)
class DetectedConcept:
    id: str
    label: str


@dataclass(frozen=True)
class ConceptAnalysisResult:
    detected: tuple[DetectedConcept, ...]
    concept_ids: tuple[str, ...]


class ConceptAnalysisService:
    def analyze(self, code: str, language_id: str) -> ConceptAnalysisResult:
        tree = parse_code(code, str(language_id).lower())
        result = detect_concepts(tree, language_id, code)
        ordered = [cid for cid in list_concept_ids() if cid in result.detected]
        for cid in sorted(result.detected):
            if cid not in ordered:
                ordered.append(cid)
        concepts = tuple(
            DetectedConcept(id=cid, label=concept_label(cid)) for cid in ordered
        )
        return ConceptAnalysisResult(
            detected=concepts,
            concept_ids=tuple(c.id for c in concepts),
        )
