from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencies.authorization import require_permission
from infrastructure.db.session import get_db
from application.learning.services.assignment_set_progress import assignment_set_progress
from api.dependencies.learning import (
    get_assignment_set_uc,
    get_create_assignment_set_uc,
    get_list_accessible_sets_uc,
    get_list_teacher_sets_uc,
    get_manage_set_items_uc,
    get_update_assignment_set_uc,
)
from api.mappers.learning import to_assignment_set
from api.learning.schemas import (
    AddAssignmentSetItemRequest,
    AssignmentSetResponse,
    CreateAssignmentSetRequest,
    UpdateAssignmentSetRequest,
)
from application.auth.dto import CurrentUserResult
from application.learning.use_cases.assignment_sets import (
    CreateAssignmentSetUseCase,
    GetAssignmentSetUseCase,
    ListAccessibleAssignmentSetsUseCase,
    ListTeacherAssignmentSetsUseCase,
    ManageAssignmentSetItemsUseCase,
    UpdateAssignmentSetUseCase,
)
from domain.policies.permissions.permissions import Permission
from shared.enums import AssignmentSetVisibility
from shared.exceptions import (
    AccessDeniedToContentError,
    AssignmentSetNotFoundError,
    GroupNotFoundError,
)

router = APIRouter(prefix="/assignment-sets", tags=["assignment-sets"])


def _assignment_set_response(
    db: Session,
    user_id: int | None,
    assignment_set,
) -> AssignmentSetResponse:
    task_ids = [item.task_id for item in assignment_set.items]
    total_tasks, solved_count = assignment_set_progress(
        db,
        user_id=user_id,
        task_ids=task_ids,
    )
    return to_assignment_set(
        assignment_set,
        total_tasks=total_tasks,
        solved_count=solved_count,
    )


def _visibility(raw: str) -> AssignmentSetVisibility:
    try:
        return AssignmentSetVisibility.parse(raw)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="visibility must be public or private",
        ) from exc


@router.post("", response_model=AssignmentSetResponse, status_code=status.HTTP_201_CREATED)
def create_set(
    body: CreateAssignmentSetRequest,
    current: CurrentUserResult = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    use_case: CreateAssignmentSetUseCase = Depends(get_create_assignment_set_uc),
):
    try:
        created = use_case.execute(
            teacher_id=current.id,
            name=body.name,
            description=body.description,
            visibility=_visibility(body.visibility),
            group_id=body.group_id,
        )
        return to_assignment_set(created)
    except GroupNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("", response_model=list[AssignmentSetResponse])
def list_sets(
    current: CurrentUserResult = Depends(require_permission(Permission.SOLVE_ASSIGNMENTS)),
    accessible_uc: ListAccessibleAssignmentSetsUseCase = Depends(get_list_accessible_sets_uc),
    db: Session = Depends(get_db),
):
    return [
        _assignment_set_response(db, current.id, s)
        for s in accessible_uc.execute(current.id, current.roles)
    ]


@router.get("/mine", response_model=list[AssignmentSetResponse])
def list_my_sets(
    include_archived: bool = False,
    current: CurrentUserResult = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    use_case: ListTeacherAssignmentSetsUseCase = Depends(get_list_teacher_sets_uc),
):
    return [to_assignment_set(s) for s in use_case.execute(current.id, include_archived)]


@router.get("/{set_id}", response_model=AssignmentSetResponse)
def get_set(
    set_id: int,
    current: CurrentUserResult = Depends(require_permission(Permission.SOLVE_ASSIGNMENTS)),
    use_case: GetAssignmentSetUseCase = Depends(get_assignment_set_uc),
    db: Session = Depends(get_db),
):
    try:
        return _assignment_set_response(
            db,
            current.id,
            use_case.execute(current.id, current.roles, set_id),
        )
    except AssignmentSetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AccessDeniedToContentError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.patch("/{set_id}", response_model=AssignmentSetResponse)
def update_set(
    set_id: int,
    body: UpdateAssignmentSetRequest,
    current: CurrentUserResult = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    use_case: UpdateAssignmentSetUseCase = Depends(get_update_assignment_set_uc),
):
    try:
        vis = _visibility(body.visibility) if body.visibility else None
        return to_assignment_set(
            use_case.execute(
                teacher_id=current.id,
                set_id=set_id,
                name=body.name,
                description=body.description,
                visibility=vis,
                group_id=body.group_id,
                is_archived=body.is_archived,
            )
        )
    except AssignmentSetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{set_id}/items", status_code=status.HTTP_204_NO_CONTENT)
def add_item(
    set_id: int,
    body: AddAssignmentSetItemRequest,
    current: CurrentUserResult = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    use_case: ManageAssignmentSetItemsUseCase = Depends(get_manage_set_items_uc),
):
    try:
        use_case.add(current.id, set_id, body.task_id, body.sort_order, body.topic)
    except AssignmentSetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{set_id}/items/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(
    set_id: int,
    task_id: int,
    current: CurrentUserResult = Depends(require_permission(Permission.MANAGE_ASSIGNMENT_SETS)),
    use_case: ManageAssignmentSetItemsUseCase = Depends(get_manage_set_items_uc),
):
    try:
        use_case.remove(current.id, set_id, task_id)
    except AssignmentSetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
