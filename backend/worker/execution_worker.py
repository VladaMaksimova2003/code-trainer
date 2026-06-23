"""Stateless execution worker — partitioned Redis queues, Docker-only."""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy.orm import configure_mappers

from application.execution.pipeline_runner import WorkerPipelineRunner
from infrastructure.db.models.task.registry import load_models
from domain.execution.job_status import JobStatus
from infrastructure.execution.execution_core import ExecutionCore
from infrastructure.execution.execution_guard import mark_worker_context
from infrastructure.execution.job_store import JobStore
from infrastructure.execution.language_loader import load_languages
from infrastructure.execution.language_watcher import start_language_watcher
from infrastructure.execution.rate_limiter import ExecutionRateLimiter
from worker.execution_handlers import (
    handle_block_reorder_validate,
    handle_compile_check,
    handle_flow_semantic_check,
    handle_process_submission,
    handle_run_tests,
)
from worker.submission_store import SubmissionStore
from infrastructure.execution.guest_rate_limiter import GuestRateLimiter
from worker.execution_settings import POLL_TIMEOUT_SECONDS, REDIS_HOST

_guest_limits = GuestRateLimiter()

_pipeline = WorkerPipelineRunner()
_store = JobStore()
_submissions = SubmissionStore()
_rate_limiter = ExecutionRateLimiter(_store._client)


def _execute(job):
    if job.op in {"full_check", "guest_full_check"}:
        return _pipeline.run_full(int(job.task_id or 0), job.code, job.language_id)
    if job.op == "lint_only":
        return _pipeline.run_lint_only(int(job.task_id or 0), job.code, job.language_id)
    if job.op == "pattern_only":
        return _pipeline.run_pattern_only(int(job.task_id or 0), job.code, job.language_id)
    if job.op in {"lint"}:
        from infrastructure.execution.execution_core import ExecutionCore

        return {"errors": ExecutionCore().lint(job.language_id, job.code)}
    if job.op in {"compile", "compile_check"}:
        return handle_compile_check(job)
    if job.op == "run_tests":
        return handle_run_tests(job)
    if job.op == "block_reorder_validate":
        return handle_block_reorder_validate(job)
    if job.op == "flow_semantic_check":
        return handle_flow_semantic_check(job)
    if job.op == "process_submission":
        return handle_process_submission(job)
    raise ValueError(f"Unknown op: {job.op}")


def _submission_id_from_job(job) -> int | None:
    if job.op != "process_submission":
        return None
    raw = (job.payload or {}).get("submission_id")
    if raw is None:
        return None
    return int(raw)


def _process(job) -> None:
    job_id = job.job_id
    submission_id = _submission_id_from_job(job)
    if submission_id is not None:
        _submissions.mark_running(submission_id)
    _store.update_status(job_id, JobStatus.RUNNING)
    try:
        output = _execute(job)
        _store.update_status(job_id, JobStatus.SUCCESS)
        _store.save_result(
            job_id,
            {"status": JobStatus.SUCCESS.value, "output": output, "error": None},
        )
    except Exception as exc:
        if submission_id is not None:
            _submissions.mark_failed(submission_id, str(exc))
        _store.update_status(job_id, JobStatus.FAILED, error=str(exc))
        _store.save_result(
            job_id,
            {"status": JobStatus.FAILED.value, "output": None, "error": str(exc)},
        )
    finally:
        _store.decrement_queue_depth()
        _rate_limiter.on_job_finished(job.user_id)
        if job.op == "guest_full_check":
            client_ip = (job.payload or {}).get("client_ip")
            if client_ip:
                _guest_limits.on_job_finished(str(client_ip))


def main() -> None:
    mark_worker_context()
    load_models()
    configure_mappers()
    load_languages()
    start_language_watcher()
    worker_id = f"execution-worker@{REDIS_HOST}"
    print(f"[{worker_id}] listening queues={_store.list_queue_names()}")

    while True:
        job = _store.dequeue_blocking(timeout=POLL_TIMEOUT_SECONDS)
        if not job:
            continue
        try:
            _process(job)
            print(f"[{worker_id}] job={job.job_id} op={job.op} done")
        except Exception as exc:
            print(f"[{worker_id}] job={job.job_id} fatal={exc}")
            time.sleep(0.1)


if __name__ == "__main__":
    main()
