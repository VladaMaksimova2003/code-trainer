"""Workspace isolation helpers and docker executor wiring."""
from __future__ import annotations

import re
from unittest.mock import MagicMock, patch

from infrastructure.execution.docker_executor import DockerExecutor
from infrastructure.execution.execution_workspace import (
    binary_path,
    isolation_shell_prefix,
    new_workspace_id,
    source_path,
    workspace_root,
)

WORKSPACE_RE = re.compile(r"/tmp/home/[a-f0-9]{16}/")


def test_workspace_paths_are_unique_per_id():
    a = new_workspace_id()
    b = new_workspace_id()
    assert a != b
    assert source_path(a, ".cpp") == f"{workspace_root(a)}/source.cpp"
    assert binary_path(a) == f"{workspace_root(a)}/app"


def test_isolation_prefix_creates_and_cleans_workspace():
    ws = "abc123def4567890"
    prefix = isolation_shell_prefix(ws)
    assert f'CT_WORKSPACE="{workspace_root(ws)}"' in prefix
    assert "mkdir -p" in prefix
    assert 'trap \'rm -rf "$CT_WORKSPACE"\' EXIT INT TERM' in prefix


def test_run_raw_shell_wraps_with_isolated_workspace():
    docker = DockerExecutor()
    captured: dict = {}

    def fake_exec(container_id, shell_cmd, timeout=None, stdin=None, profile=None):
        captured["cmd"] = shell_cmd
        captured["container_id"] = container_id
        from infrastructure.execution.docker_executor import DockerRunResult

        return DockerRunResult(stdout="ok", stderr="", returncode=0, duration_ms=1)

    with patch.object(docker, "_docker_binary", return_value="docker"):
        with patch("infrastructure.execution.docker_executor.Path.exists", return_value=True):
            with patch.object(docker, "_find_warm_runner_container", return_value="warmabc"):
                with patch.object(docker, "_exec_in_container", side_effect=fake_exec):
                    with patch.object(docker, "_maybe_recycle_warm_runner"):
                        result = docker.run_raw_shell(
                            "csharp_runner",
                            "echo hello",
                            workspace_id="deadbeefcafebabe",
                        )

    assert "CT_WORKSPACE=" in captured["cmd"]
    assert "/tmp/home/deadbeefcafebabe" in captured["cmd"]
    assert 'trap \'rm -rf "$CT_WORKSPACE"\' EXIT' in captured["cmd"]
    assert captured["container_id"] == "warmabc"
    assert result.workspace_id == "deadbeefcafebabe"


def test_run_raw_shell_uses_cold_run_when_warm_runner_missing():
    docker = DockerExecutor()
    with patch.object(docker, "_docker_binary", return_value="docker"):
        with patch("infrastructure.execution.docker_executor.Path.exists", return_value=True):
            with patch.object(docker, "_find_warm_runner_container", return_value=None):
                with patch.object(docker, "_use_warm_runners", return_value=True):
                    with patch.object(docker, "_run_limited_process") as limited:
                        limited.return_value = MagicMock(
                            stdout="",
                            stderr="",
                            returncode=0,
                        )
                        docker.run_raw_shell("csharp_runner", "echo x", workspace_id="a" * 16)

    command = limited.call_args[0][0]
    assert command[1] == "run"
    assert "--network" in command
    assert "none" in command
    assert "--user" in command
    assert "1000:1000" in command
