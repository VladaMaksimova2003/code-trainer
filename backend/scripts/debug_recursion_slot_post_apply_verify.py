"""Post-apply verification for recursion slot fix task_052 / task_053."""
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


def norm(s: str) -> str:
    return "\n".join(l.rstrip() for l in str(s).strip().splitlines()).strip()


def run_python(code: str, inp: str) -> tuple[str, str | None]:
    if not str(code or "").strip():
        return "", "empty"
    wd = tempfile.mkdtemp()
    sf = os.path.join(wd, "s.py")
    open(sf, "w", encoding="utf-8").write(code)
    r = subprocess.run([sys.executable, sf], input=inp, capture_output=True, text=True, timeout=8)
    if r.returncode != 0:
        return "", f"exit {r.returncode}"
    return r.stdout, None


def validate(code: str, tests: list) -> tuple[int, int, list[str]]:
    ok = 0
    notes: list[str] = []
    for i, tc in enumerate(tests):
        got, err = run_python(code, tc["inputs"])
        if err:
            notes.append(f"T{i+1}: {err}")
            continue
        if norm(got) == norm(tc["output"]):
            ok += 1
        else:
            notes.append(f"T{i+1}: got={norm(got)!r}")
    return ok, len(tests), notes[:4]


def fetch_api(db_id: int) -> dict:
    url = f"{API}/tasks/{db_id}?learning_language=pascal"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    report = {}

    for pid in ("task_052", "task_053"):
        cur.execute(
            """select t.id, t.title, t.test_cases, t.code_examples,
                      t.code_examples->'curriculum_showcase'->>'primary_action',
                      t.code_examples->'curriculum_showcase'->>'task_format',
                      t.code_examples->'curriculum_showcase'->>'slot_pattern_id'
               from task t
               where t.code_examples->'curriculum_showcase'->>'slot_pattern_id'=%s""",
            (pid,),
        )
        row = cur.fetchone()
        if not row:
            report[pid] = {"error": "not found"}
            continue
        did, title, tests, ce, action, fmt, pattern = row
        if isinstance(tests, str):
            tests = json.loads(tests)
        if isinstance(ce, str):
            ce = json.loads(ce)

        api = {}
        try:
            payload = fetch_api(did)
            curriculum = payload.get("curriculum") or {}
            ce_api = payload.get("code_examples") or {}
            api = {
                "title": payload.get("title"),
                "pattern_id": curriculum.get("slot_pattern_id"),
                "action": curriculum.get("action"),
                "format": curriculum.get("task_format"),
                "tests_count": len(payload.get("test_cases") or []),
                "hints_top_level": payload.get("hints"),
                "hints_count": len(payload.get("hints") or []),
                "post_solve_top_level": bool(payload.get("post_solve_explanation")),
                "post_solve_preview": (payload.get("post_solve_explanation") or "")[:120],
                "buggy_pascal_api": bool(curriculum.get("buggy_pascal") or ce_api.get("buggy_pascal")),
                "buggy_python_api": bool(ce_api.get("buggy_python")),
                "blocks_api_count": len(payload.get("blocks") or []),
            }
        except Exception as exc:
            api = {"error": str(exc)}

        entry = {
            "db_id": did,
            "title": title,
            "title_has_prefix": str(title or "").startswith("["),
            "action": action,
            "format": fmt,
            "pattern_id": pattern,
            "tests_count": len(tests or []),
            "hints_db_count": len(ce.get("hints") or []),
            "post_solve_db": bool(ce.get("post_solve_explanation")),
            "public_payload": api,
        }

        if pid == "task_052":
            py_fixed = ce.get("python") or ""
            py_buggy = ce.get("buggy_python") or ""
            f_ok, f_tot, f_notes = validate(py_fixed, tests)
            b_ok, b_tot, b_notes = validate(py_buggy, tests)
            entry.update({
                "fixed_validation": f"{f_ok}/{f_tot}",
                "fixed_notes": f_notes,
                "buggy_validation_passes": f"{b_ok}/{b_tot}",
                "buggy_notes": b_notes,
                "buggy_pascal_db": bool(ce.get("buggy_pascal")),
                "buggy_python_db": bool(ce.get("buggy_python")),
            })
        else:
            py_ref = ce.get("python") or ""
            r_ok, r_tot, r_notes = validate(py_ref, tests)
            entry["reference_validation"] = f"{r_ok}/{r_tot}"
            entry["reference_notes"] = r_notes

            cur.execute(
                """select br.language, br.blocks, br.correct_order, br.language_variants,
                          br.original_code
                   from block_reorder_task br where br.task_id=%s""",
                (did,),
            )
            br = cur.fetchone()
            if not br:
                entry["block_reorder_task"] = {"error": "MISSING — STOP"}
            else:
                lang, blocks, order, lvars, orig = br
                lvars = lvars if isinstance(lvars, dict) else json.loads(lvars or "{}")
                blocks_counts = {
                    lg: len((lvars.get(lg) or {}).get("blocks") or [])
                    for lg in ["pascal", "python", "cpp", "csharp", "java"]
                }
                orig_head = "\n".join(str(orig or "").splitlines()[:3])
                is_factorial = "factorial" in str(orig or "").lower() or "solve(n" in str(orig or "")
                is_palindrome = "IsPalindrome" in str(orig or "") or "is_palindrome" in str(orig or "")
                entry["block_reorder_task"] = {
                    "language": lang,
                    "pascal_blocks_count": len(blocks or []),
                    "blocks_by_language": blocks_counts,
                    "correct_order_len": len(order or []),
                    "original_code_head": orig_head,
                    "is_still_factorial": is_factorial,
                    "is_palindrome": is_palindrome,
                    "language_variants_keys": list(lvars.keys()),
                }
                if is_factorial or not is_palindrome:
                    entry["block_reorder_task"]["status"] = "PROBLEM — factorial or not palindrome"
                else:
                    entry["block_reorder_task"]["status"] = "OK"

        report[pid] = entry

    cur.close()
    conn.close()
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
