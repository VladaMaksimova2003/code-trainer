"""Structure presence checks — bool only, no plugins."""
from __future__ import annotations

from infrastructure.analysis.core.detector_engine import DetectorEngine
from infrastructure.analysis.core.detectors import ALL_DETECTORS, STRUCTURE_IDS
from infrastructure.analysis.core.detectors.loop import detect as detect_loop
from infrastructure.analysis.tree_sitter_gateway import parse_code


def test_six_explicit_detectors():
    assert len(ALL_DETECTORS) == 6
    assert STRUCTURE_IDS == frozenset(
        {"loop", "function", "call", "condition", "return", "assignment"}
    )


def test_loop_detect_returns_bool():
    tree = parse_code("for i in range(3):\n    pass\n", "python")
    assert detect_loop(tree) is True


def test_engine_marks_present_structures():
    code = "def f(n):\n    for i in range(n):\n        if i % 2:\n            return i\n"
    result = DetectorEngine().detect(parse_code(code, "python"))
    assert "loop" in result.detected
    assert "function" in result.detected
    assert result.counts.get("loop") == 1
