"""Starter fields are disabled for teacher-edited debug tasks."""

from __future__ import annotations

from application.tasks.use_cases.debug_code_keys import (
    read_teacher_buggy_code,
    strip_starter_fields,
    teacher_task_blocks_starters,
)


def test_read_teacher_buggy_code_ignores_starter_when_teacher_override():
    examples = {
        "teacher_assembly_override": True,
    }
    showcase = {"starter_pascal": "catalog buggy"}
    assert read_teacher_buggy_code(examples, showcase, "pascal") == ""


def test_read_teacher_buggy_code_prefers_buggy_key():
    examples = {
        "teacher_assembly_override": True,
        "buggy_pascal": "teacher buggy",
    }
    showcase = {"starter_pascal": "catalog buggy"}
    assert read_teacher_buggy_code(examples, showcase, "pascal") == "teacher buggy"


def test_strip_starter_fields_removes_catalog_keys():
    payload = {"starter_pascal": "x", "buggy_pascal": "y", "title": "T"}
    strip_starter_fields(payload)
    assert payload == {"buggy_pascal": "y", "title": "T"}


def test_teacher_task_blocks_starters_flag():
    assert teacher_task_blocks_starters({"teacher_assembly_override": True})
    assert not teacher_task_blocks_starters({})
