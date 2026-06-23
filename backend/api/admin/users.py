from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.admin.guards import ensure_can_assign_role, ensure_mutable_user
from api.dependencies.admin import (
    get_assign_role_uc,
    get_delete_user_uc,
    get_list_users_uc,
    get_remove_role_uc,
    get_set_user_blocked_uc,
    get_user_detail_uc,
)
from api.dependencies.authorization import require_permission
from api.mappers.admin import to_user_detail, to_user_list_item
from api.admin.schemas import (
    AdminUserDetailResponse,
    AdminUserListItemResponse,
    AssignRoleRequest,
    SetUserBlockedRequest,
)
from application.admin.roles import (
    AssignRoleToUserUseCase,
    RemoveRoleFromUserUseCase,
)
from application.admin.users import (
    DeleteUserUseCase,
    GetUserDetailUseCase,
    ListUsersUseCase,
    SetUserBlockedUseCase,
)
from application.auth.dto import CurrentUserResult
from shared.exceptions import UserNotFoundError
from domain.policies.permissions.permissions import Permission
from shared.enums import UserType

router = APIRouter(prefix="/users", tags=["admin-users"])


def _get_user_or_404(use_case: GetUserDetailUseCase, user_id: int):
    try:
        return use_case.execute(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("", response_model=list[AdminUserListItemResponse])
def list_users(
    include_deleted: bool = Query(default=False),
    _: CurrentUserResult = Depends(require_permission(Permission.MANAGE_USERS)),
    use_case: ListUsersUseCase = Depends(get_list_users_uc),
):
    return [to_user_list_item(u) for u in use_case.execute(include_deleted=include_deleted)]


@router.get("/{user_id}", response_model=AdminUserDetailResponse)
def get_user(
    user_id: int,
    _: CurrentUserResult = Depends(require_permission(Permission.MANAGE_USERS)),
    use_case: GetUserDetailUseCase = Depends(get_user_detail_uc),
):
    try:
        return to_user_detail(use_case.execute(user_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{user_id}/blocked", status_code=status.HTTP_204_NO_CONTENT)
def set_user_blocked(
    user_id: int,
    body: SetUserBlockedRequest,
    _: CurrentUserResult = Depends(require_permission(Permission.MANAGE_USERS)),
    detail_uc: GetUserDetailUseCase = Depends(get_user_detail_uc),
    use_case: SetUserBlockedUseCase = Depends(get_set_user_blocked_uc),
):
    user = _get_user_or_404(detail_uc, user_id)
    ensure_mutable_user(user)
    try:
        use_case.execute(user_id, body.blocked)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    _: CurrentUserResult = Depends(require_permission(Permission.MANAGE_USERS)),
    detail_uc: GetUserDetailUseCase = Depends(get_user_detail_uc),
    use_case: DeleteUserUseCase = Depends(get_delete_user_uc),
):
    user = _get_user_or_404(detail_uc, user_id)
    ensure_mutable_user(user)
    try:
        use_case.execute(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{user_id}/roles", response_model=list[str])
def assign_role(
    user_id: int,
    body: AssignRoleRequest,
    current: CurrentUserResult = Depends(require_permission(Permission.MANAGE_ROLES)),
    detail_uc: GetUserDetailUseCase = Depends(get_user_detail_uc),
    use_case: AssignRoleToUserUseCase = Depends(get_assign_role_uc),
):
    user = _get_user_or_404(detail_uc, user_id)
    ensure_mutable_user(user)
    try:
        role = UserType(body.role.lower())
        ensure_can_assign_role(current.email, role)
        return use_case.execute(user_id, role)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{user_id}/roles/{role}", response_model=list[str])
def remove_role(
    user_id: int,
    role: str,
    _: CurrentUserResult = Depends(require_permission(Permission.MANAGE_ROLES)),
    detail_uc: GetUserDetailUseCase = Depends(get_user_detail_uc),
    use_case: RemoveRoleFromUserUseCase = Depends(get_remove_role_uc),
):
    user = _get_user_or_404(detail_uc, user_id)
    ensure_mutable_user(user)
    try:
        return use_case.execute(user_id, UserType(role.lower()))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
