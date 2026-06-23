"""Public hints API — teacher UI explanations."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies.hints import get_structure_hint_service
from api.hints.construction_schemas import MpltConstructionListResponse, MpltConstructionResponse
from api.hints.schemas import StructureCatalogResponse, StructureHintResponse
from application.curriculum.display.pitfall_construction_sync import (
    MPLT_CATEGORY_NAME,
    list_mplt_constructions,
)
from application.hints.structure_hint_service import (
    StructureHintNotFoundError,
    StructureHintService,
)
from infrastructure.db.session import get_db

router = APIRouter()


@router.get("/structures", response_model=StructureCatalogResponse)
async def list_structure_hints(
    service: StructureHintService = Depends(get_structure_hint_service),
) -> StructureCatalogResponse:
    return StructureCatalogResponse(structures=service.list_structures())


@router.get("/structure/{structure_type}", response_model=list[StructureHintResponse])
async def list_hints_for_type(
    structure_type: str,
    service: StructureHintService = Depends(get_structure_hint_service),
) -> list[StructureHintResponse]:
    try:
        items = service.list_hints_for_structure(structure_type)
    except StructureHintNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return [StructureHintResponse(**item) for item in items]


@router.get("/structure/{structure_type}/{subtype}", response_model=StructureHintResponse)
async def get_structure_hint(
    structure_type: str,
    subtype: str,
    service: StructureHintService = Depends(get_structure_hint_service),
) -> StructureHintResponse:
    try:
        payload = service.get_hint(structure_type, subtype)
    except StructureHintNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return StructureHintResponse(**payload)


@router.get("/mpltransfer", response_model=MpltConstructionListResponse)
async def list_mplt_transfer_constructions(
    db: Session = Depends(get_db),
) -> MpltConstructionListResponse:
    """MPLT pitfall cards exported into the Construction hint library."""
    items = list_mplt_constructions(db)
    return MpltConstructionListResponse(
        category_name=MPLT_CATEGORY_NAME,
        items=[MpltConstructionResponse(**item) for item in items],
    )
