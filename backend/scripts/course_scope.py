"""Defense stand scope: 128 (MVP core) vs 192 (192-B full catalog)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

DefenseScope = Literal["128", "192"]

_PATTERN_NUM = re.compile(r"^task_(\d+)$")


def parse_scope(value: str) -> DefenseScope:
    normalized = str(value).strip()
    if normalized not in {"128", "192"}:
        raise ValueError(f"unsupported scope {value!r}; use 128 or 192")
    return normalized  # type: ignore[return-value]


def scope_target_count(scope: DefenseScope) -> int:
    from algo_v192_plan import V128_CORE_TASK_COUNT, V192_TARGET_TASK_COUNT

    return V128_CORE_TASK_COUNT if scope == "128" else V192_TARGET_TASK_COUNT


def scope_chapter_task_count(scope: DefenseScope) -> int:
    return 8 if scope == "128" else 12


def scope_collection_targets(scope: DefenseScope) -> dict[str, int]:
    from algo_v192_plan import V128_CHAPTER_KEYS, V192_COLLECTION_TARGETS
    from application.curriculum.shared.algo_v128_showcase import V128_COLLECTION_TARGETS

    per_chapter = scope_chapter_task_count(scope)
    if scope == "192":
        return dict(V192_COLLECTION_TARGETS)
    return {key: per_chapter for key in V128_CHAPTER_KEYS}


def pattern_num(pattern_id: str) -> int | None:
    match = _PATTERN_NUM.match(str(pattern_id or "").strip())
    return int(match.group(1)) if match else None


def demo_slots_for_scope(scope: DefenseScope) -> tuple[str, ...]:
    from validate_defense_demo_slots import DEMO_SLOTS

    limit = scope_target_count(scope)
    slots: list[str] = []
    for item in DEMO_SLOTS:
        num = pattern_num(item["pattern"])
        if num is not None and num <= limit:
            slots.append(item["slot"])
    return tuple(slots)


def validate_catalog_scope(scope: DefenseScope) -> list[str]:
    """Validate shipped catalog metadata for the chosen defense scope."""
    errors: list[str] = []
    target = scope_target_count(scope)

    from algo_v128_catalog import ALGO_SYNTAX_META, V128_CORE_TASK_COUNT, build_task_rows
    from algo_v192_plan import COURSE_VARIANT, V192_TARGET_TASK_COUNT

    core_rows = build_task_rows("pas", include_expansion=False)
    if len(core_rows) != V128_CORE_TASK_COUNT:
        errors.append(
            f"v128 core rows: expected {V128_CORE_TASK_COUNT}, got {len(core_rows)}"
        )

    if scope == "192":
        full_rows = build_task_rows("pas", include_expansion=True)
        if len(full_rows) != V192_TARGET_TASK_COUNT:
            errors.append(
                f"pas build_task_rows: expected {V192_TARGET_TASK_COUNT}, got {len(full_rows)}"
            )
        from pascal_v31_tasks import V31_TASKS

        if len(V31_TASKS) != V128_CORE_TASK_COUNT:
            errors.append(
                f"pascal V31_TASKS: expected {V128_CORE_TASK_COUNT}, got {len(V31_TASKS)}"
            )
        from application.curriculum.pascal.catalog.pascal_curriculum_v3_catalog import (
            V311_TOTAL_TASKS,
            validate_v311_catalog,
        )
        from application.curriculum.pascal.showcase.pascal_v311_registry import (
            V311_COLLECTION_TARGETS,
        )

        if V311_TOTAL_TASKS != V192_TARGET_TASK_COUNT:
            errors.append(
                f"V311_TOTAL_TASKS: expected {V192_TARGET_TASK_COUNT}, got {V311_TOTAL_TASKS}"
            )
        if sum(V311_COLLECTION_TARGETS.values()) != V192_TARGET_TASK_COUNT:
            errors.append(
                "V311_COLLECTION_TARGETS sum != "
                f"{V192_TARGET_TASK_COUNT}: {sum(V311_COLLECTION_TARGETS.values())}"
            )
        errors.extend(validate_v311_catalog())
    else:
        targets = scope_collection_targets(scope)
        if sum(targets.values()) != target:
            errors.append(f"128 collection targets sum != {target}: {sum(targets.values())}")

    for task_num in range(1, target + 1):
        key = f"task_{task_num:03d}"
        if key not in ALGO_SYNTAX_META:
            errors.append(f"missing ALGO_SYNTAX_META[{key}]")

    if scope == "192" and COURSE_VARIANT != "192-B":
        errors.append(f"expected COURSE_VARIANT=192-B, got {COURSE_VARIANT!r}")

    return errors


@dataclass(frozen=True)
class DbScopeStats:
    showcase_rows: int
    max_task_id: int
    pattern_ids: frozenset[str]
    max_pattern_num: int

    def to_dict(self) -> dict[str, int | list[str]]:
        return {
            "showcase_rows": self.showcase_rows,
            "max_task_id": self.max_task_id,
            "pattern_count": len(self.pattern_ids),
            "max_pattern_num": self.max_pattern_num,
            "pattern_ids_sample": sorted(self.pattern_ids)[:5],
        }


def collect_db_scope_stats(session) -> DbScopeStats:
    from application.curriculum.mirror.pedagogical_task_store import iter_showcase_tasks

    pattern_ids: set[str] = set()
    max_task_id = 0
    max_pattern_num = 0
    count = 0

    for row, showcase in iter_showcase_tasks(session):
        count += 1
        max_task_id = max(max_task_id, int(row.id))
        pid = str(showcase.get("exercise_pattern_id") or "").strip()
        if pid:
            pattern_ids.add(pid)
            num = pattern_num(pid)
            if num is not None:
                max_pattern_num = max(max_pattern_num, num)

    return DbScopeStats(
        showcase_rows=count,
        max_task_id=max_task_id,
        pattern_ids=frozenset(pattern_ids),
        max_pattern_num=max_pattern_num,
    )


def validate_db_scope(scope: DefenseScope, session) -> list[str]:
    """Validate PostgreSQL showcase rows against defense scope."""
    errors: list[str] = []
    target = scope_target_count(scope)
    stats = collect_db_scope_stats(session)

    if stats.showcase_rows != target:
        errors.append(
            f"DB showcase rows: expected {target}, got {stats.showcase_rows} "
            f"(max_id={stats.max_task_id}, max_pattern={stats.max_pattern_num})"
        )
    if stats.max_task_id > target:
        errors.append(
            f"DB max task id {stats.max_task_id} exceeds scope {target}; "
            f"run purge_showcase_tasks_above_id.py --max-id {target}"
        )
    if stats.max_pattern_num > target:
        errors.append(
            f"DB max exercise_pattern_id task_{stats.max_pattern_num:03d} "
            f"exceeds scope {target}"
        )

    expected_patterns = {f"task_{n:03d}" for n in range(1, target + 1)}
    missing = sorted(expected_patterns - stats.pattern_ids)
    if missing:
        preview = ", ".join(missing[:5])
        suffix = "..." if len(missing) > 5 else ""
        errors.append(f"DB missing patterns ({len(missing)}): {preview}{suffix}")

    extra = sorted(
        pid for pid in stats.pattern_ids if (num := pattern_num(pid)) is not None and num > target
    )
    if extra:
        errors.append(f"DB has expansion patterns beyond scope: {', '.join(extra[:5])}")

    return errors


def scope_report(scope: DefenseScope) -> dict[str, object]:
    from algo_v192_plan import COURSE_VARIANT

    return {
        "scope": scope,
        "variant": COURSE_VARIANT if scope == "192" else "128-core",
        "target_tasks": scope_target_count(scope),
        "chapter_tasks": scope_chapter_task_count(scope),
        "chapters": len(scope_collection_targets(scope)),
        "demo_slots": list(demo_slots_for_scope(scope)),
    }
