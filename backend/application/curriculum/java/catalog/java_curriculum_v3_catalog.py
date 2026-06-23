"""Java Course v1 pedagogical catalog."""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from application.curriculum.java.catalog.java_v311_builder_mapping import (
    assignment_for_task_format,
    builder_for_task_format,
)
from application.curriculum.java.catalog.java_v311_content import build_task_extra
from application.curriculum.java.catalog.java_v311_expected_concepts import (
    expected_concept_ids_for_row,
)
from application.curriculum.java.showcase.java_v311_registry import (
    V311_CHAPTER_ORDER,
    V311_COLLECTION_TARGETS,
    v311_collection_by_key,
)
from application.curriculum.shared.algo_v128_showcase import CHAPTER_PRIMARY_TC, primary_tc_for_chapter

_SCRIPTS = Path(__file__).resolve().parents[4] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from application.curriculum.course_scope import (
    active_target_task_count,
    iter_tasks_in_scope,
)
from java_v31_tasks import V31_CHAPTER_TITLES, V31_TASKS  # noqa: E402

V311_TOTAL_TASKS = active_target_task_count()

LANG_PATTERN = re.compile(r"pascal|python|c#|csharp|c\+\+|cpp", re.I)
FORBIDDEN_FORMATS = frozenset({"сопоставление"})
FORBIDDEN_ACTIONS = frozenset({"analyze"})

CHAPTER_TC: dict[str, str] = {
    "program_skeleton":  "program_entry",
    "io":                "stdin_read",
    "conditions":        "simple_branch",
    "conditions_multi":  "multi_branch",
    "loops":             "counted_loop",
    "loops_adv":         "loop_control",
    "static_arrays":     "indexed_sequence",
    "dynamic_arrays":    "dynamic_array",
    "strings":           "string_sequence",
    "functions":         "function_definition",
    "recursion":         "recursion",
    "algorithms":        "search_find",
    "sorting":           "sort_order",
    "records":           "key_value_map",
    "files":             "file_read",
    "units":             "import_dependency",
    "data_structures":   "stack_queue",
    "functional":        "filter_select",
    "oop":               "class_type",
    "oop_state":         "object_instance",
    "oop_inherit":       "inheritance_hierarchy",
    **CHAPTER_PRIMARY_TC,
}


def _is_algo_syntax_slot(slot_id: str) -> bool:
    return bool(re.fullmatch(r"java_\d{3}", str(slot_id or "").strip()))


@dataclass(frozen=True)
class V311TaskRecord:
    slot_id: str
    chapter_key: str
    chapter_title: str
    title: str
    task_format: str
    primary_action: str
    exercise_pattern_id: str
    educational_goal: str
    java_features: str
    difficulty: str
    pascal_mirror: str


def _row_to_record(row: tuple) -> V311TaskRecord:
    slot_id, chapter, title, fmt, action, pattern, goal, features, diff, mirror = row
    return V311TaskRecord(
        slot_id=slot_id,
        chapter_key=chapter,
        chapter_title=V31_CHAPTER_TITLES[chapter],
        title=title,
        task_format=fmt,
        primary_action=action,
        exercise_pattern_id=pattern,
        educational_goal=goal,
        java_features=features,
        difficulty=diff,
        pascal_mirror=str(mirror or "").strip(),
    )


def all_v311_task_records() -> tuple[V311TaskRecord, ...]:
    return tuple(_row_to_record(row) for row in iter_tasks_in_scope(V31_TASKS))


def records_by_chapter() -> dict[str, tuple[V311TaskRecord, ...]]:
    grouped: dict[str, list[V311TaskRecord]] = {k: [] for k in V311_CHAPTER_ORDER}
    for rec in all_v311_task_records():
        grouped[rec.chapter_key].append(rec)
    return {k: tuple(grouped[k]) for k in V311_CHAPTER_ORDER}


def catalog_record_for_slot(slot_id: str) -> V311TaskRecord | None:
    for rec in all_v311_task_records():
        if rec.slot_id == slot_id:
            return rec
    return None


def catalog_title_for_slot(slot_id: str, *, with_prefix: bool = False) -> str | None:
    rec = catalog_record_for_slot(slot_id)
    if rec is None:
        return None
    if not with_prefix:
        return rec.title
    col = v311_collection_by_key(rec.chapter_key)
    prefix = col.title_prefix if col else "[Java v1: "
    return f"{prefix}{rec.title}"


def validate_v311_catalog() -> list[str]:
    errors: list[str] = []
    records = all_v311_task_records()
    if len(records) != V311_TOTAL_TASKS:
        errors.append(f"expected {V311_TOTAL_TASKS} tasks, got {len(records)}")

    slot_ids = [r.slot_id for r in records]
    if len(set(slot_ids)) != len(slot_ids):
        errors.append("duplicate slot_id detected")

    for rec in records:
        if rec.task_format in FORBIDDEN_FORMATS:
            errors.append(f"{rec.slot_id}: forbidden format")
        if rec.primary_action in FORBIDDEN_ACTIONS:
            errors.append(f"{rec.slot_id}: forbidden action analyze")
        if not rec.pascal_mirror and not _is_algo_syntax_slot(rec.slot_id):
            errors.append(f"{rec.slot_id}: missing pascal_mirror")

    for chapter, target in V311_COLLECTION_TARGETS.items():
        count = len(records_by_chapter().get(chapter, ()))
        if count != target:
            errors.append(f"chapter {chapter}: expected {target} tasks, got {count}")

    return errors


def catalog_summary() -> dict[str, int | str]:
    by_ch = records_by_chapter()
    mirror_count = sum(1 for r in all_v311_task_records() if r.pascal_mirror)
    return {
        "total_tasks": len(all_v311_task_records()),
        "mirror_attach_tasks": mirror_count,
        "chapters": len(by_ch),
    }


def record_to_spec_dict(rec: V311TaskRecord) -> dict:
    extra = build_task_extra(
        (
            rec.slot_id,
            rec.chapter_key,
            rec.title,
            rec.task_format,
            rec.primary_action,
            rec.exercise_pattern_id,
            rec.educational_goal,
            rec.java_features,
            rec.difficulty,
            rec.pascal_mirror,
        )
    )
    extra["expected_concept_ids"] = expected_concept_ids_for_row(
        rec.slot_id, rec.chapter_key, _features=rec.java_features
    )
    col = v311_collection_by_key(rec.chapter_key)
    technical_concept_id = primary_tc_for_chapter(rec.chapter_key, CHAPTER_TC)
    return {
        "slot_id": rec.slot_id,
        "slug": rec.slot_id,
        "collection_key": rec.chapter_key,
        "title": f"{col.title_prefix if col else ''}{rec.title}",
        "description": rec.educational_goal,
        "difficulty": rec.difficulty,
        "technical_concept_id": technical_concept_id,
        "exercise_pattern_id": rec.exercise_pattern_id,
        "assignment_type": assignment_for_task_format(rec.task_format),
        "builder_key": builder_for_task_format(rec.task_format),
        "primary_action": rec.primary_action,
        "pascal_mirror": rec.pascal_mirror,
        "extra": extra,
    }
