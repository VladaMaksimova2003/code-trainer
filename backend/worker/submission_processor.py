from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from application.execution.services.pipeline import SolutionPipelineService


class SubmissionProcessor:
    def __init__(self, pipeline: SolutionPipelineService, store: Any):
        self._pipeline = pipeline
        self._store = store

    def process(self, payload: dict[str, Any]) -> dict[str, Any]:
        submission_id = int(payload["submission_id"])
        task_id = int(payload["task_id"])
        language = payload["language"]
        code = payload["code"]

        result = self._pipeline.run_full(task_id=task_id, code=code, language=language)
        self._store.persist_success(submission_id=submission_id, result=result)

        return {
            "submission_id": submission_id,
            "status": "done",
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }

    def mark_failed(self, submission_id: int, message: str) -> None:
        self._store.mark_failed(submission_id=submission_id, message=message)
