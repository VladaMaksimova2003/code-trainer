"""Teacher catalog list — display title and language tracks."""

from __future__ import annotations

from types import SimpleNamespace

from application.curriculum.mirror.curriculum_slot_mirror import canonical_title_for_slot
from application.tasks.services.catalog.task_display import display_title_for_task
from infrastructure.repositories.tasks.task_catalog import (
    _collect_task_languages,
    _dedupe_teacher_task_rows,
    _teacher_list_dedupe_key,
    _teacher_list_sort_key,
)


def _row(
    *,
    title: str,
    code_examples: dict | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        title=title,
        code_examples=code_examples or {},
        block_reorder_task=None,
        translation_task=None,
    )


def test_display_title_strips_seed_prefix_and_uses_canonical_slot_title():
    row = _row(
        title="[Pascal v3.1.1: 1. Базовый синтаксис] Первая программа на Pascal",
        code_examples={
            "python": "print('hi')",
            "curriculum_showcase": {
                "slug": "pas_001",
                "slot_id": "pas_001",
                "language_tracks": {
                    "pascal": {"slug": "pas_001"},
                    "python": {"slug": "py_001"},
                    "cpp": {"slug": "cpp_001"},
                },
            },
        },
    )
    expected = canonical_title_for_slot("pas_001")
    assert expected
    assert display_title_for_task(row.title, row.code_examples) == expected


def test_collect_task_languages_uses_showcase_tracks_not_code_example_keys():
    row = _row(
        title="Task",
        code_examples={
            "python": "print('hi')",
            "patterns": ["for_loop"],
            "pascal": "begin end.",
            "java": "class Main {}",
            "csharp": "class Main {}",
            "curriculum_showcase": {
                "slug": "psk_01",
                "language_tracks": {
                    "pascal": {"slug": "psk_01"},
                    "python": {"slug": "pyk_01"},
                    "cpp": {"slug": "cpk_01"},
                },
            },
        },
    )
    assert _collect_task_languages(row) == ["cpp", "pascal", "python"]


def test_collect_task_languages_filters_non_curriculum_keys_for_legacy_task():
    row = _row(
        title="Legacy",
        code_examples={
            "python": "print(1)",
            "patterns": ["x"],
            "curriculum_showcase": {},
            "java": "void main() {}",
        },
    )
    assert _collect_task_languages(row) == ["python", "java"]


def test_teacher_list_dedupe_key_unifies_pas_and_py_mirror_rows():
    pas = _row(
        title="Sum",
        code_examples={
            "curriculum_showcase": {"slot_id": "pas_001", "slug": "pas_001", "target_language": "pascal"},
        },
    )
    pas.id = 1
    py = _row(
        title="Sum",
        code_examples={
            "curriculum_showcase": {"slot_id": "py_001", "slug": "py_001", "target_language": "python"},
        },
    )
    py.id = 129
    assert _teacher_list_dedupe_key(pas) == _teacher_list_dedupe_key(py)


def test_dedupe_teacher_task_rows_keeps_one_row_and_merges_languages():
    pas = _row(
        title="Sum",
        code_examples={
            "pascal": "begin end.",
            "cpp": "int main() {}",
            "curriculum_showcase": {
                "slot_id": "pas_001",
                "slug": "pas_001",
                "target_language": "pascal",
                "language_tracks": {
                    "pascal": {"slug": "pas_001"},
                    "cpp": {"slug": "cpp_001"},
                },
            },
        },
    )
    pas.id = 1
    py = _row(
        title="Sum",
        code_examples={
            "python": "print(1)",
            "pascal": "begin end.",
            "cpp": "int main() {}",
            "java": "class Main {}",
            "csharp": "class Main {}",
            "curriculum_showcase": {
                "slot_id": "py_001",
                "slug": "py_001",
                "target_language": "python",
                "language_tracks": {
                    "python": {"slug": "py_001"},
                    "pascal": {"slug": "pas_001"},
                    "cpp": {"slug": "cpp_001"},
                    "java": {"slug": "java_001"},
                    "csharp": {"slug": "csharp_001"},
                },
            },
        },
    )
    py.id = 129

    deduped = _dedupe_teacher_task_rows([pas, py])
    assert len(deduped) == 1
    kept, merged = deduped[0]
    assert kept.id == 1
    assert merged == ["cpp", "csharp", "java", "pascal", "python"]


def test_teacher_list_meta_without_chapter_key_does_not_compare_none():
    from application.tasks.services.catalog.task_teacher_list_meta import teacher_list_meta_for_row

    row = _row(
        title="Standalone",
        code_examples={"curriculum_showcase": {"slug": "custom_001"}},
    )
    row.id = 99
    meta = teacher_list_meta_for_row(row)
    assert meta.chapter_key is None
    assert meta.display_order is None


def test_dedupe_teacher_task_rows_sorts_by_chapter_order_without_error():
    """Regression: walrus in sort key raised UnboundLocalError on list_for_teacher."""
    low = _row(
        title="A",
        code_examples={
            "curriculum_showcase": {
                "collection_key": "ch_loops",
                "collection_chapter_rank": 2,
                "display_order": 20,
            }
        },
    )
    low.id = 10
    high = _row(
        title="B",
        code_examples={
            "curriculum_showcase": {
                "collection_key": "ch_vars",
                "collection_chapter_rank": 0,
                "display_order": 5,
            }
        },
    )
    high.id = 5

    deduped = _dedupe_teacher_task_rows([low, high])
    assert [row.id for row, _langs in deduped] == [5, 10]
    assert _teacher_list_sort_key(deduped[0])[0] <= _teacher_list_sort_key(deduped[1])[0]
