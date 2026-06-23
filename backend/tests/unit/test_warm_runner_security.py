"""Regression: warm-runner isolation and resource limits."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from infrastructure.execution.docker_executor import DockerExecutor
from infrastructure.execution.execution_workspace import (
    binary_path,
    isolation_shell_prefix,
    new_workspace_id,
    source_path,
    warm_runner_recycle_after,
    workspace_root,
)


def test_each_submit_gets_unique_workspace_directory():
    a = new_workspace_id()
    b = new_workspace_id()
    assert workspace_root(a) != workspace_root(b)
    assert workspace_root(a) == f"/tmp/home/{a}"
    assert source_path(a, ".csx") == f"/tmp/home/{a}/source.csx"
    assert binary_path(b) == f"/tmp/home/{b}/app"


def test_isolation_prefix_removes_workspace_on_exit():
    ws = "abc123def4567890"
    prefix = isolation_shell_prefix(ws)
    assert f'CT_WORKSPACE="{workspace_root(ws)}"' in prefix
    assert "mkdir -p" in prefix
    assert 'trap \'rm -rf "$CT_WORKSPACE"\' EXIT INT TERM' in prefix


def test_cold_docker_run_enforces_limits_and_no_network():
    docker = DockerExecutor()
    with patch.object(docker, "_docker_binary", return_value="docker"):
        with patch("infrastructure.execution.docker_executor.Path.exists", return_value=True):
            with patch.object(docker, "_find_warm_runner_container", return_value=None):
                with patch.object(docker, "_use_warm_runners", return_value=False):
                    with patch.object(docker, "_run_limited_process") as limited:
                        limited.return_value = MagicMock(stdout="", stderr="", returncode=0)
                        docker.run_raw_shell("cpp_runner", "echo hi", workspace_id="b" * 16)

    command = limited.call_args[0][0]
    joined = " ".join(command)
    assert "--network none" in joined
    assert "--user 1000:1000" in joined
    assert f"--cpus={docker.DEFAULT_CPUS}" in joined
    assert f"--memory={docker.DEFAULT_MEMORY}" in joined
    assert f"--pids-limit={docker.DEFAULT_PIDS}" in joined
    assert "/tmp/home/bbbbbbbbbbbbbbbb" in command[-1]


def test_warm_runner_recycles_after_configured_exec_count():
    docker = DockerExecutor()
    container = "warmcontainer01"
    recycle_after = warm_runner_recycle_after()
    docker._warm_exec_counts[container] = recycle_after

    with patch.object(docker, "_docker_binary", return_value="docker"):
        with patch("subprocess.run") as run_mock:
            docker._maybe_recycle_warm_runner(container)

    run_mock.assert_called_once()
    assert docker._warm_exec_counts[container] == 0


def test_warm_exec_wraps_user_command_with_workspace_trap():
    docker = DockerExecutor()
    captured: dict = {}

    def fake_exec(container_id, shell_cmd, timeout=None, stdin=None, profile=None):
        captured["cmd"] = shell_cmd
        from infrastructure.execution.docker_executor import DockerRunResult

        return DockerRunResult(stdout="", stderr="", returncode=0, duration_ms=1)

    ws = "cafebabecafebabe"
    with patch.object(docker, "_docker_binary", return_value="docker"):
        with patch("infrastructure.execution.docker_executor.Path.exists", return_value=True):
            with patch.object(docker, "_use_warm_runners", return_value=True):
                with patch.object(docker, "_find_warm_runner_container", return_value="warmid"):
                    with patch.object(docker, "_exec_in_container", side_effect=fake_exec):
                        with patch.object(docker, "_maybe_recycle_warm_runner"):
                            docker.run_raw_shell(
                                "csharp_runner",
                                "echo user-code",
                                workspace_id=ws,
                            )

    assert workspace_root(ws) in captured["cmd"]
    assert "trap" in captured["cmd"]
    assert "echo user-code" in captured["cmd"]
