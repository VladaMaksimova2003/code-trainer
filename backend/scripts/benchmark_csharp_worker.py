"""Benchmark C# execution exactly as the worker does (DockerExecutor + test strategy)."""
from __future__ import annotations

import os
import sys
import time

# Allow running from repo without worker guard for local profiling only.
os.environ.setdefault("EXECUTION_WORKER", "1")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from infrastructure.execution.docker_executor import DockerExecutor
from infrastructure.execution.execution_core import ExecutionCore
from infrastructure.execution.language_registry import language_registry

SAMPLE_CODE = """\
var n = int.Parse(Console.ReadLine());
if (n % 2 == 0) Console.WriteLine("Even");
else Console.WriteLine("Odd");
"""

TEST_CASES = [
    {"inputs": "4", "output": "Even"},
    {"inputs": "7", "output": "Odd"},
]


def main() -> None:
    cfg = language_registry.get_or_raise("csharp")
    docker = DockerExecutor()
    core = ExecutionCore(docker=docker)

    print("=== Environment ===")
    print(f"EXECUTION_USE_WARM_RUNNERS={os.getenv('EXECUTION_USE_WARM_RUNNERS', 'true')}")
    print(f"compile_once={cfg.test.compile_once}")
    print(f"batch_one_shot={cfg.test.batch_one_shot}")
    print(f"timeout_seconds={cfg.test.timeout_seconds}")
    print(f"strategy={cfg.test.strategy}")
    print(f"docker_one_shot={cfg.test.docker_one_shot}")
    print(f"warm_runner_found={docker._find_warm_runner_container(cfg.docker.image)}")

    t0 = time.perf_counter()
    results = core.run_tests("csharp", SAMPLE_CODE, TEST_CASES)
    total_ms = int((time.perf_counter() - t0) * 1000)

    print("\n=== Worker run_tests (current config) ===")
    print(f"total_ms={total_ms}")
    for row in results:
        print(
            f"case={row.case} status={row.status} duration_ms={row.duration_ms} "
            f"actual={row.actual!r} message={row.message!r}"
        )

    print("\n=== Per-test isolated run_shell (legacy: one exec per test) ===")
    for index, tc in enumerate(TEST_CASES, start=1):
        t_start = time.perf_counter()
        result = docker.run_shell(
            cfg.docker.image,
            cfg.test.docker_one_shot or cfg.docker.run,
            SAMPLE_CODE,
            cfg.file_extension,
            timeout=cfg.test.timeout_seconds,
            stdin=tc["inputs"],
        )
        elapsed = int((time.perf_counter() - t_start) * 1000)
        print(
            f"test={index} wall_ms={elapsed} docker_reported_ms={result.duration_ms} "
            f"rc={result.returncode} stdout={result.stdout.strip()!r}"
        )


if __name__ == "__main__":
    main()
