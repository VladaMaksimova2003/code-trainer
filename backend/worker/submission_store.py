from __future__ import annotations

from datetime import datetime, timezone

from infrastructure.db.session import SessionLocal
from infrastructure.db.models.learning.submission import (
    Submission,
    SubmissionLintError,
    SubmissionPatternError,
    SubmissionTestResult,
)
from shared.enums import NotificationKind


class SubmissionStore:
    TERMINAL_STATUSES = frozenset({"done", "failed"})

    def load_for_execution(self, submission_id: int) -> tuple[str, str, int, int]:
        db = SessionLocal()
        try:
            submission = db.get(Submission, submission_id)
            if submission is None:
                raise ValueError(f"Submission {submission_id} not found")
            if submission.user_id is None:
                raise ValueError(f"Submission {submission_id} has no owner")
            return (
                submission.code,
                submission.language,
                int(submission.task_id),
                int(submission.user_id),
            )
        finally:
            db.close()

    def mark_running(self, submission_id: int) -> None:
        db = SessionLocal()
        try:
            submission = db.get(Submission, submission_id)
            if submission is None:
                return
            if submission.status in self.TERMINAL_STATUSES:
                return
            submission.status = "running"
            submission.updated_at = datetime.now(timezone.utc)
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def persist_success(self, submission_id: int, result: dict) -> None:
        db = SessionLocal()
        try:
            submission = db.get(Submission, submission_id)
            if not submission:
                return

            submission.status = "done"
            submission.success = bool(result.get("success"))
            submission.updated_at = datetime.now(timezone.utc)

            db.query(SubmissionLintError).filter(
                SubmissionLintError.submission_id == submission_id
            ).delete()
            db.query(SubmissionPatternError).filter(
                SubmissionPatternError.submission_id == submission_id
            ).delete()
            db.query(SubmissionTestResult).filter(
                SubmissionTestResult.submission_id == submission_id
            ).delete()

            for error in result.get("compiler_errors", []):
                db.add(
                    SubmissionLintError(
                        submission_id=submission_id,
                        error_type=error["type"],
                        text=error["text"],
                    )
                )

            for error in result.get("linter_errors", []):
                db.add(
                    SubmissionLintError(
                        submission_id=submission_id,
                        error_type=error["type"],
                        text=error["text"],
                    )
                )

            for error in result.get("pattern_errors", []):
                db.add(
                    SubmissionPatternError(
                        submission_id=submission_id,
                        error_type=error["type"],
                        text=error["text"],
                    )
                )

            for test in result.get("test_results", []):
                db.add(
                    SubmissionTestResult(
                        submission_id=submission_id,
                        case_number=test.get("case", 0),
                        status=test.get("status", "ERROR"),
                        inputs=test.get("inputs", ""),
                        expected=test.get("expected", ""),
                        actual=test.get("actual", ""),
                        message=test.get("message", ""),
                    )
                )

            db.commit()
            passed = bool(result.get("success"))
            self._notify_checked_safe(
                submission_id=submission_id,
                user_id=submission.user_id,
                task_id=submission.task_id,
                success=passed,
            )
            self._record_curriculum_progress_safe(
                submission_id=submission_id,
                user_id=submission.user_id,
                task_id=submission.task_id,
                passed=passed,
            )
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def mark_failed(self, submission_id: int, message: str) -> None:
        db = SessionLocal()
        try:
            submission = db.get(Submission, submission_id)
            if not submission:
                return

            submission.status = "failed"
            submission.success = False
            submission.updated_at = datetime.now(timezone.utc)
            db.query(SubmissionLintError).filter(
                SubmissionLintError.submission_id == submission_id
            ).delete()
            db.add(
                SubmissionLintError(
                    submission_id=submission_id,
                    error_type="INTERNAL_ERROR",
                    text=message,
                )
            )
            db.commit()
            self._notify_checked_safe(
                submission_id=submission_id,
                user_id=submission.user_id,
                task_id=submission.task_id,
                success=False,
            )
            self._record_curriculum_progress_safe(
                submission_id=submission_id,
                user_id=submission.user_id,
                task_id=submission.task_id,
                passed=False,
            )
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def _record_curriculum_progress_safe(
        self,
        *,
        submission_id: int,
        user_id: int | None,
        task_id: int,
        passed: bool,
    ) -> None:
        from application.curriculum.progress.submission_curriculum_progress import (
            record_curriculum_progress_safe,
        )

        record_curriculum_progress_safe(
            user_id=user_id,
            submission_id=submission_id,
            task_id=task_id,
            passed=passed,
        )

    def _notify_checked_safe(
        self,
        *,
        submission_id: int,
        user_id: int | None,
        task_id: int,
        success: bool,
    ) -> None:
        if user_id is None:
            return
        db = SessionLocal()
        try:
            from application.support.notifications_service import create_notification

            title = "Проверка завершена" if success else "Проверка завершена с ошибками"
            body = (
                f"Задача #{task_id}: решение принято."
                if success
                else f"Задача #{task_id}: проверьте ошибки в отчёте."
            )
            create_notification(
                db,
                user_id=int(user_id),
                kind=NotificationKind.SUBMISSION_CHECKED,
                title=title,
                body=body,
                task_id=int(task_id),
                submission_id=int(submission_id),
            )
            db.commit()
        except Exception as exc:
            db.rollback()
            print(f"[submission_store] notification skipped: {exc}")
        finally:
            db.close()
