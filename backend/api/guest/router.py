"""Anonymous demo: solve public tasks without registration (no DB persistence)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from api.guest.access import ensure_public_task
from api.guest.schemas import (
    GuestCheckQueuedResponse,
    GuestCheckRequest,
    GuestCheckResultResponse,
)
from application.execution.job_service import ExecutionJobService
from infrastructure.execution.guest_rate_limiter import GuestRateLimitError, GuestRateLimiter
from infrastructure.db.session import get_db
from shared.config import get_settings

router = APIRouter()
_job_service = ExecutionJobService()
_guest_limits = GuestRateLimiter()


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _require_guest_mode() -> None:
    if not get_settings().guest_mode.enabled:
        raise HTTPException(status_code=404, detail="Guest mode is disabled")


@router.post("/check", response_model=GuestCheckQueuedResponse)
async def guest_check_solution(
    body: GuestCheckRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    _require_guest_mode()
    ensure_public_task(db, body.task_id)
    client_ip = _client_ip(request)
    try:
        _guest_limits.check_submit(client_ip)
        payload = _job_service.submit(
            user_id=_guest_limits.guest_user_id(client_ip),
            language_id=body.language,
            code=body.code,
            op="guest_full_check",
            task_id=body.task_id,
            payload={"client_ip": client_ip, "guest": True},
        )
        _guest_limits.on_job_queued(client_ip)
        return GuestCheckQueuedResponse(job_id=payload["job_id"], status=payload["status"])
    except GuestRateLimitError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc


@router.get("/check/{job_id}", response_model=GuestCheckResultResponse)
async def guest_check_result(job_id: str, request: Request):
    _require_guest_mode()
    client_ip = _client_ip(request)
    job = _job_service._store.get_job(job_id)
    if not job or job.op != "guest_full_check":
        raise HTTPException(status_code=404, detail="Job not found")
    if job.payload.get("client_ip") != client_ip:
        raise HTTPException(status_code=403, detail="Access denied")
    if job.user_id != _guest_limits.guest_user_id(client_ip):
        raise HTTPException(status_code=403, detail="Access denied")

    raw = _job_service.get_result(job_id)
    if raw["status"] not in {"SUCCESS", "FAILED"}:
        return GuestCheckResultResponse(job_id=job_id, status=raw["status"])

    if raw["status"] == "FAILED":
        return GuestCheckResultResponse(
            job_id=job_id,
            status="FAILED",
            success=False,
            errors=raw.get("errors"),
            compiler_errors=[{"type": "EXECUTION", "text": raw.get("errors") or "Check failed"}],
        )

    output = raw.get("output") or {}
    return GuestCheckResultResponse(
        job_id=job_id,
        status="SUCCESS",
        success=bool(output.get("success")),
        compiler_errors=output.get("compiler_errors") or [],
        linter_errors=output.get("linter_errors") or [],
        pattern_errors=output.get("pattern_errors") or [],
        test_results=output.get("test_results") or [],
    )
