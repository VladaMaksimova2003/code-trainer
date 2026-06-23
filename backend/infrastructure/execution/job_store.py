"""Redis job state store — queues partitioned by language, no RPC."""
from __future__ import annotations

import json
from typing import Any

import redis

from domain.execution.job_status import JobStatus
from infrastructure.execution.execution_job import ExecutionJob
from infrastructure.execution.language_registry import language_registry
from worker.execution_settings import (
    EXECUTION_DEDUP_PREFIX,
    EXECUTION_GLOBAL_DEPTH_KEY,
    EXECUTION_JOB_KEY_PREFIX,
    EXECUTION_JOB_TTL_SECONDS,
    EXECUTION_QUEUE_DEFAULT,
    EXECUTION_QUEUE_PREFIX,
    EXECUTION_RESULT_PREFIX,
    REDIS_DB,
    REDIS_HOST,
    REDIS_PORT,
)


class JobStoreError(Exception):
    pass


class JobStore:
    def __init__(self, client: redis.Redis | None = None) -> None:
        self._client = client or redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
        )

    def queue_name_for_language(self, language_id: str) -> str:
        lang = str(language_id).lower()
        if lang in language_registry.ids():
            return f"{EXECUTION_QUEUE_PREFIX}:{lang}"
        return EXECUTION_QUEUE_DEFAULT

    def list_queue_names(self) -> list[str]:
        names = [self.queue_name_for_language(lang_id) for lang_id in language_registry.ids()]
        if EXECUTION_QUEUE_DEFAULT not in names:
            names.append(EXECUTION_QUEUE_DEFAULT)
        return names

    def _job_key(self, job_id: str) -> str:
        return f"{EXECUTION_JOB_KEY_PREFIX}{job_id}"

    def _result_key(self, job_id: str) -> str:
        return f"{EXECUTION_RESULT_PREFIX}{job_id}"

    def _dedup_key(self, dedup_key: str) -> str:
        return f"{EXECUTION_DEDUP_PREFIX}{dedup_key}"

    def save_job(self, job: ExecutionJob) -> None:
        self._client.set(
            self._job_key(job.job_id),
            job.to_json(),
            ex=EXECUTION_JOB_TTL_SECONDS,
        )

    def get_job(self, job_id: str) -> ExecutionJob | None:
        raw = self._client.get(self._job_key(job_id))
        if not raw:
            return None
        return ExecutionJob.from_json(raw)

    def update_status(
        self,
        job_id: str,
        status: JobStatus,
        *,
        error: str | None = None,
    ) -> ExecutionJob:
        job = self.get_job(job_id)
        if not job:
            raise JobStoreError(f"Job {job_id} not found")
        job.status = status
        job.updated_at = ExecutionJob.now_iso()
        if error:
            job.error = error
        self.save_job(job)
        return job

    def get_dedup_job_id(self, dedup_key: str) -> str | None:
        return self._client.get(self._dedup_key(dedup_key))

    def bind_dedup(self, dedup_key: str, job_id: str) -> None:
        self._client.set(
            self._dedup_key(dedup_key),
            job_id,
            ex=EXECUTION_JOB_TTL_SECONDS,
        )

    def enqueue(self, job: ExecutionJob) -> str:
        queue = self.queue_name_for_language(job.language_id)
        self._client.lpush(queue, job.job_id)
        self._client.incr(EXECUTION_GLOBAL_DEPTH_KEY)
        return queue

    def dequeue_blocking(self, timeout: int) -> ExecutionJob | None:
        queues = self.list_queue_names()
        item = self._client.brpop(queues, timeout=timeout)
        if not item:
            return None
        _, job_id = item
        job = self.get_job(job_id)
        if not job:
            return None
        return job

    def decrement_queue_depth(self) -> None:
        depth = int(self._client.get(EXECUTION_GLOBAL_DEPTH_KEY) or 0)
        if depth > 0:
            self._client.decr(EXECUTION_GLOBAL_DEPTH_KEY)

    def save_result(self, job_id: str, payload: dict[str, Any]) -> None:
        body = {"job_id": job_id, **payload}
        self._client.set(
            self._result_key(job_id),
            json.dumps(body),
            ex=EXECUTION_JOB_TTL_SECONDS,
        )

    def get_result(self, job_id: str) -> dict[str, Any] | None:
        raw = self._client.get(self._result_key(job_id))
        if not raw:
            return None
        return json.loads(raw)
