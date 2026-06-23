"""Teacher-edited title and per-language concepts must survive list/public reads."""

from __future__ import annotations

from types import SimpleNamespace

from application.tasks.services.authoring_expected_concepts import (
    resolve_authoring_expected_concepts_by_language,
)
from application.tasks.services.catalog.task_display import display_title_for_task
from application.tasks.services.teacher_editor_public_payload import (
    apply_teacher_editor_public_payload,
)


def test_display_title_uses_teacher_row_title_when_override():
    title = display_title_for_task(
        "Моё название",
        {
            "teacher_assembly_override": True,
            "curriculum_showcase": {"slot_id": "py_001", "title_ru": "Каталог"},
        },
    )
    assert title == "Моё название"


def test_teacher_override_keeps_per_language_expected_concepts_only_from_db():
    examples = {
        "teacher_assembly_override": True,
        "expected_concepts": {
            "pascal": ["tc_console_io"],
            "python": ["tc_loops"],
        },
        "curriculum_showcase": {
            "expected_concepts": {"pascal": ["old_catalog"]},
            "expected_concept_ids": ["old_catalog"],
            "language_tracks": {
                "python": {"expected_concept_ids": ["track_catalog"]},
            },
        },
    }
    by_lang = resolve_authoring_expected_concepts_by_language(examples)
    assert by_lang == {
        "pascal": ["tc_console_io"],
        "python": ["tc_loops"],
    }


def test_apply_teacher_public_payload_exposes_concepts_by_language():
    row = SimpleNamespace(
        title="Teacher title",
        description="Teacher description",
        difficulty="medium",
        task_type="task_translate_full_program",
        test_cases=[],
        code_examples={
            "teacher_assembly_override": True,
            "expected_concepts": {
                "pascal": ["tc_console_io"],
                "python": ["tc_loops"],
            },
            "curriculum_showcase": {"primary_action": "implement"},
        },
        block_reorder_task=None,
        translation_task=SimpleNamespace(
            source_language="python",
            source_code="print(1)",
        ),
    )
    payload = {
        "title": "Catalog",
        "curriculum": {"technical_concept_id": "arrays"},
    }
    result = apply_teacher_editor_public_payload(row, payload, learning_language="python")
    assert result["title"] == "Teacher title"
    assert result["curriculum"]["expected_concept_ids_by_language"]["python"] == ["tc_loops"]
    assert "pascal" in result["expected_concepts_by_language"]
