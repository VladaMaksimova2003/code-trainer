"""Tests for teacher-controlled chapter/task ordering."""

from __future__ import annotations

from types import SimpleNamespace

from application.curriculum.display.chapter_task_display_order import (
    effective_chapter_rank,
    merge_showcase_preserving_order,
    set_chapter_task_order,
    set_collection_chapter_order,
)
from application.tasks.services.catalog.task_teacher_list_meta import teacher_list_meta_for_row


def test_effective_chapter_rank_prefers_teacher_override():
    showcase = {"collection_chapter_rank": 50, "collection_key": "ch_loops"}
    assert effective_chapter_rank(showcase, default=3) == 50


def test_teacher_list_meta_uses_collection_chapter_rank():
    row = SimpleNamespace(
        task_type="task_translate_full_program",
        code_examples={
            "curriculum_showcase": {
                "collection_key": "ch_loops",
                "collection_chapter_rank": 50,
                "display_order": 10,
            }
        },
    )
    meta = teacher_list_meta_for_row(row)
    assert meta.chapter_order == 50


def test_set_collection_chapter_order_writes_rank_to_all_tasks(monkeypatch):
    rows = [
        SimpleNamespace(
            id=1,
            teacher_id=7,
            is_delete=False,
            code_examples={
                "curriculum_showcase": {"collection_key": "ch_a", "slot_id": "pas_1"}
            },
        ),
        SimpleNamespace(
            id=2,
            teacher_id=7,
            is_delete=False,
            code_examples={
                "curriculum_showcase": {"collection_key": "ch_b", "slot_id": "pas_2"}
            },
        ),
    ]

    class FakeSession:
        def commit(self) -> None:
            return None

    def fake_iter(_db):
        for row in rows:
            showcase = row.code_examples["curriculum_showcase"]
            yield row, showcase

    monkeypatch.setattr(
        "application.curriculum.mirror.pedagogical_task_store.iter_showcase_tasks",
        fake_iter,
    )
    monkeypatch.setattr(
        "application.curriculum.showcase.showcase_task_index.invalidate_showcase_task_index_cache",
        lambda: None,
    )
    monkeypatch.setattr(
        "application.curriculum.display.chapter_task_display_order.flag_modified",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "application.curriculum.chapters.curriculum_chapter_meta_service.persist_chapter_sort_orders",
        lambda *_args, **_kwargs: None,
    )

    ordered = set_collection_chapter_order(
        FakeSession(),
        teacher_id=7,
        ordered_chapter_keys=["ch_b", "ch_a"],
    )
    assert ordered == ["ch_b", "ch_a"]
    assert rows[0].code_examples["curriculum_showcase"]["collection_chapter_rank"] == 20
    assert rows[1].code_examples["curriculum_showcase"]["collection_chapter_rank"] == 10


def test_merge_showcase_preserving_order_keeps_teacher_rank():
    previous = {"display_order": 30, "collection_chapter_rank": 10, "primary_action": "assemble"}
    updated = {"primary_action": "debug"}
    merged = merge_showcase_preserving_order(previous, updated)
    assert merged["display_order"] == 30
    assert merged["collection_chapter_rank"] == 10
    assert merged["primary_action"] == "debug"


def test_student_showcase_task_sort_key_uses_display_order():
    from application.curriculum.display.chapter_task_display_order import student_showcase_task_sort_key

    items = [
        {"task_id": 2, "title": "B", "display_order": 20, "action": "implement"},
        {"task_id": 1, "title": "A", "display_order": 10, "action": "assemble"},
    ]
    ordered = sorted(items, key=student_showcase_task_sort_key)
    assert [item["task_id"] for item in ordered] == [1, 2]


def test_pedagogical_sort_blocks_before_debug_before_write():
    from application.curriculum.display.chapter_task_display_order import student_showcase_task_sort_key

    items = [
        {"task_id": 3, "title": "Write", "display_order": 30, "action": "translate"},
        {"task_id": 1, "title": "Blocks", "display_order": 10, "action": "assemble"},
        {"task_id": 2, "title": "Fix", "display_order": 20, "action": "debug"},
    ]
    ordered = sorted(items, key=student_showcase_task_sort_key)
    assert [item["task_id"] for item in ordered] == [1, 2, 3]


def test_wrong_legacy_action_order_puts_debug_after_write():
    """Regression: python/pascal showcase used translate→assemble→implement→debug."""
    wrong_order = ("translate", "assemble", "implement", "analyze", "debug", "recognize")

    def wrong_key(action: str | None) -> int:
        if not action:
            return len(wrong_order)
        try:
            return wrong_order.index(action)
        except ValueError:
            return len(wrong_order)

    from application.curriculum.display.chapter_task_display_order import student_showcase_task_sort_key

    items = [
        {"task_id": 54, "title": "Бинарный поиск рекурсией", "display_order": 540, "action": "debug"},
        {"task_id": 49, "title": "Факториал", "display_order": 490, "action": "implement"},
        {"task_id": 51, "title": "Рекурсивная сумма массива", "display_order": 510, "action": "assemble"},
    ]
    wrong = sorted(items, key=lambda item: student_showcase_task_sort_key(item, action_sort_key=wrong_key))
    correct = sorted(items, key=student_showcase_task_sort_key)
    assert [item["task_id"] for item in wrong] == [51, 49, 54]
    assert [item["task_id"] for item in correct] == [51, 54, 49]


def test_capstone_task_always_last():
    from application.curriculum.display.chapter_task_display_order import student_showcase_task_sort_key

    items = [
        {"task_id": 8, "title": "Итоговая: проект", "display_order": 80, "action": "assemble"},
        {"task_id": 7, "title": "Перевод", "display_order": 70, "action": "translate"},
        {"task_id": 1, "title": "Сборка", "display_order": 10, "action": "assemble"},
    ]
    ordered = sorted(items, key=student_showcase_task_sort_key)
    assert [item["task_id"] for item in ordered] == [1, 7, 8]


def test_algo_basics_catalog_pedagogical_order():
    from scripts.algo_v128_catalog import _TASK_INDEX

    basics = [row for row in _TASK_INDEX if row["chapter_key"] == "algo_basics"]
    assert len(basics) == 8
    assert [row["action"] for row in basics] == [
        "assemble",
        "assemble",
        "assemble",
        "assemble",
        "debug",
        "debug",
        "implement",
        "implement",
    ]
    assert [row["difficulty"] for row in basics] == [
        "easy",
        "easy",
        "easy",
        "easy",
        "easy",
        "easy",
        "easy",
        "medium",
    ]


def test_set_chapter_task_order_writes_display_order(monkeypatch):
    row = SimpleNamespace(
        id=11,
        teacher_id=3,
        is_delete=False,
        code_examples={
            "curriculum_showcase": {"collection_key": "ch_arrays", "slot_id": "pas_3"}
        },
    )

    class FakeSession:
        def get(self, _model, task_id):
            assert task_id == 11
            return row

        def commit(self) -> None:
            return None

    monkeypatch.setattr(
        "application.curriculum.mirror.pedagogical_task_store.unified_pedagogical_slot_key",
        lambda _showcase: None,
    )
    monkeypatch.setattr(
        "application.curriculum.mirror.pedagogical_task_store.iter_showcase_tasks",
        lambda _db: iter([]),
    )
    monkeypatch.setattr(
        "application.curriculum.showcase.showcase_task_index.invalidate_showcase_task_index_cache",
        lambda: None,
    )
    monkeypatch.setattr(
        "application.curriculum.display.chapter_task_display_order.flag_modified",
        lambda *_args, **_kwargs: None,
    )

    ordered = set_chapter_task_order(
        FakeSession(),
        teacher_id=3,
        chapter_key="ch_arrays",
        ordered_task_ids=[11],
    )
    assert ordered == [11]
    assert row.code_examples["curriculum_showcase"]["display_order"] == 10
