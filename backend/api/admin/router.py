from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.dependencies.authorization import require_permission, require_super_user
from api.dependencies.auth import (
    get_approve_teacher_role_request_use_case,
    get_create_admin_use_case,
    get_create_teacher_use_case,
    get_list_teacher_role_requests_use_case,
    get_reject_teacher_role_request_use_case,
    to_admin_create_command,
)
from api.mappers.teacher_role_request import to_teacher_role_request_response
from api.admin import assignments, statistics, users
from api.admin.concepts_router import router as concepts_router
from api.admin.tc_concepts_router import router as tc_concepts_router
from api.admin.curriculum_router import router as curriculum_router
from api.admin.hints_router import router as hints_router
from api.auth.schemas import AdminCreateUserRequest, UserCreatedResponse
from api.auth.teacher_role_schemas import TeacherRoleRequestResponse
from application.auth.use_cases.teacher_role.approve_teacher_role_request import (
    ApproveTeacherRoleRequestUseCase,
)
from application.auth.use_cases.teacher_role.create_admin import CreateAdminUseCase
from application.auth.use_cases.teacher_role.create_teacher import CreateTeacherUseCase
from application.auth.dto import CurrentUserResult
from application.auth.use_cases.teacher_role.list_teacher_role_requests import (
    ListTeacherRoleRequestsUseCase,
)
from application.auth.use_cases.teacher_role.reject_teacher_role_request import (
    RejectTeacherRoleRequestUseCase,
)
from shared.exceptions import AuthError
from domain.policies.permissions.permissions import Permission
from shared.enums import TeacherRoleRequestStatus

router = APIRouter()

router.include_router(users.router)
router.include_router(assignments.router)
router.include_router(statistics.router)
router.include_router(concepts_router)
router.include_router(tc_concepts_router)
router.include_router(hints_router)
router.include_router(curriculum_router)


@router.post("/create-teacher", response_model=UserCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_teacher(
    request: AdminCreateUserRequest,
    _: CurrentUserResult = Depends(require_permission(Permission.MANAGE_ROLES)),
    use_case: CreateTeacherUseCase = Depends(get_create_teacher_use_case),
) -> UserCreatedResponse:
    try:
        user = use_case.execute(
            to_admin_create_command(request.name, request.email, request.password)
        )
        return UserCreatedResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.primary_role.value,
        )
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/create-admin", response_model=UserCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_admin(
    request: AdminCreateUserRequest,
    _: CurrentUserResult = Depends(require_super_user()),
    use_case: CreateAdminUseCase = Depends(get_create_admin_use_case),
) -> UserCreatedResponse:
    try:
        user = use_case.execute(
            to_admin_create_command(request.name, request.email, request.password)
        )
        return UserCreatedResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.primary_role.value,
        )
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/teacher-role-requests", response_model=list[TeacherRoleRequestResponse])
async def list_teacher_role_requests(
    status_filter: str | None = Query(default=None, alias="status"),
    _: CurrentUserResult = Depends(require_permission(Permission.REVIEW_TEACHER_REQUESTS)),
    use_case: ListTeacherRoleRequestsUseCase = Depends(
        get_list_teacher_role_requests_use_case
    ),
) -> list[TeacherRoleRequestResponse]:
    status_enum = None
    if status_filter:
        try:
            status_enum = TeacherRoleRequestStatus(status_filter.lower())
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status filter.",
            ) from exc
    return [to_teacher_role_request_response(r) for r in use_case.execute(status_enum)]


@router.post(
    "/teacher-role-requests/{request_id}/approve",
    response_model=TeacherRoleRequestResponse,
)
async def approve_teacher_role_request(
    request_id: int,
    admin: CurrentUserResult = Depends(require_permission(Permission.REVIEW_TEACHER_REQUESTS)),
    use_case: ApproveTeacherRoleRequestUseCase = Depends(
        get_approve_teacher_role_request_use_case
    ),
) -> TeacherRoleRequestResponse:
    try:
        return to_teacher_role_request_response(
            use_case.execute(request_id=request_id, admin_user_id=admin.id)
        )
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post(
    "/teacher-role-requests/{request_id}/reject",
    response_model=TeacherRoleRequestResponse,
)
async def reject_teacher_role_request(
    request_id: int,
    admin: CurrentUserResult = Depends(require_permission(Permission.REVIEW_TEACHER_REQUESTS)),
    use_case: RejectTeacherRoleRequestUseCase = Depends(
        get_reject_teacher_role_request_use_case
    ),
) -> TeacherRoleRequestResponse:
    try:
        return to_teacher_role_request_response(
            use_case.execute(request_id=request_id, admin_user_id=admin.id)
        )
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
