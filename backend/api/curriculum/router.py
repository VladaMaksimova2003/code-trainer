"""Curriculum progression API — UI / task generation only."""
from __future__ import annotations

from fastapi import APIRouter

from api.curriculum.schemas import CurriculumLevelResponse
from api.curriculum.v2_router import router as v2_router
from application.curriculum.legacy.structure_progression import get_level_plan

router = APIRouter()

router.include_router(v2_router)


@router.get("/level/{level}", response_model=CurriculumLevelResponse)
async def get_curriculum_level(level: int) -> CurriculumLevelResponse:
    payload = get_level_plan(level)
    return CurriculumLevelResponse(**payload)

