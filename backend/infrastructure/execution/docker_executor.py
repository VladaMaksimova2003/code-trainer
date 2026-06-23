"""Docker-only code execution — no user code runs on the host."""
from __future__ import annotations

import base64
import logging
import os
import subprocess
import threading
import time
import uuid
from contextlib import nullcontext
from dataclasses import dataclass
from pathlib import Path
from shutil import which

from infrastructure.execution.execution_profiler import ExecutionProfiler, profiling_enabled
from infrastructure.execution.execution_workspace import (
    binary_path,
    isolation_shell_prefix,
    new_workspace_id,
    source_path,
    warm_runner_recycle_after,
)
from infrastructure.execution.output_parser import parse_diagnostics
from shared.config import get_settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DockerRunResult:
    stdout: str
    stderr: str
    returncode: int
    duration_ms: int = 0
    workspace_id: str = ""

    @property
    def combined_output(self) -> str:
        return f"{self.stderr}\n{self.stdout}".strip()


class DockerExecutor:
    DEFAULT_TIMEOUT = 5
    DEFAULT_MEMORY = "256m"
    DEFAULT_CPUS = "0.5"
    DEFAULT_PIDS = 64

    def __init__(self) -> None:
        self._max_output_bytes = get_settings().security.execution_output_max_bytes
        self._warm_exec_counts: dict[str, int] = {}

    def _docker_binary(self) -> str | None:
        for candidate in ("docker", "/usr/local/bin/docker", "/usr/bin/docker"):
            if candidate == "docker":
                found = which("docker")
                if found:
                    return found
            elif Path(candidate).is_file():
                return candidate
        return None

    def is_available(self) -> bool:
        if self._docker_binary() is None:
            return False
        return Path("/var/run/docker.sock").exists()

    def run_shell(
        self,
        image: str,
        command: str,
        code: str,
        ext: str,
        timeout: int | None = None,
        stdin: str | None = None,
        *,
        workspace_id: str | None = None,
    ) -> DockerRunResult:
        ws_id = workspace_id or new_workspace_id()
        container_path = source_path(ws_id, ext)
        app_path = binary_path(ws_id)
        shell_cmd = command.format(
            filename=container_path,
            source=container_path,
            binary=app_path,
            output=app_path,
        )
        code_b64 = base64.b64encode(code.encode("utf-8")).decode("ascii")
        inner = f"echo {code_b64} | base64 -d > {container_path} && ({shell_cmd})"
        return self.run_raw_shell(
            image,
            inner,
            timeout=timeout,
            stdin=stdin,
            workspace_id=ws_id,
        )

    def _use_warm_runners(self) -> bool:
        return os.getenv("EXECUTION_USE_WARM_RUNNERS", "true").lower() in {
            "1",
            "true",
            "yes",
        }

    def _find_warm_runner_container(self, image: str) -> str | None:
        docker_bin = self._docker_binary()
        if not docker_bin:
            return None
        for selector in (f"ancestor={image}", f"name={image}"):
            try:
                proc = subprocess.run(
                    [
                        docker_bin,
                        "ps",
                        "--filter",
                        selector,
                        "--filter",
                        "status=running",
                        "--format",
                        "{{.ID}}",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    check=False,
                )
            except Exception:
                continue
            for line in proc.stdout.splitlines():
                container_id = line.strip()
                if container_id:
                    return container_id
        return None

    def _maybe_recycle_warm_runner(self, container_id: str) -> None:
        limit = warm_runner_recycle_after()
        count = self._warm_exec_counts.get(container_id, 0) + 1
        self._warm_exec_counts[container_id] = count
        if count < limit:
            return
        docker_bin = self._docker_binary()
        if not docker_bin:
            return
        logger.info(
            "Recycling warm runner container=%s after %s execs",
            container_id[:12],
            count,
        )
        try:
            subprocess.run(
                [docker_bin, "restart", container_id],
                capture_output=True,
                timeout=30,
                check=False,
            )
        except Exception:
            logger.exception("Failed to recycle warm runner %s", container_id[:12])
        self._warm_exec_counts[container_id] = 0

    def run_raw_shell(
        self,
        image: str,
        shell_cmd: str,
        timeout: int | None = None,
        stdin: str | None = None,
        *,
        workspace_id: str | None = None,
        profile: ExecutionProfiler | None = None,
    ) -> DockerRunResult:
        docker_bin = self._docker_binary()
        if not docker_bin or not Path("/var/run/docker.sock").exists():
            raise RuntimeError("Docker is not available")

        ws_id = workspace_id or new_workspace_id()
        isolated_cmd = isolation_shell_prefix(ws_id) + shell_cmd

        if self._use_warm_runners():
            warm_id = self._find_warm_runner_container(image)
            if warm_id:
                if profile and profiling_enabled():
                    profile.mark(
                        "docker_transport",
                        mode="warm_exec",
                        container_id=warm_id[:12],
                        workspace_id=ws_id,
                    )
                result = self._exec_in_container(
                    warm_id,
                    isolated_cmd,
                    timeout=timeout,
                    stdin=stdin,
                    profile=profile,
                )
                self._maybe_recycle_warm_runner(warm_id)
                return DockerRunResult(
                    stdout=result.stdout,
                    stderr=result.stderr,
                    returncode=result.returncode,
                    duration_ms=result.duration_ms,
                    workspace_id=ws_id,
                )

        container_name = f"runner_{uuid.uuid4().hex[:8]}"
        logger.warning(
            "Cold docker run for image=%s (warm runner unavailable). "
            "Expect slower startup for heavy images (e.g. dotnet SDK).",
            image,
        )
        if profile and profiling_enabled():
            profile.mark(
                "docker_transport",
                mode="cold_run",
                container_name=container_name,
                workspace_id=ws_id,
            )
        docker_run = [
            docker_bin,
            "run",
            "--rm",
            "--name",
            container_name,
            "-i",
            "--network",
            "none",
            f"--cpus={self.DEFAULT_CPUS}",
            f"--memory={self.DEFAULT_MEMORY}",
            f"--pids-limit={self.DEFAULT_PIDS}",
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
            isolated_cmd,
        ]

        started = time.monotonic()
        try:
            with profile.stage("docker_run_process") if profile else nullcontext():
                result = self._run_limited_process(
                    docker_run,
                    container_name=container_name,
                    timeout=timeout or self.DEFAULT_TIMEOUT,
                    stdin=stdin,
                )
            duration_ms = int((time.monotonic() - started) * 1000)
            if profile and profiling_enabled():
                profile.mark(
                    "docker_run_complete",
                    duration_ms=duration_ms,
                    returncode=result.returncode,
                )
            return DockerRunResult(
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode,
                duration_ms=duration_ms,
                workspace_id=ws_id,
            )
        except subprocess.TimeoutExpired:
            self._kill_container(container_name)
            raise

    def _exec_in_container(
        self,
        container_id: str,
        shell_cmd: str,
        timeout: int | None = None,
        stdin: str | None = None,
        profile: ExecutionProfiler | None = None,
    ) -> DockerRunResult:
        docker_bin = self._docker_binary()
        if not docker_bin:
            raise RuntimeError("Docker is not available")
        command = [docker_bin, "exec", "-i", container_id, "sh", "-c", shell_cmd]
        started = time.monotonic()
        with profile.stage("docker_exec_process") if profile else nullcontext():
            result = self._run_limited_process(
                command,
                container_name=None,
                timeout=timeout or self.DEFAULT_TIMEOUT,
                stdin=stdin,
            )
        duration_ms = int((time.monotonic() - started) * 1000)
        if profile and profiling_enabled():
            profile.mark(
                "docker_exec_complete",
                duration_ms=duration_ms,
                returncode=result.returncode,
            )
        return DockerRunResult(
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode,
            duration_ms=duration_ms,
        )

    def _kill_container(self, name: str | None) -> None:
        if not name:
            return
        try:
            docker_bin = self._docker_binary() or "docker"
            subprocess.run(
                [docker_bin, "kill", name],
                capture_output=True,
                timeout=3,
            )
        except Exception:
            pass

    def _run_limited_process(
        self,
        command: list[str],
        *,
        container_name: str | None,
        timeout: int,
        stdin: str | None = None,
    ) -> DockerRunResult:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE if stdin is not None else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert process.stdout is not None
        assert process.stderr is not None

        stdout_buffer = bytearray()
        stderr_buffer = bytearray()
        lock = threading.Lock()
        total_bytes = 0
        output_truncated = False

        if stdin is not None and process.stdin is not None:
            process.stdin.write(stdin.encode("utf-8"))
            process.stdin.close()

        def reader(stream, target: bytearray) -> None:
            nonlocal total_bytes, output_truncated
            try:
                while True:
                    chunk = stream.read(4096)
                    if not chunk:
                        break
                    with lock:
                        remaining = self._max_output_bytes - total_bytes
                        if remaining > 0:
                            accepted = chunk[:remaining]
                            target.extend(accepted)
                            total_bytes += len(accepted)
                        if len(chunk) > max(remaining, 0) or total_bytes >= self._max_output_bytes:
                            output_truncated = True
                    if output_truncated:
                        self._kill_container(container_name)
                        process.kill()
                        break
            finally:
                stream.close()

        stdout_thread = threading.Thread(
            target=reader, args=(process.stdout, stdout_buffer), daemon=True
        )
        stderr_thread = threading.Thread(
            target=reader, args=(process.stderr, stderr_buffer), daemon=True
        )
        stdout_thread.start()
        stderr_thread.start()

        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self._kill_container(container_name)
            process.kill()
            raise
        finally:
            stdout_thread.join(timeout=1)
            stderr_thread.join(timeout=1)

        stderr = stderr_buffer.decode("utf-8", errors="replace")
        stdout = stdout_buffer.decode("utf-8", errors="replace")
        if output_truncated:
            marker = f"\n[output truncated after {self._max_output_bytes} bytes]"
            stderr = (stderr + marker).strip()
        return DockerRunResult(
            stdout=stdout,
            stderr=stderr,
            returncode=process.returncode if process.returncode is not None else 1,
        )

    def run_diagnostics(
        self,
        image: str,
        command: str,
        code: str,
        ext: str,
        timeout: int | None = None,
    ) -> list[str]:
        result = self.run_shell(image, command, code, ext, timeout=timeout)
        parsed = parse_diagnostics(result.combined_output, "")
        if parsed:
            return parsed
        if result.returncode != 0 or _looks_like_docker_failure(result.combined_output):
            return _docker_failure_diagnostics(result.combined_output, image)
        return []


def _looks_like_docker_failure(text: str) -> bool:
    lowered = str(text or "").lower()
    markers = (
        "pull access denied",
        "unable to find image",
        "error response from daemon",
        "docker is not available",
        "no such image",
        "repository does not exist",
        "cannot connect to the docker daemon",
    )
    return any(marker in lowered for marker in markers)


def _docker_failure_diagnostics(text: str, image: str) -> list[str]:
    lowered = str(text or "").lower()
    if "pull access denied" in lowered or "unable to find image" in lowered:
        return [
            "Line 1: "
            f"Docker-образ «{image}» не найден на сервере. "
            "Соберите runner (docker compose --profile runners build) и перезапустите worker."
        ]
    for raw in str(text or "").splitlines():
        line = raw.strip()
        if line and _looks_like_docker_failure(line):
            return [f"Line 1: {line}"]
    return [f"Line 1: Не удалось запустить проверку кода (образ {image})."]
