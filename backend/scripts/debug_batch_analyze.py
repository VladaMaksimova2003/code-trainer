"""Analyze debug tasks: canon algorithm, conflicts, test validation."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from algo_v128_catalog import ALGO_SYNTAX_META
from v128_test_suites_data import V128_TEST_SUITES

LANGS = ["python", "pascal", "cpp", "csharp", "java"]


def norm(s: str) -> str:
    return "\n".join(l.rstrip() for l in str(s).strip().splitlines()).strip()


def run_python(code: str, inp: str) -> tuple[str, str | None]:
    if not code.strip():
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
            return r.stdout, f"exit {r.returncode}: {r.stderr[:200]}"
        return r.stdout, None
    except Exception as exc:
        return "", str(exc)


def count_passes(code: str, tests: list[dict]) -> tuple[int, int, list[str]]:
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
            notes.append(f"T{i+1}: exp={tc['output']!r} got={norm(got)!r}")
    return ok, len(tests), notes


def pick_tests(pid: str, meta: dict) -> list[dict]:
    v128 = V128_TEST_SUITES.get(pid) or []
    if v128:
        return v128
    return list(meta.get("test_cases") or [])


def code_sources(meta: dict) -> dict[str, dict[str, str]]:
    impls = meta.get("implementations") or {}
    refs = meta.get("reference_codes") or {}
    out: dict[str, dict[str, str]] = {}
    for lang in LANGS:
        impl = impls.get(lang) or {}
        fixed = str(impl.get("fixed_code") or refs.get(lang) or "").strip()
        buggy = str(impl.get("buggy_code") or "").strip()
        out[lang] = {"fixed": fixed, "buggy": buggy}
    return out


def analyze(pid: str) -> dict:
    meta = dict(ALGO_SYNTAX_META.get(pid) or {})
    tests = pick_tests(pid, meta)
    codes = code_sources(meta)
    py_fixed = codes["python"]["fixed"]
    py_buggy = codes["python"]["buggy"]
    fixed_ok, fixed_total, fixed_notes = count_passes(py_fixed, tests)
    buggy_ok, buggy_total, buggy_notes = count_passes(py_buggy, tests)
    cat_tests = meta.get("test_cases") or []
    return {
        "pattern_id": pid,
        "title": meta.get("title"),
        "title_index": meta.get("raw_title"),
        "description": meta.get("detailed_description") or meta.get("short_goal"),
        "catalog_tests_n": len(cat_tests),
        "v128_tests_n": len(V128_TEST_SUITES.get(pid) or []),
        "tests_used_n": len(tests),
        "catalog_test_sample": cat_tests[:2],
        "v128_test_sample": (V128_TEST_SUITES.get(pid) or [])[:2],
        "has_fixed": {lang: bool(codes[lang]["fixed"]) for lang in LANGS},
        "has_buggy": {lang: bool(codes[lang]["buggy"]) for lang in LANGS},
        "fixed_pass": f"{fixed_ok}/{fixed_total}",
        "buggy_pass": f"{buggy_ok}/{buggy_total}",
        "fixed_notes": fixed_notes[:3],
        "buggy_notes": buggy_notes[:3],
        "py_fixed_head": py_fixed[:300],
        "py_buggy_head": py_buggy[:300],
    }


if __name__ == "__main__":
    pids = sys.argv[1:] or ["task_004", "task_007", "task_012", "task_015", "task_020"]
    print(json.dumps([analyze(p) for p in pids], ensure_ascii=False, indent=2))
