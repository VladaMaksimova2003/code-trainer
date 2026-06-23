import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import psycopg2
from import_debug_fixes import norm, run_python

DB = dict(host="localhost", port=5433, dbname="code_trainer",
          user="code_trainer", password="change_me")
TASKS = ["task_015", "task_063", "task_071", "task_079", "task_116", "task_119"]

conn = psycopg2.connect(**DB)
cur = conn.cursor()
for pid in TASKS:
    cur.execute(
        """select id, title, description, test_cases,
                  code_examples->>'python',
                  code_examples->'curriculum_showcase'
           from task where code_examples->'curriculum_showcase'->>'slot_pattern_id'=%s""",
        (pid,),
    )
    r = cur.fetchone()
    tests = r[3] if isinstance(r[3], list) else json.loads(r[3])
    py = r[4] or ""
    showcase = r[5] if isinstance(r[5], dict) else json.loads(r[5])
    ok = 0
    fails = []
    for i, t in enumerate(tests):
        got = norm(run_python(py, t.get("inputs", "")))
        exp = norm(t.get("output", ""))
        if got == exp:
            ok += 1
        else:
            fails.append({"T": i + 1, "exp": t.get("output"), "got": got})
    print("===", pid)
    print("db_id", r[0])
    print("title", r[1])
    print("desc", r[2])
    print("action", showcase.get("primary_action"), "format", showcase.get("task_format"))
    print("tests", len(tests), "validation", f"{ok}/{len(tests)}")
    for t in tests:
        print(" ", repr(t.get("inputs", "")[:60]), "->", repr(t.get("output", "")))
    print("fails", fails)
    print("py_head", py[:200].replace("\n", "\\n"))
cur.close()
conn.close()
