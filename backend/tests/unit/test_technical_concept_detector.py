"""AST-based technical concept detector."""

from __future__ import annotations

import pytest

from application.curriculum.validation.technical_concept_detector import (
    detect_technical_concepts,
    rollup_to_display_tc,
    validate_ast_node_mappings,
    validate_display_registry_illustrates,
    validate_technical_to_tc_map,
)
from application.curriculum.validation.technical_concept_registry import (
    list_technical_concept_ids,
    load_technical_to_tc_map,
)


def test_ast_maps_and_tc_rollup_are_consistent():
    assert not validate_technical_to_tc_map(), validate_technical_to_tc_map()
    assert not validate_ast_node_mappings(), validate_ast_node_mappings()
    assert len(list_technical_concept_ids()) >= 10


def test_display_registry_uses_canonical_illustrates():
    issues = validate_display_registry_illustrates()
    assert not issues, issues[:5]


def test_rollup_first_three_tc_cards():
    assert rollup_to_display_tc({"program_root", "main_entry"}) == frozenset({"tc_program_structure"})
    assert rollup_to_display_tc({"variable_declaration"}) == frozenset({"tc_variables_types"})
    assert rollup_to_display_tc({"assignment"}) == frozenset({"tc_arithmetic"})


@pytest.mark.parametrize(
    ("language", "code", "expected_technical", "expected_display"),
    [
        (
            "python",
            "print('Hello')\nx = 10",
            {"program_root", "console_output", "assignment", "variable_declaration"},
            {"tc_program_structure", "tc_console_io", "tc_arithmetic", "tc_variables_types"},
        ),
        (
            "python",
            "def main():\n    print('Hello')\n\nif __name__ == '__main__':\n    main()",
            {"main_entry", "console_output"},
            {"tc_program_structure", "tc_console_io"},
        ),
        (
            "pascal",
            "program Hello;\nbegin\n  x := 10;\nend.",
            {"program_root", "block_scope", "assignment"},
            {"tc_program_structure", "tc_arithmetic"},
        ),
        (
            "java",
            'class Main {\n    public static void main(String[] args) {\n        int x = 10;\n        System.out.println(x);\n    }\n}',
            {"main_entry", "variable_declaration", "console_output"},
            {"tc_program_structure", "tc_variables_types", "tc_console_io"},
        ),
    ],
)
def test_detect_technical_concepts_samples(language, code, expected_technical, expected_display):
    result = detect_technical_concepts(code, language)
    assert expected_technical.issubset(result.technical_ids), result.technical_ids
    assert expected_display.issubset(result.display_tc_ids), result.display_tc_ids


def test_assignment_not_triggered_by_if_condition_alone():
    result = detect_technical_concepts("if x > 0:\n    pass\n", "python")
    assert "assignment" not in result.technical_ids
    assert "conditional" in result.technical_ids


def test_arithmetic_from_binary_operator_is_signal_not_confirmed():
    result = detect_technical_concepts("x = a + b\n", "python")
    assert "arithmetic" in result.signal_ids
    assert "arithmetic" not in result.technical_ids
    assert "assignment" in result.technical_ids


def test_nested_loop_semantic_detector():
    code = "for i in range(2):\n    for j in range(2):\n        pass\n"
    result = detect_technical_concepts(code, "python")
    assert "nested_loop" in result.technical_ids
    assert "loop" in result.technical_ids


def test_python_simple_bindings_roll_up_to_variables_types():
    code = """n = int(input())
total = 0
for _ in range(n):
    load = int(input())
    total += load
print(total // n)"""
    result = detect_technical_concepts(code, "python")
    assert "variable_declaration" in result.technical_ids
    assert "tc_variables_types" in result.display_tc_ids
