"""Request-scoped prefetch index for curriculum showcase tasks."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import Any, TypeVar

from application.curriculum.cpp.showcase.cpp_v311_registry import CPP_V311_SHOWCASE_COLLECTIONS
from application.curriculum.csharp.showcase.csharp_v311_registry import CSHARP_V311_SHOWCASE_COLLECTIONS
from application.curriculum.java.showcase.java_v311_registry import JAVA_V311_SHOWCASE_COLLECTIONS
from application.curriculum.pascal.showcase.pascal_v311_registry import PASCAL_V311_SHOWCASE_COLLECTIONS
from application.curriculum.python.showcase.python_v311_registry import PYTHON_V311_SHOWCASE_COLLECTIONS
from application.curriculum.task_curriculum_link_service import TaskCurriculumLinkService

PASCAL_V311_TITLE_ROOT = "[Pascal v3.1.1:"
PYTHON_V1_TITLE_ROOT = "[Python v1:"
_INDEX_BUILD_VERSION = 3

_index_var: ContextVar["ShowcaseTaskIndex | None"] = ContextVar("showcase_task_index", default=None)
_process_cache: ShowcaseTaskIndex | None = None
_process_cache_fingerprint: tuple[int, int, bytes] | None = None

T = TypeVar("T")


def get_showcase_task_index() -> ShowcaseTaskIndex | None:
    return _index_var.get()


def _showcase_index_fingerprint(session) -> tuple[int, int, bytes]:
    """Cheap invalidation signal — full index build still scans showcase tasks once."""
    from sqlalchemy import func, select

    from infrastructure.db.models.task.task import Task as TaskModel

    count, max_id, max_updated = session.execute(
        select(
            func.count(TaskModel.id),
            func.max(TaskModel.id),
            func.max(TaskModel.updated_at),
        ).where(TaskModel.is_delete.is_(False))
    ).one()
    payload = (
        f"index-v{_INDEX_BUILD_VERSION}|{int(count or 0)}|{int(max_id or 0)}|{max_updated}\n"
    )
    return int(count or 0), int(max_id or 0), hashlib.sha256(payload.encode("utf-8")).digest()


def activate_showcase_task_index(session) -> Token:
    global _process_cache, _process_cache_fingerprint

    fingerprint = _showcase_index_fingerprint(session)
    if _process_cache is None or _process_cache_fingerprint != fingerprint:
        _process_cache = ShowcaseTaskIndex.build(session)
        _process_cache_fingerprint = fingerprint
    return _index_var.set(_process_cache)


def reset_showcase_task_index(token: Token) -> None:
    _index_var.reset(token)


def run_with_showcase_task_index(session, fn: Callable[[], T]) -> T:
    token = activate_showcase_task_index(session)
    try:
        return fn()
    finally:
        reset_showcase_task_index(token)


def invalidate_showcase_task_index_cache() -> None:
    """Drop process cache after task seed/migration (tests)."""
    global _process_cache, _process_cache_fingerprint
    _process_cache = None
    _process_cache_fingerprint = None
    from application.curriculum.mirror.pedagogical_task_store import invalidate_showcase_tasks_cache

    invalidate_showcase_tasks_cache()


@dataclass
class ShowcaseTaskIndex:
    _by_key: dict[tuple[str, str, str], list[dict[str, Any]]] = field(default_factory=dict)

    @classmethod
    def build(cls, session) -> ShowcaseTaskIndex:
        from application.curriculum.mirror.pedagogical_task_store import (
            iter_showcase_tasks,
            language_track,
            showcase_matches_collection,
            track_slug,
        )

        index = cls()
        collection_defs: list[tuple[str, str, str, str]] = []
        for col in PASCAL_V311_SHOWCASE_COLLECTIONS:
            collection_defs.append(("pascal", col.chapter_key, col.showcase_group, "3.1.1"))
        for col in PYTHON_V311_SHOWCASE_COLLECTIONS:
            collection_defs.append(("python", col.chapter_key, col.showcase_group, "1.0"))
        for col in CPP_V311_SHOWCASE_COLLECTIONS:
            collection_defs.append(("cpp", col.chapter_key, col.showcase_group, "1.0"))
        for col in CSHARP_V311_SHOWCASE_COLLECTIONS:
            collection_defs.append(("csharp", col.chapter_key, col.showcase_group, "1.0"))
        for col in JAVA_V311_SHOWCASE_COLLECTIONS:
            collection_defs.append(("java", col.chapter_key, col.showcase_group, "1.0"))

        rows = iter_showcase_tasks(session)
        link_service = TaskCurriculumLinkService(session)
        task_ids = [row.id for row, _ in rows]
        primary_by_task_lang = link_service.get_primary_links_index(task_ids)

        from application.curriculum.course_scope import showcase_row_in_scope

        for lang, col_key, group, version in collection_defs:
            for row, showcase in rows:
                if not showcase_row_in_scope(row, showcase):
                    continue
                if not language_track(showcase, lang):
                    continue
                if not showcase_matches_collection(
                    showcase,
                    language=lang,
                    collection_key=col_key,
                    group=group,
                ):
                    continue
                track = language_track(showcase, lang) or {}
                primary = primary_by_task_lang.get((row.id, lang))
                from application.curriculum.showcase.showcase_collection_tasks import (
                    build_showcase_collection_task_row,
                )

                payload = build_showcase_collection_task_row(
                    row=row,
                    showcase=showcase,
                    language=lang,
                    collection_key=col_key,
                    primary=primary,
                )
                key = (lang, col_key, version)
                index._by_key.setdefault(key, []).append(payload)

        from application.curriculum.showcase.showcase_row_dedupe import dedupe_collection_task_payloads

        for key, payloads in list(index._by_key.items()):
            index._by_key[key] = dedupe_collection_task_payloads(payloads, language=key[0])

        return index

    def chapter_task_counts(self) -> dict[str, int]:
        """Unique showcase tasks per collection_key (all language tracks)."""
        from collections import defaultdict

        seen: dict[str, set[int]] = defaultdict(set)
        for rows in self._by_key.values():
            for row in rows:
                chapter_key = str(
                    row.get("collection_key") or row.get("chapter_key") or ""
                ).strip()
                task_id = row.get("task_id")
                if chapter_key and task_id is not None:
                    seen[chapter_key].add(int(task_id))
        return {key: len(task_ids) for key, task_ids in seen.items()}

    def list_for_collection(
        self,
        language: str,
        collection_key: str,
        *,
        curriculum_version: str | int,
    ) -> list[dict[str, Any]] | None:
        key = (language, collection_key, str(curriculum_version))
        rows = self._by_key.get(key)
        if rows is None:
            return None
        from application.curriculum.showcase.showcase_row_dedupe import dedupe_collection_task_payloads

        return dedupe_collection_task_payloads(list(rows), language=language)
