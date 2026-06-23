"""Create submission rows and enqueue worker jobs (single check contract)."""
from __future__ import annotations

from sqlalchemy.orm import Session

from application.execution.job_service import ExecutionJobService
from infrastructure.db.models.learning.submission import Submission
from infrastructure.execution.rate_limiter import ExecutionRateLimitError


class SubmissionExecutionService:
    def __init__(self, job_service: ExecutionJobService | None = None) -> None:
        self._jobs = job_service or ExecutionJobService()

    def create_and_enqueue(
        self,
        db: Session,
        *,
        user_id: int,
        task_id: int,
        language: str,
        code: str,
    ) -> Submission:
        submission = Submission(
            user_id=user_id,
            task_id=task_id,
            language=language,
            code=code,
            status="queued",
            success=None,
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

        try:
            self._jobs.submit(
                user_id=str(user_id),
                language_id=language,
                code="",
                op="process_submission",
                task_id=task_id,
                payload={"submission_id": submission.id},
            )
        except ExecutionRateLimitError:
            submission.status = "failed"
            db.commit()
            raise
        except Exception:
            submission.status = "failed"
            db.commit()
            raise

        return submission
