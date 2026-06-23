"""Python Course v1 pedagogical catalog."""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from functools import lru_cache

from application.curriculum.python.catalog.python_pedagogical_slot import PedagogicalSlotSpec
from application.curriculum.python.catalog.python_known_language import validate_variants
from application.curriculum.python.catalog.python_v311_builder_mapping import (
    assignment_for_task_format,
    builder_for_task_format,
    resolve_assignment_for_extra,
    resolve_builder_for_extra,
)
from application.curriculum.python.catalog.python_v311_content import build_task_extra
from application.curriculum.python.catalog.python_v311_expected_concepts import (
    expected_concept_ids_for_row,
)
from application.curriculum.python.showcase.python_v311_registry import (
    V311_CHAPTER_ORDER,
    V311_COLLECTION_TARGETS,
    v311_collection_by_key,
)

_SCRIPTS = Path(__file__).resolve().parents[4] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from application.curriculum.course_scope import (
    active_target_task_count,
    iter_tasks_in_scope,
)
from python_v31_tasks import V31_CHAPTER_TITLES, V31_TASKS  # noqa: E402

V311_TOTAL_TASKS = active_target_task_count()

LANG_PATTERN = re.compile(r"pascal|c#|csharp|java|c\+\+", re.I)
FORBIDDEN_FORMATS = frozenset({"сопоставление"})
FORBIDDEN_ACTIONS = frozenset({"analyze"})


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
    python_features: str
    difficulty: str
    legacy_slot_id: str


CHAPTER_TC: dict[str, str] = {
    # legacy Python chapter keys
    "program_entry":      "program_entry",
    "typed_variables":    "typed_declaration",
    "expressions":        "arithmetic_ops",
    "parameters":         "parameter_passing",
    "lists":              "indexed_sequence",
    "comprehensions":     "indexed_sequence",
    "dynamic_lists":      "dynamic_array",
    "mappings":           "key_value_map",
    "modules":            "import_dependency",
    "exceptions":         "simple_branch",
    "pro_python":         "function_definition",
    "advanced_python":    "function_definition",
    "typing_diagnostics": "typed_declaration",
    "python_pitfalls":    "assignment",
    "python_diagnostics": "typed_declaration",
    "capstones":          "program_entry",
    # v4 unified chapter keys (21 chapters)
    "program_skeleton":   "program_entry",
    "io":                 "stdin_read",
    "conditions":         "simple_branch",
    "conditions_multi":   "multi_branch",
    "loops":              "counted_loop",
    "loops_adv":          "loop_control",
    "static_arrays":      "indexed_sequence",
    "dynamic_arrays":     "dynamic_array",
    "strings":            "string_sequence",
    "functions":          "function_definition",
    "recursion":          "recursion",
    "algorithms":         "search_find",
    "sorting":            "sort_order",
    "records":            "key_value_map",
    "files":              "file_read",
    "units":              "import_dependency",
    "data_structures":    "stack_queue",
    "functional":         "filter_select",
    "oop":                "class_type",
    "oop_state":          "object_instance",
    "oop_inherit":        "inheritance_hierarchy",
    # algorithm-syntax course (16 chapters)
    "algo_basics":        "program_entry",
    "branches":           "simple_branch",
    "arrays_collections": "indexed_sequence",
    "search_sort":        "search_find",
    "aggregation":        "filter_select",
    "maps":               "key_value_map",
    "files_modules":      "file_read",
    "stack_queue":        "stack_queue",
    "linked_lists":       "linked_node",
    "trees_graphs":       "tree_hierarchy",
    "inheritance_capstone": "inheritance_hierarchy",
}


def _row_to_record(row: tuple) -> V311TaskRecord:
    slot_id, chapter, title, fmt, action, pattern, goal, features, diff, legacy = row
    return V311TaskRecord(
        slot_id=slot_id,
        chapter_key=chapter,
        chapter_title=V31_CHAPTER_TITLES[chapter],
        title=title,
        task_format=fmt,
        primary_action=action,
        exercise_pattern_id=pattern,
        educational_goal=goal,
        python_features=features,
        difficulty=diff,
        legacy_slot_id=legacy or "",
    )


def all_v311_task_records() -> tuple[V311TaskRecord, ...]:
    return tuple(_row_to_record(row) for row in iter_tasks_in_scope(V31_TASKS))


def records_by_chapter() -> dict[str, tuple[V311TaskRecord, ...]]:
    grouped: dict[str, list[V311TaskRecord]] = {k: [] for k in V311_CHAPTER_ORDER}
    for rec in all_v311_task_records():
        grouped[rec.chapter_key].append(rec)
    return {k: tuple(grouped[k]) for k in V311_CHAPTER_ORDER}


def record_to_slot(rec: V311TaskRecord) -> PedagogicalSlotSpec:
    if rec.task_format in FORBIDDEN_FORMATS:
        raise ValueError(f"{rec.slot_id}: forbidden format {rec.task_format}")
    if rec.primary_action in FORBIDDEN_ACTIONS:
        raise ValueError(f"{rec.slot_id}: forbidden action {rec.primary_action}")
    extra = build_task_extra(
        (
            rec.slot_id,
            rec.chapter_key,
            rec.title,
            rec.task_format,
            rec.primary_action,
            rec.exercise_pattern_id,
            rec.educational_goal,
            rec.python_features,
            rec.difficulty,
            rec.legacy_slot_id,
        )
    )
    extra["curriculum_version"] = "1.0"
    extra["task_format"] = rec.task_format
    return PedagogicalSlotSpec(
        slot_id=rec.slot_id,
        collection_key=rec.chapter_key,
        target_tc=CHAPTER_TC[rec.chapter_key],
        primary_action=rec.primary_action,
        title_suffix=rec.title,
        short_instruction=rec.educational_goal,
        description=rec.educational_goal,
        difficulty=rec.difficulty,
        exercise_pattern_id=rec.exercise_pattern_id,
        assignment_type=resolve_assignment_for_extra(rec.task_format, extra),
        builder_key=resolve_builder_for_extra(rec.task_format, extra),
        extra=extra,
        slug=rec.slot_id,
    )


def all_v311_slots() -> tuple[PedagogicalSlotSpec, ...]:
    return tuple(record_to_slot(r) for r in all_v311_task_records())


def slots_by_chapter() -> dict[str, tuple[PedagogicalSlotSpec, ...]]:
    return {k: tuple(record_to_slot(r) for r in v) for k, v in records_by_chapter().items()}


@lru_cache(maxsize=None)
def slots_for_chapter(chapter_key: str) -> tuple[PedagogicalSlotSpec, ...]:
    key = str(chapter_key or "").strip()
    return tuple(record_to_slot(rec) for rec in all_v311_task_records() if rec.chapter_key == key)


def validate_v311_catalog() -> list[str]:
    errors: list[str] = []
    records = all_v311_task_records()
    if len(records) != V311_TOTAL_TASKS:
        errors.append(f"expected {V311_TOTAL_TASKS} tasks, got {len(records)}")

    slot_ids = [r.slot_id for r in records]
    if len(set(slot_ids)) != len(slot_ids):
        errors.append("duplicate slot_id detected")

    patterns = [r.exercise_pattern_id for r in records]
    if len(set(patterns)) != len(patterns):
        errors.append("duplicate exercise_pattern_id detected")

    for rec in records:
        for field_name, value in (
            ("title", rec.title),
            ("educational_goal", rec.educational_goal),
            ("chapter_title", rec.chapter_title),
        ):
            if LANG_PATTERN.search(value):
                errors.append(f"{rec.slot_id}: source language name in {field_name}")
        if rec.task_format in FORBIDDEN_FORMATS:
            errors.append(f"{rec.slot_id}: forbidden format")
        if not rec.exercise_pattern_id:
            errors.append(f"{rec.slot_id}: missing pattern_id")
        if not rec.python_features:
            errors.append(f"{rec.slot_id}: missing python_features")
        try:
            builder_for_task_format(rec.task_format)
        except KeyError:
            errors.append(f"{rec.slot_id}: no builder for {rec.task_format}")
        if v311_collection_by_key(rec.chapter_key) is None:
            errors.append(f"{rec.slot_id}: unregistered chapter {rec.chapter_key}")
        slot = record_to_slot(rec)
        variants = (slot.extra or {}).get("known_language_variants")
        if not variants:
            errors.append(f"{rec.slot_id}: missing known_language_variants")
        else:
            for msg in validate_variants(variants):
                errors.append(f"{rec.slot_id}: {msg}")
        expected_ids = expected_concept_ids_for_row(
            slot_id=rec.slot_id,
            chapter_key=rec.chapter_key,
            python_features=rec.python_features,
            task_format=rec.task_format,
        )
        if not expected_ids:
            errors.append(f"{rec.slot_id}: empty expected_concept_ids")
        extra = build_task_extra(
            (
                rec.slot_id,
                rec.chapter_key,
                rec.title,
                rec.task_format,
                rec.primary_action,
                rec.exercise_pattern_id,
                rec.educational_goal,
                rec.python_features,
                rec.difficulty,
                rec.legacy_slot_id,
            )
        )
        if extra.get("expected_concept_ids") != expected_ids:
            errors.append(f"{rec.slot_id}: expected_concept_ids mismatch in task extra")
        test_cases = extra.get("test_cases") or []
        if not test_cases:
            errors.append(f"{rec.slot_id}: missing test_cases")

    by_ch = records_by_chapter()
    for key, expected in V311_COLLECTION_TARGETS.items():
        got = len(by_ch.get(key, ()))
        if got != expected:
            errors.append(f"chapter {key}: expected {expected} tasks, got {got}")

    return errors


def catalog_summary() -> dict[str, Any]:
    records = all_v311_task_records()
    fmt_counts: dict[str, int] = {}
    builder_counts: dict[str, int] = {}
    for rec in records:
        fmt_counts[rec.task_format] = fmt_counts.get(rec.task_format, 0) + 1
        b = builder_for_task_format(rec.task_format)
        builder_counts[b] = builder_counts.get(b, 0) + 1
    return {
        "total_tasks": len(records),
        "chapters": len(V311_CHAPTER_ORDER),
        "format_counts": fmt_counts,
        "builder_counts": builder_counts,
    }
