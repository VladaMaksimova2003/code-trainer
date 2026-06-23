"""Teacher-selected display TC ids must survive student payload enrichment."""

from __future__ import annotations

from application.curriculum.display.pascal_tc_pedagogy import (
    _teacher_expected_concept_ids_for_language,
    resolve_expected_concept_ids,
)


def test_teacher_expected_concept_ids_accept_display_tc_cards():
    payload = {
        "expected_concepts": {
            "python": ["tc_variables", "tc_console_io", "tc_loops"],
        },
        "code_examples": {
            "expected_concepts": {
                "python": ["tc_variables", "tc_console_io", "tc_loops"],
            },
        },
    }

    ids = _teacher_expected_concept_ids_for_language(payload, "python")
    assert ids == ["tc_console_io", "tc_loops", "tc_variables"]


def test_resolve_expected_concept_ids_prefers_teacher_list_over_bundle():
    payload = {
        "technical_concept_id": "program_entry",
        "expected_concepts": {
            "python": ["tc_variables", "tc_console_io"],
        },
    }

    ids = resolve_expected_concept_ids(
        primary_tc="program_entry",
        task_payload=payload,
        learning_language="python",
    )
    assert ids == ["tc_console_io", "tc_variables"]
