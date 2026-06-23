"""Grading uses core detectors only; analytics is a separate teacher service."""
from __future__ import annotations

from infrastructure.analysis.core.core_detection_pipeline import CoreDetectionPipeline
from infrastructure.analysis.tree_sitter_gateway import parse_code


class PatternExtractor:
    def __init__(self, _settings: object | None = None) -> None:
        self._core = CoreDetectionPipeline()

    def extract(self, code: str, language: str) -> list[str]:
        tree = parse_code(code, str(language).lower())
        return sorted(self._core.detect(tree).detected)

    def extract_features(self, code: str, language: str) -> dict:
        tree = parse_code(code, str(language).lower())
        return self._core.detect(tree).to_dict()

    def build_ir(self, code: str, language: str):
        tree = parse_code(code, str(language).lower())
        return self._core.detect(tree)

    def extract_core(self, code: str, language: str) -> dict:
        return self.build_ir(code, language).to_dict()
