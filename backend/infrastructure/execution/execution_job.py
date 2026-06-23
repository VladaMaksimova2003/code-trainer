"""Execution job model for async distributed runs."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

from domain.execution.job_status import JobStatus

JobOp = Literal[
    "full_check",
    "lint_only",
    "pattern_only",
    "lint",
    "compile",
    "compile_check",
    "run_tests",
    "block_reorder_validate",
    "flow_semantic_check",
    "process_submission",
    "guest_full_check",
]


@dataclass
class ExecutionJob:
    job_id: str
    user_id: str
    language_id: str
    code: str
    op: JobOp
    status: JobStatus
    created_at: str
    dedup_key: str
    task_id: int | None = None
    test_cases: list[dict[str, Any]] = field(default_factory=list)
    updated_at: str | None = None
    error: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExecutionJob:
        return cls(
            job_id=str(data["job_id"]),
            user_id=str(data.get("user_id") or data.get("user_key") or "anonymous"),
            language_id=str(data["language_id"]),
            code=str(data["code"]),
            op=data["op"],
            status=JobStatus(str(data.get("status") or JobStatus.PENDING.value)),
            created_at=str(data.get("created_at") or cls.now_iso()),
            dedup_key=str(data.get("dedup_key") or ""),
            task_id=int(data["task_id"]) if data.get("task_id") is not None else None,
            test_cases=list(data.get("test_cases") or []),
            updated_at=data.get("updated_at"),
            error=data.get("error"),
            payload=dict(data.get("payload") or {}),
        )

    @classmethod
    def from_json(cls, raw: str) -> ExecutionJob:
        return cls.from_dict(json.loads(raw))
