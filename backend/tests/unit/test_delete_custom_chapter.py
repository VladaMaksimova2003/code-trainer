from __future__ import annotations

from types import SimpleNamespace

import pytest

from application.curriculum.chapters.curriculum_chapter_meta_service import delete_custom_chapter


class FakeSession:
    def __init__(self, row, task_count: int = 0) -> None:
        self.row = row
        self.task_count = task_count
        self.deleted = False

    def execute(self, _stmt):
        return SimpleNamespace(scalars=lambda: SimpleNamespace(first=lambda: self.row))

    def delete(self, row) -> None:
        self.deleted = True
        assert row is self.row

    def flush(self) -> None:
        return None


@pytest.fixture(autouse=True)
def patch_helpers(monkeypatch):
    monkeypatch.setattr(
        "application.curriculum.chapters.curriculum_chapter_meta_service._chapter_row",
        lambda _session, _lang, key: _session.row if _session.row and _session.row.chapter_key == key else None,
    )
    monkeypatch.setattr(
        "application.curriculum.chapters.curriculum_chapter_meta_service.count_tasks_for_chapter",
        lambda _session, _key: _session.task_count,
    )
    monkeypatch.setattr(
        "application.curriculum.chapters.curriculum_chapter_meta_service._invalidate_caches",
        lambda: None,
    )


def test_delete_custom_chapter_without_tasks():
    row = SimpleNamespace(chapter_key="my_chapter", is_custom=True)
    session = FakeSession(row, task_count=0)

    delete_custom_chapter(session, chapter_key="my_chapter", language="python")

    assert session.deleted is True


def test_delete_custom_chapter_rejects_registry():
    row = SimpleNamespace(chapter_key="loops", is_custom=False)
    session = FakeSession(row, task_count=0)

    with pytest.raises(ValueError, match="registry"):
        delete_custom_chapter(session, chapter_key="loops", language="python")


def test_delete_custom_chapter_rejects_nonempty():
    row = SimpleNamespace(chapter_key="my_chapter", is_custom=True)
    session = FakeSession(row, task_count=2)

    with pytest.raises(ValueError, match="tasks"):
        delete_custom_chapter(session, chapter_key="my_chapter", language="python")
