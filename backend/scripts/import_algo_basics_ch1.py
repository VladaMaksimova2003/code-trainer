#!/usr/bin/env python3
"""Import 8 algo_basics chapter tasks directly into PostgreSQL (teacher-provided content)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

import sqlalchemy as sa
from sqlalchemy.orm.attributes import flag_modified

from application.curriculum.mirror.pedagogical_task_store import attach_unified_showcase_meta
from application.curriculum.pascal.showcase.pascal_v311_registry import (
    v311_collection_by_key,
    v311_showcase_group,
)
from application.curriculum.showcase.showcase_task_index import invalidate_showcase_task_index_cache
from application.curriculum.validation.expected_concept_checker import detect_expected_concepts_multilang
from application.tasks.services.assignment_creation_service import create_build_from_blocks_handler
from application.tasks.services.task_patterns import apply_patterns_and_tests
from application.tasks.services.teacher_assembly_preservation import mark_teacher_assembly_override
from application.tasks.use_cases.debug_code_keys import buggy_code_key
from application.tasks.services.task_id_allocator import allocate_next_task_id
from infrastructure.db.models.task import BlockReorderTask as BlockReorderTaskModel
from infrastructure.db.models.task import Task as TaskModel
from infrastructure.db.models.task import TranslationTask as TranslationTaskModel
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal
from application.curriculum.content.v4_assembly_builder import assembly_payload_for_format
from scripts.algo_basics_ch1_user_payload import CHAPTER_KEY, TASKS
from scripts.seed_teacher import resolve_seed_teacher_id
from shared.enums import AssignmentType

_LANGS = ("pascal", "python", "cpp", "csharp", "java")


def _assembly_variant(code: str, *, task_format: str, language: str, pattern_id: str) -> dict[str, Any]:
    original, template, blocks, order = assembly_payload_for_format(
        task_format,
        language,
        code,
        pattern_id=pattern_id,
    )
    return {
        "original_code": original,
        "template": template,
        "blocks": blocks,
        "correct_order": order,
    }


def _expected_from_catalog_features(features: str) -> dict[str, list[str]]:
    """Map catalog feature tokens → technical ids from the 29-card TC registry."""
    from application.curriculum.content.catalog_feature_concepts import (
        technical_ids_from_catalog_features,
    )

    technical_ids = technical_ids_from_catalog_features(features)
    if not technical_ids:
        return {}
    return {lang: list(technical_ids) for lang in _LANGS}


def _detect_expected(codes: dict[str, str], *, features: str = "") -> dict[str, list[str]]:
    from_catalog = _expected_from_catalog_features(features)
    if from_catalog:
        return from_catalog
    samples = [(lang, codes[lang]) for lang in _LANGS if codes.get(lang, "").strip()]
    return detect_expected_concepts_multilang(samples)


def _showcase_track_meta(
    task: dict[str, Any],
    *,
    slot_id: str,
    expected: dict[str, list[str]],
    primary_action: str,
    task_format: str,
) -> dict[str, Any]:
    col = v311_collection_by_key(CHAPTER_KEY)
    goal = f"{task['short_goal']}\n\n{task['detailed_description']}".strip()
    meta: dict[str, Any] = {
        "group": v311_showcase_group(CHAPTER_KEY),
        "collection_key": CHAPTER_KEY,
        "slug": slot_id,
        "slot_id": slot_id,
        "slot_pattern_id": task["pattern_id"],
        "curriculum_version": "3.1.1",
        "target_language": "pascal",
        "technical_concept_id": "program_entry",
        "exercise_pattern_id": (
            "dbg_pascal_code_fix" if primary_action == "debug" else "asm_blocks_to_code_pascal"
        ),
        "primary_action": primary_action,
        "task_format": task_format,
        "educational_goal": goal,
        "display_order": int(task["task_num"]) * 10,
        "task_num": int(task["task_num"]),
        "expected_concepts": expected,
        "pedagogical_slot_id": f"algo_v4:{int(task['task_num']):03d}",
        "chapter1_content_rev": "2025-06-22",
    }
    if col is not None:
        meta["collection_id"] = col.collection_id
    return meta


def _create_assemble_task(session, teacher_id: int, task: dict[str, Any]) -> int:
    codes = task["codes"]
    slot_id = f"pas_{int(task['task_num']):03d}"
    task_format = str(task["task_format"])
    pattern_id = str(task["pattern_id"])
    variants = {
        lang: _assembly_variant(
            codes[lang],
            task_format=task_format,
            language=lang,
            pattern_id=pattern_id,
        )
        for lang in _LANGS
    }
    pascal = variants["pascal"]
    title = str(task["title"])
    description = f"{task['short_goal']}\n\n{task['detailed_description']}".strip()
    expected = _detect_expected(codes, features=str(task.get("features") or ""))

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
    for lang in _LANGS:
        examples[lang] = codes[lang]
    hints = list(task.get("hints") or [])
    if hints:
        examples["hints"] = hints
    row.code_examples = examples

    track_meta = _showcase_track_meta(
        task,
        slot_id=slot_id,
        expected=expected,
        primary_action="assemble",
        task_format=task["task_format"],
    )
    assemble_context = {lang: codes[lang] for lang in _LANGS}
    track_meta["assemble_context"] = assemble_context
    attach_unified_showcase_meta(row, track_meta, "pascal")
    apply_patterns_and_tests(row, patterns=None, test_cases=task["tests"])
    mark_teacher_assembly_override(row)
    flag_modified(row, "code_examples")
    session.flush()
    return task_id


def _create_debug_task(session, teacher_id: int, task: dict[str, Any]) -> int:
    fixed = task["fixed"]
    buggy = task["buggy"]
    slot_id = f"pas_{int(task['task_num']):03d}"
    title = str(task["title"])
    description = f"{task['short_goal']}\n\n{task['detailed_description']}".strip()
    expected = _detect_expected(fixed, features=str(task.get("features") or ""))

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
            source_code="",
            source_language="python",
        )
    )
    row = session.get(TaskModel, task_id)
    if row is None:
        raise RuntimeError(f"Failed to create debug task {task_id}")

    examples: dict[str, Any] = {}
    for lang in _LANGS:
        examples[lang] = fixed[lang]
        examples[buggy_code_key(lang)] = buggy[lang]
    hints = list(task.get("hints") or [])
    if hints:
        examples["hints"] = hints
    row.code_examples = examples

    track_meta = _showcase_track_meta(
        task,
        slot_id=slot_id,
        expected=expected,
        primary_action="debug",
        task_format=task["task_format"],
    )
    attach_unified_showcase_meta(row, track_meta, "pascal")
    apply_patterns_and_tests(row, patterns=None, test_cases=task["tests"])
    mark_teacher_assembly_override(row)
    flag_modified(row, "code_examples")
    session.flush()
    return task_id


def _create_implement_task(session, teacher_id: int, task: dict[str, Any]) -> int:
    codes = task["codes"]
    slot_id = f"pas_{int(task['task_num']):03d}"
    title = str(task["title"])
    description = f"{task['short_goal']}\n\n{task['detailed_description']}".strip()
    expected = _detect_expected(codes, features=str(task.get("features") or ""))

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
            source_code=codes.get("python", ""),
            source_language="python",
        )
    )
    row = session.get(TaskModel, task_id)
    if row is None:
        raise RuntimeError(f"Failed to create implement task {task_id}")

    examples: dict[str, Any] = {lang: codes[lang] for lang in _LANGS}
    hints = list(task.get("hints") or [])
    if hints:
        examples["hints"] = hints
    row.code_examples = examples

    track_meta = _showcase_track_meta(
        task,
        slot_id=slot_id,
        expected=expected,
        primary_action="implement",
        task_format=task["task_format"],
    )
    attach_unified_showcase_meta(row, track_meta, "pascal")
    apply_patterns_and_tests(row, patterns=None, test_cases=task["tests"])
    mark_teacher_assembly_override(row)
    flag_modified(row, "code_examples")
    session.flush()
    return task_id


_CH1_SLOT_IDS = frozenset(f"pas_{index:03d}" for index in range(1, 9))


def _delete_algo_basics_tasks(session) -> int:
    from application.curriculum.mirror.pedagogical_task_store import iter_showcase_tasks

    ids: list[int] = []
    for row, showcase in iter_showcase_tasks(session):
        if str(showcase.get("collection_key") or "") != CHAPTER_KEY:
            continue
        slot_id = str(showcase.get("slot_id") or showcase.get("slug") or "").strip()
        task_num = int(showcase.get("task_num") or 0)
        if slot_id in _CH1_SLOT_IDS or 1 <= task_num <= 8:
            ids.append(int(row.id))
    if not ids:
        return 0
    from scripts.reseed_v4_all import hard_delete_tasks_by_ids

    hard_delete_tasks_by_ids(session, sorted(set(ids)))
    return len(set(ids))


def import_chapter(*, replace: bool = True, teacher_email: str | None = None) -> dict[str, Any]:
    load_models()
    session = SessionLocal()
    report: dict[str, Any] = {"chapter": CHAPTER_KEY, "created": [], "replaced": 0, "errors": []}
    try:
        teacher_id = resolve_seed_teacher_id(session, teacher_email)
        if replace:
            report["replaced"] = _delete_algo_basics_tasks(session)
        for task in TASKS:
            try:
                if task["kind"] == "assemble":
                    task_id = _create_assemble_task(session, teacher_id, task)
                elif task["kind"] == "implement":
                    task_id = _create_implement_task(session, teacher_id, task)
                else:
                    task_id = _create_debug_task(session, teacher_id, task)
                report["created"].append({"task_num": task["task_num"], "id": task_id, "title": task["title"]})
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Import algo_basics chapter 1 tasks into DB")
    parser.add_argument("--no-replace", action="store_true", help="Do not delete existing ch.1 tasks")
    parser.add_argument("--teacher-email", default=None)
    args = parser.parse_args()
    report = import_chapter(replace=not args.no_replace, teacher_email=args.teacher_email)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report.get("errors") else 0


if __name__ == "__main__":
    raise SystemExit(main())
