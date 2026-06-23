"""Mirror rows must not duplicate collection task lists."""

from __future__ import annotations

from types import SimpleNamespace

from application.curriculum.showcase.showcase_collection_tasks import align_rows_to_catalog_specs
from application.curriculum.showcase.showcase_row_dedupe import (
    dedupe_collection_task_payloads,
    dedupe_showcase_task_rows,
)


def test_align_rows_to_catalog_specs_drops_extra_slugs():
    rows = [
        {"task_id": 1, "slug": "py_001"},
        {"task_id": 3, "slug": "py_003"},
        {"task_id": 129, "slug": "py_129"},
        {"task_id": 5, "slug": "py_005"},
    ]
    specs = (
        {"slug": "py_001"},
        {"slug": "py_003"},
        {"slug": "py_005"},
    )
    aligned = align_rows_to_catalog_specs(rows, specs)
    assert [row["slug"] for row in aligned] == ["py_001", "py_003", "py_005"]


def _row(task_id: int, slug: str, target: str):
    return SimpleNamespace(id=task_id), {
        "slug": slug,
        "slot_id": slug,
        "target_language": target,
        "collection_key": "ch_loops",
        "pedagogical_slot_id": f"algo_v4:{slug.split('_')[-1]}",
    }


def test_dedupe_showcase_task_rows_keeps_native_language_row():
    pas_row, pas_showcase = _row(10, "pas_001", "pascal")
    py_row, py_showcase = _row(20, "py_001", "python")
    matched = [(pas_row, pas_showcase), (py_row, py_showcase)]

    deduped = dedupe_showcase_task_rows(matched, language="pascal")
    assert [row.id for row, _ in deduped] == [10]

    deduped_py = dedupe_showcase_task_rows(matched, language="python")
    assert [row.id for row, _ in deduped_py] == [20]


def test_dedupe_collection_task_payloads():
    rows = [
        {"task_id": 10, "slug": "pas_001", "language": "pascal"},
        {"task_id": 20, "slug": "py_001", "language": "python"},
    ]
    assert dedupe_collection_task_payloads(rows, language="pascal") == [rows[0]]
    assert dedupe_collection_task_payloads(rows, language="python") == [rows[1]]


def test_available_language_tracks_for_algo_v4_unified_row():
    from application.curriculum.mirror.pedagogical_task_model import available_language_tracks

    showcase = {
        "pedagogical_slot_id": "prc_001",
        "slug": "pas_001",
        "slot_id": "pas_001",
        "language_tracks": {
            "pascal": {"slug": "pas_001"},
            "cpp": {"slug": "cpp_001"},
            "python": {"expected_concept_ids": ["stdout_write"]},
        },
    }
    assert available_language_tracks(showcase) == [
        "cpp",
        "csharp",
        "java",
        "pascal",
        "python",
    ]


def test_dedupe_prefers_unified_row_over_legacy_mirror_copy():
    unified_row, unified_showcase = _row(1, "pas_001", "pascal")
    unified_showcase["language_tracks"] = {
        "pascal": {"slug": "pas_001"},
        "python": {"slug": "py_001"},
        "cpp": {"slug": "cpp_001"},
        "csharp": {"slug": "cs_001"},
        "java": {"slug": "java_001"},
    }
    legacy_row, legacy_showcase = _row(129, "py_001", "python")
    legacy_showcase["language_tracks"] = {
        "python": {"slug": "py_001"},
        "pascal": {"slug": "pas_001"},
    }
    matched = [(legacy_row, legacy_showcase), (unified_row, unified_showcase)]

    deduped = dedupe_showcase_task_rows(matched, language="python")
    assert [row.id for row, _ in deduped] == [1]

    payloads = [
        {"task_id": 129, "slug": "py_001", "language": "python"},
        {"task_id": 1, "slug": "py_001", "language": "python"},
    ]
    assert dedupe_collection_task_payloads(payloads, language="python") == [payloads[1]]
