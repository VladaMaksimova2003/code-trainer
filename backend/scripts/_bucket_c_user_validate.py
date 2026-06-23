"""Validate ch*_user_codes fixed python vs DB tests."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import psycopg2
from import_debug_fixes import norm, run_python

DB = dict(host="localhost", port=5433, dbname="code_trainer",
          user="code_trainer", password="change_me")

SOURCES = {
    "task_015": ("ch2_user_codes.task_015", "FIXED_PYTHON"),
    "task_063": ("ch8_user_codes.task_063", "PYTHON"),
    "task_071": ("ch9_user_codes.task_071", "FIXED_PYTHON"),
    "task_079": ("ch10_user_codes.task_079", "FIXED_PYTHON"),
    "task_116": ("ch15_user_codes.task_116", "FIXED_PYTHON"),
    "task_119": ("ch15_user_codes.task_119", "PYTHON"),
}

conn = psycopg2.connect(**DB)
cur = conn.cursor()
for pid, (mod_name, attr) in SOURCES.items():
    mod = __import__(mod_name, fromlist=[attr])
    code = getattr(mod, attr)
    cur.execute(
        "select test_cases from task where code_examples->'curriculum_showcase'->>'slot_pattern_id'=%s",
        (pid,),
    )
    tests = cur.fetchone()[0]
    if isinstance(tests, str):
        tests = json.loads(tests)
    ok = 0
    for i, t in enumerate(tests):
        got = norm(run_python(code, t.get("inputs", "")))
        if got == norm(t.get("output", "")):
            ok += 1
        else:
            print(pid, "user T", i + 1, "FAIL exp", repr(t.get("output")), "got", repr(got))
    print(pid, "user_code vs DB tests:", ok, "/", len(tests))
cur.close()
conn.close()
