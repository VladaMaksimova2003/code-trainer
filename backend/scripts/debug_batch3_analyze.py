"""Batch 3 debug-import analysis: task_044, task_047, task_052, task_055, task_060."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import psycopg2

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from algo_v128_catalog import ALGO_SYNTAX_META  # noqa: E402
from v128_stage1_overlays import STAGE1_OVERLAYS  # noqa: E402
from v128_test_suites_corrections import V128_TEST_CORRECTIONS  # noqa: E402
from v128_test_suites_data import V128_TEST_SUITES  # noqa: E402

DB = dict(host="localhost", port=5433, dbname="code_trainer",
          user="code_trainer", password="change_me")

BATCH = ["task_044", "task_047", "task_052", "task_055", "task_060"]
LANGS = ["python", "pascal", "cpp", "csharp", "java"]

CHAPTER_MODULE = {
    "task_044": ("ch6_user_codes", "task_044"),
    "task_047": ("ch6_user_codes", "task_047"),
    "task_052": ("ch7_user_codes", "task_052"),
    "task_055": ("ch7_user_codes", "task_055"),
    "task_060": ("ch8_user_codes", "task_060"),
}


def norm(s: str) -> str:
    return "\n".join(l.rstrip() for l in str(s).strip().splitlines()).strip()


def run_python(code: str, inp: str) -> tuple[str, str | None]:
    if not str(code or "").strip():
        return "", "empty code"
    wd = tempfile.mkdtemp()
    sf = os.path.join(wd, "s.py")
    Path(sf).write_text(code, encoding="utf-8")
    try:
        r = subprocess.run(
            [sys.executable, sf],
            input=inp,
            capture_output=True,
            text=True,
            timeout=8,
            cwd=wd,
        )
        if r.returncode != 0:
            return r.stdout, f"exit {r.returncode}: {r.stderr[:180]}"
        return r.stdout, None
    except Exception as exc:
        return "", str(exc)


def validate(code: str, tests: list[dict]) -> dict[str, Any]:
    ok = 0
    notes: list[str] = []
    for i, tc in enumerate(tests):
        got, err = run_python(code, tc["inputs"])
        if err:
            notes.append(f"T{i+1}: {err}")
            continue
        exp = tc.get("output", "")
        if norm(got) == norm(exp):
            ok += 1
        else:
            notes.append(f"T{i+1}: exp={exp!r} got={norm(got)!r}")
    return {"pass": f"{ok}/{len(tests)}", "notes": notes[:6]}


def load_chapter_codes(pattern: str) -> dict[str, dict[str, str]]:
    mod_name, stem = CHAPTER_MODULE[pattern]
    path = SCRIPTS / mod_name / f"{stem}.py"
    spec = importlib.util.spec_from_file_location(stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out: dict[str, dict[str, str]] = {}
    for lang in LANGS:
        fixed = str(getattr(mod, f"FIXED_{lang.upper()}", "") or getattr(mod, lang.upper(), "") or "").strip()
        buggy = str(getattr(mod, f"BUGGY_{lang.upper()}", "") or "").strip()
        out[lang] = {"fixed": fixed, "buggy": buggy}
    return out


def catalog_meta(pattern: str) -> dict[str, Any]:
    base = dict(ALGO_SYNTAX_META.get(pattern) or {})
    overlay = STAGE1_OVERLAYS.get(pattern) or {}
    merged = dict(base)
    for key, val in overlay.items():
        if key == "implementations" and isinstance(val, dict):
            impl = dict(merged.get("implementations") or {})
            for lang, patch in val.items():
                cur = dict(impl.get(lang) or {})
                if isinstance(patch, dict):
                    cur.update(patch)
                impl[lang] = cur
            merged["implementations"] = impl
        elif key == "test_cases" and val:
            merged["test_cases"] = val
        else:
            merged[key] = val
    return merged


def overlay_codes(meta: dict) -> dict[str, dict[str, str]]:
    impls = meta.get("implementations") or {}
    out: dict[str, dict[str, str]] = {}
    for lang in LANGS:
        impl = impls.get(lang) or {}
        out[lang] = {
            "fixed": str(impl.get("fixed_code") or (meta.get("reference_codes") or {}).get(lang) or "").strip(),
            "buggy": str(impl.get("buggy_code") or "").strip(),
        }
    return out


def pick_canon_tests(pattern: str, meta: dict) -> tuple[list[dict], str]:
    corr = V128_TEST_CORRECTIONS.get(pattern)
    if corr:
        return [dict(t) for t in corr], "v128_test_suites_corrections"
    v128 = V128_TEST_SUITES.get(pattern) or []
    if v128:
        return [dict(t) for t in v128], "v128_test_suites_data"
    return [dict(t) for t in (meta.get("test_cases") or [])], "algo_v128_catalog"


def detect_conflicts(pattern: str, meta: dict, chapter: dict, tests: list[dict], tests_source: str) -> list[str]:
    conflicts: list[str] = []
    raw = str(meta.get("raw_title") or meta.get("title") or "")
    goal = str(meta.get("short_goal") or meta.get("detailed_description") or "")

    cat_tests = meta.get("test_cases") or []
    if cat_tests and any("19" in str(t.get("output", "")) for t in cat_tests[:3]):
        conflicts.append("algo_v128_catalog.test_cases — placeholder (сумма массива), не алгоритм задачи")

    v128_raw = V128_TEST_SUITES.get(pattern) or []
    corr = V128_TEST_CORRECTIONS.get(pattern)
    if corr and v128_raw and norm(json.dumps(v128_raw[:1], ensure_ascii=False)) != norm(json.dumps(corr[:1], ensure_ascii=False)):
        conflicts.append(
            f"v128_test_suites_data vs corrections: "
            f"raw T1 out={v128_raw[0].get('output')!r} vs corr T1 out={corr[0].get('output')!r}"
        )

    ch_fixed = chapter["python"]["fixed"]
    if pattern == "task_044":
        if "normalize" in ch_fixed.lower() or "Normalize" in ch_fixed:
            conflicts.append("ch6_user_codes — normalize/trim, не power")
        if "нормализа" in raw.lower() and "степен" in goal.lower():
            conflicts.append(f"raw_title «{raw}» vs catalog goal «{goal[:60]}…»")
        if tests_source == "v128_test_suites_corrections" and "hello" in str(v128_raw[0].get("output", "")):
            conflicts.append("corrections=power, v128_data=string normalize — нужен выбор канона")

    if pattern == "task_047":
        if "arraysum" in ch_fixed.lower() or "ArraySum" in ch_fixed:
            conflicts.append("ch6_user_codes — ArraySum, catalog goal min/max двух чисел")
        if v128_raw and str(v128_raw[0].get("output")) == "24":
            conflicts.append("v128_test_suites_data — сумма массива (24), не min max пары")
        if "5 5" in str(v128_raw):
            conflicts.append("v128_test_suites_data — тест all_equal «5 5» не согласован с суммой массива")

    if pattern == "task_052":
        if "fast_power" in ch_fixed.lower() or "FastPower" in ch_fixed:
            conflicts.append("ch7_user_codes — FastPower, catalog goal рекурсивный reverse строки")
        if v128_raw and str(v128_raw[0].get("output")) == "1024":
            conflicts.append("v128_test_suites_data — power (1024), catalog goal reverse string")
        rev_053 = V128_TEST_SUITES.get("task_053") or []
        if rev_053 and str(rev_053[0].get("output")) == "olleh":
            conflicts.append("task_053 v128 — string reverse (olleh); возможная перестановка 052↔053")

    if pattern == "task_055":
        if "quicksort" not in ch_fixed.lower() and "QuickSort" not in chapter["pascal"]["fixed"]:
            conflicts.append("chapter fixed не quicksort")

    if pattern == "task_060":
        corrupt = sum(1 for lang in LANGS if chapter[lang]["buggy"] and "Console." in chapter[lang]["buggy"])
        if corrupt >= 3:
            conflicts.append(f"ch8 BUGGY — синтаксический мусор в {corrupt}/5 языках (ожидаемо для debug)")

    return conflicts


def score_sources(chapter: dict, overlay: dict, tests: list[dict]) -> dict[str, Any]:
    candidates: list[tuple[str, str, str]] = [
        ("overlay", overlay["python"]["fixed"], overlay["python"]["buggy"]),
        ("chapter", chapter["python"]["fixed"], chapter["python"]["buggy"]),
    ]
    best = {"name": "none", "fixed": "", "buggy": "", "fixed_val": {"pass": "0/0"}, "buggy_val": {"pass": "0/0"}}
    for name, fixed, buggy in candidates:
        if not fixed:
            continue
        fv = validate(fixed, tests)
        fv_ok = fv["pass"].split("/")[0] == str(len(tests))
        if fv_ok:
            bv = validate(buggy, tests) if buggy else {"pass": "n/a", "notes": ["no buggy"]}
            best = {"name": name, "fixed": fixed, "buggy": buggy, "fixed_val": fv, "buggy_val": bv}
            break
    if best["name"] == "none":
        for name, fixed, buggy in candidates:
            if fixed:
                fv = validate(fixed, tests)
                bv = validate(buggy, tests) if buggy else {"pass": "n/a", "notes": ["no buggy"]}
                best = {"name": name, "fixed": fixed, "buggy": buggy, "fixed_val": fv, "buggy_val": bv}
    return best


def classify(pattern: str, conflicts: list[str], best: dict, chapter: dict) -> str:
    n = len(best["fixed_val"]["pass"].split("/")[-1]) if "/" in best["fixed_val"]["pass"] else 0
    ok = best["fixed_val"]["pass"].split("/")[0] == str(n) and n > 0
    canon_conflicts = [c for c in conflicts if "placeholder" not in c.lower() and "BUGGY — синтаксический" not in c]
    if pattern in {"task_044", "task_047", "task_052"}:
        return "damaged" if len(canon_conflicts) >= 2 else "unresolved"
    if ok and pattern in {"task_055", "task_060"}:
        return "clean"
    if ok:
        return "clean"
    return "damaged"


def db_row(pattern: str) -> dict | None:
    try:
        conn = psycopg2.connect(**DB)
        cur = conn.cursor()
        cur.execute(
            """select id, title, description, test_cases, code_examples
               from task where code_examples->'curriculum_showcase'->>'slot_pattern_id'=%s""",
            (pattern,),
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return None
        did, title, desc, tests, ce = row
        if isinstance(ce, str):
            ce = json.loads(ce)
        if isinstance(tests, str):
            tests = json.loads(tests)
        return {
            "db_id": did,
            "title": title,
            "description": (desc or "")[:160],
            "tests_n": len(tests or []),
            "hints_db": (ce or {}).get("hints"),
            "post_solve_db": (ce or {}).get("post_solve_explanation"),
        }
    except Exception as exc:
        return {"error": str(exc)}


def analyze(pattern: str) -> dict:
    meta = catalog_meta(pattern)
    chapter = load_chapter_codes(pattern)
    overlay = overlay_codes(meta)
    tests, tests_source = pick_canon_tests(pattern, meta)
    conflicts = detect_conflicts(pattern, meta, chapter, tests, tests_source)
    best = score_sources(chapter, overlay, tests)
    status = classify(pattern, conflicts, best, chapter)
    return {
        "pattern_id": pattern,
        "status": status,
        "db": db_row(pattern),
        "catalog_title": meta.get("title"),
        "catalog_raw_title": meta.get("raw_title"),
        "catalog_goal": meta.get("short_goal") or meta.get("detailed_description"),
        "canon_algorithm_note": "catalog goal unless user confirms other canon",
        "source_conflicts": conflicts,
        "tests_source": tests_source,
        "tests": tests,
        "fixed_validation_python": best["fixed_val"],
        "buggy_validation_python": best["buggy_val"],
        "validation_code_source": best["name"],
        "expected_concepts_pascal": (meta.get("expected_concepts") or {}).get("pascal"),
    }


def main() -> None:
    report = [analyze(pid) for pid in BATCH]
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
