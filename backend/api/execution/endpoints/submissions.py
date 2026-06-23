"""POST/GET /submissions — async execution via partitioned job queue."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.dependencies.authorization import require_permission
from api.execution.access import ensure_submission_access, ensure_task_access
from api.execution.schemas.requests import SubmissionCreateRequest
from application.auth.dto import CurrentUserResult
from application.execution.submission_execution_service import SubmissionExecutionService
from application.execution.submission_serializer import serialize_submission
from domain.policies.permissions.permissions import Permission
from infrastructure.execution.rate_limiter import ExecutionRateLimitError, ExecutionRateLimiter
from infrastructure.db.session import get_db
from infrastructure.db.models.learning.submission import Submission

router = APIRouter()
_execution = SubmissionExecutionService()


@router.get("/pending/latest")
async def get_latest_pending_submission(
    task_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.SOLVE_ASSIGNMENTS)
    ),
):
    ensure_task_access(db, current_user, task_id)
    submission = (
        db.query(Submission)
        .filter(
            Submission.user_id == current_user.id,
            Submission.task_id == task_id,
            Submission.status.in_(("queued", "running")),
        )
        .order_by(Submission.created_at.desc())
        .first()
    )
    if submission is None:
        return {"submission": None}
    submission.linter_errors
    submission.pattern_errors
    submission.test_results
    return {"submission": serialize_submission(submission)}


@router.get("/latest")
async def get_latest_submission_for_task(
    task_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.SOLVE_ASSIGNMENTS)
    ),
):
    """Latest submission id for a task — lightweight alternative to full student analytics."""
    ensure_task_access(db, current_user, task_id)
    submission = (
        db.query(Submission)
        .filter(
            Submission.user_id == current_user.id,
            Submission.task_id == task_id,
        )
        .order_by(Submission.created_at.desc())
        .first()
    )
    return {"submission_id": int(submission.id) if submission else None}


@router.post("/")
async def create_submission(
    request: SubmissionCreateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult = Depends(require_permission(Permission.SOLVE_ASSIGNMENTS)),
):
    try:
        ensure_task_access(db, current_user, request.task_id)
        submission = _execution.create_and_enqueue(
            db,
            user_id=current_user.id,
            task_id=request.task_id,
            language=request.language,
            code=request.code,
        )
        return {
            "submission_id": submission.id,
            "status": submission.status,
            "message": "Submission queued",
        }
    except ExecutionRateLimitError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Submission service unavailable: {exc}") from exc


@router.post("/{submission_id}/abandon")
async def abandon_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.SOLVE_ASSIGNMENTS)
    ),
):
    """Release a stuck queued/running submission and free execution rate-limit slots."""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    ensure_submission_access(db, current_user, submission.user_id, submission.task_id)
    if submission.status not in ("queued", "running"):
        return {"released": False, "status": submission.status}
    submission.status = "failed"
    submission.success = False
    db.commit()
    ExecutionRateLimiter().on_job_finished(str(current_user.id))
    return {"released": True, "status": submission.status}


@router.get("/{submission_id}")
async def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.SOLVE_ASSIGNMENTS)
    ),
):
    try:
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        ensure_submission_access(db, current_user, submission.user_id, submission.task_id)
        submission.linter_errors
        submission.pattern_errors
        submission.test_results
        return serialize_submission(submission)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Submission service unavailable: {exc}") from exc
