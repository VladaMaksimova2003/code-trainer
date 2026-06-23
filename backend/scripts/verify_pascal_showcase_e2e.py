#!/usr/bin/env python3
"""Verify Pascal showcase tasks via WorkerPipelineRunner."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.pascal.showcase.pascal_showcase_core import find_showcase_task_by_slug, list_showcase_tasks_for_collection
from application.curriculum.pascal.showcase.pascal_showcase_reference_solutions import (
    BLOCK_REORDER_SOLUTIONS,
    REFERENCE_SOLUTIONS,
)
from application.curriculum.pascal.showcase.pascal_showcase_registry import PASCAL_SHOWCASE_COLLECTIONS
from application.curriculum.task_curriculum_link_service import TaskCurriculumLinkService
from application.execution.block_reorder_validation import validate_block_reorder_structural
from application.execution.pipeline_runner import WorkerPipelineRunner
from application.tasks.services.block_reorder_helpers import build_entity_from_db
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal
from infrastructure.execution.execution_guard import mark_worker_context


def _run_one(session, runner, link_svc, item: dict) -> dict:
    slug = item["slug"]
    task_id = item["task_id"]
    meta = link_svc.get_task_curriculum_metadata(task_id)
    primary = meta.get("primary_link") or {}
    note = ""
    execution = "SKIPPED"

    if slug in BLOCK_REORDER_SOLUTIONS:
        payload = BLOCK_REORDER_SOLUTIONS[slug]
        task = find_showcase_task_by_slug(session, slug)
        assert task is not None and task.block_reorder_task is not None
        entity = build_entity_from_db(task, task.block_reorder_task)
        assembled = entity.build_code(payload["order"], "pascal", None)
        structural = validate_block_reorder_structural(
            session,
            task_id,
            order=payload["order"],
            language="pascal",
            assembled_code=assembled,
        )
        if not structural or not structural.get("structural_correct"):
            execution = "STRUCTURAL_FAIL"
            note = structural.get("message") if structural else "no structural result"
        else:
            result = runner.run_submission(task_id, assembled, "pascal")
            execution = "PASSED" if result["success"] else "FAILED"
            if not result["success"]:
                note = str(
                    result.get("test_results")
                    or result.get("compiler_errors")
                    or result.get("pattern_errors")
                )
    elif slug in REFERENCE_SOLUTIONS:
        result = runner.run_submission(task_id, REFERENCE_SOLUTIONS[slug], "pascal")
        execution = "PASSED" if result["success"] else "FAILED"
        if not result["success"]:
            note = str(
                result.get("test_results")
                or result.get("compiler_errors")
                or result.get("pattern_errors")
            )
    else:
        note = "no reference solution mapped"

    return {
        "collection": item.get("collection_key"),
        "slug": slug,
        "task_type": item["task_type"],
        "TC": primary.get("technical_concept_id"),
        "action": primary.get("action"),
        "pattern": primary.get("exercise_pattern_id"),
        "execution": execution,
        "notes": note,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default=None, help="Single chapter key or all")
    args = parser.parse_args()

    mark_worker_context()
    load_models()
    session = SessionLocal()
    rows: list[dict] = []
    try:
        runner = WorkerPipelineRunner()
        link_svc = TaskCurriculumLinkService(session)
        keys = (
            [args.collection]
            if args.collection
            else [c.chapter_key for c in PASCAL_SHOWCASE_COLLECTIONS]
        )
        for key in keys:
            for item in list_showcase_tasks_for_collection(session, key):
                item = dict(item)
                item["collection_key"] = key
                rows.append(_run_one(session, runner, link_svc, item))
    finally:
        session.close()

    print(json.dumps(rows, ensure_ascii=False, indent=2))
    failed = [r for r in rows if r["execution"] not in ("PASSED", "SKIPPED")]
    passed = [r for r in rows if r["execution"] == "PASSED"]
    print(
        json.dumps(
            {"passed": len(passed), "failed": len(failed), "total": len(rows)},
            ensure_ascii=False,
        )
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

