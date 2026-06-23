"""Phase 4/5 — deterministic core exam, isolated from analytics."""
from __future__ import annotations

import ast
import importlib
import importlib.util
import pkgutil

from application.analysis.core.educational_validator import EducationalValidator
from application.analysis.core.grade import grade
from domain.analysis.semantic_core import RequiredStructureSpec, get_core_structure_ids
from infrastructure.analysis.concept_ast_detector import detect_concepts
from infrastructure.analysis.core.core_detection_pipeline import CoreDetectionPipeline
from infrastructure.analysis.tree_sitter_gateway import parse_code


def test_grade_rule_one_liner():
    code = "while True:\n    break\n"
    tree = parse_code(code, "python")
    detected = detect_concepts(tree, "python", code)
    result = grade([RequiredStructureSpec("loop", 1)], detected)
    assert result.result == "PASS"
    assert result.missing == ()


def test_pass_fail_is_deterministic():
    code = "def f(n):\n    for i in range(n):\n        if i % 2:\n            return i\n"
    spec = [RequiredStructureSpec("loop", 1), RequiredStructureSpec("function", 1)]
    first = EducationalValidator().validate(code, "python", spec)
    second = EducationalValidator().validate(code, "python", spec)
    assert first.result == second.result == "PASS"
    assert first.to_dict() == second.to_dict()


def test_missing_loop_fails():
    result = EducationalValidator().validate(
        "print(42)\n",
        "python",
        [{"type": "loop", "min_count": 1}],
    )
    assert result.result == "FAIL"
    payload = result.to_dict()
    assert payload == {
        "result": "FAIL",
        "core": {"detected": payload["core"]["detected"], "missing": ["loop"]},
    }
    assert "loop" in payload["core"]["missing"]


def test_exam_structures_fixed_list():
    assert get_core_structure_ids() == frozenset(
        {"loop", "function", "call", "condition", "return", "assignment"}
    )


def test_core_package_never_imports_analytics():
    import infrastructure.analysis.core as core_pkg

    for module_info in pkgutil.walk_packages(
        core_pkg.__path__, core_pkg.__name__ + "."
    ):
        spec = importlib.util.find_spec(module_info.name)
        if not spec or not spec.origin:
            continue
        tree = ast.parse(open(spec.origin, encoding="utf-8").read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "analytics" not in alias.name
            if isinstance(node, ast.ImportFrom) and node.module:
                assert "analytics" not in node.module
