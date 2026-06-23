"""Remove legacy Pascal showcase tasks — keep only v3.1.1 (200 tasks)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

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

V311_GROUP_PREFIX = "pascal_curriculum_v311_"


def is_v311_showcase_task(task: TaskModel) -> bool:
    examples = dict(task.code_examples or {})
    showcase = examples.get("curriculum_showcase") or {}
    if showcase.get("curriculum_version") == "3.1.1":
        return True
    group = str(showcase.get("group") or "")
    return group.startswith(V311_GROUP_PREFIX)


@dataclass
class PascalLegacyPurgePlan:
    keep: list[dict[str, Any]] = field(default_factory=list)
    delete: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "keep_count": len(self.keep),
            "delete_count": len(self.delete),
            "keep": self.keep,
            "delete": self.delete,
        }


@dataclass
class PascalLegacyPurgeReport:
    dry_run: bool
    deleted_task_ids: list[int] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "dry_run": self.dry_run,
            "deleted_task_ids": self.deleted_task_ids,
            "counts": self.counts,
        }


def _task_info(task: TaskModel) -> dict[str, Any]:
    examples = dict(task.code_examples or {})
    showcase = examples.get("curriculum_showcase") or {}
    return {
        "task_id": task.id,
        "title": task.title,
        "task_type": task.task_type,
        "showcase_group": showcase.get("group"),
        "showcase_slug": showcase.get("slug"),
        "curriculum_version": showcase.get("curriculum_version"),
    }


def plan_purge_legacy_pascal_tasks(session: Session) -> PascalLegacyPurgePlan:
    rows = session.scalars(select(TaskModel).where(TaskModel.is_delete.is_(False))).all()
    plan = PascalLegacyPurgePlan()
    for task in rows:
        info = _task_info(task)
        examples = dict(task.code_examples or {})
        if not examples.get("curriculum_showcase"):
            continue
        if is_v311_showcase_task(task):
            plan.keep.append(info)
        else:
            plan.delete.append(info)
    return plan


def apply_purge_legacy_pascal_tasks(
    session: Session,
    *,
    dry_run: bool = False,
) -> PascalLegacyPurgeReport:
    plan = plan_purge_legacy_pascal_tasks(session)
    delete_ids = [row["task_id"] for row in plan.delete]
    report = PascalLegacyPurgeReport(dry_run=dry_run, deleted_task_ids=list(delete_ids))
    if not delete_ids or dry_run:
        return report

    bind = session.get_bind()
    table_names = set(inspect(bind).get_table_names())

    submission_ids: list[int] = []
    if "submission" in table_names:
        submission_ids = list(
            session.scalars(select(Submission.id).where(Submission.task_id.in_(delete_ids))).all()
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
            session.execute(delete(UserSolution).where(UserSolution.task_id.in_(delete_ids))).rowcount
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
