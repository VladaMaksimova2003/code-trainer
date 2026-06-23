"""Metrics from core detectors (deterministic)."""
from __future__ import annotations

from dataclasses import asdict, dataclass

from tree_sitter import Tree

from infrastructure.analysis.core.core_detection_pipeline import CoreDetectionPipeline


@dataclass(frozen=True)
class AstFeatures:
    has_loops: bool = False
    has_functions: bool = False
    has_conditionals: bool = False
    has_calls: bool = False
    has_assignments: bool = False
    has_returns: bool = False
    loop_count: int = 0
    function_count: int = 0
    conditional_count: int = 0
    call_count: int = 0
    return_count: int = 0
    assignment_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


class AstFeatureExtractor:
    def __init__(self, pipeline: CoreDetectionPipeline | None = None) -> None:
        self._core = pipeline or CoreDetectionPipeline()

    def extract(self, tree: Tree) -> AstFeatures:
        core = self._core.detect(tree)
        counts = core.counts
        return AstFeatures(
            has_loops=counts.get("loop", 0) > 0,
            has_functions=counts.get("function", 0) > 0,
            has_conditionals=counts.get("condition", 0) > 0,
            has_calls=counts.get("call", 0) > 0,
            has_assignments=counts.get("assignment", 0) > 0,
            has_returns=counts.get("return", 0) > 0,
            loop_count=counts.get("loop", 0),
            function_count=counts.get("function", 0),
            conditional_count=counts.get("condition", 0),
            call_count=counts.get("call", 0),
            return_count=counts.get("return", 0),
            assignment_count=counts.get("assignment", 0),
        )
