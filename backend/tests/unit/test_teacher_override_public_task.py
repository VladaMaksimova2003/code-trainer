"""Teacher override must win over curriculum catalog on public task payloads."""

from __future__ import annotations

from application.curriculum.display.showcase_display import sanitize_public_task_payload


def test_sanitize_public_task_keeps_teacher_title_and_description():
    payload = {
        "id": 7,
        "title": "Teacher custom title",
        "description": "Teacher custom description",
        "teacher_assembly_override": True,
        "code_examples": {
            "teacher_assembly_override": True,
            "curriculum_showcase": {
                "slot_id": "py_001",
                "primary_action": "assemble",
                "educational_goal": "Catalog goal text",
                "expected_concept_ids": ["old_concept"],
            },
            "expected_concepts": {"python": ["stdout_write"]},
            "patterns": ["stdout_write"],
        },
    }

    sanitized = sanitize_public_task_payload(payload)

    assert sanitized["title"] == "Teacher custom title"
    assert sanitized["description"] == "Teacher custom description"
    assert sanitized["expected_concept_ids"]
    assert sanitized["curriculum"]["expected_concept_ids"]
