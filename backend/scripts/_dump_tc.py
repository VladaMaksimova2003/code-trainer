import json
import psycopg2

c = psycopg2.connect(host="localhost", port=5433, dbname="code_trainer", user="code_trainer", password="change_me")
cur = c.cursor()
for tid in (4, 7):
    cur.execute("select test_cases, code_examples from task where id=%s", (tid,))
    tc, ce = cur.fetchone()
    tc = json.loads(tc) if isinstance(tc, str) else tc
    ce = json.loads(ce) if isinstance(ce, str) else ce
    print("TASK", tid)
    for t in tc:
        print(" ", t)
    print("cpp head:", (ce.get("cpp") or "")[:200].replace("\n", "\\n"))
    print()
