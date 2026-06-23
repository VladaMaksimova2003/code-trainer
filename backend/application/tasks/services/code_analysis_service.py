"""Teacher reference-code analysis — detected concepts from concepts.yml."""
from __future__ import annotations

from dataclasses import dataclass

from application.analysis.concept_analysis_service import (
    ConceptAnalysisService,
    DetectedConcept,
)


@dataclass(frozen=True)
class DetectedPattern:
    id: str
    type: str
    label: str
    source_construct: str


@dataclass(frozen=True)
class AnalysisResult:
    patterns: tuple[DetectedPattern, ...]
    raw_constructs: tuple[str, ...]
    exam: dict
    analytics: dict | None = None


class CodeAnalysisService:
    def __init__(self, concept_analysis: ConceptAnalysisService | None = None) -> None:
        self._concepts = concept_analysis or ConceptAnalysisService()

    def analyze(self, code: str, language: str) -> AnalysisResult:
        result = self._concepts.analyze(code, language)
        patterns = tuple(
            DetectedPattern(
                id=concept.id,
                type=concept.id,
                label=concept.label,
                source_construct=concept.id,
            )
            for concept in result.detected
        )
        detected_ids = list(result.concept_ids)
        return AnalysisResult(
            patterns=patterns,
            raw_constructs=result.concept_ids,
            exam={
                "result": "PASS",
                "core": {"detected": detected_ids, "missing": []},
            },
            analytics=None,
        )
