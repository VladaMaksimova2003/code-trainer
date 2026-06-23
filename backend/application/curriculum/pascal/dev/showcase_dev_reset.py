"""Dev-only cleanup: remove legacy/showcase tasks, keep Pascal curriculum v2 showcase."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import delete, inspect, select
from sqlalchemy.orm import Session

from application.curriculum.pascal.legacy.loops.loops_showcase_data import SHOWCASE_GROUP
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


class DevResetNotAllowedError(RuntimeError):
    """Raised when dev reset safety checks fail."""


def assert_dev_reset_allowed() -> None:
    env = (os.environ.get("ENV") or "").strip().lower()
    allow = (os.environ.get("ALLOW_DEV_RESET") or "").strip()
    if env == "dev" or allow == "1":
        return
    raise DevResetNotAllowedError(
        "Dev reset blocked. Set ENV=dev or ALLOW_DEV_RESET=1 before running."
    )


def is_pascal_curriculum_showcase_task(task: TaskModel) -> bool:
    examples = dict(task.code_examples or {})
    showcase = examples.get("curriculum_showcase") or {}
    return showcase.get("group") == SHOWCASE_GROUP


@dataclass
class TaskResetRow:
    task_id: int
    title: str
    task_type: str
    reason: str
    showcase_group: str | None = None
    showcase_slug: str | None = None


@dataclass
class ShowcaseDevResetPlan:
    keep: list[TaskResetRow] = field(default_factory=list)
    delete: list[TaskResetRow] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "keep_count": len(self.keep),
            "delete_count": len(self.delete),
            "keep": [row.__dict__ for row in self.keep],
            "delete": [row.__dict__ for row in self.delete],
        }


@dataclass
class ShowcaseDevResetReport:
    dry_run: bool
    deleted_task_ids: list[int] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "dry_run": self.dry_run,
            "deleted_task_ids": self.deleted_task_ids,
            "counts": self.counts,
        }


def _task_row(task: TaskModel, *, reason: str) -> TaskResetRow:
    examples = dict(task.code_examples or {})
    showcase = examples.get("curriculum_showcase") or {}
    return TaskResetRow(
        task_id=task.id,
        title=task.title,
        task_type=task.task_type,
        reason=reason,
        showcase_group=showcase.get("group"),
        showcase_slug=showcase.get("slug"),
    )


def plan_showcase_dev_reset(session: Session) -> ShowcaseDevResetPlan:
    rows = session.scalars(select(TaskModel).order_by(TaskModel.id.asc())).all()
    plan = ShowcaseDevResetPlan()
    for task in rows:
        if is_pascal_curriculum_showcase_task(task):
            plan.keep.append(_task_row(task, reason="pascal_curriculum_loops_v1"))
        else:
            plan.delete.append(_task_row(task, reason="legacy_or_old_showcase"))
    return plan


def apply_showcase_dev_reset(session: Session, *, dry_run: bool = False) -> ShowcaseDevResetReport:
    plan = plan_showcase_dev_reset(session)
    delete_ids = [row.task_id for row in plan.delete]
    report = ShowcaseDevResetReport(dry_run=dry_run, deleted_task_ids=list(delete_ids))

    if not delete_ids:
        return report

    if dry_run:
        return report

    bind = session.get_bind()
    table_names = set(inspect(bind).get_table_names())

    submission_ids: list[int] = []
    if "submission" in table_names:
        submission_ids = list(
            session.scalars(
                select(Submission.id).where(Submission.task_id.in_(delete_ids))
            ).all()
        )

    if submission_ids and "submission_lint_error" in table_names:
        report.counts["submission_lint_error"] = (
            session.execute(
                delete(SubmissionLintError).where(
                    SubmissionLintError.submission_id.in_(submission_ids)
                )
            ).rowcount
            or 0
        )
    if submission_ids and "submission_pattern_error" in table_names:
        report.counts["submission_pattern_error"] = (
            session.execute(
                delete(SubmissionPatternError).where(
                    SubmissionPatternError.submission_id.in_(submission_ids)
                )
            ).rowcount
            or 0
        )
    if submission_ids and "submission_test_result" in table_names:
        report.counts["submission_test_result"] = (
            session.execute(
                delete(SubmissionTestResult).where(
                    SubmissionTestResult.submission_id.in_(submission_ids)
                )
            ).rowcount
            or 0
        )

    if "submission" in table_names:
        report.counts["submission"] = (
            session.execute(delete(Submission).where(Submission.task_id.in_(delete_ids))).rowcount
            or 0
        )
    if "user_solution" in table_names:
        report.counts["user_solution"] = (
            session.execute(
                delete(UserSolution).where(UserSolution.task_id.in_(delete_ids))
            ).rowcount
            or 0
        )
    if "collection_task_association" in table_names:
        report.counts["collection_task_association"] = (
            session.execute(
                delete(collection_task_association_table).where(
                    collection_task_association_table.c.task_id.in_(delete_ids)
                )
            ).rowcount
            or 0
        )
    if "task_construction_association" in table_names:
        report.counts["task_construction_association"] = (
            session.execute(
                delete(task_construction_association_table).where(
                    task_construction_association_table.c.task_id.in_(delete_ids)
                )
            ).rowcount
            or 0
        )
    if "task_version" in table_names:
        report.counts["task_version"] = (
            session.execute(delete(TaskVersion).where(TaskVersion.task_id.in_(delete_ids))).rowcount
            or 0
        )
    if "task_curriculum_link" in table_names:
        report.counts["task_curriculum_link"] = (
            session.execute(
                delete(TaskCurriculumLinkModel).where(
                    TaskCurriculumLinkModel.task_id.in_(delete_ids)
                )
            ).rowcount
            or 0
        )
    if "block_reorder_task" in table_names:
        report.counts["block_reorder_task"] = (
            session.execute(
                delete(BlockReorderTask).where(BlockReorderTask.task_id.in_(delete_ids))
            ).rowcount
            or 0
        )
    if "translation_task" in table_names:
        report.counts["translation_task"] = (
            session.execute(
                delete(TranslationTask).where(TranslationTask.task_id.in_(delete_ids))
            ).rowcount
            or 0
        )
    report.counts["task"] = (
        session.execute(delete(TaskModel).where(TaskModel.id.in_(delete_ids))).rowcount or 0
    )

    return report

