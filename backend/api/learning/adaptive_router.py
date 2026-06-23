"""Adaptive learning API — profile + post-check adaptation."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.learning.adaptive_schemas import AdaptiveCheckRequest
from api.dependencies.authorization import require_permission
from application.auth.dto import CurrentUserResult
from application.learning.adaptive.adaptive_learning_service import AdaptiveLearningService
from domain.policies.permissions.permissions import Permission
from infrastructure.db.session import get_db

router = APIRouter(prefix="/adaptive")


@router.get("/profile")
async def get_adaptive_profile(
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(require_permission(Permission.VIEW_OWN_PROGRESS)),
):
    return AdaptiveLearningService().get_profile(db, user.id)


@router.post("/check")
async def adaptive_structure_check(
    body: AdaptiveCheckRequest,
    db: Session = Depends(get_db),
    user: CurrentUserResult = Depends(require_permission(Permission.VIEW_OWN_PROGRESS)),
):
    """Core PASS/FAIL + profile update + adaptive decision (core pipeline unchanged)."""
    return AdaptiveLearningService().process_check(
        db,
        user_id=user.id,
        code=body.code,
        language_id=body.language,
        required=body.required,
    )
