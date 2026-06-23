"""View another user's profile (teacher public page or student scoped to a teacher)."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.dependencies.auth import get_current_user
from application.auth.dto import CurrentUserResult
from application.users.services import public_profile_service
from infrastructure.db.session import get_db

router = APIRouter()


@router.get("/{user_id}")
def get_user_profile(
    user_id: int,
    teacher_id: int | None = Query(default=None, description="Scope student stats to this teacher"),
    db: Session = Depends(get_db),
    viewer: CurrentUserResult = Depends(get_current_user),
):
    try:
        if teacher_id is not None:
            return public_profile_service.build_student_teacher_profile_view(
                db, user_id, teacher_id, viewer
            )
        from application.users.services.teacher_service import is_teacher_user
        from infrastructure.db.models.user import User

        user = db.get(User, user_id)
        if user is None:
            raise ValueError("User not found")
        if is_teacher_user(db, user):
            return public_profile_service.build_teacher_profile_view(db, user_id, viewer)
        raise ValueError("teacher_id is required for student profiles")
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
