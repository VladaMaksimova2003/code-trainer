"""Read-only bucket C conflict audit (no DB writes)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import psycopg2

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from algo_v128_catalog import ALGO_SYNTAX_META, _TASK_INDEX  # noqa: E402
from import_debug_fixes import norm, run_python  # noqa: E402
from v128_test_suites_corrections import V128_TEST_CORRECTIONS  # noqa: E402
from v128_test_suites_data import V128_TEST_SUITES  # noqa: E402

DB = dict(host="localhost", port=5433, dbname="code_trainer",
          user="code_trainer", password="change_me")

TASKS = ["task_015", "task_063", "task_071", "task_079", "task_116", "task_119"]

USER_CODE = {
    "task_015": SCRIPTS / "ch2_user_codes" / "task_015.py",
    "task_063": SCRIPTS / "ch8_user_codes" / "task_063.py",
    "task_071": SCRIPTS / "ch9_user_codes" / "task_071.py",
    "task_079": SCRIPTS / "ch10_user_codes" / "task_079.py",
    "task_116": SCRIPTS / "ch15_user_codes" / "task_116.py",
    "task_119": SCRIPTS / "ch15_user_codes" / "task_119.py",
}

PAYLOAD_MODULES = {
    "task_015": "branches_ch2_user_payload",
    "task_063": "search_sort_ch8_user_payload",
    "task_071": "aggregation_ch9_user_payload",
    "task_079": "maps_ch10_user_payload",
    "task_116": "oop_ch15_user_payload",
    "task_119": "oop_ch15_user_payload",
}


def catalog_entry(pid: str) -> dict:
    row = next((e for e in _TASK_INDEX if e.get("pattern_id") == pid), {})
    meta = ALGO_SYNTAX_META.get(pid) or {}
    return {
        "catalog_title": row.get("title"),
        "catalog_goal": row.get("goal"),
        "catalog_action": row.get("action"),
        "catalog_format_ru": row.get("format_ru"),
        "meta_raw_title": meta.get("raw_title"),
        "meta_title": meta.get("title"),
        "meta_short_goal": meta.get("short_goal"),
        "meta_detailed_description": meta.get("detailed_description"),
        "meta_action": meta.get("action"),
        "meta_format_ru": meta.get("format_ru"),
        "meta_test_cases": meta.get("test_cases"),
    }


def load_user_python(path: Path) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    if "PYTHON = " in text:
        start = text.index('PYTHON = """') + len('PYTHON = """')
        end = text.index('"""', start)
        return text[start:end]
    return text[:500]


def load_payload_meta(module_name: str, pid: str) -> dict | None:
    try:
        mod = __import__(module_name)
        payloads = getattr(mod, "USER_PAYLOADS", None) or getattr(mod, "PAYLOADS", None)
        if isinstance(payloads, dict) and pid in payloads:
            return payloads[pid]
        titles = getattr(mod, "TASK_TITLES", None) or getattr(mod, "META", None)
        if isinstance(titles, dict) and pid in titles:
            return titles[pid]
    except Exception as exc:
        return {"error": str(exc)}
    return None


def validate_py(code: str, tests: list) -> dict:
    if not code.strip():
        return {"fixed_validation": "n/a", "per_test": []}
    ok = 0
    per = []
    for i, tc in enumerate(tests or []):
        inp = tc.get("inputs", "")
        exp = tc.get("output", "")
        try:
            got = run_python(code, inp)
        except Exception as exc:
            got = f"ERR:{exc}"
        match = norm(got) == norm(exp)
        if match:
            ok += 1
        per.append({
            "test": f"T{i+1}",
            "expected": exp,
            "got": norm(got),
            "ok": match,
            "inputs_preview": repr(inp[:80]),
        })
    return {
        "fixed_validation": f"{ok}/{len(tests or [])}",
        "per_test": per,
    }


def main() -> None:
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    report = {}
    for pid in TASKS:
        cur.execute(
            """select id, title, description, test_cases, code_examples
               from task where code_examples->'curriculum_showcase'->>'slot_pattern_id'=%s""",
            (pid,),
        )
        row = cur.fetchone()
        if not row:
            report[pid] = {"error": "not in DB"}
            continue
        did, title, desc, tests, ce = row
        if isinstance(tests, str):
            tests = json.loads(tests)
        if isinstance(ce, str):
            ce = json.loads(ce)
        showcase = ce.get("curriculum_showcase") or {}
        py_db = str(ce.get("python") or "")
        user_py = load_user_python(USER_CODE[pid])
        payload = load_payload_meta(PAYLOAD_MODULES[pid], pid)
        v128_data = V128_TEST_SUITES.get(pid)
        v128_corr = V128_TEST_CORRECTIONS.get(pid)
        cat = catalog_entry(pid)
        report[pid] = {
            "db_id": did,
            "slot_identity": {
                "pattern_id": pid,
                "title": title,
                "description": desc,
                "primary_action": showcase.get("primary_action"),
                "task_format": showcase.get("task_format"),
            },
            "catalog": cat,
            "db_tests": tests,
            "db_code_python_head": py_db[:400].replace("\n", "\\n"),
            "db_code_validation": validate_py(py_db, tests),
            "user_code_python_head": user_py[:400].replace("\n", "\\n"),
            "user_code_validation": validate_py(user_py, tests),
            "v128_test_suites_data": v128_data,
            "v128_test_suites_corrections": v128_corr,
            "user_payload_meta": payload,
        }
    cur.close()
    conn.close()
    out = SCRIPTS.parent.parent / "docs" / "_bucket_c_audit_raw.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
