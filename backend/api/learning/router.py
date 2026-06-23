from fastapi import APIRouter

from api.learning import assignment_sets, groups, teachers
from api.learning.adaptive_router import router as adaptive_router

router = APIRouter()
router.include_router(groups.router)
router.include_router(assignment_sets.router)
router.include_router(teachers.router)
router.include_router(adaptive_router)
