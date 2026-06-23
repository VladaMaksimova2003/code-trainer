"""Course scope filters expansion tasks (129-192) from student views."""

from __future__ import annotations

from application.curriculum.course_scope import (
    showcase_row_in_scope,
    task_pattern_in_scope,
)


def test_task_pattern_in_scope_default_128():
    assert task_pattern_in_scope("task_128") is True
    assert task_pattern_in_scope("task_129") is True
    assert task_pattern_in_scope("task_130") is False
    assert task_pattern_in_scope("task_192") is False


def test_showcase_row_filters_expansion_pattern():
    row = type("Row", (), {"id": 131})()
    assert showcase_row_in_scope(row, {"exercise_pattern_id": "task_131"}) is False
    assert showcase_row_in_scope(row, {"exercise_pattern_id": "task_008"}) is True


def test_showcase_row_filters_expansion_slot():
    row = type("Row", (), {"id": 131})()
    assert showcase_row_in_scope(row, {"slot_id": "pas_131"}) is False
    assert showcase_row_in_scope(row, {"slot_id": "pas_008"}) is True


def test_showcase_row_task_129_requires_catalog_slot():
    row = type("Row", (), {"id": 200})()
    assert showcase_row_in_scope(
        row,
        {"exercise_pattern_id": "task_129", "slot_id": "py_129"},
    ) is False
    assert showcase_row_in_scope(
        row,
        {"exercise_pattern_id": "task_129", "slot_id": "py_007"},
    ) is True
    assert showcase_row_in_scope(
        row,
        {"exercise_pattern_id": "task_129", "slot_id": "pas_007"},
    ) is True
