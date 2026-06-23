"""Users/settings root router.

Sub-routers:
  endpoints.account         — GET/PATCH /settings/account, POST /settings/change-password, logout
  endpoints.learning        — GET/PATCH /settings/learning
  endpoints.teacher_profile — GET/PATCH /settings/teacher, GET /settings/teacher/overview
"""
from fastapi import APIRouter

from api.users.endpoints.account import router as account_router
from api.users.endpoints.learning import router as learning_router
from api.users.endpoints.teacher_profile import router as teacher_router

router = APIRouter()

router.include_router(account_router)
router.include_router(learning_router)
router.include_router(teacher_router)
