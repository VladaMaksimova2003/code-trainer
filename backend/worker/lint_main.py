import json
import time
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import redis

from application.execution.pipeline_runner import WorkerPipelineRunner
from infrastructure.db.models.task.registry import load_models
from infrastructure.execution.execution_guard import mark_worker_context
from worker.settings import (
    LINT_QUEUE_NAME,
    LINT_RESULT_PREFIX,
    POLL_TIMEOUT_SECONDS,
    REDIS_DB,
    REDIS_HOST,
    REDIS_PORT,
)

load_models()
_pipeline = WorkerPipelineRunner()


def _connect_redis() -> redis.Redis:
    return redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
    )


def main() -> None:
    mark_worker_context()
    client = _connect_redis()
    print(
        f"[lint-worker] listening queue={LINT_QUEUE_NAME} redis={REDIS_HOST}:{REDIS_PORT}"
    )

    while True:
        item = client.brpop(LINT_QUEUE_NAME, timeout=POLL_TIMEOUT_SECONDS)
        if not item:
            continue

        _, raw = item
        payload = None
        try:
            payload = json.loads(raw)
            request_id = payload["request_id"]
            task_id = int(payload["task_id"])
            language = payload["language"]
            code = payload["code"]

            lint_result = _pipeline.run_lint_only(
                task_id=task_id, code=code, language=language
            )
            response = {
                "request_id": request_id,
                "status": "done",
                "task_id": task_id,
                "linter_errors": lint_result.get("linter_errors", []),
            }
            client.set(
                f"{LINT_RESULT_PREFIX}{request_id}", json.dumps(response), ex=300
            )
            print(f"[lint-worker] processed request_id={request_id}")
        except Exception as exc:
            request_id = (
                payload.get("request_id") if isinstance(payload, dict) else None
            )
            if request_id:
                client.set(
                    f"{LINT_RESULT_PREFIX}{request_id}",
                    json.dumps(
                        {
                            "request_id": request_id,
                            "status": "failed",
                            "linter_errors": [
                                {"type": "INTERNAL_ERROR", "text": str(exc)}
                            ],
                        }
                    ),
                    ex=120,
                )
            print(f"[lint-worker] failed payload={raw} error={exc}")
            time.sleep(0.1)


if __name__ == "__main__":
    main()
