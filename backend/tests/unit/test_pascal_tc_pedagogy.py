"""Tests — Pascal pedagogical expected concepts."""

from __future__ import annotations

from application.curriculum.collections.curriculum_next_service import (
    resolve_next_in_ordered_tasks,
)
from application.curriculum.display.pascal_tc_pedagogy import (
    build_expected_concepts_payload,
    resolve_expected_concept_ids,
)
from application.curriculum.display.showcase_display import sanitize_public_task_payload
from application.curriculum.pascal.catalog.pascal_v311_expected_concepts import (
    expected_concept_ids_for_row,
)


def test_resolve_next_empty_collection_is_not_completed():
    next_task, completed = resolve_next_in_ordered_tasks([], {}, title_prefix="")
    assert next_task is None
    assert completed is False


def test_oop_class_type_bundle_includes_field_access():
    ids = resolve_expected_concept_ids(
        primary_tc="class_type",
        task_payload={"code_examples": {"pascal": "type T = class end;"}},
    )
    assert "class_type" in ids
    assert "object_instance" in ids
    assert "field_access" in ids
    assert len(ids) >= 5


def test_build_expected_concepts_has_cards_and_hierarchy():
    payload = build_expected_concepts_payload(primary_tc="inheritance_hierarchy")
    assert payload["expected_concepts"]
    assert any(c["id"] == "tc_oop_inheritance" for c in payload["expected_concepts"])
    assert payload["concept_hierarchy"]
    assert payload["concept_hierarchy"][0]["label"] == "Наследование"
    assert any(line["concept_id"] == "parent_class" for line in payload["concept_hierarchy"])


def test_expected_concept_cards_use_display_registry():
    payload = build_expected_concepts_payload(
        primary_tc="simple_branch",
        task_payload={"expected_concept_ids": ["simple_branch"]},
    )
    card = payload["expected_concepts"][0]
    assert card["id"] == "tc_conditionals"
    assert card["name_ru"] == "Условия и ветвление"
    assert "examples_by_language" in card
    assert card["examples_by_language"]["python"]
    assert card["examples_by_language"]["pascal"]


def test_sanitize_exposes_expected_concepts_not_glossary():
    payload = sanitize_public_task_payload(
        {
            "id": 1,
            "title": "[Pascal] Класс",
            "code_examples": {
                "python": "class P: pass",
                "curriculum_showcase": {
                    "target_language": "pascal",
                    "technical_concept_id": "class_type",
                },
            },
            "curriculum": {"language": "pascal"},
        }
    )
    assert payload["expected_concepts"]
    assert payload["expected_concept_ids"]
    assert "target_hints_ru" in payload
    assert "class_type" in payload["expected_concept_ids"]
    names = [c["name_ru"] for c in payload["expected_concepts"]]
    assert any("класс" in name.lower() for name in names)


def test_resolve_expected_concepts_uses_explicit_list():
    ids = resolve_expected_concept_ids(
        primary_tc="program_entry",
        task_payload={
            "expected_concept_ids": ["block_scope"],
            "pascal_features": "program; begin; end",
        },
    )
    assert ids == ["tc_program_structure"]


def test_resolve_expected_concepts_uses_teacher_per_language():
    ids = resolve_expected_concept_ids(
        primary_tc="program_entry",
        task_payload={
            "expected_concept_ids": ["program_entry", "variable_decl", "assignment"],
            "expected_concepts": {
                "pascal": ["simple_branch", "block_scope"],
                "python": ["simple_branch", "for_loop_counter"],
            },
        },
        learning_language="pascal",
    )
    assert ids == ["tc_conditionals", "tc_program_structure"]


def test_psk_12_has_only_block_scope_at_creation():
    ids = expected_concept_ids_for_row(
        slot_id="psk_12",
        chapter_key="program_skeleton",
        pascal_features="begin; end",
        task_format="сборка_фрагмента",
    )
    assert ids == ["block_scope"]
