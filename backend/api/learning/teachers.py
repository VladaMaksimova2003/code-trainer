from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.dependencies.authorization import require_permission
from api.dependencies.learning import (
    get_search_teachers_uc,
    get_teacher_public_profile_uc,
    get_teacher_students_progress_uc,
)
from api.mappers.learning import to_assignment_set, to_student_progress, to_teacher_search
from api.learning.schemas import (
    StudentProgressItemResponse,
    TeacherProfileDetailResponse,
    TeacherSearchResultResponse,
)
from application.auth.dto import CurrentUserResult
from application.learning.services.student_progress import ListTeacherStudentsProgressUseCase
from application.learning.services.teacher_search import (
    GetTeacherPublicProfileUseCase,
    SearchTeachersUseCase,
)
from domain.policies.permissions.permissions import Permission

router = APIRouter(prefix="/teachers", tags=["teacher-discovery"])


@router.get("/search", response_model=list[TeacherSearchResultResponse])
def search_teachers(
    name: str | None = Query(default=None),
    language: str | None = Query(default=None),
    specialization: str | None = Query(default=None),
    limit: int = Query(default=50, le=100),
    _: CurrentUserResult = Depends(require_permission(Permission.BROWSE_TEACHERS)),
    use_case: SearchTeachersUseCase = Depends(get_search_teachers_uc),
):
    return [
        to_teacher_search(r)
        for r in use_case.execute(name=name, language=language, specialization=specialization, limit=limit)
    ]


@router.get("/{teacher_id}/profile", response_model=TeacherProfileDetailResponse)
def teacher_public_profile(
    teacher_id: int,
    _: CurrentUserResult = Depends(require_permission(Permission.BROWSE_TEACHERS)),
    use_case: GetTeacherPublicProfileUseCase = Depends(get_teacher_public_profile_uc),
):
    profile, public_sets = use_case.execute(teacher_id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
    base = to_teacher_search(profile)
    return TeacherProfileDetailResponse(
        **base.model_dump(),
        public_assignment_sets=[to_assignment_set(s) for s in public_sets],
    )


@router.get("/{teacher_id}/students/progress", response_model=list[StudentProgressItemResponse])
def teacher_students_progress(
    teacher_id: int,
    current: CurrentUserResult = Depends(require_permission(Permission.VIEW_STUDENT_RESULTS)),
    use_case: ListTeacherStudentsProgressUseCase = Depends(get_teacher_students_progress_uc),
):
    if current.id != teacher_id:
        from domain.policies.rbac.rbac import has_role, normalize_role
        from shared.enums import UserType

        roles = frozenset(normalize_role(r) for r in current.roles)
        if not has_role(roles, UserType.ADMIN):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return [to_student_progress(r) for r in use_case.execute(teacher_id)]
