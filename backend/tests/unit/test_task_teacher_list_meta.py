"""Teacher task list metadata must reflect teacher-edited activity types."""

from __future__ import annotations

from types import SimpleNamespace

from application.tasks.services.catalog.task_teacher_list_meta import teacher_list_meta_for_row
from shared.enums import AssignmentType


def _row(**kwargs):
    defaults = {
        "task_type": AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
        "code_examples": {},
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_teacher_override_uses_task_type_not_stale_showcase_action():
    row = _row(
        task_type=AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
        code_examples={
            "teacher_assembly_override": True,
            "curriculum_showcase": {
                "primary_action": "assemble",
                "collection_key": "ch_arrays",
            },
        },
    )

    meta = teacher_list_meta_for_row(row)

    assert meta.primary_action == "implement"
    assert meta.activity_label == "Написать"


def test_teacher_override_keeps_debug_when_showcase_is_debug():
    row = _row(
        task_type=AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
        code_examples={
            "teacher_assembly_override": True,
            "curriculum_showcase": {
                "primary_action": "debug",
                "task_format": "исправление",
                "collection_key": "ch_arrays",
            },
        },
    )

    meta = teacher_list_meta_for_row(row)

    assert meta.primary_action == "debug"
    assert meta.is_debug_task is True
