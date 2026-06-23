"""Teacher-controlled task order inside a curriculum chapter."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from infrastructure.db.models.task import Task as TaskModel

_ALGO_SLOT_RE = re.compile(r"^(?:pas|py|cpp|java|csharp|plh|pyk|cpk|psk)_(\d+)$", re.IGNORECASE)

# Study order inside a chapter: blocks → fix → write; capstone always last.
SHOWCASE_PEDAGOGICAL_ACTION_ORDER = (
    "assemble",
    "debug",
    "translate",
    "implement",
    "analyze",
    "recognize",
)

_CAPSTONE_TITLE_RE = re.compile(r"итоговая", re.IGNORECASE)


def pedagogical_action_sort_key(action: str | None) -> int:
    if not action:
        return len(SHOWCASE_PEDAGOGICAL_ACTION_ORDER)
    normalized = str(action).strip().lower()
    try:
        return SHOWCASE_PEDAGOGICAL_ACTION_ORDER.index(normalized)
    except ValueError:
        return len(SHOWCASE_PEDAGOGICAL_ACTION_ORDER)


def is_capstone_title(title: str) -> bool:
    return bool(_CAPSTONE_TITLE_RE.search(str(title or "").strip()))


def is_capstone_showcase_row(row: dict[str, Any]) -> bool:
    from application.curriculum.display.showcase_display import strip_showcase_title_prefix

    title = str(row.get("title") or "")
    return is_capstone_title(strip_showcase_title_prefix(title))


def compute_pedagogical_display_order(
    *,
    title: str,
    action: str | None,
    task_num: int,
) -> int:
    """Persisted order: action tier first, capstone pinned to the end."""
    if is_capstone_title(title):
        return 900_000 + int(task_num) * 10
    tier = pedagogical_action_sort_key(action)
    return tier * 10_000 + int(task_num) * 10


def showcase_pedagogical_sort_key(row: dict[str, Any]) -> tuple[int, int, int, int]:
    action = row.get("action") or row.get("primary_action")
    return (
        1 if is_capstone_showcase_row(row) else 0,
        pedagogical_action_sort_key(str(action or "")),
        effective_display_order_for_row(row),
        int(row.get("task_id") or 0),
    )


def default_display_order_from_showcase(showcase: dict[str, Any]) -> int:
    raw = showcase.get("display_order")
    if raw is not None:
        try:
            return int(raw)
        except (TypeError, ValueError):
            pass
    task_num = showcase.get("task_num")
    if task_num is not None:
        try:
            return int(task_num) * 10
        except (TypeError, ValueError):
            pass
    slot = str(showcase.get("slot_id") or showcase.get("slug") or "").strip()
    match = _ALGO_SLOT_RE.match(slot)
    if match:
        return int(match.group(1)) * 10
    return 999_999


def effective_display_order(showcase: dict[str, Any]) -> int:
    return default_display_order_from_showcase(showcase)


def effective_display_order_for_row(row: dict[str, Any]) -> int:
    raw = row.get("display_order")
    if raw is not None:
        try:
            return int(raw)
        except (TypeError, ValueError):
            pass
    return 999_999


def showcase_row_sort_key(
    row: dict[str, Any],
    *,
    tc_index: dict[str, int],
    spec_index: dict[str, int],
    action_sort_key,
) -> tuple[int, int, int, int, int, int]:
    capstone, action_rank, display_order, task_id = showcase_pedagogical_sort_key(row)
    if action_sort_key is not pedagogical_action_sort_key:
        action_rank = action_sort_key(row.get("action"))
    return (
        capstone,
        action_rank,
        tc_index.get(str(row.get("technical_concept_id") or ""), 999),
        display_order,
        spec_index.get(str(row.get("slug") or ""), 999),
        task_id,
    )


def student_showcase_task_sort_key(
    item: dict[str, Any],
    *,
    action_sort_key=None,
) -> tuple[int, int, int, int, str]:
    """Sort student task cards: capstone last, then action tier, then catalog order."""
    rank_fn = action_sort_key or pedagogical_action_sort_key
    capstone = 1 if is_capstone_showcase_row(item) else 0
    return (
        capstone,
        rank_fn(item.get("action")),
        effective_display_order_for_row(item),
        int(item.get("task_id") or 0),
        str(item.get("title") or ""),
    )


_ORDER_PRESERVE_FIELDS = ("display_order", "collection_chapter_rank")


def merge_showcase_preserving_order(
    previous: dict[str, Any] | None,
    updated: dict[str, Any],
) -> dict[str, Any]:
    """Keep teacher-defined chapter/task order when showcase metadata is rewritten."""
    merged = dict(updated)
    if not isinstance(previous, dict):
        return merged
    for field in _ORDER_PRESERVE_FIELDS:
        if merged.get(field) is None and previous.get(field) is not None:
            merged[field] = previous[field]
    return merged


def sync_showcase_order_fields_across_mirror_group(
    db: Session,
    row: TaskModel,
) -> None:
    """Ensure every mirror row for the slot shares the same persisted order fields."""
    from application.curriculum.mirror.pedagogical_task_store import (
        iter_showcase_tasks,
        unified_pedagogical_slot_key,
    )

    showcase = dict((row.code_examples or {}).get("curriculum_showcase") or {})
    unified = unified_pedagogical_slot_key(showcase)
    if not unified:
        return

    siblings: list[TaskModel] = []
    for sibling_row, sibling_showcase in iter_showcase_tasks(db):
        if sibling_row.teacher_id != row.teacher_id:
            continue
        if unified_pedagogical_slot_key(sibling_showcase) == unified:
            siblings.append(sibling_row)
    if not siblings:
        return

    best_order: int | None = None
    best_chapter_rank: int | None = None
    for sibling_row in siblings:
        sibling_showcase = dict((sibling_row.code_examples or {}).get("curriculum_showcase") or {})
        raw_order = sibling_showcase.get("display_order")
        if raw_order is not None:
            try:
                order_value = int(raw_order)
            except (TypeError, ValueError):
                order_value = None
            if order_value is not None:
                if best_order is None or order_value < best_order:
                    best_order = order_value
        raw_rank = sibling_showcase.get("collection_chapter_rank")
        if raw_rank is not None:
            try:
                rank_value = int(raw_rank)
            except (TypeError, ValueError):
                rank_value = None
            if rank_value is not None:
                if best_chapter_rank is None or rank_value < best_chapter_rank:
                    best_chapter_rank = rank_value

    for sibling_row in siblings:
        sibling_showcase = dict((sibling_row.code_examples or {}).get("curriculum_showcase") or {})
        changed = False
        if best_order is not None and sibling_showcase.get("display_order") != best_order:
            sibling_showcase["display_order"] = best_order
            changed = True
        if best_chapter_rank is not None and sibling_showcase.get("collection_chapter_rank") != best_chapter_rank:
            sibling_showcase["collection_chapter_rank"] = best_chapter_rank
            changed = True
        if not changed:
            continue
        examples = dict(sibling_row.code_examples or {})
        examples["curriculum_showcase"] = sibling_showcase
        sibling_row.code_examples = examples
        flag_modified(sibling_row, "code_examples")


def effective_chapter_rank(showcase: dict[str, Any], *, default: int | None = None) -> int | None:
    raw = showcase.get("collection_chapter_rank")
    if raw is not None:
        try:
            return int(raw)
        except (TypeError, ValueError):
            pass
    return default


def _write_showcase_field(task_row: TaskModel, field: str, value: int) -> None:
    examples = dict(task_row.code_examples or {})
    showcase = dict(examples.get("curriculum_showcase") or {})
    showcase[field] = int(value)
    examples["curriculum_showcase"] = showcase
    task_row.code_examples = examples
    flag_modified(task_row, "code_examples")
    if hasattr(task_row, "updated_at"):
        task_row.updated_at = datetime.now(timezone.utc)


def _write_display_order(task_row: TaskModel, display_order: int) -> None:
    _write_showcase_field(task_row, "display_order", display_order)


def _write_collection_chapter_rank(task_row: TaskModel, chapter_rank: int) -> None:
    _write_showcase_field(task_row, "collection_chapter_rank", chapter_rank)


def set_chapter_task_order(
    db: Session,
    *,
    teacher_id: int,
    chapter_key: str,
    ordered_task_ids: list[int],
) -> list[int]:
    from application.curriculum.mirror.pedagogical_task_store import (
        iter_showcase_tasks,
        unified_pedagogical_slot_key,
    )

    normalized_chapter = chapter_key.strip()
    if not normalized_chapter:
        raise ValueError("chapter_key is required")
    if not ordered_task_ids:
        raise ValueError("task_ids must not be empty")

    canonical_rows: dict[int, TaskModel] = {}
    for task_id in ordered_task_ids:
        row = db.get(TaskModel, int(task_id))
        if row is None or row.is_delete:
            raise ValueError(f"Task {task_id} not found")
        if row.teacher_id != teacher_id:
            raise ValueError(f"Task {task_id} does not belong to this teacher")
        showcase = (row.code_examples or {}).get("curriculum_showcase")
        if not isinstance(showcase, dict):
            raise ValueError(f"Task {task_id} is not a curriculum task")
        row_chapter = str(showcase.get("collection_key") or "").strip()
        if row_chapter != normalized_chapter:
            raise ValueError(f"Task {task_id} belongs to chapter {row_chapter!r}, not {normalized_chapter!r}")
        canonical_rows[int(task_id)] = row

    unified_by_canonical: dict[int, str | None] = {}
    for task_id, row in canonical_rows.items():
        showcase = dict((row.code_examples or {}).get("curriculum_showcase") or {})
        unified_by_canonical[task_id] = unified_pedagogical_slot_key(showcase)

    mirror_rows_by_unified: dict[str, list[TaskModel]] = {}
    for row, showcase in iter_showcase_tasks(db):
        if row.teacher_id != teacher_id:
            continue
        unified = unified_pedagogical_slot_key(showcase)
        if not unified:
            continue
        mirror_rows_by_unified.setdefault(unified, []).append(row)

    for order_index, task_id in enumerate(ordered_task_ids):
        display_order = (order_index + 1) * 10
        row = canonical_rows[int(task_id)]
        unified = unified_by_canonical.get(int(task_id))
        targets = [row]
        if unified:
            targets = mirror_rows_by_unified.get(unified, [row])
        for target in targets:
            _write_display_order(target, display_order)

    db.commit()

    from application.curriculum.showcase.showcase_task_index import invalidate_showcase_task_index_cache

    invalidate_showcase_task_index_cache()
    return [int(task_id) for task_id in ordered_task_ids]


def set_collection_chapter_order(
    db: Session,
    *,
    teacher_id: int,
    ordered_chapter_keys: list[str],
) -> list[str]:
    """Persist teacher-defined chapter order inside curriculum collections."""
    from application.curriculum.mirror.pedagogical_task_store import iter_showcase_tasks

    normalized_keys = [str(key).strip() for key in ordered_chapter_keys if str(key).strip()]
    if not normalized_keys:
        raise ValueError("chapter_keys must not be empty")

    rank_by_key = {
        chapter_key: (order_index + 1) * 10
        for order_index, chapter_key in enumerate(normalized_keys)
    }
    allowed = set(rank_by_key)

    updated = 0
    for row, showcase in iter_showcase_tasks(db):
        if row.teacher_id != teacher_id:
            continue
        chapter_key = str(showcase.get("collection_key") or "").strip()
        if chapter_key not in allowed:
            continue
        _write_collection_chapter_rank(row, rank_by_key[chapter_key])
        updated += 1

    if updated == 0:
        raise ValueError("No curriculum tasks found for the requested chapters")

    from application.curriculum.chapters.curriculum_chapter_meta_service import (
        persist_chapter_sort_orders,
    )

    persist_chapter_sort_orders(db, teacher_id=teacher_id, rank_by_key=rank_by_key)

    db.commit()

    from application.curriculum.showcase.showcase_task_index import invalidate_showcase_task_index_cache

    invalidate_showcase_task_index_cache()
    return normalized_keys
