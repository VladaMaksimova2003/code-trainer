"""Tasks API — root router.

Sub-routers:
  endpoints.list_tasks   — GET /tasks, GET /tasks/{id}, GET /tasks/types
  endpoints.patterns     — GET /tasks/patterns
  endpoints.analysis     — POST /tasks/analyze-code
  endpoints.assignments  — POST /tasks/assignments
  endpoints.block_reorder — POST /tasks/block-reorder, POST /tasks/block-reorder/{id}/submit
  endpoints.code_assembly — CRUD /tasks/code-assembly
  endpoints.translation — GET/PUT /tasks/translation
"""
from fastapi import APIRouter

from api.tasks.endpoints.list_tasks import router as list_router
from api.tasks.endpoints.patterns import router as patterns_router
from api.tasks.endpoints.analysis import router as analysis_router
from api.tasks.endpoints.detect_concepts import router as detect_concepts_router
from api.tasks.endpoints.scan_concepts import router as scan_concepts_router
from api.tasks.endpoints.assignments import router as assignments_router
from api.tasks.endpoints.block_reorder import router as block_reorder_router
from api.tasks.endpoints.code_assembly import router as code_assembly_router
from api.tasks.endpoints.flowchart import router as flowchart_router
from api.tasks.endpoints.translation import router as translation_router
from api.tasks.endpoints.debug_codes import router as debug_codes_router

router = APIRouter()

router.include_router(assignments_router, prefix="/assignments")
router.include_router(block_reorder_router)
router.include_router(code_assembly_router)
router.include_router(flowchart_router)
router.include_router(translation_router)
router.include_router(debug_codes_router)
router.include_router(patterns_router)
router.include_router(analysis_router)
router.include_router(detect_concepts_router)
router.include_router(scan_concepts_router)
# list_router has GET "" and "/{task_id}" — must be last to avoid masking other routes
router.include_router(list_router)
