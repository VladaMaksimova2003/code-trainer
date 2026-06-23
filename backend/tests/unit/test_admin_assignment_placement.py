"""Tests for admin assignment placement labels."""

from __future__ import annotations

from types import SimpleNamespace

from application.admin.assignment_placement import admin_assignment_placement_for_row


def _task(**kwargs):
    defaults = {
        "task_type": "task_translate_full_program",
        "code_examples": {
            "curriculum_showcase": {
                "collection_key": "maps",
                "target_language": "pascal",
                "group": "pascal_curriculum_v311_maps",
                "collection_id": "pascal_maps_v311",
            }
        },
    }
    payload = {**defaults, **kwargs}
    return SimpleNamespace(**payload)


def test_admin_assignment_placement_resolves_collection_chapter_and_teacher():
    row = _task()
    placement = admin_assignment_placement_for_row(
        row,
        chapter_titles={"maps": "10. Словари и key-value структуры"},
        teacher_name="Seed Teacher",
        teacher_email="teacher@example.com",
    )
    assert placement.collection_title == "Pascal"
    assert placement.chapter_title == "10. Словари и key-value структуры"
    assert placement.chapter_key == "maps"
    assert placement.language == "pascal"
    assert placement.chapter_slug == "maps"
    assert placement.teacher_name == "Seed Teacher"
    assert placement.teacher_email == "teacher@example.com"


def test_admin_assignment_placement_without_showcase_meta():
    row = _task(code_examples={})
    placement = admin_assignment_placement_for_row(
        row,
        chapter_titles={},
        teacher_name=None,
        teacher_email=None,
    )
    assert placement.collection_title is None
    assert placement.chapter_title is None
    assert placement.teacher_name is None
