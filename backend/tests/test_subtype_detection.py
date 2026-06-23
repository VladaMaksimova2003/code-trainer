"""Subtype enrichment — does not change core PASS/FAIL."""
from __future__ import annotations

from application.analysis.core.educational_validator import EducationalValidator
from domain.analysis.semantic_core import RequiredStructureSpec
from infrastructure.analysis.metadata.subtype_detector import detect_subtypes
from infrastructure.analysis.tree_sitter_gateway import parse_code


def test_python_foreach_and_nested_loop():
    code = "for i in range(2):\n    for j in range(2):\n        pass\n"
    tree = parse_code(code, "python")
    subtypes = detect_subtypes(tree, "python")
    assert "foreach" in subtypes.get("loop", set())
    assert "nested_loop" in subtypes.get("loop", set())


def test_python_method_subtype():
    code = "class A:\n    def run(self):\n        pass\n"
    tree = parse_code(code, "python")
    subtypes = detect_subtypes(tree, "python")
    assert "method" in subtypes.get("function", set())


def test_pass_fail_unchanged_without_subtype_requirement():
    code = "def f(n):\n    for i in range(n):\n        pass\n"
    spec = [RequiredStructureSpec("loop", 1), RequiredStructureSpec("function", 1)]
    result = EducationalValidator().validate(code, "python", spec)
    assert result.result == "PASS"

    result_fail = EducationalValidator().validate("print(1)\n", "python", spec)
    assert result_fail.result == "FAIL"
    assert "loop" in result_fail.missing
