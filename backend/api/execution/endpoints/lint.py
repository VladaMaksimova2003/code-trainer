"""POST/GET /submissions/lint — async linting queue."""
import hashlib
import json
import os
import uuid
from datetime import datetime, timezone

import redis
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies.authorization import require_permission
from api.execution.access import ensure_job_access, ensure_task_access
from api.execution.schemas.requests import LintCreateRequest
from application.auth.dto import CurrentUserResult
from domain.policies.permissions.permissions import Permission
from infrastructure.db.session import get_db

router = APIRouter(prefix="/lint")

LINT_QUEUE_NAME = os.getenv("LINT_QUEUE", "lint:queue")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
LINT_RESULT_PREFIX = os.getenv("LINT_RESULT_PREFIX", "lint:result:")
LINT_DEDUP_PREFIX = os.getenv("LINT_DEDUP_PREFIX", "lint:dedup:")
LINT_DEDUP_TTL_SECONDS = int(os.getenv("LINT_DEDUP_TTL_SECONDS", "15"))


def _redis_client() -> redis.Redis:
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


def _build_lint_fingerprint(request: LintCreateRequest) -> str:
    payload = f"{request.task_id}:{request.language}:{request.code}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _build_lint_dedup_key(request: LintCreateRequest, user_key: str) -> str:
    return f"{LINT_DEDUP_PREFIX}{user_key}:{request.task_id}:{request.language}"


@router.post("")
@router.post("/")
async def create_lint_request(
    request: LintCreateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.SOLVE_ASSIGNMENTS)
    ),
):
    ensure_task_access(db, current_user, request.task_id)
    client = _redis_client()
    user_key = str(current_user.id)
    fingerprint = _build_lint_fingerprint(request)
    dedup_key = _build_lint_dedup_key(request, user_key)
    raw_cached = client.get(dedup_key)
    if raw_cached:
        cached = json.loads(raw_cached)
        if cached.get("request_id") and cached.get("fingerprint") == fingerprint:
            return {"request_id": cached["request_id"], "status": "queued", "deduplicated": True}
    request_id = str(uuid.uuid4())
    payload = {
        "request_id": request_id,
        "user_id": user_key,
        "task_id": request.task_id,
        "language": request.language,
        "code": request.code,
        "session_id": request.session_id,
        "queued_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        client.set(
            f"{LINT_RESULT_PREFIX}{request_id}",
            json.dumps({"request_id": request_id, "status": "pending", "user_id": user_key}),
            ex=300,
        )
        client.set(
            dedup_key,
            json.dumps({"request_id": request_id, "fingerprint": fingerprint}),
            ex=LINT_DEDUP_TTL_SECONDS,
        )
        client.lpush(LINT_QUEUE_NAME, json.dumps(payload))
        return {"request_id": request_id, "status": "queued"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Lint queue unavailable: {exc}") from exc


@router.get("/{request_id}")
async def get_lint_result(
    request_id: str,
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.SOLVE_ASSIGNMENTS)
    ),
):
    try:
        raw = _redis_client().get(f"{LINT_RESULT_PREFIX}{request_id}")
        if not raw:
            raise HTTPException(status_code=404, detail="Lint request not found")
        payload = json.loads(raw)
        ensure_job_access(current_user, str(payload.get("user_id") or ""))
        return payload
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(status_code=503, detail=f"Lint result unavailable: {exc}") from exc
