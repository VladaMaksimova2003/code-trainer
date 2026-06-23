"""GET /tasks/patterns — display TC catalog for assignment authoring."""
from fastapi import APIRouter, Depends

from application.auth.dto import CurrentUserResult
from api.tasks.schemas.responses import PatternCatalogItem, PatternCatalogResponse
from api.dependencies.authorization import require_permission
from domain.policies.permissions.permissions import Permission
from application.tasks.services.authoring_expected_concepts import (
    build_tc_catalog_card,
    list_tc_catalog_entries,
)

router = APIRouter()


@router.get("/patterns", response_model=PatternCatalogResponse)
async def list_assignment_patterns(
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.CREATE_ASSIGNMENTS)
    ),
):
    """All display TC cards from tc_display_registry.json."""
    patterns: list[PatternCatalogItem] = []
    for concept_id, entry in list_tc_catalog_entries():
        card = build_tc_catalog_card(concept_id) or {}
        patterns.append(
            PatternCatalogItem(
                id=concept_id,
                type=concept_id,
                label=str(entry.get("name_ru") or card.get("name_ru") or concept_id),
                description=str(entry.get("description_ru") or card.get("description_ru") or "") or None,
                card={
                    "id": concept_id,
                    "name_ru": card.get("name_ru") or entry.get("name_ru"),
                    "description_ru": card.get("description_ru") or entry.get("description_ru"),
                    "descriptions_by_language": card.get("descriptions_by_language") or {},
                    "examples_by_language": card.get("examples_by_language") or entry.get("examples_by_language") or {},
                    "pascal_template": card.get("pascal_template") or "",
                },
            )
        )
    return PatternCatalogResponse(patterns=patterns, source="tc_display_registry.json", total=len(patterns))
