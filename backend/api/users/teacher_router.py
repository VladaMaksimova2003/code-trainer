from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencies.auth import get_current_user
from api.dependencies.authorization import require_permission, require_roles
from application.users import teacher_service
from application.auth.dto import CurrentUserResult
from domain.policies.rbac.role import Role
from infrastructure.db.session import get_db

router = APIRouter()


@router.get("/profile")
def get_my_teacher_profile(
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(require_roles(Role.TEACHER, Role.ADMIN)),
):
    return teacher_service.build_profile_bundle(db, user.id, viewer=user)


@router.get("/{teacher_id}/profile")
def get_teacher_profile(
    teacher_id: int,
    db: Session = Depends(get_db),
    viewer: CurrentUserResult = Depends(get_current_user),
):
    try:
        return teacher_service.build_profile_bundle(db, teacher_id, viewer=viewer)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found",
        ) from None


@router.get("/{teacher_id}/tasks")
def get_teacher_tasks(
    teacher_id: int,
    db: Session = Depends(get_db),
    _: CurrentUserResult = Depends(get_current_user),
):
    try:
        return {"tasks": teacher_service.list_teacher_tasks(db, teacher_id)}
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found",
        ) from None


@router.get("/{teacher_id}/activity")
def get_teacher_activity(
    teacher_id: int,
    db: Session = Depends(get_db),
    _: CurrentUserResult = Depends(get_current_user),
):
    try:
        return teacher_service.build_activity_payload(db, teacher_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found",
        ) from None
