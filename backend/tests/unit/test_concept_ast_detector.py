"""Concept detection via concepts.yml ast_nodes."""
from __future__ import annotations

from application.analysis.core.educational_validator import EducationalValidator
from application.analysis.educational_vocabulary import normalize_construction_tags
from domain.analysis.semantic_core import RequiredStructureSpec
from domain.learning.skill_groups import CONCEPT_IDS
from infrastructure.analysis.concept_ast_detector import detect_concepts
from infrastructure.analysis.tree_sitter_gateway import parse_code


def test_seventeen_concepts_in_registry():
    assert len(CONCEPT_IDS) == 17
    assert "io" in CONCEPT_IDS
    assert "nested_loops" in CONCEPT_IDS


def test_loop_detected_by_for_statement():
    tree = parse_code("for i in range(3):\n    pass\n", "python")
    result = detect_concepts(tree, "python")
    assert "loop" in result.detected


def test_io_detected_by_input_print():
    code = "n = int(input())\nprint(n)\n"
    tree = parse_code(code, "python")
    result = detect_concepts(tree, "python", code)
    assert "io" in result.detected


def test_nested_loops_detected():
    code = "for i in range(2):\n    for j in range(2):\n        pass\n"
    tree = parse_code(code, "python")
    result = detect_concepts(tree, "python", code)
    assert "nested_loops" in result.detected


def test_legacy_tags_normalize_to_concepts():
    assert normalize_construction_tags(["for_loop", "io"]) == ["loop", "io"]


def test_call_and_return_not_exam_ids():
    from application.analysis.educational_vocabulary import get_exam_structure_ids

    assert "call" not in get_exam_structure_ids()
    assert "return" not in get_exam_structure_ids()


def test_validator_missing_loop_fails():
    result = EducationalValidator().validate("print(42)\n", "python", ["loop"])
    assert result.result == "FAIL"
    assert "loop" in result.missing


def test_validator_teacher_legacy_for_loop_tag():
    result = EducationalValidator().validate(
        "for i in range(3):\n    pass\n",
        "python",
        ["for_loop"],
    )
    assert result.result == "PASS"


def test_grade_with_function_spec():
    code = "def f():\n    return 1\n"
    specs = [RequiredStructureSpec("function", 1)]
    result = EducationalValidator().validate(code, "python", specs)
    assert result.result == "PASS"
