"""Tests for apply_patterns_and_tests edge cases."""

from __future__ import annotations

from types import SimpleNamespace

from application.tasks.services.task_patterns import apply_patterns_and_tests


def test_apply_patterns_falls_back_to_flat_list_when_by_language_empty():
    row = SimpleNamespace(
        code_examples={
            "curriculum_showcase": {
                "expected_concept_ids": ["old_concept"],
                "expected_concepts": {"pascal": ["old_concept"]},
            }
        },
        test_cases=[],
    )

    apply_patterns_and_tests(
        row,
        patterns=["stdout_write", "program_entry"],
        patterns_by_language={},
        test_cases=None,
    )

    assert row.code_examples["patterns"] == ["stdout_write", "program_entry"]
    showcase = row.code_examples["curriculum_showcase"]
    assert showcase["expected_concept_ids"] == ["stdout_write", "program_entry"]
    assert showcase["expected_concepts"]["pascal"] == ["stdout_write", "program_entry"]


def test_apply_patterns_by_language_updates_showcase():
    row = SimpleNamespace(
        code_examples={"curriculum_showcase": {"target_language": "pascal"}},
        test_cases=[],
    )
    block = SimpleNamespace(language="pascal")
    row.block_reorder_task = block

    apply_patterns_and_tests(
        row,
        patterns=None,
        patterns_by_language={"pascal": ["for_loop"], "python": ["while_loop"]},
        test_cases=None,
    )

    assert row.code_examples["expected_concepts"] == {
        "pascal": ["for_loop"],
        "python": ["while_loop"],
    }
    showcase = row.code_examples["curriculum_showcase"]
    assert showcase["expected_concepts"]["pascal"] == ["for_loop"]
    assert showcase["expected_concept_ids"] == ["for_loop"]
