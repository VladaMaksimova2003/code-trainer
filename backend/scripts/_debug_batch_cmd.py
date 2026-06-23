import subprocess

script = r"""
from infrastructure.execution.language_registry import language_registry
from infrastructure.execution.execution_workspace import source_path, binary_path, new_workspace_id, isolation_shell_prefix
from infrastructure.execution.test_strategies import CompileAndRunTestStrategy
import base64
cfg = language_registry.get_or_raise('csharp')
ws = new_workspace_id()
cp = source_path(ws, cfg.file_extension)
bp = binary_path(ws)
strat = CompileAndRunTestStrategy(docker=None)
run_cmd = strat._format_one_shot(cfg, cp, bp)
code_b64 = base64.b64encode(b'int x=0;').decode('ascii')
steps = [f'echo {code_b64} | base64 -d > {cp}', f'echo CASE1', run_cmd]
shell_cmd = ' && '.join(steps)
full = isolation_shell_prefix(ws) + shell_cmd
print('PREFIX:', isolation_shell_prefix(ws))
print('RUN_CMD:', run_cmd[:150])
print('FULL_HEAD:', full[:350])
"""
subprocess.run(["docker", "exec", "code_trainer_dev-worker-1", "python", "-c", script])
