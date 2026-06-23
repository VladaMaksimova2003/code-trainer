"""Tests for display TC detection in reference code."""

from application.curriculum.validation.expected_concept_checker import (
    detect_expected_concepts_in_code,
    detect_expected_concepts_multilang,
)


def test_detect_python_io_and_loop():
    code = (
        "n = int(input())\n"
        "total = 0\n"
        "for _ in range(n):\n"
        "    total += int(input())\n"
        "print(total)\n"
    )
    found = set(detect_expected_concepts_in_code(code, language="python"))
    assert "tc_console_io" in found
    assert "tc_loops" in found
    assert "tc_arithmetic" in found
    assert "console_input" not in found
    assert "console_output" not in found


def test_detect_multilang_samples():
    by_lang = detect_expected_concepts_multilang(
        [
            ("python", "print(1)"),
            ("pascal", "begin\nwriteln(1);\nend."),
        ]
    )
    assert "python" in by_lang
    assert "pascal" in by_lang
    assert "tc_console_io" in by_lang["python"]
    assert "tc_program_structure" in by_lang["pascal"] or "tc_console_io" in by_lang["pascal"]
