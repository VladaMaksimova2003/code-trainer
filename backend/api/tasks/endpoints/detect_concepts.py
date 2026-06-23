"""POST /tasks/detect-expected-concepts — scan reference code per language."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from application.auth.dto import CurrentUserResult
from application.curriculum.validation.expected_concept_checker import (
    _label_for,
    detect_expected_concepts_multilang,
)
from api.dependencies.authorization import require_permission
from api.tasks.schemas.requests import DetectExpectedConceptsRequest
from api.tasks.schemas.responses import (
    DetectExpectedConceptsResponse,
    DetectedExpectedConceptItem,
)
from domain.policies.permissions.permissions import Permission

router = APIRouter()


@router.post("/detect-expected-concepts", response_model=DetectExpectedConceptsResponse)
async def detect_expected_concepts(
    request: DetectExpectedConceptsRequest,
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.CREATE_ASSIGNMENTS)
    ),
):
    """Analyze each language sample and return detected display TC cards."""
    samples = [(item.language, item.code) for item in request.samples]
    by_lang_ids = detect_expected_concepts_multilang(samples)

    by_language: dict[str, list[DetectedExpectedConceptItem]] = {}
    union: list[str] = []
    seen_union: set[str] = set()

    for lang, concept_ids in by_lang_ids.items():
        items: list[DetectedExpectedConceptItem] = []
        for concept_id in concept_ids:
            label = _label_for(concept_id, concept_id)
            items.append(DetectedExpectedConceptItem(id=concept_id, label=label))
            if concept_id not in seen_union:
                seen_union.add(concept_id)
                union.append(concept_id)
        by_language[lang] = items

    return DetectExpectedConceptsResponse(by_language=by_language, suggested_ids=union)
