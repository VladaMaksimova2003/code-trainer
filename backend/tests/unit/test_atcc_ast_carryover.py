"""Unit tests for Tree-sitter ATCC carryover layer."""

from application.curriculum.display.atcc_ast_carryover import detect_atcc_carryover_ast


def test_ast_detects_writeln_call_in_python():
    hits = detect_atcc_carryover_ast(
        "pascal",
        "python",
        "n = 1\nwriteln(n)\n",
        expected_concepts=["stdout_write"],
    )
    assert hits
    assert hits[0].concept_id == "stdout_write"
    assert hits[0].fragment == "writeln(...)"


def test_ast_ignores_writeln_inside_string_literal():
    hits = detect_atcc_carryover_ast(
        "pascal",
        "python",
        "msg = 'writeln(n)'\nprint(msg)\n",
        expected_concepts=["stdout_write"],
    )
    assert not hits


def test_ast_detects_print_call_in_pascal():
    code = "program Demo;\nvar n: integer;\nbegin\n  readln(n);\n  print(n);\nend.\n"
    hits = detect_atcc_carryover_ast(
        "python",
        "pascal",
        code,
        expected_concepts=["stdout_write"],
    )
    assert hits
    assert hits[0].concept_id == "stdout_write"
