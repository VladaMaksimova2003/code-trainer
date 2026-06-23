from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies.authorization import require_permission
from api.execution.access import ensure_job_access, ensure_task_access
from application.execution.job_service import ExecutionJobService
from application.execution.submission_execution_service import SubmissionExecutionService
from application.auth.dto import CurrentUserResult
from infrastructure.execution.rate_limiter import ExecutionRateLimitError
from api.execution.solution_schemas import (
    JobQueuedResponse,
    JobResultResponse,
    JobStatusResponse,
    SolutionSubmitRequest,
    SubmissionQueuedResponse,
)
from domain.policies.permissions.permissions import Permission
from infrastructure.db.session import get_db

router = APIRouter()
_job_service = ExecutionJobService()
_submission_execution = SubmissionExecutionService(_job_service)


def _user_id(current_user: CurrentUserResult) -> str:
    return str(current_user.id)


@router.post("/submit", response_model=SubmissionQueuedResponse)
async def submit_solution(
    request: SolutionSubmitRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.SOLVE_ASSIGNMENTS)
    ),
):
    """Full check via submission record (preferred contract)."""
    try:
        ensure_task_access(db, current_user, request.task_id)
        submission = _submission_execution.create_and_enqueue(
            db,
            user_id=current_user.id,
            task_id=request.task_id,
            language=request.language,
            code=request.code,
        )
        return SubmissionQueuedResponse(
            submission_id=submission.id,
            status=submission.status,
        )
    except ExecutionRateLimitError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc


@router.post("/check", response_model=SubmissionQueuedResponse)
async def check_solution(
    request: SolutionSubmitRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.SOLVE_ASSIGNMENTS)
    ),
):
    return await submit_solution(request, db, current_user)


@router.post("/lint", response_model=JobQueuedResponse)
async def lint_solution(
    request: SolutionSubmitRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.SOLVE_ASSIGNMENTS)
    ),
):
    try:
        ensure_task_access(db, current_user, request.task_id)
        payload = _job_service.submit(
            user_id=_user_id(current_user),
            language_id=request.language,
            code=request.code,
            op="lint_only",
            task_id=request.task_id,
        )
        return JobQueuedResponse(**payload)
    except ExecutionRateLimitError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc


@router.post("/patterns", response_model=JobQueuedResponse)
async def check_patterns(
    request: SolutionSubmitRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.SOLVE_ASSIGNMENTS)
    ),
):
    try:
        ensure_task_access(db, current_user, request.task_id)
        payload = _job_service.submit(
            user_id=_user_id(current_user),
            language_id=request.language,
            code=request.code,
            op="pattern_only",
            task_id=request.task_id,
        )
        return JobQueuedResponse(**payload)
    except ExecutionRateLimitError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc


@router.get("/result/{job_id}", response_model=JobResultResponse)
async def get_solution_result(
    job_id: str,
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.SOLVE_ASSIGNMENTS)
    ),
):
    job = _job_service._store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    ensure_job_access(current_user, job.user_id)
    return JobResultResponse(**_job_service.get_result(job_id))


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_solution_status(
    job_id: str,
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.SOLVE_ASSIGNMENTS)
    ),
):
    job = _job_service._store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    ensure_job_access(current_user, job.user_id)
    return JobStatusResponse(**_job_service.get_status(job_id))
