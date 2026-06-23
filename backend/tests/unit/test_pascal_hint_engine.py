"""Tests — Pascal hint engine and showcase hint enrichment."""

from __future__ import annotations

from application.curriculum.display.pascal_hint_engine import (
    GENERIC_BEGIN_END_ONLY,
    build_hint_payload,
    target_hint_for_tc,
    transfer_hint_for_tc,
)
from application.curriculum.display.pascal_tc_detection import resolve_technical_concepts
from application.curriculum.display.showcase_display import enrich_pascal_showcase_hints, sanitize_public_task_payload


def test_target_hint_assignment():
    hint = target_hint_for_tc("assignment")
    assert hint is not None
    assert ":=" in hint
    assert GENERIC_BEGIN_END_ONLY not in hint


def test_transfer_hint_python_stdout():
    hint = transfer_hint_for_tc("python", "stdout_write")
    assert hint is not None
    assert "print" in hint.lower()
    assert "writeln" in hint.lower()


def test_transfer_hint_cpp_stdout():
    hint = transfer_hint_for_tc("cpp", "stdout_write")
    assert hint is not None
    assert "cout" in hint.lower()


def test_build_hint_payload_includes_transfer_layers():
    payload = build_hint_payload(
        technical_concepts=["assignment", "simple_branch"],
        known_languages=["python", "cpp"],
    )
    assert payload["technical_concepts"] == ["assignment", "simple_branch"]
    assert len(payload["target_hints_ru"]) == 2
    assert "python" in payload["transfer_hints_by_language"]
    assert "cpp" in payload["transfer_hints_by_language"]
    assert GENERIC_BEGIN_END_ONLY not in payload["concept_hints_ru"]


def test_example_assignment_task_hints():
    """Catalog slot vai_s09 — assignment."""
    tcs = resolve_technical_concepts(
        primary_tc="assignment",
        task_payload={
            "code_examples": {"pascal": "begin\n  result := a - b;\n  writeln(result);\nend."},
        },
    )
    hints = build_hint_payload(technical_concepts=tcs, known_languages=["python"])
    assert tcs[0] == "assignment"
    assert any(":=" in item["text"] for item in hints["target_hints_ru"])
    assert hints["transfer_hints_by_language"]["python"][0]["concept_id"] == "assignment"


def test_example_simple_branch_task_hints():
    tcs = resolve_technical_concepts(
        primary_tc="simple_branch",
        task_payload={
            "code_examples": {
                "python": "if x > 0:\n    print('yes')\nelse:\n    print('no')",
                "pascal": "if x > 0 then writeln('yes') else writeln('no');",
            },
        },
    )
    hints = build_hint_payload(technical_concepts=tcs, known_languages=["python"])
    assert "simple_branch" in hints["technical_concepts"]
    assert hints["transfer_hints_by_language"]["python"]


def test_example_counted_loop_task_hints():
    tcs = resolve_technical_concepts(
        primary_tc="counted_loop",
        task_payload={
            "code_examples": {
                "python": "for i in range(1, n + 1):\n    print(i)",
                "pascal": "for i := 1 to n do writeln(i);",
            },
        },
    )
    hints = build_hint_payload(technical_concepts=tcs, known_languages=["python"])
    assert "counted_loop" in hints["technical_concepts"]
    assert any("for i := 1 to n" in item["text"] for item in hints["target_hints_ru"])


def test_example_conditional_expression_task_hints():
    hints = build_hint_payload(
        technical_concepts=["conditional_expression"],
        known_languages=["python", "cpp"],
    )
    assert any("тернар" in item["text"].lower() or "if" in item["text"].lower() for item in hints["target_hints_ru"])
    assert hints["transfer_hints_by_language"]["python"]
    assert hints["transfer_hints_by_language"]["cpp"]


def test_example_indexed_sequence_task_hints():
    tcs = resolve_technical_concepts(
        primary_tc="indexed_sequence",
        task_payload={
            "code_examples": {
                "python": "a = [1, 2, 3]\nprint(a[0] + a[1] + a[2])",
                "pascal": "var a: array[1..3] of integer;\nbegin\n  writeln(a[1] + a[2] + a[3]);\nend.",
            },
        },
    )
    hints = build_hint_payload(technical_concepts=tcs, known_languages=["python"])
    assert "indexed_sequence" in hints["technical_concepts"]
    assert hints["transfer_hints_by_language"]["python"]


def test_sanitize_public_task_payload_enriches_pascal_hints():
    payload = sanitize_public_task_payload(
        {
            "id": 1,
            "title": "[Pascal] Присваивание",
            "language": "python",
            "code_examples": {
                "python": "x = 1",
                "pascal": "x := 1;",
                "curriculum_showcase": {
                    "target_language": "pascal",
                    "technical_concept_id": "assignment",
                },
            },
            "curriculum": {"language": "pascal"},
        }
    )
    assert payload["language"] == "pascal"
    assert payload["concept_hints_ru"]
    assert GENERIC_BEGIN_END_ONLY not in payload["concept_hints_ru"]
    assert payload["curriculum"]["target_hints_ru"]
    assert payload["curriculum"]["transfer_hints_by_language"]["python"]


def test_enrich_pascal_showcase_hints_no_begin_end_only():
    payload = enrich_pascal_showcase_hints(
        {
            "curriculum": {
                "language": "pascal",
                "technical_concept_id": "switch_selection",
            },
            "code_examples": {"pascal": "case x of 1: writeln(1); end;"},
        }
    )
    assert payload["concept_hints_ru"]
    assert all(GENERIC_BEGIN_END_ONLY not in hint for hint in payload["concept_hints_ru"])
