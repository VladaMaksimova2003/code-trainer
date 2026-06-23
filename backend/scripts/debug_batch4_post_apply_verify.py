"""Post-apply verification for debug import Batch 4 (task_012, task_020)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

import psycopg2

SCRIPTS = Path(__file__).resolve().parent
BACKEND = SCRIPTS.parent
sys.path.insert(0, str(BACKEND))

DB = dict(host="localhost", port=5433, dbname="code_trainer", user="code_trainer", password="change_me")
API = os.environ.get("MPLT_API", "http://127.0.0.1:9000")
PATTERNS = ["task_012", "task_020"]


def norm(s: str) -> str:
    return "\n".join(l.rstrip() for l in str(s).strip().splitlines()).strip()


def run_python(code: str, inp: str) -> str:
    wd = tempfile.mkdtemp()
    sf = os.path.join(wd, "s.py")
    Path(sf).write_text(code, encoding="utf-8")
    r = subprocess.run([sys.executable, sf], input=inp, capture_output=True, text=True, timeout=8)
    return norm(r.stdout)


def validate_code(code: str, tests: list) -> tuple[int, int, list[str]]:
    ok = 0
    notes: list[str] = []
    for i, tc in enumerate(tests):
        got = run_python(code, tc.get("inputs", ""))
        if got == norm(tc.get("output", "")):
            ok += 1
        else:
            notes.append(f"T{i+1}")
    return ok, len(tests), notes


def fetch_api(db_id: int) -> dict:
    url = f"{API}/tasks/{db_id}?learning_language=pascal"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    report: dict = {"patterns": {}, "canon_notes": {
        "t5_removed": "placeholder 3\\n1\\n2\\n3\\n→6 removed from both tasks",
        "task_012_canon": "valid/invalid output",
        "task_020_canon": "read-until-zero I/O",
    }}
    for pid in PATTERNS:
        cur.execute(
            """select id, title, description, test_cases, code_examples
               from task where code_examples->'curriculum_showcase'->>'slot_pattern_id'=%s""",
            (pid,),
        )
        row = cur.fetchone()
        if not row:
            report["patterns"][pid] = {"error": "not found"}
            continue
        did, title, desc, tests, ce = row
        if isinstance(tests, str):
            tests = json.loads(tests)
        if isinstance(ce, str):
            ce = json.loads(ce)
        showcase = ce.get("curriculum_showcase") or {}
        py_fixed = str(ce.get("python") or "")
        py_buggy = str(ce.get("buggy_python") or "")
        f_ok, f_total, _ = validate_code(py_fixed, tests or [])
        b_ok, b_total, b_pass = validate_code(py_buggy, tests or [])
        buggy_fail = b_total - b_ok
        api = {}
        try:
            api = fetch_api(did)
        except Exception as exc:
            api = {"error": str(exc)}
        api_ce = api.get("code_examples") or {} if isinstance(api, dict) else {}
        report["patterns"][pid] = {
            "db_id": did,
            "title": title,
            "title_has_chapter_prefix": title.strip().startswith("["),
            "tests_count": len(tests or []),
            "fixed_validation": f"{f_ok}/{f_total}",
            "buggy_validation": f"{buggy_fail}/{b_total} fail",
            "buggy_pass_tests": b_pass,
            "hints_top_level": api.get("hints") or ce.get("hints"),
            "hints_count": len(api.get("hints") or ce.get("hints") or []),
            "post_solve_top_level": bool(
                api.get("post_solve_explanation") or ce.get("post_solve_explanation")
            ),
            "buggy_pascal_present": bool(ce.get("buggy_pascal")),
            "buggy_python_present": bool(ce.get("buggy_python")),
            "teacher_override": bool(ce.get("teacher_assembly_override")),
            "pattern_id": showcase.get("slot_pattern_id"),
            "primary_action": showcase.get("primary_action"),
            "task_format": showcase.get("task_format"),
            "public_payload": {
                "title": api.get("title"),
                "tests_count": len(api.get("test_cases") or []),
                "hints": api.get("hints"),
                "post_solve": (api.get("post_solve_explanation") or "")[:80],
                "buggy_pascal_head": "\n".join(str(api_ce.get("buggy_pascal") or "").splitlines()[:3]),
                "action": (api.get("curriculum") or {}).get("action"),
                "format": (api.get("curriculum") or {}).get("task_format"),
            },
        }
    cur.close()
    conn.close()
    out = BACKEND.parent / "docs" / "debug_import_batch4_итог.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
