from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencies.authorization import require_permission
from application.learning.use_cases.groups.dashboard import (
    assign_catalog_to_group,
    build_group_dashboard,
    build_student_assigned_catalogs,
    build_student_group_task_progress,
    build_student_group_workspace,
    build_student_joined_groups_overview,
    build_student_own_group_catalogs,
)
from infrastructure.db.session import get_db
from infrastructure.repositories.learning.group import SqlAlchemyGroupRepository
from api.dependencies.learning import (
    get_create_group_uc,
    get_delete_group_uc,
    get_generate_invitation_uc,
    get_join_group_uc,
    get_list_student_groups_uc,
    get_list_teacher_groups_uc,
)
from api.mappers.learning import to_group, to_invitation
from api.learning.schemas import (
    AssignCatalogToGroupRequest,
    CreateGroupRequest,
    GenerateInvitationRequest,
    GroupDashboardResponse,
    GroupResponse,
    StudentGroupTaskProgressResponse,
    StudentGroupWorkspaceResponse,
    StudentJoinedGroupOverviewResponse,
    StudentAssignedCatalogSummaryResponse,
    InvitationCodeResponse,
    JoinGroupRequest,
)
from application.auth.dto import CurrentUserResult
from application.learning.use_cases.groups.groups import (
    CreateGroupUseCase,
    DeleteGroupUseCase,
    GenerateInvitationCodeUseCase,
    JoinGroupByInvitationUseCase,
    ListStudentGroupsUseCase,
    ListTeacherGroupsUseCase,
)
from domain.policies.permissions.permissions import Permission
from shared.exceptions import (
    AlreadyGroupMemberError,
    GroupNotFoundError,
    InvalidInvitationCodeError,
)

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(
    body: CreateGroupRequest,
    current: CurrentUserResult = Depends(require_permission(Permission.MANAGE_GROUPS)),
    use_case: CreateGroupUseCase = Depends(get_create_group_uc),
):
    return to_group(use_case.execute(teacher_id=current.id, name=body.name))


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(
    group_id: int,
    current: CurrentUserResult = Depends(require_permission(Permission.MANAGE_GROUPS)),
    use_case: DeleteGroupUseCase = Depends(get_delete_group_uc),
) -> None:
    try:
        use_case.execute(teacher_id=current.id, group_id=group_id)
    except GroupNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/mine", response_model=list[GroupResponse])
def list_my_teacher_groups(
    current: CurrentUserResult = Depends(require_permission(Permission.MANAGE_GROUPS)),
    use_case: ListTeacherGroupsUseCase = Depends(get_list_teacher_groups_uc),
    db: Session = Depends(get_db),
):
    repo = SqlAlchemyGroupRepository(db)
    out: list[GroupResponse] = []
    for g in use_case.execute(current.id):
        base = to_group(g)
        out.append(
            GroupResponse(
                id=base.id,
                name=base.name,
                teacher_id=base.teacher_id,
                created_at=base.created_at,
                member_count=len(repo.list_member_ids(g.id)),
            )
        )
    return out


@router.get("/joined/overview", response_model=list[StudentJoinedGroupOverviewResponse])
def list_joined_groups_overview(
    current: CurrentUserResult = Depends(require_permission(Permission.JOIN_GROUPS)),
    db: Session = Depends(get_db),
):
    return build_student_joined_groups_overview(db, current.id)


@router.get("/joined/assigned-catalogs", response_model=list[StudentAssignedCatalogSummaryResponse])
def list_joined_assigned_catalogs(
    current: CurrentUserResult = Depends(require_permission(Permission.JOIN_GROUPS)),
    db: Session = Depends(get_db),
):
    return build_student_assigned_catalogs(db, current.id)


@router.get("/joined", response_model=list[GroupResponse])
def list_joined_groups(
    current: CurrentUserResult = Depends(require_permission(Permission.JOIN_GROUPS)),
    use_case: ListStudentGroupsUseCase = Depends(get_list_student_groups_uc),
):
    return [to_group(g) for g in use_case.execute(current.id)]


@router.post("/{group_id}/invitations", response_model=InvitationCodeResponse)
def generate_invitation(
    group_id: int,
    body: GenerateInvitationRequest,
    current: CurrentUserResult = Depends(require_permission(Permission.MANAGE_GROUPS)),
    use_case: GenerateInvitationCodeUseCase = Depends(get_generate_invitation_uc),
):
    try:
        return to_invitation(
            use_case.execute(
                teacher_id=current.id,
                group_id=group_id,
                max_uses=body.max_uses,
                expires_in_days=body.expires_in_days,
            )
        )
    except GroupNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{group_id}/dashboard", response_model=GroupDashboardResponse)
def get_group_dashboard(
    group_id: int,
    catalog_id: int | None = None,
    current: CurrentUserResult = Depends(require_permission(Permission.MANAGE_GROUPS)),
    db: Session = Depends(get_db),
):
    data = build_group_dashboard(db, current.id, group_id, catalog_id=catalog_id)
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return data


@router.get(
    "/{group_id}/workspace",
    response_model=StudentGroupWorkspaceResponse,
)
def get_my_group_workspace(
    group_id: int,
    current: CurrentUserResult = Depends(require_permission(Permission.JOIN_GROUPS)),
    db: Session = Depends(get_db),
):
    data = build_student_group_workspace(db, current.id, group_id)
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return data


@router.get(
    "/{group_id}/my-catalogs",
    response_model=StudentGroupTaskProgressResponse,
)
def get_my_group_catalogs(
    group_id: int,
    current: CurrentUserResult = Depends(require_permission(Permission.JOIN_GROUPS)),
    db: Session = Depends(get_db),
):
    data = build_student_own_group_catalogs(db, current.id, group_id)
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return data


@router.get(
    "/{group_id}/students/{student_id}/tasks-progress",
    response_model=StudentGroupTaskProgressResponse,
)
def get_student_tasks_progress(
    group_id: int,
    student_id: int,
    current: CurrentUserResult = Depends(require_permission(Permission.MANAGE_GROUPS)),
    db: Session = Depends(get_db),
):
    data = build_student_group_task_progress(db, current.id, group_id, student_id)
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return data


@router.post("/{group_id}/catalogs", status_code=status.HTTP_200_OK)
def assign_group_catalog(
    group_id: int,
    body: AssignCatalogToGroupRequest,
    current: CurrentUserResult = Depends(require_permission(Permission.MANAGE_GROUPS)),
    db: Session = Depends(get_db),
):
    try:
        result = assign_catalog_to_group(
            db,
            current.id,
            group_id,
            body.catalog_id,
            deadline_at=body.deadline_at,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return result


@router.post("/join", response_model=GroupResponse)
def join_group(
    body: JoinGroupRequest,
    current: CurrentUserResult = Depends(require_permission(Permission.JOIN_GROUPS)),
    use_case: JoinGroupByInvitationUseCase = Depends(get_join_group_uc),
):
    try:
        return to_group(use_case.execute(student_id=current.id, code=body.code))
    except InvalidInvitationCodeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except AlreadyGroupMemberError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except GroupNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
