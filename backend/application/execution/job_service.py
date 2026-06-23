"""Async execution job API — enqueue only, never wait."""
from __future__ import annotations

from typing import Any

from domain.execution.job_status import JobStatus
from infrastructure.execution.job_builder import build_job
from infrastructure.execution.job_store import JobStore
from infrastructure.execution.rate_limiter import ExecutionRateLimitError, ExecutionRateLimiter


class ExecutionJobService:
    def __init__(
        self,
        store: JobStore | None = None,
        rate_limiter: ExecutionRateLimiter | None = None,
    ) -> None:
        self._store = store or JobStore()
        self._rate_limiter = rate_limiter or ExecutionRateLimiter(self._store._client)

    def submit(
        self,
        *,
        user_id: str,
        language_id: str,
        code: str,
        op: str,
        task_id: int | None = None,
        test_cases: list[dict] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        existing = self._resolve_dedup(
            user_id, task_id, code, op, language_id, payload
        )
        if existing:
            return {
                "job_id": existing.job_id,
                "status": existing.status.value,
                "deduplicated": True,
            }

        self._rate_limiter.check_submit(user_id, op=op)
        job = build_job(
            user_id=user_id,
            language_id=language_id,
            code=code,
            op=op,  # type: ignore[arg-type]
            task_id=task_id,
            test_cases=test_cases,
            payload=payload,
        )
        if payload:
            job.payload.update(payload)
        if (
            op == "process_submission"
            and payload
            and payload.get("submission_id") is not None
        ):
            job.code = ""
            job.dedup_key = f"submission:{payload['submission_id']}:{op}"

        self._store.save_job(job)
        job.status = JobStatus.QUEUED
        job.updated_at = job.now_iso()
        self._store.save_job(job)
        self._store.bind_dedup(job.dedup_key, job.job_id)
        self._store.enqueue(job)
        self._rate_limiter.on_job_queued(user_id)

        return {
            "job_id": job.job_id,
            "status": job.status.value,
            "deduplicated": False,
        }

    def get_status(self, job_id: str) -> dict[str, Any]:
        job = self._store.get_job(job_id)
        if not job:
            return {"job_id": job_id, "status": "UNKNOWN"}
        payload: dict[str, Any] = {
            "job_id": job.job_id,
            "status": job.status.value,
            "language": job.language_id,
            "op": job.op,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
        }
        if job.status.is_terminal():
            result = self._store.get_result(job_id)
            if result:
                payload["result"] = result
        return payload

    def get_result(self, job_id: str) -> dict[str, Any]:
        job = self._store.get_job(job_id)
        if not job:
            return {"job_id": job_id, "status": "UNKNOWN"}
        if not job.status.is_terminal():
            return {
                "job_id": job_id,
                "status": job.status.value,
                "output": None,
                "errors": None,
            }
        stored = self._store.get_result(job_id) or {}
        return {
            "job_id": job_id,
            "status": job.status.value,
            "output": stored.get("output"),
            "errors": stored.get("error") or job.error,
            "validation": stored.get("output"),
        }

    def _resolve_dedup(
        self,
        user_id: str,
        task_id: int | None,
        code: str,
        op: str,
        language_id: str,
        payload: dict | None,
    ):
        from infrastructure.execution.job_builder import build_dedup_key

        if op == "process_submission" and payload and payload.get("submission_id") is not None:
            dedup = f"submission:{payload['submission_id']}:{op}"
        else:
            dedup = build_dedup_key(
                user_id, task_id, code, op, language_id, payload  # type: ignore[arg-type]
            )
        existing_id = self._store.get_dedup_job_id(dedup)
        if not existing_id:
            return None
        job = self._store.get_job(existing_id)
        if not job:
            return None
        if job.status in {JobStatus.QUEUED, JobStatus.RUNNING, JobStatus.PENDING}:
            return job
        return None
