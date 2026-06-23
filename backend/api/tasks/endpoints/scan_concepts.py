"""POST /tasks/scan-expected-concepts — TC42 detection report for student/teacher code."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from application.auth.dto import CurrentUserResult
from application.curriculum.validation.expected_concept_checker import analyze_expected_concepts
from api.dependencies.auth import get_optional_current_user
from api.tasks.schemas.requests import ScanExpectedConceptsRequest
from api.tasks.schemas.responses import ScanExpectedConceptsResponse, ScannedExpectedConceptItem

router = APIRouter()


@router.post("/scan-expected-concepts", response_model=ScanExpectedConceptsResponse)
async def scan_expected_concepts(
    request: ScanExpectedConceptsRequest,
    current_user: CurrentUserResult | None = Depends(get_optional_current_user),
):
    """Scan code for TC42 concepts and explain why each expected item was not detected."""
    del current_user
    items = analyze_expected_concepts(
        request.code,
        language=request.language,
        concept_ids=request.concept_ids,
    )
    detected_ids = [item.id for item in items if item.detected]
    return ScanExpectedConceptsResponse(
        items=[
            ScannedExpectedConceptItem(
                id=item.id,
                label=item.label,
                detected=item.detected,
                reason=item.reason,
            )
            for item in items
        ],
        detected_ids=detected_ids,
    )
