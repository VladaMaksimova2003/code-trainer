"""Compare warm docker exec vs cold docker run for a language runner.

Run inside the worker container (Docker socket mounted):

    docker exec code_trainer_dev-worker-1 python scripts/benchmark_warm_vs_cold.py
    docker exec code_trainer_dev-worker-1 python scripts/benchmark_warm_vs_cold.py --language pascal --runs 5

Prints JSON summary suitable for VKR table 9 / section 4.6.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import statistics
import subprocess
import sys
import time
import uuid

os.environ.setdefault("EXECUTION_WORKER", "1")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from infrastructure.execution.docker_executor import DockerExecutor
from infrastructure.execution.execution_core import ExecutionCore
from infrastructure.execution.language_registry import language_registry

SAMPLES: dict[str, dict[str, object]] = {
    "python": {
        "code": "n = int(input())\nprint('Even' if n % 2 == 0 else 'Odd')\n",
        "tests": [{"inputs": "4", "output": "Even"}, {"inputs": "7", "output": "Odd"}],
    },
    "pascal": {
        "code": """program Main;
var n: integer;
begin
  readln(n);
  if n mod 2 = 0 then writeln('Even') else writeln('Odd');
end.
""",
        "tests": [{"inputs": "4", "output": "Even"}, {"inputs": "7", "output": "Odd"}],
    },
    "csharp": {
        "code": """var n = int.Parse(Console.ReadLine());
if (n % 2 == 0) Console.WriteLine("Even");
else Console.WriteLine("Odd");
""",
        "tests": [{"inputs": "4", "output": "Even"}, {"inputs": "7", "output": "Odd"}],
    },
}


def cold_docker_run(image: str, shell_cmd: str, timeout: int = 30) -> tuple[int, int, str]:
    name = f"bench_{uuid.uuid4().hex[:8]}"
    cmd = [
        "docker",
        "run",
        "--rm",
        "--name",
        name,
        "-i",
        "--network",
        "none",
        "--cpus=0.5",
        "--memory=256m",
        "--read-only",
        "--tmpfs",
        "/tmp:rw,nosuid,nodev,noexec,size=50m",
        "--tmpfs",
        "/runner:rw,nosuid,nodev,size=50m",
        "--tmpfs",
        "/tmp/home:rw,exec,size=50m",
        "--env",
        "HOME=/tmp/home",
        "--user",
        "1000:1000",
        "--cap-drop=ALL",
        "--security-opt",
        "no-new-privileges",
        image,
        "sh",
        "-c",
        shell_cmd,
    ]
    t0 = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    ms = int((time.perf_counter() - t0) * 1000)
    return ms, proc.returncode, (proc.stdout or "").strip()


def build_one_shot_shell(cfg, code: str, stdin: str) -> str:
    ext = cfg.file_extension
    container_path = f"/tmp/home/source{ext}"
    one_shot = cfg.test.docker_one_shot or cfg.docker.run
    shell_cmd = one_shot.format(
        filename=container_path,
        source=container_path,
        binary="/tmp/home/app",
    )
    code_b64 = base64.b64encode(code.encode("utf-8")).decode("ascii")
    inner = f"echo {code_b64} | base64 -d > {container_path} && ({shell_cmd})"
    if stdin:
        return f"mkdir -p /tmp/home && printf '{stdin}\\n' | {inner}"
    return f"mkdir -p /tmp/home && {inner}"


def summarize(values: list[int]) -> dict[str, int | float]:
    if not values:
        return {"min_ms": 0, "max_ms": 0, "avg_ms": 0, "median_ms": 0}
    return {
        "min_ms": min(values),
        "max_ms": max(values),
        "avg_ms": round(statistics.mean(values), 1),
        "median_ms": int(statistics.median(values)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Warm vs cold execution benchmark")
    parser.add_argument("--language", default="python", choices=sorted(SAMPLES))
    parser.add_argument("--runs", type=int, default=3)
    args = parser.parse_args()

    sample = SAMPLES[args.language]
    code = str(sample["code"])
    tests = list(sample["tests"])  # type: ignore[arg-type]

    cfg = language_registry.get_or_raise(args.language)
    docker = DockerExecutor()
    core = ExecutionCore(docker=docker)
    image = cfg.docker.image
    warm_id = docker._find_warm_runner_container(image)

    cold_ms: list[int] = []
    warm_ms: list[int] = []
    shell = build_one_shot_shell(cfg, code, str(tests[0]["inputs"]))

    for _ in range(args.runs):
        ms, rc, out = cold_docker_run(image, shell)
        cold_ms.append(ms)
        if rc != 0:
            print(f"cold warning: rc={rc} stdout={out!r}", file=sys.stderr)

    if warm_id:
        for _ in range(args.runs):
            t0 = time.perf_counter()
            result = docker.run_raw_shell(image, shell, timeout=cfg.test.timeout_seconds + 10)
            warm_ms.append(int((time.perf_counter() - t0) * 1000))
            if result.returncode != 0:
                print(
                    f"warm warning: rc={result.returncode} stdout={result.stdout.strip()!r}",
                    file=sys.stderr,
                )
    else:
        print("warm runner container not found", file=sys.stderr)

    t0 = time.perf_counter()
    pipeline_results = core.run_tests(args.language, code, tests)
    pipeline_ms = int((time.perf_counter() - t0) * 1000)

    summary = {
        "language": args.language,
        "image": image,
        "warm_runner": warm_id or None,
        "runs": args.runs,
        "test_case": tests[0],
        "cold_docker_run_ms": summarize(cold_ms),
        "warm_docker_exec_ms": summarize(warm_ms),
        "pipeline_run_tests_ms": pipeline_ms,
        "pipeline_cases": [
            {
                "case": row.case,
                "status": row.status,
                "duration_ms": row.duration_ms,
            }
            for row in pipeline_results
        ],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
