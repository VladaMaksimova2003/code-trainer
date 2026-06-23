"""Unit tests for showcase collection task row metadata."""

from __future__ import annotations

from application.curriculum.showcase.showcase_collection_tasks import (
    build_showcase_collection_task_row,
    resolve_showcase_row_metadata,
)


class _Row:
    id = 57
    title = "[7. Рекурсия] Факториал"
    task_type = "translation"
    difficulty = "medium"


def test_resolve_showcase_row_metadata_falls_back_to_showcase_without_primary_link():
    showcase = {
        "slug": "pas_049",
        "target_language": "pascal",
        "collection_key": "recursion",
        "technical_concept_id": "program_entry",
        "primary_action": "implement",
        "language_tracks": {
            "pascal": {
                "slug": "pas_049",
                "collection_key": "recursion",
                "technical_concept_id": "program_entry",
                "primary_action": "implement",
            },
        },
    }
    meta = resolve_showcase_row_metadata(showcase=showcase, language="python", primary=None)
    assert meta["technical_concept_id"] == "program_entry"
    assert meta["action"] == "implement"


def test_build_showcase_collection_task_row_for_imported_task():
    showcase = {
        "slug": "pas_001",
        "target_language": "pascal",
        "collection_key": "algo_basics",
        "technical_concept_id": "program_entry",
        "primary_action": "assemble",
        "pedagogical_slot_id": "algo_v4:001",
        "language_tracks": {
            "pascal": {
                "slug": "pas_001",
                "collection_key": "algo_basics",
                "technical_concept_id": "program_entry",
            },
        },
    }
    row = build_showcase_collection_task_row(
        row=_Row(),
        showcase=showcase,
        language="python",
        collection_key="algo_basics",
        primary=None,
    )
    assert row["technical_concept_id"] == "program_entry"
    assert row["slug"] == "py_001"
