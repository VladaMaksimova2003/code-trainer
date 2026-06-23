"""Tests for Pascal expected concept validation."""

from __future__ import annotations

from application.curriculum.validation.expected_concept_checker import (
    missing_expected_concept_messages,
)


def test_missing_pascal_assignment():
    messages = missing_expected_concept_messages(
        "begin\nwriteln('hi');\nend.",
        ["assignment"],
        language="pascal",
    )
    assert messages
    assert "Присваивание" in messages[0]


def test_present_pascal_assignment():
    code = "begin\n  x := 1;\n  writeln(x);\nend."
    assert missing_expected_concept_messages(code, ["assignment"], language="pascal") == []
