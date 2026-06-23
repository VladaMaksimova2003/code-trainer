from infrastructure.execution.execution_workspace import source_path, binary_path, new_workspace_id
from infrastructure.execution.language_registry import language_registry

cfg = language_registry.get_or_raise("csharp")
ws = new_workspace_id()
cp = source_path(ws, cfg.file_extension)
bp = binary_path(ws)
cmd = cfg.test.docker_one_shot.format(filename=cp, source=cp, binary=bp, output=bp)
print(cmd)
