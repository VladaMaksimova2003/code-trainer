"""Settings — teacher profile."""
from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies.auth import get_current_user
from api.dependencies.settings import (
    get_teacher_overview_uc,
    get_teacher_settings_uc,
    get_update_teacher_uc,
    user_roles_set,
)
from api.users.schemas.requests import UpdateTeacherSettingsRequest
from api.users.schemas.responses import (
    AvatarResponse,
    TeacherOverviewItemResponse,
    TeacherOverviewResponse,
    TeacherSettingsResponse,
)
from application.users.services.avatar_service import AvatarService
from application.auth.dto import CurrentUserResult
from application.users.use_cases.teacher_prefs import (
    GetTeacherOverviewUseCase,
    GetTeacherSettingsUseCase,
    UpdateTeacherSettingsUseCase,
)
from application.users.dto import UpdateTeacherProfileCommand
from shared.exceptions import TeacherProfileAccessError

router = APIRouter()


@router.get("/teacher", response_model=TeacherSettingsResponse)
def get_teacher_settings(
    roles=Depends(user_roles_set),
    current: CurrentUserResult = Depends(get_current_user),
    use_case: GetTeacherSettingsUseCase = Depends(get_teacher_settings_uc),
):
    try:
        data = use_case.execute(current.id, roles)
    except TeacherProfileAccessError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    avatar = AvatarService.get_avatar(data.user_id, data.full_name)
    return TeacherSettingsResponse(
        full_name=data.full_name,
        bio=data.bio,
        specialization=data.specialization,
        supported_languages=list(data.supported_languages),
        is_public=data.is_public,
        avatar=AvatarResponse(initial=avatar.initial, color=avatar.color),
    )


@router.patch("/teacher", response_model=TeacherSettingsResponse)
def update_teacher_settings(
    body: UpdateTeacherSettingsRequest,
    roles=Depends(user_roles_set),
    current: CurrentUserResult = Depends(get_current_user),
    use_case: UpdateTeacherSettingsUseCase = Depends(get_update_teacher_uc),
):
    try:
        data = use_case.execute(
            current.id, roles,
            UpdateTeacherProfileCommand(
                full_name=body.full_name,
                bio=body.bio,
                specialization=body.specialization,
                supported_languages=body.supported_languages,
                is_public=body.is_public,
            ),
        )
    except TeacherProfileAccessError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    avatar = AvatarService.get_avatar(data.user_id, data.full_name)
    return TeacherSettingsResponse(
        full_name=data.full_name,
        bio=data.bio,
        specialization=data.specialization,
        supported_languages=list(data.supported_languages),
        is_public=data.is_public,
        avatar=AvatarResponse(initial=avatar.initial, color=avatar.color),
    )


@router.get("/teacher/overview", response_model=TeacherOverviewResponse)
def teacher_overview(
    roles=Depends(user_roles_set),
    current: CurrentUserResult = Depends(get_current_user),
    use_case: GetTeacherOverviewUseCase = Depends(get_teacher_overview_uc),
):
    try:
        overview = use_case.execute(current.id, roles)
    except TeacherProfileAccessError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return TeacherOverviewResponse(
        groups=[TeacherOverviewItemResponse(id=g.id, name=g.name, extra=g.extra) for g in overview.groups],
        assignment_sets=[TeacherOverviewItemResponse(id=s.id, name=s.name, extra=s.extra) for s in overview.assignment_sets],
    )
