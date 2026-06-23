"""FastAPI application entry point.

Run with:
    uvicorn main:app --reload
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.auth.router import router as auth_router
from api.admin.router import router as admin_router
from api.tasks.router import router as tasks_router
from api.tasks.catalogs_router import router as catalogs_router
from api.execution.solutions_router import router as solutions_router
from api.execution.submissions_router import router as submissions_router
from api.execution.flows_router import router as flows_router
from api.users.teacher_router import router as teacher_router
from api.users.student_router import router as student_router
from api.users.public_profiles_router import router as public_profiles_router
from api.users.settings_router import router as settings_router
from api.learning.router import router as learning_router
from api.analytics.router import router as analytics_router
from api.support.router import router as support_router
from api.notifications.router import router as notifications_router
from api.languages.router import router as languages_router
from api.hints.router import router as hints_router
from api.curriculum.router import router as curriculum_router
from api.guest.router import router as guest_router
from infrastructure.db.init_db import init_db
from infrastructure.execution.language_loader import load_languages
from infrastructure.hints.hint_loader import load_structure_hints
from infrastructure.execution.language_watcher import start_language_watcher
from shared.config import get_settings

_SIZE_LIMITED_PREFIXES = ("/solutions", "/submissions", "/flows", "/tasks")
_ROOT_PATH = os.getenv("ROOT_PATH", "").strip()
_ENABLE_OPENAPI = os.getenv("ENABLE_OPENAPI_DOCS", "").strip().lower() in {"1", "true", "yes"}


def _cors_origins() -> list[str]:
    return get_settings().cors_origin_list()


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_settings()
    load_languages()
    load_structure_hints()
    watcher = start_language_watcher()
    init_db()
    try:
        yield
    finally:
        watcher.stop()

app = FastAPI(
    title="Code Trainer API",
    description="Educational platform for code checking",
    version="0.1.0",
    lifespan=lifespan,
    root_path=_ROOT_PATH,
    docs_url="/docs" if _ENABLE_OPENAPI else None,
    redoc_url="/redoc" if _ENABLE_OPENAPI else None,
    openapi_url="/openapi.json" if _ENABLE_OPENAPI else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


def _cors_headers_for_request(request: Request) -> dict[str, str]:
    origin = request.headers.get("origin")
    if origin and origin in _cors_origins():
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
        }
    return {}


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    headers = _cors_headers_for_request(request)
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=headers,
        )
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc) or "Internal server error"},
        headers=headers,
    )


@app.middleware("http")
async def limit_request_body_size(request: Request, call_next):
    if request.method not in {"POST", "PUT", "PATCH"}:
        return await call_next(request)
    if not request.url.path.startswith(_SIZE_LIMITED_PREFIXES):
        return await call_next(request)

    settings = get_settings()
    max_bytes = settings.security.request_body_max_bytes
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > max_bytes:
                return JSONResponse(
                    status_code=413,
                    content={
                        "detail": f"Request body is too large. Limit is {max_bytes} bytes."
                    },
                )
        except ValueError:
            pass

    body = await request.body()
    if len(body) > max_bytes:
        return JSONResponse(
            status_code=413,
            content={"detail": f"Request body is too large. Limit is {max_bytes} bytes."},
        )

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    request._receive = receive
    return await call_next(request)

app.include_router(auth_router,        prefix="/auth",        tags=["auth"])
app.include_router(tasks_router,       prefix="/tasks",       tags=["tasks"])
app.include_router(catalogs_router,                           tags=["catalogs"])
app.include_router(solutions_router,   prefix="/solutions",   tags=["solutions"])
app.include_router(submissions_router, prefix="/submissions",  tags=["submissions"])
app.include_router(flows_router,       prefix="/flows",        tags=["flows"])
app.include_router(admin_router,       prefix="/admin",        tags=["admin"])
app.include_router(teacher_router,     prefix="/teacher",      tags=["teacher"])
app.include_router(student_router,     prefix="/student",      tags=["student"])
app.include_router(public_profiles_router, prefix="/users",   tags=["users"])
app.include_router(settings_router,    prefix="/settings",     tags=["settings"])
app.include_router(learning_router,                            tags=["learning"])
app.include_router(analytics_router,                           tags=["analytics"])
app.include_router(support_router,     prefix="/support",    tags=["support"])
app.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
app.include_router(languages_router,   prefix="/languages",   tags=["languages"])
app.include_router(hints_router,       prefix="/hints",       tags=["hints"])
app.include_router(curriculum_router,  prefix="/curriculum",  tags=["curriculum"])
app.include_router(guest_router,         prefix="/guest",       tags=["guest"])


@app.get("/")
async def root() -> dict:
    return {"message": "Code Trainer API", "version": "0.1.0"}


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
