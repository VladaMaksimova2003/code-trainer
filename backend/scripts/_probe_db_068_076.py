"""Probe current DB state for 068/076."""
import json
import psycopg2

DB = dict(host="localhost", port=5433, dbname="code_trainer",
          user="code_trainer", password="change_me")

conn = psycopg2.connect(**DB)
cur = conn.cursor()
for pid in ("task_068", "task_076"):
    cur.execute(
        """select id, title, description, test_cases,
                  code_examples->>'python', code_examples->>'buggy_python'
           from task where code_examples->'curriculum_showcase'->>'slot_pattern_id'=%s""",
        (pid,),
    )
    r = cur.fetchone()
    print("===", pid, "db_id", r[0])
    print("title:", r[1])
    print("desc:", (r[2] or "")[:200])
    tests = r[3] if isinstance(r[3], list) else json.loads(r[3])
    print("tests:", len(tests))
    for i, t in enumerate(tests, 1):
        print(f"  T{i} in={repr(t.get('inputs',''))} out={repr(t.get('output',''))}")
    print("py head:", (r[4] or "")[:250].replace("\n", "\\n"))
    print("buggy head:", (r[5] or "")[:250].replace("\n", "\\n"))
cur.close()
conn.close()
