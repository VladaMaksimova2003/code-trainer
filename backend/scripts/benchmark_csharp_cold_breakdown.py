"""Break down cold `docker run` latency for C# one-shot."""
from __future__ import annotations

import json
import subprocess
import textwrap
import time
import uuid

IMAGE = "csharp_runner"

SHELL = textwrap.dedent(
    r"""
    now_ms() { date +%s%3N; }
    SCRIPT='var n = int.Parse(Console.ReadLine()); if (n % 2 == 0) Console.WriteLine("Even"); else Console.WriteLine("Odd");'

    t=$(now_ms); echo '{"s":"container_start_script","ms":0}'; t0=$t

    t=$(now_ms); mkdir -p /tmp/home
    echo '{"s":"mkdir","ms":'"$((t-t0))"'}'; t0=$t

    t=$(now_ms); printf '%s\n' "$SCRIPT" > /tmp/home/source.csx
    echo '{"s":"write","ms":'"$((t-t0))"'}'; t0=$t

    t=$(now_ms); dotnet --version >/dev/null 2>&1
    echo '{"s":"dotnet_version_warmup","ms":'"$((t-t0))"'}'; t0=$t

    t=$(now_ms); printf '4\n' | DOTNET_NOLOGO=1 dotnet-script /tmp/home/source.csx
    echo '{"s":"dotnet_script_run1","ms":'"$((t-t0))"'}'; t0=$t

    t=$(now_ms); printf '7\n' | DOTNET_NOLOGO=1 dotnet-script /tmp/home/source.csx
    echo '{"s":"dotnet_script_run2","ms":'"$((t-t0))"'}'
    """
).strip()


def cold_run() -> tuple[int, list[dict]]:
    name = f"cold_{uuid.uuid4().hex[:8]}"
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
        IMAGE,
        "sh",
        "-c",
        SHELL,
    ]
    t0 = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    wall = int((time.perf_counter() - t0) * 1000)
    stages = []
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                stages.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return wall, stages


if __name__ == "__main__":
    wall, stages = cold_run()
    print(json.dumps({"cold_docker_run_total_ms": wall, "stages": stages}, ensure_ascii=False, indent=2))
