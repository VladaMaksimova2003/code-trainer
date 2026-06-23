#!/usr/bin/env python3
"""Run C# batch inside worker with command capture."""
import sys
from pathlib import Path

sys.path.insert(0, "/app")
from infrastructure.execution.docker_executor import DockerExecutor, DockerRunResult
from infrastructure.execution.language_registry import language_registry
from infrastructure.execution.test_strategies import CompileAndRunTestStrategy
from import_debug_fixes import T004_REF

class CaptureDocker(DockerExecutor):
    last_cmd: str = ""

    def run_raw_shell(self, image, shell_cmd, timeout=None, stdin=None, *, workspace_id=None, profile=None):
        from infrastructure.execution.execution_workspace import isolation_shell_prefix, new_workspace_id
        ws_id = workspace_id or new_workspace_id()
        self.last_cmd = isolation_shell_prefix(ws_id) + shell_cmd
        print("=== FULL CMD (first 500) ===")
        print(self.last_cmd[:500])
        print("=== CT_WORKSPACE in cmd ===", "CT_WORKSPACE=" in self.last_cmd)
        print("=== ws=CT in cmd ===", 'ws="$CT_WORKSPACE"' in self.last_cmd)
        return super().run_raw_shell(image, shell_cmd, timeout=timeout, stdin=stdin, workspace_id=ws_id, profile=profile)

docker = CaptureDocker()
strat = CompileAndRunTestStrategy(docker)
cfg = language_registry.get_or_raise("csharp")
code = T004_REF["csharp"]
tests = [{"inputs": "5\n100\n-20\n0\n50\n-1\n", "output": "2"}]
results = strat.run(cfg, code, tests)
print("results:", [(r.status, r.message[:80] if r.message else "") for r in results])
