import re

from domain.entities.language import DockerConfig, LanguageConfig, LanguageFeature, TestConfig
from infrastructure.execution.docker_executor import DockerExecutor, DockerRunResult
from infrastructure.execution.test_strategies import CompileAndRunTestStrategy

DOTNET_ONE_SHOT = (
    'ws="$CT_WORKSPACE" && rm -rf "$ws/app" && cp -a /runner/template/. "$ws/app/" && '
    'cp {source} "$ws/app/Program.cs" && cd "$ws/app" && '
    "DOTNET_NOLOGO=1 dotnet build --no-restore -v q >/dev/null 2>&1 && "
    "DOTNET_NOLOGO=1 dotnet run --no-build -v q --no-launch-profile"
)


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
            stdout="__CT_CASE_1__\nEven\n__CT_CASE_2__\nOdd\n",
            stderr="",
            returncode=0,
            duration_ms=1200,
            workspace_id=workspace_id or "",
        )

    def _find_warm_runner_container(self, image):
        return "warm123"


def _cfg() -> LanguageConfig:
    return LanguageConfig(
        id="csharp",
        label="C#",
        file_extension=".cs",
        supported_features=frozenset({LanguageFeature.TEST}),
        docker=DockerConfig(
            image="csharp_runner",
            run=DOTNET_ONE_SHOT.format(source="{filename}", filename="{filename}"),
        ),
        test=TestConfig(
            strategy="compile_and_run",
            batch_one_shot=True,
            timeout_seconds=15,
            docker_one_shot=DOTNET_ONE_SHOT,
        ),
    )


def test_batch_one_shot_writes_once_and_runs_all_cases_in_one_exec():
    docker = _FakeDocker()
    strategy = CompileAndRunTestStrategy(docker)
    code = 'Console.WriteLine("x");'
    test_cases = [{"inputs": "4", "output": "Even"}, {"inputs": "7", "output": "Odd"}]

    results = strategy.run(_cfg(), code, test_cases)

    assert docker.last_shell_cmd is not None
    assert re.search(r"base64 -d > /tmp/home/[a-f0-9]{16}/source\.cs", docker.last_shell_cmd)
    assert docker.last_shell_cmd.count("dotnet run --no-build") == 2
    assert "/runner/template" in docker.last_shell_cmd
    assert "__CT_CASE_1__" in docker.last_shell_cmd
    assert "__CT_CASE_2__" in docker.last_shell_cmd
    assert '> "$CT_WORKSPACE/.stdin"' in docker.last_shell_cmd
    assert "| ws=" not in docker.last_shell_cmd
    assert [row.status for row in results] == ["PASSED", "PASSED"]
