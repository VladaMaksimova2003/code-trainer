"""Dry-run validation + public payload preview for Batch 3 damaged (044/047). Mini-audit 052/053."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

import psycopg2

SCRIPTS = Path(__file__).resolve().parent
BACKEND = SCRIPTS.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from algo_v128_catalog import ALGO_SYNTAX_META, _TASK_INDEX  # noqa: E402
from debug_batch3_t044_t047 import T044_REF, T044_BUGGY, T044_TESTS  # noqa: E402
from debug_batch3_t044_t047 import T047_REF, T047_BUGGY, T047_TESTS  # noqa: E402
from import_debug_fixes import LANGS, OVERRIDES, norm, run_python, validate  # noqa: E402
from v128_test_suites_data import V128_TEST_SUITES  # noqa: E402

DB = dict(host="localhost", port=5433, dbname="code_trainer",
          user="code_trainer", password="change_me")
API = os.environ.get("MPLT_API", "http://127.0.0.1:9000")

DAMAGED = ["task_044", "task_047"]
AUDIT_PAIR = ["task_052", "task_053"]


def merge_override_into_row(ce: dict, spec: dict) -> dict:
    """Mirror import_debug_fixes apply logic without DB write."""
    new_ce = dict(ce)
    showcase = dict(new_ce.get("curriculum_showcase") or {})
    concepts = list(spec.get("concepts") or [])
    concepts_by_lang = {lang: list(concepts) for lang in LANGS}

    for lang in LANGS:
        fixed = str((spec.get("ref") or {}).get(lang) or "").strip()
        buggy = str((spec.get("buggy") or {}).get(lang) or "").strip()
        if fixed:
            new_ce[lang] = fixed
        if buggy:
            new_ce[f"buggy_{lang}"] = buggy

    if concepts:
        new_ce["patterns"] = list(concepts)
        new_ce["expected_concepts"] = concepts_by_lang
        showcase["expected_concept_ids"] = list(concepts)
        showcase["expected_concepts"] = concepts_by_lang
    if spec.get("hints"):
        new_ce["hints"] = list(spec["hints"])
        showcase["hints"] = list(spec["hints"])
    if spec.get("post_solve"):
        new_ce["post_solve_explanation"] = str(spec["post_solve"])
        showcase["post_solve_explanation"] = str(spec["post_solve"])

    new_ce["teacher_assembly_override"] = True
    new_ce["curriculum_showcase"] = showcase
    return new_ce


def preview_public_payload(db_row: dict, spec: dict) -> dict[str, Any]:
    from application.curriculum.display.showcase_display import finalize_student_task_payload

    did, title, desc, tests, ce = db_row
    if isinstance(ce, str):
        ce = json.loads(ce)
    merged_ce = merge_override_into_row(ce or {}, spec)
    raw_payload = {
        "id": did,
        "title": spec["title"],
        "description": spec["description"],
        "test_cases": spec["tests"],
        "code_examples": merged_ce,
        "curriculum": dict((ce or {}).get("curriculum_showcase") or {}),
    }
    showcase = merged_ce.get("curriculum_showcase") or {}
    raw_payload["curriculum"].update(
        {
            "slot_pattern_id": showcase.get("slot_pattern_id"),
            "primary_action": showcase.get("primary_action"),
            "task_format": showcase.get("task_format"),
            "action": showcase.get("primary_action"),
        }
    )
    finalized = finalize_student_task_payload(raw_payload)
    ce_f = finalized.get("code_examples") or {}
    tests_top = finalized.get("test_cases") or []
    return {
        "title": finalized.get("title"),
        "description": (finalized.get("description") or "")[:120],
        "test_cases_count": len(tests_top),
        "first_test": tests_top[0] if tests_top else None,
        "hints_top_level": finalized.get("hints"),
        "post_solve_preview": (finalized.get("post_solve_explanation") or "")[:160],
        "expected_concepts_pascal": (ce_f.get("expected_concepts") or {}).get("pascal"),
        "fixed_python_lines": len(str(ce_f.get("python") or "").splitlines()),
        "buggy_pascal_present": bool(ce_f.get("buggy_pascal")),
        "buggy_python_present": bool(ce_f.get("buggy_python")),
        "fixed_python_head": "\n".join(str(ce_f.get("python") or "").splitlines()[:4]),
        "buggy_python_head": "\n".join(str(ce_f.get("buggy_python") or "").splitlines()[:4]),
    }


def fields_changed(db_row: dict, spec: dict) -> dict[str, Any]:
    did, old_title, old_desc, old_tests, ce = db_row
    if isinstance(old_tests, str):
        old_tests = json.loads(old_tests)
    if isinstance(ce, str):
        ce = json.loads(ce)
    merged = merge_override_into_row(ce or {}, spec)
    return {
        "db_id": did,
        "title": {"from": old_title, "to": spec["title"]},
        "description_changed": (old_desc or "").strip() != spec["description"].strip(),
        "tests_count": {"from": len(old_tests or []), "to": len(spec["tests"])},
        "fixed_langs": [lang for lang in LANGS if (spec.get("ref") or {}).get(lang)],
        "buggy_langs": [lang for lang in LANGS if (spec.get("buggy") or {}).get(lang)],
        "hints_added": bool(spec.get("hints")),
        "post_solve_added": bool(spec.get("post_solve")),
        "expected_concepts": spec.get("concepts"),
    }


def validation_report(pid: str, spec: dict) -> dict[str, Any]:
    ref = spec["ref"]["python"]
    bug = spec["buggy"]["python"]
    fixed_notes: list[str] = []
    buggy_notes: list[str] = []
    fixed_ok = 0
    buggy_fail = 0
    for i, tc in enumerate(spec["tests"]):
        got = run_python(ref, tc["inputs"])
        if norm(got) == norm(tc["output"]):
            fixed_ok += 1
        else:
            fixed_notes.append(f"T{i+1}: exp={tc['output']!r} got={norm(got)!r}")
        try:
            bgot = run_python(bug, tc["inputs"])
        except Exception as exc:
            bgot = f"ERR:{exc}"
        if norm(bgot) != norm(tc["output"]):
            buggy_fail += 1
        else:
            buggy_notes.append(f"T{i+1}: buggy passes (exp={tc['output']!r})")
    return {
        "fixed_validation": f"{fixed_ok}/{len(spec['tests'])}",
        "fixed_notes": fixed_notes,
        "buggy_validation": f"{buggy_fail}/{len(spec['tests'])} fail",
        "buggy_pass_notes": buggy_notes,
    }


def fetch_live_api(db_id: int) -> dict[str, Any]:
    url = f"{API}/tasks/{db_id}?learning_language=pascal"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    ce = payload.get("code_examples") or {}
    curriculum = payload.get("curriculum") or {}
    tests = payload.get("test_cases") or []
    return {
        "title": payload.get("title") or curriculum.get("title"),
        "description": (payload.get("description") or "")[:120],
        "action": curriculum.get("action") or (ce.get("curriculum_showcase") or {}).get("primary_action"),
        "format": curriculum.get("task_format") or (ce.get("curriculum_showcase") or {}).get("task_format"),
        "tests_count": len(tests),
        "tests": [{"inputs": t.get("inputs"), "output": t.get("output")} for t in tests[:5]],
        "fixed_pascal_head": "\n".join(str(ce.get("pascal") or "").splitlines()[:6]),
        "buggy_pascal_head": "\n".join(str(ce.get("buggy_pascal") or "").splitlines()[:6]),
        "fixed_python_head": "\n".join(str(ce.get("python") or "").splitlines()[:4]),
        "buggy_python_head": "\n".join(str(ce.get("buggy_python") or "").splitlines()[:4]),
        "hints_top": payload.get("hints"),
        "post_solve_top": (payload.get("post_solve_explanation") or "")[:100],
    }


def catalog_entry(pattern: str) -> dict[str, Any]:
    row = next((e for e in _TASK_INDEX if e.get("pattern_id") == pattern), {})
    meta = ALGO_SYNTAX_META.get(pattern) or {}
    return {
        "catalog_list_title": row.get("title"),
        "catalog_action": row.get("action"),
        "catalog_format_ru": row.get("format_ru"),
        "catalog_goal": row.get("goal"),
        "meta_raw_title": meta.get("raw_title"),
        "meta_title": meta.get("title"),
        "meta_action": meta.get("action"),
        "meta_format_ru": meta.get("format_ru"),
        "meta_goal": meta.get("short_goal"),
    }


def load_ch7_module(task_num: int):
    path = SCRIPTS / f"ch7_user_codes/task_{task_num:03d}.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ch7_code_summary(task_num: int) -> dict[str, Any]:
    mod = load_ch7_module(task_num)
    py = str(getattr(mod, "PYTHON", "") or getattr(mod, "FIXED_PYTHON", "") or "")
    pas = str(getattr(mod, "PASCAL", "") or getattr(mod, "FIXED_PASCAL", "") or "")
    return {
        "has_fixed_buggy_split": bool(getattr(mod, "FIXED_PYTHON", None)),
        "python_kind": "FastPower" if "fast_power" in py.lower() or "FastPower" in py else (
            "ReverseString" if "reverse_string" in py.lower() or "ReverseString" in py else "other"
        ),
        "pascal_kind": "FastPower" if "FastPower" in pas else (
            "ReverseString" if "ReverseString" in pas else "other"
        ),
        "python_head": "\n".join(py.splitlines()[:4]),
    }


def audit_pair(pattern: str, db_row) -> dict[str, Any]:
    did, title, desc, tests, ce = db_row
    if isinstance(tests, str):
        tests = json.loads(tests)
    if isinstance(ce, str):
        ce = json.loads(ce)
    showcase = ce.get("curriculum_showcase") or {}
    task_num = int(pattern.split("_")[1])
    live_api = {}
    try:
        live_api = fetch_live_api(did)
    except Exception as exc:
        live_api = {"error": str(exc)}

    return {
        "pattern_id": pattern,
        "db_id": did,
        "db_title": title,
        "db_description": (desc or "")[:120],
        "db_tests_count": len(tests or []),
        "db_tests": [{"inputs": t.get("inputs"), "output": t.get("output")} for t in (tests or [])[:5]],
        "showcase_primary_action": showcase.get("primary_action"),
        "showcase_task_format": showcase.get("task_format"),
        "catalog": catalog_entry(pattern),
        "v128_tests": V128_TEST_SUITES.get(pattern),
        "ch7_user_codes": ch7_code_summary(task_num),
        "db_code_examples": {
            "fixed_pascal_head": "\n".join(str(ce.get("pascal") or "").splitlines()[:6]),
            "buggy_pascal_head": "\n".join(str(ce.get("buggy_pascal") or "").splitlines()[:6]),
            "fixed_python_head": "\n".join(str(ce.get("python") or "").splitlines()[:4]),
            "buggy_python_head": "\n".join(str(ce.get("buggy_python") or "").splitlines()[:4]),
        },
        "live_public_payload": live_api,
    }


def main() -> None:
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    report: dict[str, Any] = {"damaged_dry_run": {}, "pair_audit_052_053": {}}

    for pid in DAMAGED:
        spec = OVERRIDES[pid]
        cur.execute(
            """select id, title, description, test_cases, code_examples
               from task where code_examples->'curriculum_showcase'->>'slot_pattern_id'=%s""",
            (pid,),
        )
        row = cur.fetchone()
        if not row:
            report["damaged_dry_run"][pid] = {"error": "not in DB"}
            continue
        val = validation_report(pid, spec)
        import_ok = validate(pid, spec)
        report["damaged_dry_run"][pid] = {
            "validation": val,
            "import_validate_ok": import_ok,
            "fields_changed": fields_changed(row, spec),
            "public_payload_preview_after_apply": preview_public_payload(row, spec),
            "risks": _risks(pid, val),
        }

    for pid in AUDIT_PAIR:
        cur.execute(
            """select id, title, description, test_cases, code_examples
               from task where code_examples->'curriculum_showcase'->>'slot_pattern_id'=%s""",
            (pid,),
        )
        row = cur.fetchone()
        if row:
            report["pair_audit_052_053"][pid] = audit_pair(pid, row)

    cur.close()
    conn.close()
    print(json.dumps(report, ensure_ascii=False, indent=2))


def _risks(pid: str, val: dict) -> list[str]:
    risks: list[str] = []
    if val.get("buggy_pass_notes"):
        risks.append(f"buggy проходит часть тестов: {val['buggy_pass_notes']}")
    if pid == "task_044":
        risks.append("DB/ch6 ранее содержали normalize-string; apply перезапишет все 5 языков power-кодом.")
        risks.append("catalog raw_title «нормализация» в ALGO_SYNTAX_META останется до отдельной синхронизации meta.")
    if pid == "task_047":
        risks.append("v128_test_suites_data всё ещё sum-массива — apply заменит test_cases в DB на min/max.")
        risks.append("ch6_user_codes/task_047.py (ArraySum) не обновляется этим import-скриптом.")
    return risks


if __name__ == "__main__":
    main()
