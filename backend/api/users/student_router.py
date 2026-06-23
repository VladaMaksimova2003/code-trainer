from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.users import recommendations_router as recommendations_router
from api.dependencies.auth import get_request_teacher_role_use_case
from api.dependencies.authorization import require_permission, require_roles
from api.mappers.teacher_role_request import to_teacher_role_request_response
from api.auth.teacher_role_schemas import (
    TeacherRoleRequestCreate,
    TeacherRoleRequestResponse,
)
from application.users import student_service
from application.auth.dto import CurrentUserResult
from application.auth.use_cases.teacher_role.request_teacher_role import RequestTeacherRoleUseCase
from shared.exceptions import AuthError
from domain.policies.permissions.permissions import Permission
from domain.policies.rbac.role import Role
from infrastructure.db.session import get_db

router = APIRouter()
router.include_router(
    recommendations_router.router,
    prefix="/recommendations",
    tags=["recommendations"],
)


@router.get("/profile")
def get_my_student_profile(
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(require_permission(Permission.VIEW_OWN_PROGRESS)),
):
    try:
        return student_service.build_student_profile(db, user)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        ) from None


@router.post(
    "/teacher-role-request",
    response_model=TeacherRoleRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def request_teacher_role(
    body: TeacherRoleRequestCreate,
    user: CurrentUserResult = Depends(require_roles(Role.STUDENT)),
    use_case: RequestTeacherRoleUseCase = Depends(get_request_teacher_role_use_case),
):
    try:
        result = use_case.execute(user_id=user.id, message=body.message)
        return to_teacher_role_request_response(result)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
