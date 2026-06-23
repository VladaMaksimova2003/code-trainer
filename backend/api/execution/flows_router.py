from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies.authorization import require_permission
from api.execution.access import ensure_job_access, ensure_task_access
from application.auth.dto import CurrentUserResult
from application.execution.job_service import ExecutionJobService
from application.execution.services.flow_validation_service import FlowValidationService
from application.execution.use_cases.check_flow import CheckFlowUseCase
from application.execution.flow_dto import CheckFlowDTO
from application.tasks.services.catalog.task_catalog_orchestrator import get_task, get_task_flow_spec
from domain.policies.permissions.permissions import Permission
from infrastructure.db.session import get_db

router = APIRouter()
_job_service = ExecutionJobService()
_FLOW_TASK_TYPES = {"blocks", "diagram", "task_flowchart_to_code"}


@router.post("/check")
async def check_flow(
    request: CheckFlowDTO,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.SOLVE_ASSIGNMENTS)
    ),
):
    """Structural flowchart validation (block types and graph connectivity)."""
    ensure_task_access(db, current_user, request.task_id)
    task = get_task(db=db, task_id=request.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.get("type") not in _FLOW_TASK_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Flow check is available only for flowchart task types",
        )

    flow_spec = get_task_flow_spec(db=db, task_id=request.task_id) or {}

    use_case = CheckFlowUseCase(validator=FlowValidationService())
    result = use_case.execute(request, flow_spec, task=task)
    return result.model_dump()


@router.get("/validate/result/{job_id}")
async def get_flow_validate_result(
    job_id: str,
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.SOLVE_ASSIGNMENTS)
    ),
):
    """Poll semantic flow validation result."""
    job = _job_service._store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    ensure_job_access(current_user, job.user_id)
    payload = _job_service.get_result(job_id)
    validation = payload.get("validation") or {}
    if validation:
        errors = validation.get("errors") or []
        payload["success"] = len(errors) == 0
        payload["errors"] = errors
        payload["execution_results"] = validation.get("execution_results") or []
        payload["test_cases"] = validation.get("test_cases") or []
        payload["semantic_checked"] = validation.get("semantic_checked", False)
    return payload
