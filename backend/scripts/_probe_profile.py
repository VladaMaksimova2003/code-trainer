import sys
sys.path.insert(0, "/app")
from infrastructure.db.models.task.registry import load_models
load_models()
from infrastructure.db.session import SessionLocal
from application.tasks.services.catalog.task_catalog_orchestrator import get_task_pattern_key
from application.curriculum.display.mplt_submit_profile import resolve_mplt_submit_profile
from application.curriculum.display.transfer_pitfall_detector import detect_transfer_pitfalls

load_models()
db = SessionLocal()
for tid in [2,4,5,7,28]:
    pk = get_task_pattern_key(db, tid)
    prof = resolve_mplt_submit_profile(db, tid, submission_language="pascal")
    print("task", tid, "pattern", pk, "dominant", prof.dominant_pitfall_id if prof else None, "debug", prof.debug_id if prof else None)
db.close()

code = """var total, n: integer; begin readln(n); total := 10; writeln(total / n); end."""
hits = detect_transfer_pitfalls(pitfall_id="integer_division", transfer_type="FCC", source_language="python", target_language="pascal", code=code, test_results=[{"status":"FAILED"}], buggy_code="")
print("FCC hits", hits)
