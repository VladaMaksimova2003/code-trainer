#!/usr/bin/env python3
import sys
sys.path.insert(0, "/app")
from infrastructure.execution.docker_executor import DockerExecutor
from infrastructure.execution.language_registry import language_registry
from infrastructure.execution.test_strategies import CompileAndRunTestStrategy
from infrastructure.execution.execution_workspace import isolation_shell_prefix
from import_debug_fixes import T004_REF

class CaptureDocker(DockerExecutor):
    last_full: str = ""

    def run_raw_shell(self, image, shell_cmd, timeout=None, stdin=None, *, workspace_id=None, profile=None):
        from infrastructure.execution.execution_workspace import new_workspace_id
        ws_id = workspace_id or new_workspace_id()
        self.last_full = isolation_shell_prefix(ws_id) + shell_cmd
        return super().run_raw_shell(image, shell_cmd, timeout=timeout, stdin=stdin, workspace_id=ws_id, profile=profile)

docker = CaptureDocker()
strat = CompileAndRunTestStrategy(docker)
cfg = language_registry.get_or_raise("csharp")
code = T004_REF["csharp"]
tests = [{"inputs": "5\n100\n-20\n0\n50\n-1\n", "output": "2"}]
strat.run(cfg, code, tests)
open("/tmp/csharp_cmd.txt", "w").write(docker.last_full)
print("written", len(docker.last_full))
