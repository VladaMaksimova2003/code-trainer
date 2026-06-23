"""Build execution jobs with deduplication."""
from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any

from domain.execution.job_status import JobStatus
from infrastructure.execution.execution_job import ExecutionJob, JobOp


def build_dedup_key(
    user_id: str,
    task_id: int | None,
    code: str,
    op: JobOp,
    language_id: str,
    payload: dict | None = None,
) -> str:
    raw = f"{user_id}:{task_id}:{language_id}:{op}:{code}"
    if payload:
        raw += ":" + hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode("utf-8")
        ).hexdigest()[:16]
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build_job(
    *,
    user_id: str,
    language_id: str,
    code: str,
    op: JobOp,
    task_id: int | None = None,
    test_cases: list[dict[str, Any]] | None = None,
    payload: dict[str, Any] | None = None,
    job_id: str | None = None,
) -> ExecutionJob:
    jid = job_id or str(uuid.uuid4())
    dedup = build_dedup_key(user_id, task_id, code, op, language_id, payload)
    return ExecutionJob(
        job_id=jid,
        user_id=user_id,
        language_id=str(language_id).lower(),
        code=code,
        op=op,
        status=JobStatus.PENDING,
        created_at=ExecutionJob.now_iso(),
        dedup_key=dedup,
        task_id=task_id,
        test_cases=list(test_cases or []),
    )
