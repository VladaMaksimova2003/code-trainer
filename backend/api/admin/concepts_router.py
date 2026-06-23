"""Admin CRUD for programming concepts (concepts.yml)."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field

from api.dependencies.authorization import require_permission
from application.auth.dto import CurrentUserResult
from domain.policies.permissions.permissions import Permission
from infrastructure.analysis.concept_registry import (
    get_concept,
    list_concept_ids,
    load_concepts,
    to_response_dict,
    update_concept,
)

router = APIRouter(prefix="/concepts")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ConceptResponse(BaseModel):
    id: str
    name: str
    description: str
    hint: str
    level: int
    equivalents: dict[str, list[str]] = Field(default_factory=dict)
    ast_nodes: dict[str, list[str]] = Field(default_factory=dict)
    patterns: dict[str, str] = Field(default_factory=dict)


class ConceptPatchRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    hint: str | None = None
    # Частичное обновление: только переданные языки будут обновлены.
    # Например: {"python": "new code", "java": "new code"}
    patterns: dict[str, str] | None = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=list[ConceptResponse])
async def list_concepts(
    _: CurrentUserResult = Depends(require_permission(Permission.MANAGE_USERS)),
) -> list[ConceptResponse]:
    """Список всех концептов с их описаниями и примерами."""
    concepts = load_concepts()
    return [
        ConceptResponse(**to_response_dict(cid, data))
        for cid, data in concepts.items()
    ]


@router.get("/{concept_id}", response_model=ConceptResponse)
async def get_concept_by_id(
    concept_id: str,
    _: CurrentUserResult = Depends(require_permission(Permission.MANAGE_USERS)),
) -> ConceptResponse:
    """Один концепт по id."""
    data = get_concept(concept_id)
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Concept '{concept_id}' not found",
        )
    return ConceptResponse(**to_response_dict(concept_id, data))


@router.patch("/{concept_id}", response_model=ConceptResponse)
async def patch_concept(
    concept_id: str,
    body: ConceptPatchRequest,
    _: CurrentUserResult = Depends(require_permission(Permission.MANAGE_USERS)),
) -> ConceptResponse:
    """
    Обновить поля концепта.

    Можно обновить: name, description, hint, и/или примеры кода (patterns) для отдельных языков.
    Обновление patterns частичное — только переданные языки изменятся, остальные сохранятся.

    Изменения сразу записываются в concepts.yml.
    """
    patch: dict[str, Any] = {}
    if body.name is not None:
        patch["name"] = body.name
    if body.description is not None:
        patch["description"] = body.description
    if body.hint is not None:
        patch["hint"] = body.hint
    if body.patterns is not None:
        patch["patterns"] = body.patterns

    if not patch:
        # Ничего не передано — просто вернуть текущий концепт
        data = get_concept(concept_id)
        if data is None:
            raise HTTPException(status_code=404, detail=f"Concept '{concept_id}' not found")
        return ConceptResponse(**to_response_dict(concept_id, data))

    try:
        updated = update_concept(concept_id, patch)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except OSError as exc:
        raise HTTPException(status_code=503, detail=f"Failed to save concepts.yml: {exc}") from exc

    return ConceptResponse(**to_response_dict(concept_id, updated))
