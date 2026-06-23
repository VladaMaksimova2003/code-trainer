"""Tests for in-process showcase task index cache invalidation."""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from application.curriculum.showcase import showcase_task_index as index_mod


def test_showcase_index_fingerprint_changes_when_task_updated_at_changes():
    first_updated = datetime(2024, 1, 1, tzinfo=timezone.utc)
    second_updated = datetime(2024, 1, 2, tzinfo=timezone.utc)

    session = SimpleNamespace(
        execute=lambda stmt: SimpleNamespace(one=lambda: (10, 100, first_updated))
    )
    first = index_mod._showcase_index_fingerprint(session)

    session.execute = lambda stmt: SimpleNamespace(one=lambda: (10, 100, second_updated))
    second = index_mod._showcase_index_fingerprint(session)
    assert first != second


def test_invalidate_showcase_task_index_cache_clears_process_cache():
    index_mod._process_cache = index_mod.ShowcaseTaskIndex()
    index_mod._process_cache_fingerprint = (1, 1, b"test")
    index_mod.invalidate_showcase_task_index_cache()
    assert index_mod._process_cache is None
    assert index_mod._process_cache_fingerprint is None
