"""Dry-run / apply for recursion slot corruption: task_052 (debug), task_053 (assemble).

Does NOT swap slots, change pattern_id, action, format, or task order.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2.extras import Json

SCRIPTS = Path(__file__).resolve().parent
BACKEND = SCRIPTS.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from debug_recursion_slot_t052_t053 import (  # noqa: E402
    T052_BUGGY,
    T052_CONCEPTS,
    T052_DESC,
    T052_HINTS,
    T052_POST,
    T052_REF,
    T052_TESTS,
    T052_TITLE,
    T053_CONCEPTS,
    T053_DESC,
    T053_HINTS,
    T053_POST,
    T053_REF,
    T053_TESTS,
    T053_TITLE,
)

DB = dict(host="localhost", port=5433, dbname="code_trainer",
          user="code_trainer", password="change_me")

LANGS = ["pascal", "python", "cpp", "csharp", "java"]
TASK_FORMAT_053 = "сборка_программы"

T052_SPEC = {
    "kind": "debug",
    "title": T052_TITLE,
    "description": T052_DESC,
    "ref": T052_REF,
    "buggy": T052_BUGGY,
    "tests": T052_TESTS,
    "concepts": T052_CONCEPTS,
    "hints": T052_HINTS,
    "post_solve": T052_POST,
}

T053_SPEC = {
    "kind": "assemble",
    "title": T053_TITLE,
    "description": T053_DESC,
    "ref": T053_REF,
    "tests": T053_TESTS,
    "concepts": T053_CONCEPTS,
    "hints": T053_HINTS,
    "post_solve": T053_POST,
    "task_format": TASK_FORMAT_053,
}

SPECS = {"task_052": T052_SPEC, "task_053": T053_SPEC}


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
            return r.stdout, f"exit {r.returncode}: {r.stderr[:160]}"
        return r.stdout, None
    except Exception as exc:
        return "", str(exc)


def validate_python(code: str, tests: list[dict]) -> dict[str, Any]:
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
    return {"pass": f"{ok}/{len(tests)}", "notes": notes}


def validate_buggy_fails(code: str, tests: list[dict]) -> dict[str, Any]:
    fail = 0
    pass_notes: list[str] = []
    for i, tc in enumerate(tests):
        got, err = run_python(code, tc["inputs"])
        if err:
            fail += 1
            continue
        if norm(got) == norm(tc["output"]):
            pass_notes.append(f"T{i+1}: buggy passes")
        else:
            fail += 1
    return {"fail": f"{fail}/{len(tests)}", "pass_notes": pass_notes}


def build_assembly_variants(
    ref: dict[str, str],
    task_format: str,
    *,
    pattern_id: str | None = None,
) -> dict[str, dict[str, Any]]:
    from application.curriculum.content.v4_assembly_builder import assembly_variant

    out: dict[str, dict[str, Any]] = {}
    for lang in LANGS:
        code = str(ref.get(lang) or "").strip()
        if not code:
            continue
        variant = assembly_variant(
            lang,
            code,
            task_format=task_format,
            pattern_id=pattern_id,
        )
        out[lang] = variant
    return out


def merge_task_code_examples(ce: dict, spec: dict, pid: str) -> dict:
    new_ce = dict(ce or {})
    showcase = dict(new_ce.get("curriculum_showcase") or {})
    concepts = list(spec.get("concepts") or [])
    concepts_by_lang = {lang: list(concepts) for lang in LANGS}

    for lang in LANGS:
        fixed = str((spec.get("ref") or {}).get(lang) or "").strip()
        if fixed:
            new_ce[lang] = fixed
        if spec.get("kind") == "debug":
            buggy = str((spec.get("buggy") or {}).get(lang) or "").strip()
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

    if spec.get("kind") == "assemble":
        variants = build_assembly_variants(spec["ref"], spec["task_format"])
        primary = variants.get("pascal") or variants.get("python") or {}
        if primary:
            new_ce["original_code"] = primary.get("original_code") or spec["ref"].get("pascal", "")
            new_ce["template"] = primary.get("template") or "___"
            new_ce["blocks"] = list(primary.get("blocks") or [])
            new_ce["correct_order"] = list(primary.get("correct_order") or [])
        klv: dict[str, dict[str, str]] = {}
        for lang in LANGS:
            code = str(spec["ref"].get(lang) or "").strip()
            if code:
                klv[lang] = {"source_code": code, "explanation": f"Эталон на {lang}."}
        new_ce["known_language_variants"] = klv
        showcase["known_language_variants"] = klv

    return new_ce


def preview_public_payload(db_row: tuple, spec: dict, pid: str) -> dict[str, Any]:
    from application.curriculum.display.showcase_display import finalize_student_task_payload

    did, title, desc, tests, ce = db_row
    if isinstance(ce, str):
        ce = json.loads(ce)
    merged_ce = merge_task_code_examples(ce or {}, spec, pid)
    showcase = merged_ce.get("curriculum_showcase") or {}
    raw = {
        "id": did,
        "title": spec["title"],
        "description": spec["description"],
        "test_cases": spec["tests"],
        "code_examples": merged_ce,
        "curriculum": {
            "slot_pattern_id": showcase.get("slot_pattern_id"),
            "primary_action": showcase.get("primary_action"),
            "task_format": showcase.get("task_format"),
            "action": showcase.get("primary_action"),
        },
    }
    if spec.get("kind") == "assemble":
        variants = build_assembly_variants(spec["ref"], spec["task_format"])
        py_asm = variants.get("python") or {}
        raw["blocks"] = py_asm.get("blocks")
        raw["correct_order"] = py_asm.get("correct_order")
        raw["template"] = py_asm.get("template")
    finalized = finalize_student_task_payload(raw)
    ce_f = finalized.get("code_examples") or {}
    out: dict[str, Any] = {
        "title": finalized.get("title"),
        "description": (finalized.get("description") or "")[:120],
        "pattern_id": (finalized.get("curriculum") or {}).get("slot_pattern_id") or showcase.get("slot_pattern_id"),
        "action": showcase.get("primary_action"),
        "format": showcase.get("task_format"),
        "tests_count": len(finalized.get("test_cases") or []),
        "first_test": (finalized.get("test_cases") or [None])[0],
        "hints": finalized.get("hints"),
        "post_solve": (finalized.get("post_solve_explanation") or "")[:160],
        "expected_concepts_pascal": (ce_f.get("expected_concepts") or {}).get("pascal"),
    }
    if spec.get("kind") == "debug":
        out["buggy_pascal"] = bool(ce_f.get("buggy_pascal"))
        out["fixed_python_head"] = "\n".join(str(ce_f.get("python") or "").splitlines()[:4])
        out["buggy_python_head"] = "\n".join(str(ce_f.get("buggy_python") or "").splitlines()[:4])
    else:
        asm = build_assembly_variants(spec["ref"], spec["task_format"])
        py = asm.get("python") or {}
        out["assemble_blocks_count"] = len(py.get("blocks") or [])
        out["assemble_blocks_preview"] = list(py.get("blocks") or [])[:8]
        out["assemble_correct_order"] = py.get("correct_order")
        out["assemble_template"] = py.get("template")
        out["reference_python_head"] = "\n".join(str(spec["ref"].get("python") or "").splitlines()[:4])
    return out


def validate_all() -> bool:
    ok = True
    s052 = SPECS["task_052"]
    fv = validate_python(s052["ref"]["python"], s052["tests"])
    bv = validate_buggy_fails(s052["buggy"]["python"], s052["tests"])
    print(f"  [validate] task_052 fixed {fv['pass']}")
    if fv["notes"]:
        print(f"    {fv['notes']}")
        ok = False
    print(f"  [validate] task_052 buggy fail {bv['fail']}")
    if bv["pass_notes"]:
        print(f"    pass: {bv['pass_notes']}")
    if bv["fail"].split("/")[0] == "0":
        print("  [validate] task_052 WARNING: buggy passes all tests")
        ok = False

    s053 = SPECS["task_053"]
    fv3 = validate_python(s053["ref"]["python"], s053["tests"])
    print(f"  [validate] task_053 reference {fv3['pass']}")
    if fv3["notes"]:
        print(f"    {fv3['notes']}")
        ok = False
    variants = build_assembly_variants(s053["ref"], s053["task_format"])
    for lang in LANGS:
        v = variants.get(lang) or {}
        blocks = list(v.get("blocks") or [])
        if len(blocks) < 4:
            print(f"  [validate] task_053 {lang} blocks too few: {len(blocks)}")
            ok = False
    py_blocks = list((variants.get("python") or {}).get("blocks") or [])
    print(f"  [validate] task_053 python assembly blocks: {len(py_blocks)}")
    return ok


def apply_specs(cur, apply: bool) -> None:
    for pid, spec in SPECS.items():
        cur.execute(
            """select id, title, description, test_cases, code_examples
               from task where code_examples->'curriculum_showcase'->>'slot_pattern_id'=%s""",
            (pid,),
        )
        row = cur.fetchone()
        if not row:
            print(f"  {pid}: NOT FOUND")
            continue
        did, old_title, _desc, _tc, ce = row
        if isinstance(ce, str):
            ce = json.loads(ce)
        showcase = (ce or {}).get("curriculum_showcase") or {}
        new_ce = merge_task_code_examples(ce or {}, spec, pid)

        print(f"  {pid} (DB id {did})")
        print(f"    title : {old_title!r} -> {spec['title']!r}")
        print(f"    action/format unchanged: {showcase.get('primary_action')!r} / {showcase.get('task_format')!r}")
        print(f"    tests -> {len(spec['tests'])}")

        if spec["kind"] == "assemble":
            variants = build_assembly_variants(spec["ref"], spec["task_format"])
            primary = variants["pascal"]
            print(f"    block_reorder pascal blocks: {len(primary['blocks'])}")
            if apply:
                cur.execute(
                    """update block_reorder_task set
                         language=%s,
                         original_code=%s,
                         template=%s,
                         blocks=%s,
                         correct_order=%s,
                         language_variants=%s
                       where task_id=%s""",
                    (
                        "pascal",
                        primary["original_code"],
                        primary["template"],
                        Json(primary["blocks"]),
                        Json(primary["correct_order"]),
                        Json(variants),
                        did,
                    ),
                )

        if apply:
            cur.execute(
                """update task set title=%s, description=%s,
                          code_examples=%s, test_cases=%s, updated_at=now()
                   where id=%s""",
                (
                    spec["title"],
                    spec["description"],
                    json.dumps(new_ce, ensure_ascii=False),
                    json.dumps(spec["tests"], ensure_ascii=False),
                    did,
                ),
            )


def build_report() -> dict[str, Any]:
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    report: dict[str, Any] = {}
    for pid, spec in SPECS.items():
        cur.execute(
            """select id, title, description, test_cases, code_examples
               from task where code_examples->'curriculum_showcase'->>'slot_pattern_id'=%s""",
            (pid,),
        )
        row = cur.fetchone()
        if not row:
            report[pid] = {"error": "not found"}
            continue
        entry: dict[str, Any] = {
            "title": spec["title"],
            "description": spec["description"],
            "tests": spec["tests"],
            "expected_concepts": spec["concepts"],
            "hints": spec["hints"],
            "post_solve": spec["post_solve"],
            "public_payload_preview": preview_public_payload(row, spec, pid),
            "risks": _risks(pid, spec),
        }
        if spec["kind"] == "debug":
            entry["fixed_validation"] = validate_python(spec["ref"]["python"], spec["tests"])
            entry["buggy_validation"] = validate_buggy_fails(spec["buggy"]["python"], spec["tests"])
        else:
            entry["reference_validation"] = validate_python(spec["ref"]["python"], spec["tests"])
            variants = build_assembly_variants(spec["ref"], spec["task_format"])
            entry["assemble_blocks_preview"] = {
                lang: {
                    "blocks_count": len(v.get("blocks") or []),
                    "blocks": list(v.get("blocks") or [])[:10],
                    "correct_order": v.get("correct_order"),
                    "template": v.get("template"),
                }
                for lang, v in variants.items()
            }
        report[pid] = entry
    cur.close()
    conn.close()
    return report


def _risks(pid: str, spec: dict) -> list[str]:
    risks: list[str] = []
    if pid == "task_052":
        risks.append("buggy T2 (a) может проходить — базовый случай одинаков.")
        risks.append("task_type остаётся task_translate_full_program (как у других debug ch7).")
        risks.append("ch7_user_codes/task_052.py (FastPower) не обновляется этим скриптом.")
        risks.append("v128_test_suites_data.task_052 (power) остаётся в repo до отдельной синхронизации.")
    if pid == "task_053":
        risks.append("block_reorder_task перезаписывает factorial-блоки на palindrome.")
        risks.append("ch7_user_codes/task_053.py (ReverseString) не обновляется этим скриптом.")
        risks.append("ALGO_SYNTAX_META raw_title «разворот» остаётся до meta-sync.")
    risks.append("pattern_id / primary_action / task_format не меняются.")
    return risks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--preview", action="store_true", help="JSON report for dry-run review")
    args = ap.parse_args()

    print("== VALIDATION ==")
    if not validate_all():
        print("\nValidation failed.")
        sys.exit(1)

    if args.preview or not args.apply:
        report = build_report()
        print(json.dumps(report, ensure_ascii=False, indent=2))

    print("\n== %s ==" % ("APPLY" if args.apply else "DRY-RUN"))
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    apply_specs(cur, args.apply)
    if args.apply:
        conn.commit()
        print("\nCommitted.")
    else:
        print("\nDry-run only. Re-run with --apply after confirmation.")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
