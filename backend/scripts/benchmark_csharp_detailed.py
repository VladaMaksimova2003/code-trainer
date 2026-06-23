"""Detailed C# stage timings via docker exec into warm csharp_runner."""
from __future__ import annotations

import json
import subprocess
import textwrap
import time

CONTAINER = "code_trainer_dev-csharp_runner-1"

PROFILE_SH = textwrap.dedent(
    r"""
    #!/bin/sh
    now_ms() { date +%s%3N; }

    SCRIPT='var n = int.Parse(Console.ReadLine());
    if (n % 2 == 0) Console.WriteLine("Even");
    else Console.WriteLine("Odd");'

    echo '{"phase":"env","dotnet":"'"$(dotnet --version 2>/dev/null || echo missing)"'"}'

    t=$(now_ms)
    mkdir -p /tmp/home
    echo '{"phase":"mkdir","ms":'"$(( $(now_ms) - t ))"'}'

    t=$(now_ms)
    printf '%s\n' "$SCRIPT" > /tmp/home/source.csx
    echo '{"phase":"write_source","ms":'"$(( $(now_ms) - t ))"'}'

    for run in 1 2 3; do
      t=$(now_ms)
      out=$(printf '4\n' | DOTNET_NOLOGO=1 dotnet-script /tmp/home/source.csx 2>/tmp/home/err.log)
      ms=$(( $(now_ms) - t ))
      err=$(tr '\n' ' ' </tmp/home/err.log | head -c 200)
      printf '{"phase":"dotnet_script_run","run":%s,"ms":%s,"stdout":"%s","stderr":"%s"}\n' \
        "$run" "$ms" "$out" "$err"
    done

    t=$(now_ms)
    DOTNET_NOLOGO=1 dotnet-script --check /tmp/home/source.csx >/tmp/home/check.out 2>/tmp/home/check.err || true
    echo '{"phase":"dotnet_script_check","ms":'"$(( $(now_ms) - t ))"'}'

    if command -v /usr/bin/time >/dev/null 2>&1; then
      /usr/bin/time -p sh -c 'printf "4\n" | DOTNET_NOLOGO=1 dotnet-script /tmp/home/source.csx' 2>/tmp/home/time.log || true
      tr '\n' '|' </tmp/home/time.log
      echo
    fi

    echo '{"phase":"nuget_dirs","paths":"'"$(find /tmp/home /home/runner -maxdepth 4 -type d \( -name .nuget -o -name nuget -o -name .dotnet -o -name cache \) 2>/dev/null | tr '\n' ';')"'}'
    """
).strip()


def docker_exec(script: str) -> str:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "sh", "-c", script],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout)
    return proc.stdout


def main() -> None:
    print("=== Detailed profile inside warm csharp_runner ===")
    t0 = time.perf_counter()
    out = docker_exec(PROFILE_SH)
    wall = int((time.perf_counter() - t0) * 1000)
    print(f"host_wall_ms={wall}")
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("{"):
            try:
                print(json.dumps(json.loads(line), ensure_ascii=False))
            except json.JSONDecodeError:
                print(line)
        else:
            print(line)


if __name__ == "__main__":
    main()
