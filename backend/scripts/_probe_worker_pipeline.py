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
    import json
    print(json.dumps({
        "success": result.get("success"),
        "pattern_errors": result.get("pattern_errors"),
        "test_count": len(result.get("test_results") or []),
        "failed": sum(1 for t in (result.get("test_results") or []) if t.get("status") != "PASSED"),
    }, ensure_ascii=False, indent=2))
finally:
    db.close()
