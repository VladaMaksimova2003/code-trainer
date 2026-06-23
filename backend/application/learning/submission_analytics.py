"""Shared submission/task analytics helpers (no recommendations imports)."""

from __future__ import annotations

from sqlalchemy.orm import Session, joinedload

from application.tasks.services.catalog.task_catalog_orchestrator import LEGACY_TASKS_DB
from infrastructure.db.models.learning.group import Group, group_member_association_table
from infrastructure.db.models.learning.submission import Submission
from infrastructure.db.models.task import Task as TaskModel
from sqlalchemy import select

LEVEL_LABELS = (
    (0.33, "начальный"),
    (0.66, "средний"),
    (1.01, "продвинутый"),
)


def compute_level(completion_ratio: float) -> str:
    for threshold, label in LEVEL_LABELS:
        if completion_ratio < threshold:
            return label
    return "продвинутый"


def task_constructions(db: Session, task: TaskModel) -> list[str]:
    """Теги навыков: code_examples.patterns, затем constructions в БД, затем legacy."""
    from application.tasks.services.catalog.task_query import _resolve_task_constructions

    legacy = LEGACY_TASKS_DB.get(task.id, {})
    legacy_list = list(legacy.get("constructions", []))
    db_tags = [c.name for c in task.constructions] if task.constructions else []
    return _resolve_task_constructions(task.code_examples, db_tags or legacy_list)


def classify_submission_errors(submission: Submission) -> str:
    """Return primary error category for a failed submission: syntax | logic | runtime."""
    if submission.success is True:
        return "none"
    compiler = [e for e in submission.linter_errors if e.error_type == "COMPILER"]
    if compiler:
        return "syntax"
    if submission.pattern_errors:
        return "logic"
    failed_tests = [
        t
        for t in submission.test_results
        if (t.status or "").upper() not in {"OK", "PASSED", "PASS", "ACCEPTED"}
    ]
    if failed_tests:
        messages = " ".join(
            (t.message or "") + (t.actual or "") for t in failed_tests
        ).lower()
        if any(
            token in messages
            for token in ("runtime", "exception", "segmentation", "traceback", "error:")
        ):
            return "runtime"
        return "logic"
    internal = [e for e in submission.linter_errors if e.error_type == "INTERNAL_ERROR"]
    if internal:
        return "runtime"
    if submission.linter_errors:
        return "syntax"
    if submission.success is False:
        return "logic"
    return "logic"


def load_task_map(db: Session, task_ids: set[int]) -> dict[int, TaskModel]:
    if not task_ids:
        return {}
    rows = (
        db.query(TaskModel)
        .options(joinedload(TaskModel.constructions))
        .filter(TaskModel.id.in_(task_ids))
        .all()
    )
    return {t.id: t for t in rows}


def teacher_group_student_ids(db: Session, teacher_id: int) -> set[int]:
    return set(
        db.execute(
            select(group_member_association_table.c.student_id)
            .join(Group, Group.id == group_member_association_table.c.group_id)
            .where(Group.teacher_id == teacher_id)
        ).scalars().all()
    )
