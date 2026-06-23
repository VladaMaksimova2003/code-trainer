import re

from domain.entities.language import DockerConfig, LanguageConfig, LanguageFeature, TestConfig
from infrastructure.execution.docker_executor import DockerExecutor, DockerRunResult
from infrastructure.execution.test_strategies import CompileAndRunTestStrategy

APP_IN_WORKSPACE_RE = re.compile(r"\| /tmp/home/[a-f0-9]{16}/app")
APP_NOT_FOUND = "/tmp/home/app: not found"


class _FakeDocker(DockerExecutor):
    def __init__(self) -> None:
        self.last_shell_cmd: str | None = None

    def run_raw_shell(
        self,
        image,
        shell_cmd,
        timeout=None,
        stdin=None,
        workspace_id=None,
        profile=None,
    ):
        self.last_shell_cmd = shell_cmd
        return DockerRunResult(
            stdout="",
            stderr="source.cpp:1:1: error: expected unqualified-id",
            returncode=1,
            duration_ms=50,
            workspace_id=workspace_id or "",
        )


def _cfg() -> LanguageConfig:
    return LanguageConfig(
        id="cpp",
        label="C++",
        file_extension=".cpp",
        supported_features=frozenset({LanguageFeature.TEST}),
        docker=DockerConfig(
            image="cpp_runner",
            compile="g++ -std=c++17 {filename} -o {binary} 2>&1",
        ),
        test=TestConfig(
            strategy="compile_and_run",
            compile_once=True,
            timeout_seconds=2,
            compile=("g++", "{source}", "-o", "{binary}"),
        ),
    )


def test_compile_once_batch_uses_and_chain_and_skips_run_on_compile_failure():
    docker = _FakeDocker()
    strategy = CompileAndRunTestStrategy(docker)
    broken = "#include <iostream>\nint main() { broken"
    test_cases = [{"inputs": "1 2 3", "output": "5"}]

    results = strategy.run(_cfg(), broken, test_cases)

    assert docker.last_shell_cmd is not None
    assert "; " not in docker.last_shell_cmd
    assert " && " in docker.last_shell_cmd
    assert APP_IN_WORKSPACE_RE.search(docker.last_shell_cmd)
    assert results[0].status == "ERROR"
    assert "error" in results[0].message.lower()
    assert APP_NOT_FOUND not in results[0].actual
    assert APP_NOT_FOUND not in results[0].message
