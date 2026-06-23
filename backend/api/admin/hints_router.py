"""Admin CRUD for structure hints (does not affect core grading)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.admin.hints_schemas import HintAdminResponse, HintUpsertRequest
from api.dependencies.authorization import require_permission
from api.dependencies.hints import get_structure_hint_service
from infrastructure.db.session import get_db
from application.auth.dto import CurrentUserResult
from application.hints.structure_hint_service import StructureHintService
from domain.policies.permissions.permissions import Permission

router = APIRouter(prefix="/hints")


@router.get("", response_model=list[HintAdminResponse])
async def list_admin_hints(
    _: CurrentUserResult = Depends(require_permission(Permission.MANAGE_USERS)),
    service: StructureHintService = Depends(get_structure_hint_service),
) -> list[HintAdminResponse]:
    return [
        HintAdminResponse(
            id=item.get("id"),
            type=item["type"],
            subtype=item["subtype"],
            title=item["title"],
            difficulty=item["difficulty"],
            explanation=item["explanation"],
            examples=item.get("examples") or {},
            source=item.get("source") or "yaml",
        )
        for item in service.list_hints()
    ]


@router.post("", response_model=HintAdminResponse, status_code=status.HTTP_200_OK)
async def upsert_admin_hint(
    body: HintUpsertRequest,
    db: Session = Depends(get_db),
    _: CurrentUserResult = Depends(require_permission(Permission.MANAGE_USERS)),
    service: StructureHintService = Depends(get_structure_hint_service),
) -> HintAdminResponse:
    try:
        payload = service.upsert_hint(
            structure_type=body.type,
            subtype=body.subtype,
            difficulty=body.difficulty,
            explanation=body.explanation,
            examples=body.examples,
            title=body.title,
        )
        db.commit()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return HintAdminResponse(
        id=payload.get("id"),
        type=payload["type"],
        subtype=payload["subtype"],
        title=payload["title"],
        difficulty=payload["difficulty"],
        explanation=payload["explanation"],
        examples=payload.get("examples") or {},
        source=payload.get("source") or "db",
    )


@router.delete("/{hint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin_hint(
    hint_id: int,
    db: Session = Depends(get_db),
    _: CurrentUserResult = Depends(require_permission(Permission.MANAGE_USERS)),
    service: StructureHintService = Depends(get_structure_hint_service),
) -> None:
    try:
        deleted = service.delete_hint(hint_id)
        if deleted:
            db.commit()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="Hint not found")
