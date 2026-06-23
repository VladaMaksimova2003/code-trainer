"""Tests for ATCC idiom engine and carryover detection."""

from application.curriculum.display.atcc_idiom_engine import (
    build_atcc_hint_payload,
    detect_atcc_carryover,
    idiom_hint,
)


def test_idiom_hint_pascal_to_python_stdout():
    hint = idiom_hint("pascal", "python", "stdout_write")
    assert hint is not None
    assert "print" in hint


def test_idiom_hint_python_to_pascal_stdout():
    hint = idiom_hint("python", "pascal", "stdout_write")
    assert hint is not None
    assert "writeln" in hint


def test_detect_pascal_writeln_in_python_submission():
    code = "n = int(input())\nwriteln(n)\n"
    warnings = detect_atcc_carryover(
        "pascal",
        "python",
        code,
        expected_concepts=["stdout_write", "stdin_read"],
    )
    assert warnings
    assert "ATCC" in warnings[0]["text"]
    assert "writeln" in warnings[0]["text"]
    assert warnings[0]["detection"] == "ast"


def test_detect_writeln_in_string_not_flagged_when_parse_ok():
    code = "msg = 'writeln(n)'\nprint(msg)\n"
    warnings = detect_atcc_carryover(
        "pascal",
        "python",
        code,
        expected_concepts=["stdout_write"],
    )
    assert not warnings


def test_detect_python_print_not_flagged_on_python():
    code = "print(int(input()))\n"
    warnings = detect_atcc_carryover(
        "pascal",
        "python",
        code,
        expected_concepts=["stdout_write"],
    )
    assert not warnings


def test_detect_python_print_in_pascal_submission():
    code = "program Demo;\nvar n: integer;\nbegin\n  readln(n);\n  print(n);\nend.\n"
    warnings = detect_atcc_carryover(
        "python",
        "pascal",
        code,
        expected_concepts=["stdout_write", "stdin_read"],
    )
    assert warnings
    assert "print" in warnings[0]["text"]


def test_build_atcc_hint_payload():
    payload = build_atcc_hint_payload(
        technical_concepts=["stdout_write", "counted_loop"],
        source_language="pascal",
        target_language="python",
    )
    assert payload["source_language"] == "pascal"
    assert payload["target_language"] == "python"
    assert len(payload["atcc_idiom_hints"]) >= 1
