"""Regression: C# batch_one_shot and warm docker exec transport."""
from __future__ import annotations

import re
from unittest.mock import patch

from domain.entities.language import DockerConfig, LanguageConfig, LanguageFeature, TestConfig
from infrastructure.execution.docker_executor import DockerExecutor, DockerRunResult
from infrastructure.execution.language_registry import language_registry
from infrastructure.execution.test_strategies import CompileAndRunTestStrategy

WORKSPACE_SOURCE_RE = re.compile(r"/tmp/home/[a-f0-9]{16}/source\.cs")
DOTNET_RUN_RE = re.compile(r"dotnet run --no-build")


class _RecordingDocker(DockerExecutor):
    def __init__(self) -> None:
        super().__init__()
        self.calls: list[dict] = []

    def run_raw_shell(
        self,
        image,
        shell_cmd,
        timeout=None,
        stdin=None,
        workspace_id=None,
        profile=None,
    ):
        self.calls.append(
            {
                "image": image,
                "shell_cmd": shell_cmd,
                "workspace_id": workspace_id,
            }
        )
        return DockerRunResult(
            stdout="__CT_CASE_1__\n4\n__CT_CASE_2__\n7\n",
            stderr="",
            returncode=0,
            duration_ms=900,
            workspace_id=workspace_id or "",
        )


def test_csharp_yml_enables_batch_one_shot():
    cfg = language_registry.get_or_raise("csharp")
    assert cfg.test.batch_one_shot is True
    assert cfg.test.timeout_seconds == 15


def test_batch_one_shot_single_docker_invocation_with_workspace():
    docker = _RecordingDocker()
    strategy = CompileAndRunTestStrategy(docker)
    code = 'var n=int.Parse(Console.ReadLine()); Console.WriteLine(n);'
    test_cases = [{"inputs": "4", "output": "4"}, {"inputs": "7", "output": "7"}]

    results = strategy.run(
        language_registry.get_or_raise("csharp"),
        code,
        test_cases,
    )

    assert len(docker.calls) == 1
    cmd = docker.calls[0]["shell_cmd"]
    assert WORKSPACE_SOURCE_RE.search(cmd)
    assert cmd.count("dotnet run --no-build") == 2
    assert cmd.count("base64 -d >") == 1
    assert "__CT_CASE_1__" in cmd
    assert "__CT_CASE_2__" in cmd
    assert " && " in cmd
    assert "; " not in cmd
    assert [row.status for row in results] == ["PASSED", "PASSED"]


def test_warm_exec_used_when_runner_available():
    docker = DockerExecutor()
    seen: dict = {}

    def fake_exec(container_id, shell_cmd, timeout=None, stdin=None, profile=None):
        seen["mode"] = "exec"
        seen["container_id"] = container_id
        return DockerRunResult(stdout="", stderr="", returncode=0, duration_ms=5)

    with patch.object(docker, "_docker_binary", return_value="docker"):
        with patch("infrastructure.execution.docker_executor.Path.exists", return_value=True):
            with patch.object(docker, "_use_warm_runners", return_value=True):
                with patch.object(docker, "_find_warm_runner_container", return_value="warm123456"):
                    with patch.object(docker, "_exec_in_container", side_effect=fake_exec):
                        with patch.object(docker, "_maybe_recycle_warm_runner"):
                            docker.run_raw_shell("csharp_runner", "echo ping")

    assert seen.get("mode") == "exec"
    assert seen.get("container_id") == "warm123456"


def test_cold_run_not_used_when_warm_runner_present():
    docker = DockerExecutor()

    with patch.object(docker, "_docker_binary", return_value="docker"):
        with patch("infrastructure.execution.docker_executor.Path.exists", return_value=True):
            with patch.object(docker, "_use_warm_runners", return_value=True):
                with patch.object(docker, "_find_warm_runner_container", return_value="warm999"):
                    with patch.object(
                        docker,
                        "_exec_in_container",
                        return_value=DockerRunResult("", "", 0, 1),
                    ):
                        with patch.object(docker, "_maybe_recycle_warm_runner"):
                            with patch.object(docker, "_run_limited_process") as cold:
                                docker.run_raw_shell("csharp_runner", "echo ping")
                                cold.assert_not_called()
