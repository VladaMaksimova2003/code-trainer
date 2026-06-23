#!/usr/bin/env python3
"""Import teacher-provided curriculum chapter tasks into PostgreSQL."""

from __future__ import annotations

from typing import Any

import sqlalchemy as sa
from sqlalchemy.orm.attributes import flag_modified

from application.curriculum.display.chapter_task_display_order import compute_pedagogical_display_order
from application.curriculum.shared.algo_v128_showcase import primary_tc_for_chapter
from application.curriculum.pascal.showcase.pascal_v311_registry import (
    v311_collection_by_key,
    v311_showcase_group,
)
from application.curriculum.mirror.pedagogical_task_store import attach_unified_showcase_meta
from application.curriculum.showcase.showcase_task_index import invalidate_showcase_task_index_cache
from application.curriculum.validation.expected_concept_checker import detect_expected_concepts_multilang
from application.tasks.services.assignment_creation_service import create_build_from_blocks_handler
from application.tasks.services.task_patterns import apply_patterns_and_tests
from application.tasks.services.task_id_allocator import allocate_next_task_id
from application.tasks.use_cases.debug_code_keys import buggy_code_key
from infrastructure.db.models.task import Task as TaskModel
from infrastructure.db.models.task import TranslationTask as TranslationTaskModel
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal
from scripts.seed_teacher import resolve_seed_teacher_id
from shared.enums import AssignmentType

LANGS = ("pascal", "python", "cpp", "csharp", "java")
_FREE_FORM_TEMPLATE = "___"


def _assembly_variant(code: str) -> dict[str, Any]:
    lines = code.splitlines()
    blocks = [line for line in lines if line.strip()] or list(lines)
    order = list(range(len(blocks)))
    return {
        "original_code": code,
        "template": _FREE_FORM_TEMPLATE,
        "blocks": blocks,
        "correct_order": order,
    }


def _detect_expected(codes: dict[str, str]) -> dict[str, list[str]]:
    samples = [(lang, codes[lang]) for lang in LANGS if codes.get(lang, "").strip()]
    return detect_expected_concepts_multilang(samples)


def _exercise_pattern(primary_action: str) -> str:
    if primary_action == "debug":
        return "dbg_pascal_code_fix"
    if primary_action == "implement":
        return "tr_pascal_to_python_code"
    return "asm_blocks_to_code_pascal"


def _showcase_track_meta(
    chapter_key: str,
    task: dict[str, Any],
    *,
    slot_id: str,
    expected: dict[str, list[str]],
    primary_action: str,
    task_format: str,
) -> dict[str, Any]:
    col = v311_collection_by_key(chapter_key)
    goal = f"{task['short_goal']}\n\n{task['detailed_description']}".strip()
    meta: dict[str, Any] = {
        "group": v311_showcase_group(chapter_key),
        "collection_key": chapter_key,
        "slug": slot_id,
        "slot_id": slot_id,
        "slot_pattern_id": task["pattern_id"],
        "curriculum_version": "3.1.1",
        "target_language": "pascal",
        "technical_concept_id": primary_tc_for_chapter(chapter_key),
        "exercise_pattern_id": _exercise_pattern(primary_action),
        "primary_action": primary_action,
        "task_format": task_format,
        "educational_goal": goal,
        "display_order": compute_pedagogical_display_order(
            title=str(task["title"]),
            action=primary_action,
            task_num=int(task["task_num"]),
        ),
        "task_num": int(task["task_num"]),
        "expected_concepts": expected,
        "pedagogical_slot_id": f"algo_v4:{int(task['task_num']):03d}",
    }
    if col is not None:
        meta["collection_id"] = col.collection_id
    return meta


def _create_assemble_task(session, chapter_key: str, teacher_id: int, task: dict[str, Any]) -> int:
    codes = task["codes"]
    slot_id = f"pas_{int(task['task_num']):03d}"
    variants = {lang: _assembly_variant(codes[lang]) for lang in LANGS}
    pascal = variants["pascal"]
    title = str(task["title"])
    description = f"{task['short_goal']}\n\n{task['detailed_description']}".strip()
    expected = _detect_expected(codes)

    result = create_build_from_blocks_handler(
        session,
        assignment_type=AssignmentType.TASK_BUILD_FROM_BLOCKS.value,
        language="pascal",
        original_code=pascal["original_code"],
        template=pascal["template"],
        blocks=pascal["blocks"],
        correct_order=pascal["correct_order"],
        language_variants=variants,
        title=title,
        description=description,
        difficulty=task["difficulty"],
        teacher_id=teacher_id,
        test_cases=task["tests"],
    )
    task_id = int(result["task_id"])
    row = session.get(TaskModel, task_id)
    if row is None:
        raise RuntimeError(f"Failed to load task {task_id}")

    examples = dict(row.code_examples or {})
    for lang in LANGS:
        examples[lang] = codes[lang]
    row.code_examples = examples

    track_meta = _showcase_track_meta(
        chapter_key,
        task,
        slot_id=slot_id,
        expected=expected,
        primary_action="assemble",
        task_format=task["task_format"],
    )
    track_meta["assemble_context"] = {lang: codes[lang] for lang in LANGS}
    attach_unified_showcase_meta(row, track_meta, "pascal")
    apply_patterns_and_tests(row, patterns=None, test_cases=task["tests"])
    flag_modified(row, "code_examples")
    session.flush()
    return task_id


def _create_debug_task(session, chapter_key: str, teacher_id: int, task: dict[str, Any]) -> int:
    fixed = task["fixed"]
    buggy = task["buggy"]
    slot_id = f"pas_{int(task['task_num']):03d}"
    title = str(task["title"])
    description = f"{task['short_goal']}\n\n{task['detailed_description']}".strip()
    expected = _detect_expected(fixed)

    task_id = allocate_next_task_id(session)
    session.execute(
        sa.insert(TaskModel.__table__).values(
            id=task_id,
            teacher_id=teacher_id,
            title=title,
            description=description,
            difficulty=task["difficulty"],
            task_type=AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
            test_cases=task["tests"],
            code_examples={},
            flow_spec={"target_language": "pascal"},
        )
    )
    session.execute(
        sa.insert(TranslationTaskModel.__table__).values(
            task_id=task_id,
            source_code=fixed.get("pascal", ""),
            source_language="pascal",
        )
    )
    row = session.get(TaskModel, task_id)
    if row is None:
        raise RuntimeError(f"Failed to create debug task {task_id}")

    examples: dict[str, Any] = {}
    for lang in LANGS:
        examples[lang] = fixed[lang]
        examples[buggy_code_key(lang)] = buggy[lang]
    row.code_examples = examples

    track_meta = _showcase_track_meta(
        chapter_key,
        task,
        slot_id=slot_id,
        expected=expected,
        primary_action="debug",
        task_format=task["task_format"],
    )
    attach_unified_showcase_meta(row, track_meta, "pascal")
    apply_patterns_and_tests(row, patterns=None, test_cases=task["tests"])
    flag_modified(row, "code_examples")
    session.flush()
    return task_id


def _create_translation_task(session, chapter_key: str, teacher_id: int, task: dict[str, Any]) -> int:
    codes = task["codes"]
    slot_id = f"pas_{int(task['task_num']):03d}"
    title = str(task["title"])
    description = f"{task['short_goal']}\n\n{task['detailed_description']}".strip()
    expected = _detect_expected(codes)

    task_id = allocate_next_task_id(session)
    session.execute(
        sa.insert(TaskModel.__table__).values(
            id=task_id,
            teacher_id=teacher_id,
            title=title,
            description=description,
            difficulty=task["difficulty"],
            task_type=AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
            test_cases=task["tests"],
            code_examples={lang: codes[lang] for lang in LANGS},
            flow_spec={"target_language": "pascal"},
        )
    )
    session.execute(
        sa.insert(TranslationTaskModel.__table__).values(
            task_id=task_id,
            source_code=codes.get("pascal", ""),
            source_language="pascal",
        )
    )
    row = session.get(TaskModel, task_id)
    if row is None:
        raise RuntimeError(f"Failed to create translation task {task_id}")

    track_meta = _showcase_track_meta(
        chapter_key,
        task,
        slot_id=slot_id,
        expected=expected,
        primary_action="implement",
        task_format=task["task_format"],
    )
    attach_unified_showcase_meta(row, track_meta, "pascal")
    apply_patterns_and_tests(row, patterns=None, test_cases=task["tests"])
    flag_modified(row, "code_examples")
    session.flush()
    return task_id


def _delete_chapter_tasks(session, chapter_key: str, task_nums: set[int]) -> int:
    from application.curriculum.mirror.pedagogical_task_store import iter_showcase_tasks

    ids: list[int] = []
    for row, showcase in iter_showcase_tasks(session):
        if str(showcase.get("collection_key") or "") != chapter_key:
            continue
        task_num = int(showcase.get("task_num") or 0)
        if task_num in task_nums:
            ids.append(int(row.id))
    if not ids:
        return 0
    from scripts.reseed_v4_all import hard_delete_tasks_by_ids

    hard_delete_tasks_by_ids(session, ids)
    return len(ids)


def import_user_chapter(
    chapter_key: str,
    tasks: list[dict[str, Any]],
    *,
    replace: bool = True,
    teacher_email: str | None = None,
) -> dict[str, Any]:
    load_models()
    session = SessionLocal()
    task_nums = {int(task["task_num"]) for task in tasks}
    report: dict[str, Any] = {"chapter": chapter_key, "created": [], "replaced": 0, "errors": []}
    try:
        teacher_id = resolve_seed_teacher_id(session, teacher_email)
        if replace:
            report["replaced"] = _delete_chapter_tasks(session, chapter_key, task_nums)
        for task in tasks:
            try:
                kind = task["kind"]
                if kind == "assemble":
                    task_id = _create_assemble_task(session, chapter_key, teacher_id, task)
                elif kind == "debug":
                    task_id = _create_debug_task(session, chapter_key, teacher_id, task)
                elif kind == "translation":
                    task_id = _create_translation_task(session, chapter_key, teacher_id, task)
                else:
                    raise ValueError(f"Unknown kind: {kind}")
                report["created"].append(
                    {"task_num": task["task_num"], "id": task_id, "title": task["title"], "kind": kind}
                )
            except Exception as exc:
                report["errors"].append(f"task_{task['task_num']:03d}: {exc}")
        if report["errors"]:
            session.rollback()
        else:
            session.commit()
            invalidate_showcase_task_index_cache()
        return report
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
