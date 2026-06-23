"""Tests — detecting and preserving teacher block assembly edits."""

from __future__ import annotations

from application.tasks.services.teacher_assembly_preservation import (
    relation_assembly_differs_from_catalog,
    should_preserve_teacher_assembly,
)
from application.tasks.use_cases.block_reorder.get import _refresh_curriculum_assembly_variants


class _Relation:
    language = "pascal"
    template = "begin\n  {0}\nend."
    blocks = ["writeln(1);", "writeln(2);"]
    correct_order = [0]
    language_variants = {}


class _Task:
    code_examples = {
        "curriculum_showcase": {
            "slot_id": "pas_001",
            "task_format": "сборка_программы",
            "primary_action": "assemble",
        }
    }

    block_reorder_task = _Relation()


def test_should_preserve_when_db_differs_from_catalog():
    assert relation_assembly_differs_from_catalog(_Task.block_reorder_task, _Task.code_examples)


def test_refresh_skipped_when_db_has_language_variants():
    task = _Task()
    task.block_reorder_task = _Relation()
    payload = {"language_variants": {}}
    _refresh_curriculum_assembly_variants(task, payload)
    assert payload["language_variants"]["pascal"]["blocks"]


def test_should_preserve_with_explicit_flag():
    task = _Task()
    task.code_examples = {**_Task.code_examples, "teacher_assembly_override": True}
    assert should_preserve_teacher_assembly(task, _Relation())


def test_refresh_keeps_custom_template():
    task = _Task()
    task.code_examples = {**_Task.code_examples, "teacher_assembly_override": True}
    task.block_reorder_task = _Relation()
    payload = {"language_variants": {}}
    _refresh_curriculum_assembly_variants(task, payload)
    assert payload["language_variants"]["pascal"]["template"].startswith("begin")
