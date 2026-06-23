"""Default runtime course scope is 128 tasks (16 chapters × 8)."""

from __future__ import annotations

from application.curriculum.course_scope import (
    active_chapter_task_count,
    active_collection_targets,
    active_target_task_count,
    get_course_scope,
    iter_tasks_in_scope,
)
from application.curriculum.shared.algo_v128_showcase import curriculum_catalog_tasks_total


def test_default_scope_is_128(monkeypatch):
    monkeypatch.delenv("COURSE_SCOPE", raising=False)
    assert get_course_scope() == "128"
    assert active_target_task_count() == 128
    assert active_chapter_task_count() == 8
    assert sum(active_collection_targets().values()) == 128
    assert curriculum_catalog_tasks_total() == 128


def test_pascal_catalog_respects_default_scope():
    from application.curriculum.pascal.catalog import pascal_curriculum_v3_catalog as catalog
    from application.curriculum.pascal.showcase import pascal_v311_registry as registry

    assert catalog.V311_TOTAL_TASKS == 128
    records = catalog.all_v311_task_records()
    assert len(records) == 128
    assert sum(registry.V311_COLLECTION_TARGETS.values()) == 128
    assert catalog.validate_v311_catalog() == []


def test_iter_tasks_in_scope_filters_expansion():
    from pascal_v31_tasks import V31_TASKS

    scoped = iter_tasks_in_scope(V31_TASKS)
    assert len(scoped) == 128
    assert scoped[-1][5] == "task_128"
