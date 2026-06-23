import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import psycopg2
from import_debug_fixes import norm, run_python
from v128_test_suites_data import V128_TEST_SUITES

DB = dict(host="localhost", port=5433, dbname="code_trainer",
          user="code_trainer", password="change_me")

conn = psycopg2.connect(**DB)
cur = conn.cursor()
for pid in ["task_063", "task_071", "task_116", "task_119"]:
    cur.execute("select code_examples->>'python' from task where code_examples->'curriculum_showcase'->>'slot_pattern_id'=%s", (pid,))
    py = cur.fetchone()[0] or ""
    tests = V128_TEST_SUITES.get(pid, [])
    ok = 0
    for i, t in enumerate(tests):
        got = norm(run_python(py, t["inputs"]))
        if got == norm(t["output"]):
            ok += 1
        else:
            print(pid, "v128data T", i+1, "FAIL", repr(t["output"][:40]), "got", repr(got[:40]))
    print(pid, "DB code vs v128_data:", ok, "/", len(tests))
cur.close(); conn.close()
