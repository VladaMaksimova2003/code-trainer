"""Compare warm docker exec vs cold docker run for C# one-shot."""
from __future__ import annotations

import base64
import os
import subprocess
import sys
import time
import uuid

os.environ.setdefault("EXECUTION_WORKER", "1")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from infrastructure.execution.docker_executor import DockerExecutor

CODE = """\
using System;
class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        if (n % 2 == 0) Console.WriteLine("Even");
        else Console.WriteLine("Odd");
    }
}
"""

IMAGE = "csharp_runner"
EXT = ".csx"
COMMAND = "DOTNET_NOLOGO=1 dotnet-script {filename}"


def build_shell_cmd(code: str, stdin: str = "4") -> str:
    container_path = f"/tmp/home/source{EXT}"
    shell_cmd = COMMAND.format(filename=container_path)
    code_b64 = base64.b64encode(code.encode("utf-8")).decode("ascii")
    inner = f"echo {code_b64} | base64 -d > {container_path} && ({shell_cmd})"
    if stdin:
        return f"mkdir -p /tmp/home && printf '{stdin}\\n' | {inner}"
    return f"mkdir -p /tmp/home && {inner}"


def cold_docker_run(shell_cmd: str, timeout: int = 30) -> tuple[int, int, str]:
    docker_bin = "docker"
    name = f"bench_{uuid.uuid4().hex[:8]}"
    cmd = [
        docker_bin,
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
        IMAGE,
        "sh",
        "-c",
        shell_cmd,
    ]
    t0 = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    ms = int((time.perf_counter() - t0) * 1000)
    return ms, proc.returncode, (proc.stdout or "").strip()


def main() -> None:
    docker = DockerExecutor()
    warm_id = docker._find_warm_runner_container(IMAGE)
    shell = build_shell_cmd(CODE)

    print("=== Cold docker run (new container each time) ===")
    for i in (1, 2):
        ms, rc, out = cold_docker_run(shell)
        print(f"run{i}: wall_ms={ms} rc={rc} stdout={out!r}")

    print("\n=== Warm docker exec (existing csharp_runner) ===")
    if not warm_id:
        print("no warm runner")
        return
    for i in (1, 2, 3):
        t0 = time.perf_counter()
        result = docker.run_raw_shell(IMAGE, shell, timeout=30)
        ms = int((time.perf_counter() - t0) * 1000)
        print(
            f"exec{i}: wall_ms={ms} docker_ms={result.duration_ms} "
            f"rc={result.returncode} stdout={result.stdout.strip()!r}"
        )


if __name__ == "__main__":
    main()
