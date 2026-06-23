from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.dependencies.authorization import require_permission
from application.tasks.services.recommendation_service import (
    get_catalog_navigation,
    get_next_recommendation,
)
from application.auth.dto import CurrentUserResult
from domain.policies.permissions.permissions import Permission
from infrastructure.db.session import get_db

router = APIRouter()


class NextRecommendationResponse(BaseModel):
    task_id: int
    title: str | None = None
    topic_id: int
    type_id: str
    skills_required: list[str]
    mode: str = "adaptive"


class CatalogNavigationResponse(BaseModel):
    catalog_id: int
    task_ids: list[int]
    current_task_id: int | None = None
    prev_task_id: int | None = None
    next_task_id: int | None = None
    mode: str = "manual"


@router.get("/next", response_model=NextRecommendationResponse | None)
def next_recommended_task(
    current_task_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(require_permission(Permission.SOLVE_ASSIGNMENTS)),
):
    result = get_next_recommendation(
        db,
        user.id,
        user.roles,
        current_task_id=current_task_id,
    )
    if result is None:
        return None
    return NextRecommendationResponse(**result)


@router.get("/catalogs/{catalog_id}/navigation", response_model=CatalogNavigationResponse)
def catalog_task_navigation(
    catalog_id: int,
    current_task_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(require_permission(Permission.SOLVE_ASSIGNMENTS)),
):
    try:
        payload = get_catalog_navigation(
            db,
            user.id,
            user.roles,
            catalog_id,
            current_task_id=current_task_id,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    return CatalogNavigationResponse(**payload)
