"""Execution/submissions root router.

Sub-routers:
  endpoints.submissions — POST/GET /submissions
  endpoints.lint        — POST/GET /submissions/lint
"""
from fastapi import APIRouter

from api.execution.endpoints.submissions import router as submissions_router
from api.execution.endpoints.lint import router as lint_router

router = APIRouter()

router.include_router(lint_router)
router.include_router(submissions_router)
