"""Verify C# uses warm docker exec with EXECUTION_PROFILE=1."""
from __future__ import annotations

import json
import logging
import os
import sys

os.environ.setdefault("EXECUTION_WORKER", "1")
os.environ.setdefault("EXECUTION_PROFILE", "1")
os.environ.setdefault("EXECUTION_USE_WARM_RUNNERS", "true")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

logging.basicConfig(level=logging.INFO, format="%(message)s")

from infrastructure.execution.execution_core import ExecutionCore
from infrastructure.execution.docker_executor import DockerExecutor
from infrastructure.execution.language_registry import language_registry

CODE = """\
var n = int.Parse(Console.ReadLine());
if (n % 2 == 0) Console.WriteLine("Even");
else Console.WriteLine("Odd");
"""

TEST_CASES = [{"inputs": "4", "output": "Even"}]


def main() -> None:
    cfg = language_registry.get_or_raise("csharp")
    docker = DockerExecutor()

    print("=== Config ===")
    print(f"EXECUTION_USE_WARM_RUNNERS={os.getenv('EXECUTION_USE_WARM_RUNNERS')}")
    print(f"batch_one_shot={cfg.test.batch_one_shot}")
    print(f"warm_runner={docker._find_warm_runner_container(cfg.docker.image)}")

    core = ExecutionCore(docker=docker)
    results = core.run_tests("csharp", CODE, TEST_CASES)

    print("=== Results ===")
    for row in results:
        print(
            json.dumps(
                {
                    "case": row.case,
                    "status": row.status,
                    "actual": row.actual,
                    "duration_ms": row.duration_ms,
                },
                ensure_ascii=False,
            )
        )
    print("Check worker logs above for execution_stage with mode=warm_exec")


if __name__ == "__main__":
    main()
