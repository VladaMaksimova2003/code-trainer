#!/usr/bin/env python3
"""Full reset and reseed for algorithm-syntax course (128 tasks × 5 languages).

Steps:
  1. Hard-delete ALL showcase tasks across all languages (any version).
  2. Seed Pascal  — 16 chapters, 128 tasks (creates unified task rows).
  3. Seed Python  — 16 chapters, 128 tasks.
  4. Seed C++ / C# / Java — attach language tracks to unified tasks.

Run:
  cd backend
  poetry run python scripts/reseed_v4_all.py
  poetry run python scripts/reseed_v4_all.py --dry-run   # show what would be deleted
  poetry run python scripts/reseed_v4_all.py --lang pascal  # one language only (no purge)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import delete, inspect, select
from sqlalchemy.orm import Session

from infrastructure.db.models.learning.submission import (
    Submission,
    SubmissionLintError,
    SubmissionPatternError,
    SubmissionTestResult,
)
from infrastructure.db.models.learning.user_solution import UserSolution
from infrastructure.db.models.task.collection import collection_task_association_table
from infrastructure.db.models.task.construction import task_construction_association_table
from infrastructure.db.models.task.task import Task as TaskModel
from infrastructure.db.models.task.task import (
    BlockReorderTask,
    TranslationTask,
)
from infrastructure.db.models.task.task_curriculum_link import TaskCurriculumLinkModel
from infrastructure.db.models.task.task_version import TaskVersion
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal
from scripts.seed_teacher import DEFAULT_SEED_TEACHER_EMAIL, resolve_seed_teacher_id


# ---------------------------------------------------------------------------
# Full showcase purge (all languages, all versions)
# ---------------------------------------------------------------------------

def _find_all_showcase_task_ids(session: Session) -> list[int]:
    """Return IDs of every task that has a curriculum_showcase entry."""
    rows = session.scalars(
        select(TaskModel).where(TaskModel.is_delete.is_(False))
    ).all()
    ids: list[int] = []
    for task in rows:
        examples = dict(task.code_examples or {})
        if examples.get("curriculum_showcase"):
            ids.append(task.id)
    # Also include soft-deleted showcase tasks so they are fully removed
    soft_deleted = session.scalars(
        select(TaskModel).where(TaskModel.is_delete.is_(True))
    ).all()
    for task in soft_deleted:
        examples = dict(task.code_examples or {})
        if examples.get("curriculum_showcase"):
            ids.append(task.id)
    return ids


def hard_delete_tasks_by_ids(
    session: Session,
    ids: list[int],
    *,
    dry_run: bool = False,
) -> dict:
    """Hard-delete tasks and dependent rows."""
    unique_ids = sorted({int(task_id) for task_id in ids if task_id})
    result: dict = {"found": len(unique_ids), "dry_run": dry_run, "counts": {}}
    if not unique_ids or dry_run:
        return result

    bind = session.get_bind()
    table_names = set(inspect(bind).get_table_names())

    submission_ids: list[int] = []
    if "submission" in table_names:
        submission_ids = list(
            session.scalars(
                select(Submission.id).where(Submission.task_id.in_(unique_ids))
            ).all()
        )

    def _del(stmt) -> int:
        return session.execute(stmt).rowcount or 0

    if submission_ids and "submission_lint_error" in table_names:
        result["counts"]["submission_lint_error"] = _del(
            delete(SubmissionLintError).where(SubmissionLintError.submission_id.in_(submission_ids))
        )
    if submission_ids and "submission_pattern_error" in table_names:
        result["counts"]["submission_pattern_error"] = _del(
            delete(SubmissionPatternError).where(SubmissionPatternError.submission_id.in_(submission_ids))
        )
    if submission_ids and "submission_test_result" in table_names:
        result["counts"]["submission_test_result"] = _del(
            delete(SubmissionTestResult).where(SubmissionTestResult.submission_id.in_(submission_ids))
        )
    if "submission" in table_names:
        result["counts"]["submission"] = _del(
            delete(Submission).where(Submission.task_id.in_(unique_ids))
        )
    if "user_solution" in table_names:
        result["counts"]["user_solution"] = _del(
            delete(UserSolution).where(UserSolution.task_id.in_(unique_ids))
        )
    if "collection_task_association" in table_names:
        result["counts"]["collection_task_association"] = _del(
            delete(collection_task_association_table).where(
                collection_task_association_table.c.task_id.in_(unique_ids)
            )
        )
    if "task_construction_association" in table_names:
        result["counts"]["task_construction_association"] = _del(
            delete(task_construction_association_table).where(
                task_construction_association_table.c.task_id.in_(unique_ids)
            )
        )
    if "task_version" in table_names:
        result["counts"]["task_version"] = _del(
            delete(TaskVersion).where(TaskVersion.task_id.in_(unique_ids))
        )
    if "task_curriculum_link" in table_names:
        result["counts"]["task_curriculum_link"] = _del(
            delete(TaskCurriculumLinkModel).where(TaskCurriculumLinkModel.task_id.in_(unique_ids))
        )
    if "block_reorder_task" in table_names:
        result["counts"]["block_reorder_task"] = _del(
            delete(BlockReorderTask).where(BlockReorderTask.task_id.in_(unique_ids))
        )
    if "translation_task" in table_names:
        result["counts"]["translation_task"] = _del(
            delete(TranslationTask).where(TranslationTask.task_id.in_(unique_ids))
        )
    result["counts"]["task"] = _del(
        delete(TaskModel).where(TaskModel.id.in_(unique_ids))
    )
    return result


def purge_all_showcase_tasks(
    session: Session,
    *,
    dry_run: bool = False,
) -> dict:
    """Hard-delete every showcase task (all languages, all versions)."""
    ids = _find_all_showcase_task_ids(session)
    result = hard_delete_tasks_by_ids(session, ids, dry_run=dry_run)
    result["dry_run"] = dry_run
    return result


def purge_showcase_tasks_above_id(
    session: Session,
    *,
    max_id: int = 128,
    dry_run: bool = False,
) -> dict:
    """Remove legacy mirror rows (e.g. standalone Python copies with id > 128)."""
    ids = list(
        session.scalars(select(TaskModel.id).where(TaskModel.id > max_id)).all()
    )
    result = hard_delete_tasks_by_ids(session, ids, dry_run=dry_run)
    result["max_id"] = max_id
    result["dry_run"] = dry_run
    return result


# ---------------------------------------------------------------------------
# Pascal seed
# ---------------------------------------------------------------------------

def _seed_pascal(session: Session, teacher_id: int) -> dict:
    from application.curriculum.pascal.catalog.pascal_curriculum_v3_catalog import (
        catalog_summary,
        validate_v311_catalog,
    )
    from application.curriculum.pascal.showcase.pascal_showcase_core import (
        list_showcase_tasks_for_collection,
        seed_pascal_v311_showcase_collection,
    )
    from application.curriculum.pascal.showcase.pascal_v311_registry import (
        PASCAL_V311_SHOWCASE_COLLECTIONS,
        V311_CHAPTER_ORDER,
    )
    from application.curriculum.pascal.showcase.pascal_v311_showcase_all_specs import (
        all_pascal_v311_showcase_specs,
    )

    errors = validate_v311_catalog()
    if errors:
        return {"validation": "FAILED", "errors": errors}

    summary = catalog_summary()
    all_specs = all_pascal_v311_showcase_specs()
    reports: list[dict] = []
    exit_code = 0

    for key in V311_CHAPTER_ORDER:
        if key not in all_specs:
            print(f"  [Pascal] WARNING: no specs for chapter {key}", flush=True)
            continue
        report = seed_pascal_v311_showcase_collection(
            session, key, all_specs[key], teacher_id=teacher_id
        )
        payload = report.to_dict()
        payload["tasks"] = list_showcase_tasks_for_collection(
            session, key, curriculum_version="3.1.1"
        )
        reports.append(payload)
        if payload["errors"]:
            exit_code = 1
        created = payload["totals"]["created"]
        linked = payload["totals"]["linked"]
        print(f"  [Pascal] {key}: created={created} linked={linked} errors={len(payload['errors'])}", flush=True)

    return {
        "lang": "pascal",
        "validation": "OK",
        "summary": summary,
        "exit_code": exit_code,
        "totals": {
            "created": sum(r["totals"]["created"] for r in reports),
            "linked": sum(r["totals"]["linked"] for r in reports),
            "skipped": sum(r["totals"]["skipped"] for r in reports),
            "errors": sum(len(r["errors"]) for r in reports),
        },
        "registered_collections": len(PASCAL_V311_SHOWCASE_COLLECTIONS),
    }


# ---------------------------------------------------------------------------
# Python seed
# ---------------------------------------------------------------------------

def _seed_python(session: Session, teacher_id: int) -> dict:
    from application.curriculum.python.catalog.python_curriculum_v3_catalog import (
        catalog_summary,
        validate_v311_catalog,
    )
    from application.curriculum.python.showcase.python_showcase_core import (
        list_showcase_tasks_for_collection,
        seed_python_v311_showcase_collection,
    )
    from application.curriculum.python.showcase.python_v311_registry import (
        PYTHON_V311_SHOWCASE_COLLECTIONS,
        V311_CHAPTER_ORDER,
    )
    from application.curriculum.python.showcase.python_v311_showcase_all_specs import (
        all_python_v311_showcase_specs,
    )

    errors = validate_v311_catalog()
    if errors:
        return {"validation": "FAILED", "errors": errors}

    summary = catalog_summary()
    all_specs = all_python_v311_showcase_specs()
    reports: list[dict] = []
    exit_code = 0

    for key in V311_CHAPTER_ORDER:
        if key not in all_specs:
            print(f"  [Python] WARNING: no specs for chapter {key}", flush=True)
            continue
        report = seed_python_v311_showcase_collection(
            session, key, all_specs[key], teacher_id=teacher_id
        )
        payload = report.to_dict()
        payload["tasks"] = list_showcase_tasks_for_collection(
            session, key, curriculum_version="1.0"
        )
        reports.append(payload)
        if payload["errors"]:
            exit_code = 1
        created = payload["totals"]["created"]
        linked = payload["totals"]["linked"]
        print(f"  [Python] {key}: created={created} linked={linked} errors={len(payload['errors'])}", flush=True)

    return {
        "lang": "python",
        "validation": "OK",
        "summary": summary,
        "exit_code": exit_code,
        "totals": {
            "created": sum(r["totals"]["created"] for r in reports),
            "linked": sum(r["totals"]["linked"] for r in reports),
            "skipped": sum(r["totals"]["skipped"] for r in reports),
            "errors": sum(len(r["errors"]) for r in reports),
        },
        "registered_collections": len(PYTHON_V311_SHOWCASE_COLLECTIONS),
    }


# ---------------------------------------------------------------------------
# C++ seed
# ---------------------------------------------------------------------------

def _seed_cpp(session: Session, teacher_id: int) -> dict:
    from application.curriculum.cpp.catalog.cpp_curriculum_v3_catalog import (
        catalog_summary,
        validate_v311_catalog,
    )
    from application.curriculum.cpp.showcase.cpp_showcase_core import (
        list_cpp_tasks_for_collection,
        seed_cpp_collection,
    )
    from application.curriculum.cpp.showcase.cpp_v311_showcase_all_specs import specs_for_chapters
    from application.curriculum.cpp.showcase.cpp_v311_registry import (
        CPP_V311_SHOWCASE_COLLECTIONS,
        V311_CHAPTER_ORDER,
    )

    errors = validate_v311_catalog()
    if errors:
        return {"validation": "FAILED", "errors": errors}

    summary = catalog_summary()
    all_specs = specs_for_chapters(tuple(V311_CHAPTER_ORDER))
    reports: list[dict] = []
    exit_code = 0

    for key in V311_CHAPTER_ORDER:
        if key not in all_specs:
            print(f"  [C++] WARNING: no specs for chapter {key}", flush=True)
            continue
        report = seed_cpp_collection(
            session, key, all_specs[key], teacher_id=teacher_id
        )
        payload = report.to_dict()
        payload["tasks"] = list_cpp_tasks_for_collection(session, key)
        reports.append(payload)
        if payload["errors"]:
            exit_code = 1
        created = payload["totals"]["created"]
        attached = payload["totals"]["attached"]
        print(f"  [C++] {key}: created={created} attached={attached} errors={len(payload['errors'])}", flush=True)

    return {
        "lang": "cpp",
        "validation": "OK",
        "summary": summary,
        "exit_code": exit_code,
        "totals": {
            "created": sum(r["totals"]["created"] for r in reports),
            "attached": sum(r["totals"]["attached"] for r in reports),
            "skipped": sum(r["totals"]["skipped"] for r in reports),
            "errors": sum(len(r["errors"]) for r in reports),
        },
        "registered_collections": len(CPP_V311_SHOWCASE_COLLECTIONS),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _seed_csharp(session: Session, teacher_id: int) -> dict:
    from application.curriculum.csharp.catalog.csharp_curriculum_v3_catalog import (
        catalog_summary,
        validate_v311_catalog,
    )
    from application.curriculum.csharp.showcase.csharp_showcase_core import (
        list_csharp_tasks_for_collection,
        seed_csharp_collection,
    )
    from application.curriculum.csharp.showcase.csharp_v311_registry import (
        CSHARP_V311_SHOWCASE_COLLECTIONS,
        V311_CHAPTER_ORDER,
    )
    from application.curriculum.csharp.showcase.csharp_v311_showcase_all_specs import (
        specs_for_chapters,
    )

    errors = validate_v311_catalog()
    if errors:
        return {"validation": "FAILED", "errors": errors}

    summary = catalog_summary()
    all_specs = specs_for_chapters(tuple(V311_CHAPTER_ORDER))
    reports: list[dict] = []
    exit_code = 0

    for key in V311_CHAPTER_ORDER:
        if key not in all_specs:
            print(f"  [C#] WARNING: no specs for chapter {key}", flush=True)
            continue
        report = seed_csharp_collection(
            session, key, all_specs[key], teacher_id=teacher_id
        )
        payload = report.to_dict()
        payload["tasks"] = list_csharp_tasks_for_collection(session, key)
        reports.append(payload)
        if payload["errors"]:
            exit_code = 1
        attached = payload["totals"]["attached"]
        print(f"  [C#] {key}: attached={attached} errors={len(payload['errors'])}", flush=True)

    return {
        "lang": "csharp",
        "validation": "OK",
        "summary": summary,
        "exit_code": exit_code,
        "totals": {
            "attached": sum(r["totals"]["attached"] for r in reports),
            "skipped": sum(r["totals"]["skipped"] for r in reports),
            "errors": sum(len(r["errors"]) for r in reports),
        },
        "registered_collections": len(CSHARP_V311_SHOWCASE_COLLECTIONS),
    }


def _seed_java(session: Session, teacher_id: int) -> dict:
    from application.curriculum.java.catalog.java_curriculum_v3_catalog import (
        catalog_summary,
        validate_v311_catalog,
    )
    from application.curriculum.java.showcase.java_showcase_core import (
        list_java_tasks_for_collection,
        seed_java_collection,
    )
    from application.curriculum.java.showcase.java_v311_registry import (
        JAVA_V311_SHOWCASE_COLLECTIONS,
        V311_CHAPTER_ORDER,
    )
    from application.curriculum.java.showcase.java_v311_showcase_all_specs import (
        specs_for_chapters,
    )

    errors = validate_v311_catalog()
    if errors:
        return {"validation": "FAILED", "errors": errors}

    summary = catalog_summary()
    all_specs = specs_for_chapters(tuple(V311_CHAPTER_ORDER))
    reports: list[dict] = []
    exit_code = 0

    for key in V311_CHAPTER_ORDER:
        if key not in all_specs:
            print(f"  [Java] WARNING: no specs for chapter {key}", flush=True)
            continue
        report = seed_java_collection(
            session, key, all_specs[key], teacher_id=teacher_id
        )
        payload = report.to_dict()
        payload["tasks"] = list_java_tasks_for_collection(session, key)
        reports.append(payload)
        if payload["errors"]:
            exit_code = 1
        attached = payload["totals"]["attached"]
        print(f"  [Java] {key}: attached={attached} errors={len(payload['errors'])}", flush=True)

    return {
        "lang": "java",
        "validation": "OK",
        "summary": summary,
        "exit_code": exit_code,
        "totals": {
            "attached": sum(r["totals"]["attached"] for r in reports),
            "skipped": sum(r["totals"]["skipped"] for r in reports),
            "errors": sum(len(r["errors"]) for r in reports),
        },
        "registered_collections": len(JAVA_V311_SHOWCASE_COLLECTIONS),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Full v4 reseed (270 tasks × 5 languages)")
    parser.add_argument(
        "--lang",
        default=None,
        choices=["pascal", "python", "cpp", "csharp", "java"],
        help="Seed only one language (skips purge if combined with --skip-purge)",
    )
    parser.add_argument(
        "--skip-purge",
        action="store_true",
        help="Do not delete existing showcase tasks — only seed missing ones.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show how many tasks would be deleted; do not commit anything.",
    )
    parser.add_argument(
        "--teacher-email",
        default=DEFAULT_SEED_TEACHER_EMAIL,
    )
    from scripts.catalog_sync_guard import add_force_catalog_sync_argument, ensure_catalog_sync_allowed

    add_force_catalog_sync_argument(parser)
    args = parser.parse_args()

    if args.dry_run:
        pass
    elif not ensure_catalog_sync_allowed(force=args.force_catalog_sync):
        return 2

    load_models()
    session = SessionLocal()
    output: dict = {}
    exit_code = 0

    try:
        # Step 1: purge
        if not args.skip_purge:
            print("Step 1: purging ALL existing showcase tasks ...", flush=True)
            purge_result = purge_all_showcase_tasks(session, dry_run=args.dry_run)
            output["purge"] = purge_result
            print(
                f"  found={purge_result['found']} "
                f"deleted_tasks={purge_result['counts'].get('task', 0)} "
                f"dry_run={purge_result['dry_run']}",
                flush=True,
            )
            if args.dry_run:
                session.rollback()
                print(json.dumps(output, ensure_ascii=False, indent=2))
                return 0
            session.flush()
        else:
            print("Step 1: skipped (--skip-purge)", flush=True)

        teacher_id = resolve_seed_teacher_id(session, args.teacher_email)

        def _apply(step: str, result: dict) -> bool:
            """Apply result; return False if validation failed (caller should stop)."""
            nonlocal exit_code
            output[step] = result
            if result.get("validation") == "FAILED":
                print(f"  {step.upper()} catalog validation FAILED:", flush=True)
                for e in result.get("errors", []):
                    print(f"    {e}", flush=True)
                exit_code = 1
                return False
            if result.get("exit_code", 0):
                exit_code = 1
            return True

        # Step 2: Pascal (must succeed — Python and C++ depend on Pascal task rows)
        pascal_ok = True
        if args.lang in (None, "pascal"):
            print("Step 2: seeding Pascal ...", flush=True)
            pascal_ok = _apply("pascal", _seed_pascal(session, teacher_id))
            session.flush()
            if not pascal_ok and args.lang is None:
                print("  Pascal validation failed — aborting Python + C++ seed.", flush=True)
        else:
            print("Step 2: Pascal skipped (--lang filter)", flush=True)

        # Step 3: Python
        if args.lang in (None, "python") and (args.lang == "python" or pascal_ok):
            print("Step 3: seeding Python ...", flush=True)
            _apply("python", _seed_python(session, teacher_id))
            session.flush()
        elif not pascal_ok:
            print("Step 3: Python skipped (Pascal failed)", flush=True)
        else:
            print("Step 3: Python skipped (--lang filter)", flush=True)

        # Step 4: C++
        if args.lang in (None, "cpp") and (args.lang == "cpp" or pascal_ok):
            print("Step 4: seeding C++ ...", flush=True)
            _apply("cpp", _seed_cpp(session, teacher_id))
            session.flush()
        elif not pascal_ok:
            print("Step 4: C++ skipped (Pascal failed)", flush=True)
        else:
            print("Step 4: C++ skipped (--lang filter)", flush=True)

        # Step 5: C#
        if args.lang in (None, "csharp") and (args.lang == "csharp" or pascal_ok):
            print("Step 5: seeding C# ...", flush=True)
            _apply("csharp", _seed_csharp(session, teacher_id))
            session.flush()
        elif not pascal_ok:
            print("Step 5: C# skipped (Pascal failed)", flush=True)
        else:
            print("Step 5: C# skipped (--lang filter)", flush=True)

        # Step 6: Java
        if args.lang in (None, "java") and (args.lang == "java" or pascal_ok):
            print("Step 6: seeding Java ...", flush=True)
            _apply("java", _seed_java(session, teacher_id))
            session.flush()
        elif not pascal_ok:
            print("Step 6: Java skipped (Pascal failed)", flush=True)
        else:
            print("Step 6: Java skipped (--lang filter)", flush=True)

        session.commit()
        print("\n=== DONE ===", flush=True)
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return exit_code

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
