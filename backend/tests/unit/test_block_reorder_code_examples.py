from application.tasks.use_cases.block_reorder.get import (
    _build_code_examples,
    _reference_code_for_language,
)
from domain.entities.tasks.block_reorder_task import BlockReorderTask
from shared.enums import Difficulty, TaskType


class _Relation:
    language = "python"
    original_code = "print(1)"
    language_variants = {
        "cpp": {
            "original_code": "#include <iostream>\nint main() { return 0; }",
            "blocks": ["return 0;"],
            "correct_order": [0],
        }
    }


class _Task:
    code_examples = {}


def _entity() -> BlockReorderTask:
    return BlockReorderTask(
        id=1,
        teacher_id=1,
        title="t",
        description="d",
        difficulty=Difficulty.EASY,
        task_type=TaskType.BLOCK_REORDER,
        original_code="print(1)",
        template=None,
        blocks=["print(1)"],
        correct_order=[0],
        language="python",
        language_variants=_Relation.language_variants,
    )


def test_reference_code_for_language_does_not_fallback_to_primary():
    entity = _entity()
    relation = _Relation()
    assert _reference_code_for_language(entity, relation, "cpp", {}) != "print(1)"
    assert "iostream" in _reference_code_for_language(entity, relation, "cpp", {})


def test_reference_code_for_language_returns_empty_without_variant():
    entity = _entity()
    relation = _Relation()
    assert _reference_code_for_language(entity, relation, "java", {}) == ""


def test_build_code_examples_never_exposes_original_code():
    entity = _entity()
    relation = _Relation()
    relation.language_variants = {"cpp": {"blocks": ["print(1)"]}}
    assert _build_code_examples(entity, relation, _Task()) == {}


def test_build_code_examples_only_explicit_task_rows():
    entity = _entity()
    relation = _Relation()
    task = _Task()
    task.code_examples = {"python": "teacher hint"}
    assert _build_code_examples(entity, relation, task) == {"python": "teacher hint"}


def test_build_code_examples_preserves_curriculum_showcase_dict():
    entity = _entity()
    relation = _Relation()
    task = _Task()
    showcase = {
        "slug": "psk_03",
        "expected_concept_ids": ["program_entry", "block_scope"],
        "pascal_features": "program; begin; end",
    }
    task.code_examples = {
        "python": "print(1)",
        "curriculum_showcase": showcase,
        "patterns": ["io"],
    }
    assert _build_code_examples(entity, relation, task) == {
        "python": "print(1)",
        "curriculum_showcase": showcase,
        "patterns": ["io"],
    }
