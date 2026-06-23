"""Read-only audit of all v128 debug slots after apply 052/053."""
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import psycopg2

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from algo_v128_catalog import ALGO_SYNTAX_META, _TASK_INDEX  # noqa: E402
from v128_test_suites_data import V128_TEST_SUITES  # noqa: E402

DB = dict(host="localhost", port=5433, dbname="code_trainer",
          user="code_trainer", password="change_me")

CATALOG_DEBUG = [r for r in _TASK_INDEX if r.get("action") == "debug"]
CATALOG_DEBUG_IDS = {r["pattern_id"] for r in CATALOG_DEBUG}

# Tasks written via import_debug_fixes / import_recursion_slot_fixes (confirmed applies)
APPLIED_IMPORT_IDS = {
    "task_004", "task_007",
    "task_023", "task_028", "task_031", "task_036", "task_039",
    "task_044", "task_047", "task_055", "task_060",
    "task_052",
}


def norm(s: str) -> str:
    return "\n".join(l.rstrip() for l in str(s).strip().splitlines()).strip()


def run_python(code: str, inp: str) -> tuple[str, str | None]:
    if not str(code or "").strip():
        return "", "empty"
    wd = tempfile.mkdtemp()
    sf = os.path.join(wd, "s.py")
    Path(sf).write_text(code, encoding="utf-8")
    try:
        r = subprocess.run(
            [sys.executable, sf], input=inp, capture_output=True, text=True, timeout=8, cwd=wd,
        )
        if r.returncode != 0:
            return r.stdout, f"exit {r.returncode}"
        return r.stdout, None
    except Exception as exc:
        return "", str(exc)


def validate_pair(code: str, tests: list) -> dict[str, Any]:
    if not tests:
        return {"pass": "0/0", "ok": 0, "total": 0, "notes": ["no tests"]}
    ok = 0
    notes: list[str] = []
    for i, tc in enumerate(tests):
        got, err = run_python(code, tc.get("inputs", ""))
        if err:
            notes.append(f"T{i+1}:{err[:40]}")
            continue
        if norm(got) == norm(tc.get("output", "")):
            ok += 1
        else:
            notes.append(f"T{i+1}")
    return {"pass": f"{ok}/{len(tests)}", "ok": ok, "total": len(tests), "notes": notes[:3]}


def load_import_overrides() -> set[str]:
    path = SCRIPTS / "import_debug_fixes.py"
    spec = importlib.util.spec_from_file_location("import_debug_fixes", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return set((mod.OVERRIDES or {}).keys()) & CATALOG_DEBUG_IDS


def algo_keywords(goal: str) -> set[str]:
    g = goal.lower()
    keys: set[str] = set()
    rules = [
        (r"степен|power|\^", "power"),
        (r"min|max|миним|максим", "minmax"),
        (r"reverse|разворот", "reverse"),
        (r"palindrome|палиндром", "palindrome"),
        (r"quicksort|quick sort", "quicksort"),
        (r"bubble|пузыр", "bubble"),
        (r"sort|сортир", "sort"),
        (r"сумм|sum", "sum"),
        (r"поиск|search|find", "search"),
        (r"частот|freq|гистограм", "freq"),
        (r"rle|сжати", "rle"),
        (r"положитель|positive", "positive"),
        (r"factorial|факториал", "factorial"),
        (r"merge|слиян", "merge"),
        (r"вставк|insert", "insert"),
        (r"подстрок|substring", "substring"),
    ]
    for pat, tag in rules:
        if re.search(pat, g):
            keys.add(tag)
    return keys


def code_tags(code: str) -> set[str]:
    c = code.lower()
    tags: set[str] = set()
    mapping = {
        "power": ["power", "fastpower", "**", "result *", "result *=", "result +="],
        "minmax": ["minpair", "maxpair", "min(", "max("],
        "reverse": ["reversestring", "reverse_string", "s[-1]"],
        "palindrome": ["ispalindrome", "is_palindrome", "'yes'", '"yes"'],
        "quicksort": ["quicksort", "quick sort", "pivot"],
        "bubble": ["bubble", "a[j] > a[j + 1]", "a[j + 1]"],
        "sort": ["sort("],
        "sum": ["arraysum", "array_sum", "total +="],
        "search": ["find(", "binary", "search"],
        "freq": ["freq[", "histogram"],
        "rle": ["count", "result + s[i]", "rle"],
        "positive": ["amount > 0", "count"],
        "factorial": ["factorial", "solve(n"],
        "merge": ["merge", "two pointer"],
        "insert": ["insert", "pos"],
        "substring": ["find(", "substr", "index"],
    }
    for tag, needles in mapping.items():
        if any(n in c for n in needles):
            tags.add(tag)
    return tags


def test_shape_tags(tests: list) -> set[str]:
    if not tests:
        return set()
    t0 = tests[0]
    inp = str(t0.get("inputs", ""))
    out = str(t0.get("output", ""))
    tags: set[str] = set()
    if re.match(r"^\d+ \d+\n", inp) and out.isdigit():
        tags.add("power")
    if out in {"yes", "no"} or "yes" in out:
        tags.add("palindrome")
    if " " in out.strip() and all(p.isdigit() or (p[0] == "-" and p[1:].isdigit()) for p in out.split() if p):
        if len(out.split()) == 2 and all(x.isdigit() or x.lstrip("-").isdigit() for x in out.split()):
            tags.add("minmax")
        else:
            tags.add("array_out")
    if inp.endswith("\n") and "\n" in inp and not inp.split("\n")[0].strip().isdigit():
        if out.isalpha() or out.islower():
            tags.add("reverse")
    if out.isdigit() and "\n" in inp:
        tags.add("sum")
    return tags


def detect_conflicts(
    pattern: str,
    desc: str,
    goal: str,
    tests: list,
    fixed: str,
    fixed_val: dict,
) -> list[str]:
    conflicts: list[str] = []
    gtags = algo_keywords(desc) | algo_keywords(goal)
    ctags = code_tags(fixed)
    ttags = test_shape_tags(tests)

    if fixed_val["ok"] < fixed_val["total"]:
        conflicts.append("tests ↔ code")

    if gtags and ctags and not (gtags & ctags):
        conflicts.append("description ↔ code")

    if gtags and ttags and not (gtags & ttags):
        conflicts.append("description ↔ tests")

    v128 = V128_TEST_SUITES.get(pattern) or []
    if v128 and tests and norm(json.dumps(v128[:1], ensure_ascii=False)) != norm(json.dumps(tests[:1], ensure_ascii=False)):
        meta = ALGO_SYNTAX_META.get(pattern) or {}
        if gtags and test_shape_tags([{"inputs": v128[0].get("inputs", ""), "output": v128[0].get("output", "")}]):
            if not (gtags & test_shape_tags([{"inputs": v128[0].get("inputs", ""), "output": v128[0].get("output", "")}])):
                pass  # repo v128 differs but DB may be curated

    meta = ALGO_SYNTAX_META.get(pattern) or {}
    raw_title = str(meta.get("raw_title") or "")
    if raw_title and goal and raw_title.lower() not in goal.lower() and goal[:20].lower() not in raw_title.lower():
        if any(w in raw_title.lower() for w in ("матриц", "нормализа", "массив", "fastpower", "разворот")) and pattern in APPLIED_IMPORT_IDS:
            pass
        elif pattern not in APPLIED_IMPORT_IDS:
            if "description ↔ code" not in conflicts and gtags and ctags and not (gtags & ctags):
                conflicts.append("description ↔ code")

    return sorted(set(conflicts))


def classify(
    pattern: str,
    fixed_val: dict,
    buggy_val: dict,
    has_buggy: bool,
    hints_n: int,
    post_solve: bool,
    conflicts: list[str],
    teacher_override: bool,
) -> str:
    fixed_ok = fixed_val["total"] > 0 and fixed_val["ok"] == fixed_val["total"]
    buggy_fail = buggy_val["total"] > 0 and buggy_val["ok"] < buggy_val["total"]
    has_pedagogy = hints_n > 0 and post_solve

    if pattern in APPLIED_IMPORT_IDS and teacher_override and fixed_ok and has_buggy and has_pedagogy:
        if buggy_fail or buggy_val["ok"] < buggy_val["total"]:
            return "applied"

    if len(conflicts) >= 2 or ("description ↔ tests" in conflicts and "description ↔ code" in conflicts):
        return "unresolved"

    if not has_buggy or not fixed_ok:
        return "damaged"

    if not has_pedagogy:
        return "damaged"

    if not buggy_fail and buggy_val["total"] > 0:
        return "damaged"

    if conflicts:
        return "damaged"

    if fixed_ok and has_buggy and buggy_fail and has_pedagogy:
        return "clean"

    return "damaged"


def audit_row(cur, pattern: str, catalog_row: dict) -> dict[str, Any]:
    cur.execute(
        """select id, title, description, test_cases, code_examples
           from task where code_examples->'curriculum_showcase'->>'slot_pattern_id'=%s""",
        (pattern,),
    )
    row = cur.fetchone()
    if not row:
        return {
            "task_id": pattern,
            "title": catalog_row.get("title"),
            "status": "damaged",
            "error": "not in DB",
        }

    did, title, desc, tests, ce = row
    if isinstance(tests, str):
        tests = json.loads(tests)
    if isinstance(ce, str):
        ce = json.loads(ce)
    ce = ce or {}
    showcase = ce.get("curriculum_showcase") or {}

    py_fixed = str(ce.get("python") or "")
    py_buggy = str(ce.get("buggy_python") or "")
    has_buggy = bool(py_buggy.strip()) and bool(ce.get("buggy_pascal"))
    hints = ce.get("hints") or showcase.get("hints") or []
    post_solve = bool(ce.get("post_solve_explanation") or showcase.get("post_solve_explanation"))
    teacher_override = bool(ce.get("teacher_assembly_override"))

    fixed_val = validate_pair(py_fixed, tests or [])
    buggy_val = validate_pair(py_buggy, tests or []) if py_buggy.strip() else {"pass": "n/a", "ok": 0, "total": len(tests or []), "notes": ["no buggy"]}

    goal = str(catalog_row.get("goal") or desc or "")
    conflicts = detect_conflicts(pattern, str(desc or ""), goal, tests or [], py_fixed, fixed_val)
    status = classify(pattern, fixed_val, buggy_val, has_buggy, len(hints), post_solve, conflicts, teacher_override)

    return {
        "task_id": pattern,
        "db_id": did,
        "title": title,
        "status": status,
        "fixed_validation": fixed_val["pass"],
        "buggy_validation": buggy_val["pass"] if py_buggy.strip() else "n/a",
        "tests_count": len(tests or []),
        "hints": len(hints),
        "post_solve": post_solve,
        "has_buggy_split": has_buggy,
        "conflicts": conflicts,
        "teacher_override": teacher_override,
    }


def main() -> None:
    override_ids = load_import_overrides()
    APPLIED_IMPORT_IDS.update(override_ids & CATALOG_DEBUG_IDS)

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    rows = [audit_row(cur, r["pattern_id"], r) for r in sorted(CATALOG_DEBUG, key=lambda x: x["task_num"])]
    cur.close()
    conn.close()

    summary = {
        "total_debug_slots": len(rows),
        "by_status": {},
        "rows": rows,
        "remaining_damaged": [r["task_id"] for r in rows if r["status"] == "damaged"],
        "remaining_unresolved": [r["task_id"] for r in rows if r["status"] == "unresolved"],
        "without_buggy_split": [r["task_id"] for r in rows if not r.get("has_buggy_split")],
        "without_hints_post_solve": [
            r["task_id"] for r in rows
            if r.get("hints", 0) == 0 or not r.get("post_solve")
        ],
        "with_conflicts": [
            {"task_id": r["task_id"], "conflicts": r.get("conflicts") or []}
            for r in rows if r.get("conflicts")
        ],
    }
    for st in ("applied", "clean", "damaged", "unresolved"):
        summary["by_status"][st] = sum(1 for r in rows if r.get("status") == st)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
