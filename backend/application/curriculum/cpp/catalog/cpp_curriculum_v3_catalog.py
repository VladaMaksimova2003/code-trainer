"""C++ Course v1 pedagogical catalog."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from application.curriculum.cpp.catalog.cpp_v311_builder_mapping import (
    assignment_for_task_format,
    builder_for_task_format,
)
from application.curriculum.cpp.catalog.cpp_v311_content import build_task_extra
from application.curriculum.cpp.catalog.cpp_v311_expected_concepts import (
    expected_concept_ids_for_row,
)
from application.curriculum.cpp.showcase.cpp_v311_registry import (
    V311_CHAPTER_ORDER,
    V311_COLLECTION_TARGETS,
    v311_collection_by_key,
)
from application.curriculum.mirror.curriculum_slot_mirror_cpp import (
    CPP_ONLY_SLOTS,
    is_cpp_only_slot,
)

_SCRIPTS = Path(__file__).resolve().parents[4] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from application.curriculum.course_scope import (
    active_target_task_count,
    iter_tasks_in_scope,
)
from cpp_v31_tasks import V31_CHAPTER_TITLES, V31_TASKS  # noqa: E402

V311_TOTAL_TASKS = active_target_task_count()
MVP2_TOTAL_TASKS = V311_TOTAL_TASKS  # legacy alias

LANG_PATTERN = re.compile(r"pascal|python|java|c#|csharp", re.I)
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
    cpp_features: str
    difficulty: str
    pascal_mirror: str


CHAPTER_TC: dict[str, str] = {
    # legacy C++ chapter keys
    "cpp_entry":          "program_entry",
    "cpp_types":          "typed_declaration",
    "cpp_io":             "stdin_read",
    "cpp_expr":           "arithmetic_ops",
    "cpp_cond":           "simple_branch",
    "cpp_loops":          "counted_loop",
    "cpp_functions":      "function_definition",
    "cpp_params":         "parameter_passing",
    "cpp_arrays":         "indexed_sequence",
    "cpp_vector":         "dynamic_array",
    "cpp_string":         "string_sequence",
    "cpp_pointers":       "reference_semantics",
    "cpp_files":          "file_read",
    "cpp_headers":        "import_dependency",
    "cpp_recursion":      "recursion",
    "cpp_oop":            "class_type",
    "cpp_pitfalls":       "assignment",
    "cpp_diagnostics":    "typed_declaration",
    "cpp_preprocessor":   "preprocessor_directives",
    "cpp_templates":      "templates",
    "cpp_enums":          "enum_class",
    "cpp_stl_associative": "stl_containers",
    "cpp_stl_algorithms": "stl_algorithms",
    "cpp_move":           "move_semantics",
    "cpp_exceptions":     "exceptions",
    "cpp_capstones":      "program_entry",
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

SLOT_TC_OVERRIDE: dict[str, str] = {
    "cppt_04": "dynamic_allocation",
    "cppt_05": "dynamic_allocation",
    "cppt_06": "dynamic_allocation",
    "cppt_07": "dynamic_allocation",
    "cppt_10": "dynamic_allocation",
    "cppt_11": "dynamic_allocation",
    "cppt_12": "dynamic_allocation",
    "cppt_13": "dynamic_allocation",
    "cppt_14": "dynamic_allocation",
    "cppt_15": "dynamic_allocation",
    "cppt_16": "dynamic_allocation",
    "cpas_10": "key_value_map",
    "cpalg_08": "key_value_map",
}


def _is_algo_syntax_slot(slot_id: str) -> bool:
    return bool(re.fullmatch(r"cpp_\d{3}", str(slot_id or "").strip()))


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
        cpp_features=features,
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


def validate_v311_catalog() -> list[str]:
    errors: list[str] = []
    records = all_v311_task_records()
    if len(records) != V311_TOTAL_TASKS:
        errors.append(f"expected {V311_TOTAL_TASKS} tasks, got {len(records)}")

    slot_ids = [r.slot_id for r in records]
    if len(set(slot_ids)) != len(slot_ids):
        errors.append("duplicate slot_id detected")

    for rec in records:
        for field_name, value in (
            ("title", rec.title),
            ("educational_goal", rec.educational_goal),
        ):
            if LANG_PATTERN.search(value):
                errors.append(f"{rec.slot_id}: source language name in {field_name}")
        if rec.task_format in FORBIDDEN_FORMATS:
            errors.append(f"{rec.slot_id}: forbidden format")
        if rec.primary_action in FORBIDDEN_ACTIONS:
            errors.append(f"{rec.slot_id}: forbidden action analyze")
        mirror = rec.pascal_mirror
        algo_slot = _is_algo_syntax_slot(rec.slot_id)
        if mirror and rec.slot_id in CPP_ONLY_SLOTS:
            errors.append(f"{rec.slot_id}: cpp-only slot must not have pascal mirror")
        if not mirror and rec.slot_id not in CPP_ONLY_SLOTS and not algo_slot:
            errors.append(f"{rec.slot_id}: mirror slot missing pascal_mirror")
        if rec.slot_id in CPP_ONLY_SLOTS and not is_cpp_only_slot(rec.slot_id):
            errors.append(f"{rec.slot_id}: not registered in CPP_ONLY_SLOTS")

    for chapter, target in V311_COLLECTION_TARGETS.items():
        count = len(records_by_chapter().get(chapter, ()))
        if count != target:
            errors.append(f"chapter {chapter}: expected {target} tasks, got {count}")

    return errors


def catalog_summary() -> dict[str, int | str]:
    by_ch = records_by_chapter()
    mirror_count = sum(1 for r in all_v311_task_records() if r.pascal_mirror)
    group_c = len(all_v311_task_records()) - mirror_count
    return {
        "total_tasks": len(all_v311_task_records()),
        "mirror_attach_tasks": mirror_count,
        "cpp_only_tasks": group_c,
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
            rec.cpp_features,
            rec.difficulty,
            rec.pascal_mirror,
        )
    )
    extra["expected_concept_ids"] = expected_concept_ids_for_row(
        rec.slot_id, rec.chapter_key, _features=rec.cpp_features
    )
    col = v311_collection_by_key(rec.chapter_key)
    technical_concept_id = SLOT_TC_OVERRIDE.get(rec.slot_id) or CHAPTER_TC[rec.chapter_key]
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


_SLOT_INDEX: dict[str, V311TaskRecord] | None = None


def catalog_record_for_slot(slot_id: str) -> V311TaskRecord | None:
    global _SLOT_INDEX
    if _SLOT_INDEX is None:
        _SLOT_INDEX = {rec.slot_id: rec for rec in all_v311_task_records()}
    return _SLOT_INDEX.get(str(slot_id or "").strip())


def catalog_title_for_slot(slot_id: str, *, with_prefix: bool = False) -> str | None:
    rec = catalog_record_for_slot(slot_id)
    if rec is None:
        return None
    if not with_prefix:
        return rec.title
    col = v311_collection_by_key(rec.chapter_key)
    prefix = col.title_prefix if col else "[C++ v1: "
    return f"{prefix}{rec.title}"
