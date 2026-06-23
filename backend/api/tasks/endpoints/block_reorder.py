"""Block-reorder task endpoints (create, submit)."""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from application.auth.dto import CurrentUserResult
from application.execution.job_service import ExecutionJobService
from application.tasks.services.content_access_service import ContentAccessService
from application.tasks.use_cases.block_reorder.create import create_block_reorder_task
from application.tasks.use_cases.block_reorder.validate import validate_block_reorder_solution
from api.tasks.schemas.requests import BlockReorderCreateRequest, BlockReorderSolutionRequest
from api.dependencies.authorization import require_permission
from domain.policies.permissions.permissions import Permission
from domain.policies.rbac.rbac import normalize_role
from infrastructure.db.session import get_db
from infrastructure.db.models.learning.submission import Submission, SubmissionTestResult
from application.curriculum.progress.submission_curriculum_progress import (
    record_curriculum_progress_in_session,
)
from shared.exceptions import AccessDeniedToContentError

router = APIRouter(prefix="/block-reorder")
_job_service = ExecutionJobService()


def _find_block_submission(
    db: Session,
    user_id: int,
    task_id: int,
    code: str,
) -> Submission | None:
    return (
        db.query(Submission)
        .filter(
            Submission.user_id == user_id,
            Submission.task_id == task_id,
            Submission.code == code,
        )
        .order_by(Submission.id.desc())
        .first()
    )


def _record_block_submission(
    db: Session,
    current_user: CurrentUserResult,
    task_id: int,
    language: str | None,
    result: dict,
) -> None:
    code = str(result.get("assembled_code") or "")
    is_success = bool(result.get("correct"))
    existing = _find_block_submission(db, current_user.id, task_id, code)
    if existing is not None:
        if is_success and not existing.success:
            existing.success = True
            existing.status = "done"
            existing.updated_at = datetime.now(timezone.utc)
            record_curriculum_progress_in_session(
                db,
                user_id=current_user.id,
                submission_id=existing.id,
                task_id=task_id,
                passed=True,
            )
            db.commit()
        return
    submission = Submission(
        user_id=current_user.id,
        task_id=task_id,
        language=language or "",
        code=code,
        status="done",
        success=is_success,
        updated_at=datetime.now(timezone.utc),
    )
    db.add(submission)
    db.flush()
    for item in result.get("execution_results") or []:
        db.add(
            SubmissionTestResult(
                submission_id=submission.id,
                case_number=int(item.get("case", 0) or 0),
                status=str(item.get("status", "ERROR")),
                inputs=str(item.get("inputs", "")),
                expected=str(item.get("expected", "")),
                actual=str(item.get("actual", "")),
                message=str(item.get("message", "")),
            )
        )
    record_curriculum_progress_in_session(
        db,
        user_id=current_user.id,
        submission_id=submission.id,
        task_id=task_id,
        passed=is_success,
    )
    db.commit()


@router.post("")
async def create_block_reorder(
    request: BlockReorderCreateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.CREATE_ASSIGNMENTS)
    ),
):
    """Create a block reorder task."""
    return create_block_reorder_task(
        db,
        title=request.title,
        description=request.description,
        difficulty=request.difficulty,
        original_code=request.original_code,
        template=request.template,
        language=request.language,
        language_variants=request.language_variants,
        teacher_id=current_user.id,
        blocks=request.blocks,
        correct_order=request.correct_order,
        test_cases=request.test_cases,
    )


@router.post("/{task_id}/submit")
async def submit_block_reorder(
    task_id: int,
    request: BlockReorderSolutionRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.SOLVE_ASSIGNMENTS)
    ),
):
    """Validate user order for a block reorder task."""
    access = ContentAccessService(db)
    roles = frozenset(normalize_role(r) for r in current_user.roles)
    try:
        access.ensure_task_access(current_user.id, roles, task_id)
    except AccessDeniedToContentError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    result = validate_block_reorder_solution(
        db,
        task_id,
        request.order,
        request.language,
        request.indents,
        assembled_code=request.assembled_code,
        user_id=str(current_user.id),
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Block reorder task not found")
    if not result.get("execution_job_id"):
        _record_block_submission(db, current_user, task_id, request.language, result)
    return result


@router.get("/validate/result/{job_id}")
async def get_block_reorder_validate_result(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.SOLVE_ASSIGNMENTS)
    ),
):
    """Poll block-reorder validation (Docker runs in execution worker only)."""
    payload = _job_service.get_result(job_id)
    validation = payload.get("validation") or {}
    if payload.get("status") in {"SUCCESS", "FAILED"} and validation:
        merged = {**validation, "execution_job_id": job_id, "status": payload["status"]}
        if validation.get("task_id"):
            _record_block_submission(
                db,
                current_user,
                int(validation["task_id"]),
                validation.get("language"),
                merged,
            )
        return merged
    return payload
