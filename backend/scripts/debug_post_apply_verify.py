"""Post-apply verification for debug import task_004 / task_007."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import urllib.request

import psycopg2

DB = dict(host="localhost", port=5433, dbname="code_trainer",
          user="code_trainer", password="change_me")
API = os.environ.get("MPLT_API", "http://127.0.0.1:9000")

CASES = {
    "task_004": {"db_id": 5, "pattern": "task_004"},
    "task_007": {"db_id": 6, "pattern": "task_007"},
}


def norm(s: str) -> str:
    return "\n".join(l.rstrip() for l in str(s).strip().splitlines()).strip()


def run_python(code: str, inp: str) -> str:
    wd = tempfile.mkdtemp()
    sf = os.path.join(wd, "s.py")
    open(sf, "w", encoding="utf-8").write(code)
    r = subprocess.run([sys.executable, sf], input=inp, capture_output=True, text=True, timeout=8)
    return norm(r.stdout)


def validate_code(code: str, tests: list) -> tuple[int, int]:
    ok = 0
    for tc in tests:
        if run_python(code, tc["inputs"]) == norm(tc["output"]):
            ok += 1
    return ok, len(tests)


def fetch_api(db_id: int) -> dict:
    url = f"{API}/tasks/{db_id}?learning_language=pascal"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    report = {}

    for pid, meta in CASES.items():
        cur.execute(
            """select id, title, description, test_cases, code_examples
               from task where code_examples->'curriculum_showcase'->>'slot_pattern_id'=%s""",
            (pid,),
        )
        row = cur.fetchone()
        if not row:
            report[pid] = {"error": "not found"}
            continue
        did, title, desc, tests, ce = row
        if isinstance(ce, str):
            ce = json.loads(ce)
        if isinstance(tests, str):
            tests = json.loads(tests)
        showcase = ce.get("curriculum_showcase") or {}

        py_fixed = ce.get("python") or ""
        py_buggy = ce.get("buggy_python") or ""
        fixed_ok, fixed_total = validate_code(py_fixed, tests)
        buggy_ok, buggy_total = validate_code(py_buggy, tests)

        api = {}
        try:
            payload = fetch_api(did)
            curriculum = payload.get("curriculum") or {}
            transfer = payload.get("transfer") or curriculum.get("transfer") or {}
            ce_api = payload.get("code_examples") or {}
            tests_top = payload.get("test_cases") or []
            api = {
                "title": payload.get("title") or curriculum.get("title"),
                "pattern_id": (ce.get("curriculum_showcase") or {}).get("slot_pattern_id"),
                "primary_action": (ce.get("curriculum_showcase") or {}).get("primary_action"),
                "task_format": (ce.get("curriculum_showcase") or {}).get("task_format"),
                "buggy_pascal_in_curriculum": bool(curriculum.get("buggy_pascal")),
                "buggy_pascal_head": (curriculum.get("buggy_pascal") or "")[:120],
                "tests_count": len(tests_top),
                "first_test": tests_top[0] if tests_top else None,
                "hints_in_code_examples": ce_api.get("hints"),
                "post_solve_in_code_examples": ce_api.get("post_solve_explanation"),
                "hints_top_level": payload.get("hints"),
                "post_solve_top_level": payload.get("post_solve_explanation"),
                "debug_id": transfer.get("debug_id"),
            }
        except Exception as exc:
            api = {"error": str(exc)}

        report[pid] = {
            "db_id": did,
            "title_db": title,
            "title_has_chapter_prefix": title.strip().startswith("["),
            "description_len": len(desc or ""),
            "tests_count": len(tests),
            "test_names": [t.get("name") for t in tests],
            "fixed_validation": f"{fixed_ok}/{fixed_total}",
            "buggy_validation": f"{buggy_ok}/{buggy_total} pass (expect < {fixed_total})",
            "expected_concepts": ce.get("expected_concepts", {}).get("pascal") or showcase.get("expected_concept_ids"),
            "hints_db": ce.get("hints") or showcase.get("hints"),
            "post_solve_db": (ce.get("post_solve_explanation") or showcase.get("post_solve_explanation") or "")[:200],
            "pattern_id": showcase.get("slot_pattern_id"),
            "primary_action": showcase.get("primary_action"),
            "task_format": showcase.get("task_format"),
            "buggy_pascal_head": (ce.get("buggy_pascal") or "")[:150],
            "fixed_pascal_head": (ce.get("pascal") or "")[:150],
            "api": api,
        }

    cur.close()
    conn.close()
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
