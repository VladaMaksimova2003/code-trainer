"""Admin CRUD for pedagogical display TC cards (tc_display_registry.json)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field

from api.dependencies.authorization import require_permission
from application.auth.dto import CurrentUserResult
from application.curriculum.display.tc_display_registry_service import (
    get_merged_tc_concept,
    list_tc_concept_summaries,
    to_admin_response,
    update_tc_concept,
)
from domain.policies.permissions.permissions import Permission

router = APIRouter(prefix="/tc-concepts")


class TcConceptExample(BaseModel):
    title: str = ""
    code: str = ""


class TcConceptSummaryResponse(BaseModel):
    id: str
    name_ru: str
    description_ru: str
    source: str = "tc_display_registry.json"
    has_overrides: bool = False


class TcConceptResponse(BaseModel):
    id: str
    name_ru: str
    description_ru: str
    examples_by_language: dict[str, list[TcConceptExample]] = Field(default_factory=dict)
    source: str = "tc_display_registry.json"
    has_overrides: bool = False


class TcConceptPatchRequest(BaseModel):
    name_ru: str | None = None
    description_ru: str | None = None
    examples_by_language: dict[str, list[TcConceptExample]] | None = None


def _serialize_entry(concept_id: str, entry: dict[str, Any]) -> TcConceptResponse:
    payload = to_admin_response(concept_id, entry)
    examples = {
        lang: [TcConceptExample(**item) for item in items if isinstance(item, dict)]
        for lang, items in (payload.get("examples_by_language") or {}).items()
        if isinstance(items, list)
    }
    return TcConceptResponse(
        id=str(payload["id"]),
        name_ru=str(payload["name_ru"]),
        description_ru=str(payload["description_ru"]),
        examples_by_language=examples,
        source=str(payload.get("source") or "tc_display_registry.json"),
        has_overrides=bool(payload.get("has_overrides")),
    )


@router.get("", response_model=list[TcConceptSummaryResponse])
async def list_tc_concepts(
    _: CurrentUserResult = Depends(require_permission(Permission.MANAGE_USERS)),
) -> list[TcConceptSummaryResponse]:
    """Concept list for admin sidebar (metadata only, no code examples)."""
    return [TcConceptSummaryResponse(**item) for item in list_tc_concept_summaries()]


@router.get("/{concept_id}", response_model=TcConceptResponse)
async def get_tc_concept(
    concept_id: str,
    _: CurrentUserResult = Depends(require_permission(Permission.MANAGE_USERS)),
) -> TcConceptResponse:
    entry = get_merged_tc_concept(concept_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Concept '{concept_id}' not found")
    return _serialize_entry(concept_id, entry)


@router.patch("/{concept_id}", response_model=TcConceptResponse)
async def patch_tc_concept(
    concept_id: str,
    body: TcConceptPatchRequest,
    _: CurrentUserResult = Depends(require_permission(Permission.MANAGE_USERS)),
) -> TcConceptResponse:
    patch: dict[str, Any] = {}
    if body.name_ru is not None:
        patch["name_ru"] = body.name_ru
    if body.description_ru is not None:
        patch["description_ru"] = body.description_ru
    if body.examples_by_language is not None:
        patch["examples_by_language"] = {
            lang: [item.model_dump() for item in items]
            for lang, items in body.examples_by_language.items()
        }

    if not patch:
        entry = get_merged_tc_concept(concept_id)
        if entry is None:
            raise HTTPException(status_code=404, detail=f"Concept '{concept_id}' not found")
        return _serialize_entry(concept_id, entry)

    try:
        updated = update_tc_concept(concept_id, patch)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except OSError as exc:
        raise HTTPException(status_code=503, detail=f"Failed to save overrides: {exc}") from exc

    return _serialize_entry(concept_id, updated)
