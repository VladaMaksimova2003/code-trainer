from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.dependencies.admin import (
    get_activate_version_uc,
    get_archive_assignment_uc,
    get_create_version_uc,
    get_list_assignments_uc,
    get_list_versions_uc,
    get_set_assignment_status_uc,
)
from api.dependencies.authorization import require_permission
from api.mappers.admin import to_assignment_item, to_version_item
from api.admin.schemas import (
    AdminAssignmentListItemResponse,
    AdminAssignmentVersionResponse,
    SetAssignmentWorkflowRequest,
)
from application.admin.assignments import (
    ActivateAssignmentVersionUseCase,
    ArchiveAssignmentUseCase,
    CreateAssignmentVersionUseCase,
    ListAssignmentVersionsUseCase,
    ListAssignmentsUseCase,
    SetAssignmentWorkflowStatusUseCase,
)
from application.auth.dto import CurrentUserResult
from domain.policies.permissions.permissions import Permission
from shared.enums import AssignmentWorkflowStatus

router = APIRouter(prefix="/assignments", tags=["admin-assignments"])


@router.get("", response_model=list[AdminAssignmentListItemResponse])
def list_assignments(
    include_deleted: bool = Query(default=True),
    _: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    use_case: ListAssignmentsUseCase = Depends(get_list_assignments_uc),
):
    return [to_assignment_item(a) for a in use_case.execute(include_deleted=include_deleted)]


@router.patch("/{task_id}/workflow-status", status_code=status.HTTP_204_NO_CONTENT)
def set_workflow_status(
    task_id: int,
    body: SetAssignmentWorkflowRequest,
    _: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    use_case: SetAssignmentWorkflowStatusUseCase = Depends(get_set_assignment_status_uc),
):
    try:
        status_enum = AssignmentWorkflowStatus(body.status.lower())
        use_case.execute(task_id, status_enum)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{task_id}/archive", status_code=status.HTTP_204_NO_CONTENT)
def archive_assignment(
    task_id: int,
    _: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    use_case: ArchiveAssignmentUseCase = Depends(get_archive_assignment_uc),
):
    try:
        use_case.execute(task_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{task_id}/versions", response_model=list[AdminAssignmentVersionResponse])
def list_versions(
    task_id: int,
    _: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    use_case: ListAssignmentVersionsUseCase = Depends(get_list_versions_uc),
):
    return [to_version_item(v) for v in use_case.execute(task_id)]


@router.post("/{task_id}/versions", response_model=AdminAssignmentVersionResponse)
def create_version(
    task_id: int,
    _: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    use_case: CreateAssignmentVersionUseCase = Depends(get_create_version_uc),
):
    try:
        return to_version_item(use_case.execute(task_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{task_id}/versions/{version_id}/activate", status_code=status.HTTP_204_NO_CONTENT)
def activate_version(
    task_id: int,
    version_id: int,
    _: CurrentUserResult = Depends(require_permission(Permission.EDIT_ASSIGNMENTS)),
    use_case: ActivateAssignmentVersionUseCase = Depends(get_activate_version_uc),
):
    try:
        use_case.execute(task_id, version_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
