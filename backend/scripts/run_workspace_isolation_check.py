"""Manual/integration check: submit A file must not leak to submit B."""
from __future__ import annotations

import subprocess
import sys

sys.path.insert(0, ".")

from infrastructure.execution.docker_executor import DockerExecutor
from infrastructure.execution.execution_workspace import isolation_shell_prefix, new_workspace_id


def main() -> int:
    docker = DockerExecutor()
    if not docker.is_available():
        print("SKIP: Docker not available")
        return 0

    warm = docker._find_warm_runner_container("csharp_runner")
    if not warm:
        print("SKIP: csharp_runner warm container not running")
        return 0

    docker_bin = docker._docker_binary()
    assert docker_bin

    ws_a = new_workspace_id()
    ws_b = new_workspace_id()
    marker = "CT_ISOLATION_MARKER"
    cmd_a = (
        isolation_shell_prefix(ws_a)
        + f'echo "{marker}" > "$CT_WORKSPACE/secret.txt" && ls "$CT_WORKSPACE"'
    )
    cmd_b = (
        isolation_shell_prefix(ws_b)
        + f'if [ -f "/tmp/home/{ws_a}/secret.txt" ]; then echo LEAK; else echo OK; fi'
    )

    proc_a = subprocess.run(
        [docker_bin, "exec", warm, "sh", "-c", cmd_a],
        capture_output=True,
        text=True,
        timeout=60,
    )
    print("submit A:", proc_a.returncode, proc_a.stdout.strip(), proc_a.stderr.strip())
    if proc_a.returncode != 0:
        return 1

    proc_b = subprocess.run(
        [docker_bin, "exec", warm, "sh", "-c", cmd_b],
        capture_output=True,
        text=True,
        timeout=60,
    )
    print("submit B:", proc_b.returncode, proc_b.stdout.strip(), proc_b.stderr.strip())
    if proc_b.returncode != 0 or "LEAK" in proc_b.stdout:
        return 1

    proc_cleanup = subprocess.run(
        [
            docker_bin,
            "exec",
            warm,
            "sh",
            "-c",
            f"test ! -d /tmp/home/{ws_a} || test ! -f /tmp/home/{ws_a}/secret.txt",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    print("cleanup:", proc_cleanup.returncode)
    return 0 if proc_cleanup.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
