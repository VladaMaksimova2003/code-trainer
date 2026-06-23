import sys
sys.path.insert(0, "/app")
from infrastructure.db.models.task.registry import load_models
load_models()
from infrastructure.db.session import SessionLocal
from application.execution.pipeline_runner import WorkerPipelineRunner

code = """var total, n: integer;
begin
  readln(n);
  total := 10;
  writeln(total / n);
end."""

db = SessionLocal()
try:
    runner = WorkerPipelineRunner()
    result = runner.run_submission(4, code, "pascal")
    print("success", result.get("success"))
    print("pattern_errors", result.get("pattern_errors"))
    print("tests", [(t.get("case"), t.get("status")) for t in result.get("test_results") or []])
finally:
    db.close()
