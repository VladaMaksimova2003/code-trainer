"""Runtime course scope: 128 (MVP core) or 192 (full v192-B expansion).

Set ``COURSE_SCOPE=192`` to ship the full 192-task catalog; default is ``128``.
"""

from __future__ import annotations

import os
import re
from typing import Any, Iterable, Literal, TypeVar

DefenseScope = Literal["128", "192"]

_PATTERN_NUM = re.compile(r"^task_(\d+)$")
_SLOT_NUM = re.compile(r"^(?:pas|py|cpp|cs|java)_(\d+)$", re.IGNORECASE)
_TaskRow = TypeVar("_TaskRow")


def get_course_scope() -> DefenseScope:
    raw = os.environ.get("COURSE_SCOPE", "128").strip()
    if raw not in {"128", "192"}:
        return "128"
    return raw  # type: ignore[return-value]


def pattern_num(pattern_id: str) -> int | None:
    match = _PATTERN_NUM.match(str(pattern_id or "").strip())
    return int(match.group(1)) if match else None


def active_target_task_count() -> int:
    if get_course_scope() == "192":
        try:
            from algo_v192_plan import V192_TARGET_TASK_COUNT

            return int(V192_TARGET_TASK_COUNT)
        except ImportError:
            pass
    try:
        from algo_v128_catalog import V128_CORE_TASK_COUNT

        return int(V128_CORE_TASK_COUNT)
    except ImportError:
        return 128


def active_chapter_task_count() -> int:
    return 12 if get_course_scope() == "192" else 8


def active_collection_targets() -> dict[str, int]:
    from application.curriculum.shared.algo_v128_showcase import (
        V128_CHAPTER_KEYS,
        V128_COLLECTION_TARGETS,
    )

    if get_course_scope() == "192":
        try:
            from algo_v192_plan import V192_COLLECTION_TARGETS

            return dict(V192_COLLECTION_TARGETS)
        except ImportError:
            pass
    return {key: V128_COLLECTION_TARGETS.get(key, 8) for key in V128_CHAPTER_KEYS}


def _pattern_in_core_index(pattern_id: str, *, limit: int) -> bool:
    """True when pattern_id is wired to a shipped slot (e.g. task_129 at pas_007)."""
    try:
        from algo_v128_catalog import _TASK_INDEX
    except ImportError:
        return False
    key = str(pattern_id or "").strip()
    if not key:
        return False
    for row in _TASK_INDEX:
        if int(row.get("task_num") or 0) > limit:
            continue
        if str(row.get("pattern_id") or "").strip() == key:
            return True
    return False


def task_pattern_in_scope(pattern_id: str) -> bool:
    num = pattern_num(pattern_id)
    if num is None:
        return True
    limit = active_target_task_count()
    if num <= limit:
        return True
    return _pattern_in_core_index(pattern_id, limit=limit)


def iter_tasks_in_scope(rows: Iterable[_TaskRow]) -> tuple[_TaskRow, ...]:
    return tuple(row for row in rows if task_pattern_in_scope(str(row[5])))


def slot_num(slot_id: str) -> int | None:
    match = _SLOT_NUM.match(str(slot_id or "").strip())
    return int(match.group(1)) if match else None


def slot_id_in_scope(slot_id: str) -> bool:
    num = slot_num(slot_id)
    if num is None:
        return True
    return num <= active_target_task_count()


def _core_task_num_for_pattern(pattern_id: str) -> int | None:
    try:
        from algo_v128_catalog import _TASK_INDEX
    except ImportError:
        return None
    key = str(pattern_id or "").strip()
    for row in _TASK_INDEX:
        if str(row.get("pattern_id") or "").strip() == key:
            return int(row.get("task_num") or 0)
    return None


def _expansion_pattern_allowed_for_slot(pattern_id: str, slot_id: str) -> bool:
    """Patterns above the core limit must use their catalog slot (task_129 → *_007)."""
    num = pattern_num(pattern_id)
    if num is None or num <= active_target_task_count():
        return True
    if not _pattern_in_core_index(pattern_id, limit=active_target_task_count()):
        return False
    expected = _core_task_num_for_pattern(pattern_id)
    if expected is None or expected <= 0:
        return False
    actual = slot_num(slot_id)
    return actual == expected


def showcase_pattern_from_payload(showcase: dict[str, Any]) -> str:
    return str(
        showcase.get("exercise_pattern_id")
        or showcase.get("slot_pattern_id")
        or ""
    ).strip()


def showcase_row_in_scope(row: Any, showcase: dict[str, Any]) -> bool:
    """Hide v192-B expansion slots (task_129+) from student collection views."""
    pattern = showcase_pattern_from_payload(showcase)
    slot = str(showcase.get("slot_id") or showcase.get("slug") or "").strip()
    if pattern and slot and not _expansion_pattern_allowed_for_slot(pattern, slot):
        return False
    if pattern:
        return task_pattern_in_scope(pattern)
    if slot:
        return slot_id_in_scope(slot)
    row_id = getattr(row, "id", None)
    if row_id is not None:
        return int(row_id) <= active_target_task_count()
    return True


def filter_showcase_matches_in_scope(
    matched: Iterable[tuple[Any, dict[str, Any]]],
) -> list[tuple[Any, dict[str, Any]]]:
    return [(row, showcase) for row, showcase in matched if showcase_row_in_scope(row, showcase)]


def curriculum_task_in_scope(task: Any) -> bool:
    """Keep teacher/custom tasks; drop out-of-scope algorithm-syntax showcase rows."""
    examples = task.code_examples if isinstance(getattr(task, "code_examples", None), dict) else {}
    showcase = examples.get("curriculum_showcase") if isinstance(examples, dict) else None
    if not isinstance(showcase, dict) or not showcase:
        return True
    return showcase_row_in_scope(task, showcase)


def filter_task_ids_to_course_scope(task_ids: Iterable[int], session: Any) -> set[int]:
    """Drop expansion unified task ids when DB still contains a 192-B seed."""
    from sqlalchemy import select

    from infrastructure.db.models.task.task import Task as TaskModel

    ids = {int(tid) for tid in task_ids}
    if get_course_scope() == "192":
        return ids
    limit = active_target_task_count()
    over = sorted(tid for tid in ids if tid > limit)
    if not over:
        return ids
    rows = session.execute(select(TaskModel).where(TaskModel.id.in_(over))).scalars().all()
    hidden: set[int] = set()
    for row in rows:
        if not curriculum_task_in_scope(row):
            hidden.add(int(row.id))
    return ids - hidden
