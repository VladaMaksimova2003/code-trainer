"""Bridge: core exam + adaptive layer (single call site for APIs)."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from application.learning.adaptive.adaptive_learning_service import AdaptiveLearningService


def check_with_adaptive_learning(
    db: Session,
    *,
    user_id: int,
    code: str,
    language_id: str,
    required: list,
    commit: bool = True,
) -> dict[str, Any]:
    return AdaptiveLearningService().process_check(
        db,
        user_id=user_id,
        code=code,
        language_id=language_id,
        required=required,
        commit=commit,
    )
