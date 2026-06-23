"""Settings — learning preferences."""
from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies.auth import get_current_user
from api.dependencies.settings import get_learning_preferences_uc, get_update_learning_uc
from api.users.schemas.requests import UpdateLearningPreferencesRequest
from api.users.schemas.responses import LearningPreferencesResponse
from application.auth.dto import CurrentUserResult
from application.users.use_cases.learning_prefs import (
    GetLearningPreferencesUseCase,
    UpdateLearningPreferencesUseCase,
)
from application.users.dto import UpdateLearningPreferencesCommand
from shared.exceptions import ProfileError

router = APIRouter()


@router.get("/learning", response_model=LearningPreferencesResponse)
def get_learning_preferences(
    current: CurrentUserResult = Depends(get_current_user),
    use_case: GetLearningPreferencesUseCase = Depends(get_learning_preferences_uc),
):
    prefs = use_case.execute(current.id)
    return LearningPreferencesResponse(
        preferred_languages=list(prefs.preferred_languages),
        preferred_difficulty=prefs.preferred_difficulty,
        preferred_topics=list(prefs.preferred_topics),
        study_place=prefs.study_place,
        study_group=prefs.study_group,
    )


@router.patch("/learning", response_model=LearningPreferencesResponse)
def update_learning_preferences(
    body: UpdateLearningPreferencesRequest,
    current: CurrentUserResult = Depends(get_current_user),
    use_case: UpdateLearningPreferencesUseCase = Depends(get_update_learning_uc),
):
    try:
        prefs = use_case.execute(
            current.id,
            UpdateLearningPreferencesCommand(
                preferred_languages=body.preferred_languages,
                preferred_difficulty=body.preferred_difficulty,
                preferred_topics=body.preferred_topics,
                study_place=body.study_place,
                study_group=body.study_group,
            ),
        )
    except ProfileError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return LearningPreferencesResponse(
        preferred_languages=list(prefs.preferred_languages),
        preferred_difficulty=prefs.preferred_difficulty,
        preferred_topics=list(prefs.preferred_topics),
        study_place=prefs.study_place,
        study_group=prefs.study_group,
    )
