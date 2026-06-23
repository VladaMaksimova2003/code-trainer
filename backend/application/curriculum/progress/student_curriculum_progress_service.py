"""Simple curriculum task progress (MVP — no mastery/review)."""

from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from application.curriculum.task_curriculum_link_service import TaskCurriculumLinkService
from application.learning.skill_progress_service import normalize_curriculum_language
from infrastructure.db.models.learning.student_curriculum_progress import (
    StudentCurriculumProgressModel,
)
from infrastructure.db.models.learning.submission import Submission
from infrastructure.repositories.curriculum.student_curriculum_progress_repository import (
    StudentCurriculumProgressRepository,
)

PROGRESS_STATUS_NOT_STARTED = "not_started"
PROGRESS_STATUS_FAILED = "failed"
PROGRESS_STATUS_PASSED = "passed"


@dataclass(frozen=True)
class _BatchProgressSnapshot:
    progress: dict[tuple[int, str], str]
    submission_passed: frozenset[tuple[int, str]]


_batch_snapshot: ContextVar[_BatchProgressSnapshot | None] = ContextVar(
    "batch_progress_snapshot",
    default=None,
)


def activate_batch_progress_cache(session: Session, user_id: int | None) -> Token | None:
    """Prefetch curriculum progress + submission wins for one request (collections/home)."""
    if user_id is None:
        return None
    rows = StudentCurriculumProgressRepository(session).list_all_for_user(user_id)
    progress = {
        (row.task_id, row.language.strip().lower()): progress_status_from_row(row)
        for row in rows
    }
    submission_rows = session.execute(
        select(
            Submission.task_id,
            Submission.language,
            func.max(case((Submission.success.is_(True), 1), else_=0)).label("solved"),
        )
        .where(Submission.user_id == user_id)
        .group_by(Submission.task_id, Submission.language)
    ).all()
    submission_passed: set[tuple[int, str]] = set()
    for row in submission_rows:
        if not bool(row.solved):
            continue
        lang = normalize_curriculum_language(row.language) or str(row.language or "").strip().lower()
        if lang:
            submission_passed.add((int(row.task_id), lang))
    snapshot = _BatchProgressSnapshot(
        progress=progress,
        submission_passed=frozenset(submission_passed),
    )
    return _batch_snapshot.set(snapshot)


def reset_batch_progress_cache(token: Token | None) -> None:
    if token is not None:
        _batch_snapshot.reset(token)


def get_batch_progress_cache() -> dict[tuple[int, str], str] | None:
    snapshot = _batch_snapshot.get()
    return snapshot.progress if snapshot is not None else None


def get_batch_submission_passed() -> frozenset[tuple[int, str]] | None:
    snapshot = _batch_snapshot.get()
    return snapshot.submission_passed if snapshot is not None else None


def progress_status_from_row(row: StudentCurriculumProgressModel | None) -> str:
    if row is None:
        return PROGRESS_STATUS_NOT_STARTED
    if row.passed_count > 0:
        return PROGRESS_STATUS_PASSED
    if row.attempts_count > 0:
        return PROGRESS_STATUS_FAILED
    return PROGRESS_STATUS_NOT_STARTED


def _row_to_dict(row: StudentCurriculumProgressModel) -> dict[str, Any]:
    return {
        "task_id": row.task_id,
        "language": row.language,
        "learning_concept_id": row.learning_concept_id,
        "technical_concept_id": row.technical_concept_id,
        "action": row.action,
        "exercise_pattern_id": row.exercise_pattern_id,
        "attempts_count": row.attempts_count,
        "passed_count": row.passed_count,
        "last_status": row.last_status,
        "last_submission_id": row.last_submission_id,
        "last_attempt_at": row.last_attempt_at.isoformat() if row.last_attempt_at else None,
        "first_passed_at": row.first_passed_at.isoformat() if row.first_passed_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        "progress_status": progress_status_from_row(row),
    }


def _percent(passed: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(100.0 * passed / total, 1)


class StudentCurriculumProgressService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repo = StudentCurriculumProgressRepository(session)

    def _passed_task_ids_from_submissions(
        self,
        user_id: int,
        task_ids: list[int],
        language: str,
    ) -> set[int]:
        if not task_ids:
            return set()
        batch_passed = get_batch_submission_passed()
        lang = normalize_curriculum_language(language) or language.strip().lower()
        if batch_passed is not None:
            return {tid for tid in task_ids if (tid, lang) in batch_passed}
        rows = self._session.execute(
            select(
                Submission.task_id,
                func.max(case((Submission.success.is_(True), 1), else_=0)).label("solved"),
            )
            .where(
                Submission.user_id == user_id,
                Submission.task_id.in_(task_ids),
                func.lower(Submission.language) == lang,
            )
            .group_by(Submission.task_id)
        ).all()
        return {int(row.task_id) for row in rows if bool(row.solved)}

    def _merge_passed_task_ids(
        self,
        user_id: int,
        task_ids: list[int],
        language: str,
        passed_task_ids: set[int],
    ) -> set[int]:
        if not task_ids:
            return passed_task_ids
        submission_passed = self._passed_task_ids_from_submissions(user_id, task_ids, language)
        return passed_task_ids | submission_passed

    def record_submission_result(
        self,
        user_id: int,
        submission_id: int,
        task_id: int,
        *,
        passed: bool,
        learning_language: str | None = None,
    ) -> None:
        """Update progress when a submission reaches a terminal state."""
        if user_id is None:
            return

        lang = self._resolve_learning_language(submission_id, learning_language)
        link_service = TaskCurriculumLinkService(self._session)
        primary = link_service.get_primary_link_for_task(task_id, language=lang)
        if not primary:
            return
        track_language = str(primary["language"]).strip().lower()
        if lang and track_language != lang:
            return

        now = datetime.now(timezone.utc)
        row = self._repo.get_by_user_task_language(user_id, task_id, track_language)
        if row is None:
            row = StudentCurriculumProgressModel(
                user_id=user_id,
                task_id=task_id,
                language=track_language,
                learning_concept_id=str(primary["learning_concept_id"]),
                technical_concept_id=str(primary["technical_concept_id"]),
                action=str(primary["action"]),
                exercise_pattern_id=str(primary["exercise_pattern_id"]),
                attempts_count=0,
                passed_count=0,
            )
            self._session.add(row)

        row.attempts_count += 1
        row.last_submission_id = submission_id
        row.last_attempt_at = now
        row.updated_at = now
        row.last_status = "passed" if passed else "failed"

        if passed and row.passed_count == 0:
            row.passed_count = 1
            row.first_passed_at = now

        self._session.flush()

    def _resolve_learning_language(
        self,
        submission_id: int,
        learning_language: str | None,
    ) -> str | None:
        if learning_language:
            return learning_language.strip().lower()
        submission = self._session.get(Submission, submission_id)
        if submission is not None and submission.language:
            return submission.language.strip().lower()
        return None

    def get_progress_for_task(
        self,
        user_id: int,
        task_id: int,
        *,
        language: str | None = None,
    ) -> dict[str, Any]:
        if language:
            row = self._repo.get_by_user_task_language(user_id, task_id, language)
        else:
            row = self._repo.get_by_user_and_task(user_id, task_id)
        status = progress_status_from_row(row)
        if row is None:
            return {
                "task_id": task_id,
                "progress_status": status,
                "attempts_count": 0,
                "passed_count": 0,
            }
        payload = _row_to_dict(row)
        return payload

    def get_progress_for_learning_concept(
        self,
        user_id: int,
        language: str,
        learning_concept_id: str,
        *,
        task_ids: list[int],
        tasks_by_tc: dict[str, list[int]] | None = None,
    ) -> dict[str, Any]:
        """Aggregate progress for a learning concept over a fixed task set (e.g. showcase)."""
        lang = language.strip().lower()
        batch = get_batch_progress_cache()
        if batch is not None:
            status_by_task = {
                tid: batch.get((tid, lang), PROGRESS_STATUS_NOT_STARTED) for tid in task_ids
            }
            passed_task_ids = {
                tid for tid, status in status_by_task.items() if status == PROGRESS_STATUS_PASSED
            }
            passed_task_ids = self._merge_passed_task_ids(
                user_id,
                task_ids,
                lang,
                passed_task_ids,
            )
            for tid in passed_task_ids:
                status_by_task[tid] = PROGRESS_STATUS_PASSED
            total = len(task_ids)
            passed = len(passed_task_ids)

            by_tc: dict[str, dict[str, Any]] = {}
            if tasks_by_tc:
                for tc_id, tc_task_ids in tasks_by_tc.items():
                    tc_total = len(tc_task_ids)
                    tc_passed = sum(1 for tid in tc_task_ids if tid in passed_task_ids)
                    by_tc[tc_id] = {
                        "technical_concept_id": tc_id,
                        "total_tasks": tc_total,
                        "passed_tasks": tc_passed,
                        "progress_percent": _percent(tc_passed, tc_total),
                    }

            return {
                "language": lang,
                "learning_concept_id": learning_concept_id,
                "total_tasks": total,
                "passed_tasks": passed,
                "progress_percent": _percent(passed, total),
                "by_technical_concept": by_tc,
                "by_task_id": {
                    tid: {
                        "task_id": tid,
                        "progress_status": status_by_task[tid],
                        "attempts_count": 0,
                        "passed_count": 1 if tid in passed_task_ids else 0,
                    }
                    for tid in task_ids
                },
            }

        rows = self._repo.list_for_user_tasks(user_id, task_ids, language=lang)
        by_task_id = {row.task_id: row for row in rows}

        passed_task_ids = {tid for tid, row in by_task_id.items() if row.passed_count > 0}
        passed_task_ids = self._merge_passed_task_ids(
            user_id,
            task_ids,
            lang,
            passed_task_ids,
        )
        total = len(task_ids)
        passed = len(passed_task_ids)

        by_tc: dict[str, dict[str, Any]] = {}
        if tasks_by_tc:
            for tc_id, tc_task_ids in tasks_by_tc.items():
                tc_total = len(tc_task_ids)
                tc_passed = sum(1 for tid in tc_task_ids if tid in passed_task_ids)
                by_tc[tc_id] = {
                    "technical_concept_id": tc_id,
                    "total_tasks": tc_total,
                    "passed_tasks": tc_passed,
                    "progress_percent": _percent(tc_passed, tc_total),
                }

        return {
            "language": lang,
            "learning_concept_id": learning_concept_id,
            "total_tasks": total,
            "passed_tasks": passed,
            "progress_percent": _percent(passed, total),
            "by_technical_concept": by_tc,
            "by_task_id": {
                tid: {
                    "task_id": tid,
                    "progress_status": (
                        PROGRESS_STATUS_PASSED
                        if tid in passed_task_ids
                        else progress_status_from_row(by_task_id.get(tid))
                    ),
                    "attempts_count": (by_task_id[tid].attempts_count if tid in by_task_id else 0),
                    "passed_count": (
                        1 if tid in passed_task_ids else (by_task_id[tid].passed_count if tid in by_task_id else 0)
                    ),
                }
                for tid in task_ids
            },
        }
