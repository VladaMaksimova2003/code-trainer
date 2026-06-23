import json
import psycopg2
import sys
sys.path.insert(0, ".")
from application.tasks.services.block_reorder_helpers import build_entity_from_db
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal
from infrastructure.db.models.task.task import Task

load_models()
DB = dict(host="localhost", port=5433, dbname="code_trainer", user="code_trainer", password="change_me")

conn = psycopg2.connect(**DB)
cur = conn.cursor()

for tid in (4, 7):
    cur.execute("select test_cases, code_examples from task where id=%s", (tid,))
    tc_raw, ce_raw = cur.fetchone()
    ce = json.loads(ce_raw) if isinstance(ce_raw, str) else ce_raw
    tc = json.loads(tc_raw) if isinstance(tc_raw, str) else tc_raw
    print(f"\n===== TASK {tid} =====")
    print("tests:", [t.get("output") for t in tc])
    for lang in ["pascal", "python"]:
        code = ce.get(lang, "")
        print(f"\n--- {lang} fixed ({len(code)} chars) ---")
        print(code[:500])
        buggy = ce.get(f"buggy_{lang}", "")
        if buggy:
            print(f"\n--- {lang} buggy ---")
            print(buggy[:400])
    print("hints:", ce.get("hints"))
    print("post:", (ce.get("post_solve_explanation") or "")[:120])

# assemble blocks task 4
db = SessionLocal()
task = db.query(Task).filter(Task.id == 4).first()
entity = build_entity_from_db(task)
blocks = entity.blocks if entity else []
print(f"\n===== TASK 4 blocks: {len(blocks)} =====")
if blocks:
    assembled = "\n".join(b.text for b in sorted(blocks, key=lambda x: x.order))
    print(assembled[:600])

db.close()
