"""Exam detection — runs bool structure checks via DetectorEngine."""
from __future__ import annotations

from tree_sitter import Tree

from domain.analysis.core_detection import CoreDetectionResult
from infrastructure.analysis.core.detector_engine import DetectorEngine, get_default_engine


class CoreDetectionPipeline:
    def __init__(self, engine: DetectorEngine | None = None) -> None:
        self._engine = engine or get_default_engine()


    def detect(self, tree: Tree) -> CoreDetectionResult:
        return self._engine.detect(tree)
