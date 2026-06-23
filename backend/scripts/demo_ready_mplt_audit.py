#!/usr/bin/env python3
"""Read-only DEMO_READY audit for 4 MPLT showcase tasks."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

SCRIPTS = Path(__file__).resolve().parent
BACKEND = SCRIPTS.parent
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(SCRIPTS))

from algo_v128_catalog import ALGO_SYNTAX_META, _TASK_INDEX  # noqa: E402
from application.curriculum.content.algo_syntax_showcase_meta import (  # noqa: E402
    transfer_meta_for_language_pair,
)
from application.curriculum.content.v4_reference_code import get_reference_code  # noqa: E402
from application.curriculum.display.algorithm_debug_detector import (  # noqa: E402
    detect_algorithm_debug,
)
from application.curriculum.display.showcase_display import sanitize_public_task_payload  # noqa: E402
from application.curriculum.display.transfer_pitfall_detector import (  # noqa: E402
    detect_transfer_pitfalls,
)
from application.curriculum.display.v128_transfer_meta import resolve_v128_transfer_meta  # noqa: E402
from v128_test_suites_data import V128_TEST_SUITES  # noqa: E402

DB = dict(
    host="localhost",
    port=5433,
    dbname="code_trainer",
    user="code_trainer",
    password="change_me",
)
API = os.environ.get("MPLT_API", "http://127.0.0.1:9000")

LANGS = ("pascal", "python", "cpp", "csharp", "java")
MPLT_PAIRS = [
    ("python", "pascal"),
    ("python", "cpp"),
    ("python", "csharp"),
    ("python", "java"),
    ("pascal", "python"),
    ("pascal", "cpp"),
    ("pascal", "csharp"),
    ("pascal", "java"),
    ("cpp", "pascal"),
    ("cpp", "python"),
    ("cpp", "csharp"),
    ("cpp", "java"),
    ("csharp", "pascal"),
    ("csharp", "python"),
    ("csharp", "cpp"),
    ("csharp", "java"),
    ("java", "pascal"),
    ("java", "python"),
    ("java", "cpp"),
    ("java", "csharp"),
]

AUDIT_TASKS = (
    "task_006",
    "task_003",
    "task_007",
    "task_004",
    "task_053",
)

PAYLOAD_FIELDS = (
    "title",
    "description",
    "pattern_id",
    "action",
    "task_format",
    "test_cases",
    "hints",
    "post_solve_explanation",
    "expected_concepts",
    "code_examples",
)

GENERIC_FEEDBACK_PATTERNS = (
    r"обратите внимание",
    r"будьте внимательны",
    r"проверьте код",
    r"возможна ошибка",
    r"перенос может",
)


def norm(s: str) -> str:
    return "\n".join(l.rstrip() for l in str(s).strip().splitlines()).strip()


def parse_json(val: Any) -> Any:
    if isinstance(val, str):
        return json.loads(val)
    return val


def run_python(code: str, inp: str) -> tuple[str, str | None]:
    if not str(code or "").strip():
        return "", "empty"
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
            err = (r.stderr or r.stdout or "").strip()[:80]
            if "SyntaxError" in err:
                return r.stdout, f"SyntaxError"
            return r.stdout, f"exit {r.returncode}: {err}"
        return r.stdout, None
    except Exception as exc:
        return "", str(exc)[:80]


def validate_code(code: str, tests: list) -> dict[str, Any]:
    if not tests:
        return {"pass": "0/0", "ok": 0, "total": 0, "notes": ["no tests"]}
    ok = 0
    notes: list[str] = []
    for i, tc in enumerate(tests):
        got, err = run_python(code, tc.get("inputs", ""))
        if err:
            notes.append(f"T{i+1}:{err}")
            continue
        if norm(got) == norm(tc.get("output", "")):
            ok += 1
        else:
            notes.append(f"T{i+1}")
    return {"pass": f"{ok}/{len(tests)}", "ok": ok, "total": len(tests), "notes": notes[:5]}


def get_lang_code(ce: dict, lang: str, *, fixed: bool = True) -> str:
    key = lang if fixed else f"buggy_{lang}"
    direct = str(ce.get(key) or "").strip()
    if direct:
        return direct
    impls = ce.get("implementations") or {}
    impl = impls.get(lang) or {}
    if fixed:
        return str(
            impl.get("fixed_code") or impl.get("reference_code") or ce.get(lang) or ""
        ).strip()
    return str(impl.get("buggy_code") or ce.get(f"buggy_{lang}") or "").strip()


def get_expected_concepts(ce: dict, lang: str) -> list:
    ec = ce.get("expected_concepts") or {}
    if isinstance(ec, dict):
        return list(ec.get(lang) or ec.get("all") or [])
    return []


def get_hints(ce: dict, lang: str) -> list:
    hints = ce.get("hints") or {}
    if isinstance(hints, dict):
        return list(hints.get(lang) or hints.get("all") or [])
    if isinstance(hints, list):
        return hints
    return []


def get_post_solve(ce: dict, lang: str) -> str:
    ps = ce.get("post_solve_explanation") or {}
    if isinstance(ps, dict):
        return str(ps.get(lang) or ps.get("all") or "").strip()
    return str(ps or "").strip()


def load_db_task(pattern_id: str) -> dict[str, Any] | None:
    try:
        import psycopg2
    except ImportError:
        return None
    try:
        conn = psycopg2.connect(**DB)
    except Exception as exc:
        return {"_db_error": str(exc)}
    cur = conn.cursor()
    cur.execute(
        """
        select id, title, description, task_type, test_cases, code_examples
        from task
        where code_examples->'curriculum_showcase'->>'slot_pattern_id' = %s
        limit 1
        """,
        (pattern_id,),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return None
    did, title, desc, task_type, tests, ce = row
    tests = parse_json(tests) or []
    ce = parse_json(ce) or {}
    showcase = ce.get("curriculum_showcase") or {}
    return {
        "db_id": did,
        "title": title,
        "description": desc,
        "task_type": str(task_type or ""),
        "test_cases": tests if isinstance(tests, list) else [],
        "code_examples": ce,
        "curriculum_showcase": showcase,
    }


def build_public_payload(db_task: dict, *, source: str, target: str) -> dict[str, Any]:
    ce = db_task.get("code_examples") or {}
    showcase = db_task.get("curriculum_showcase") or {}
    transfer = transfer_meta_for_language_pair(
        showcase.get("slot_pattern_id") or "",
        source_language=source,
        target_language=target,
    )
    raw = {
        "id": db_task.get("db_id"),
        "title": db_task.get("title"),
        "description": db_task.get("description"),
        "test_cases": db_task.get("test_cases") or [],
        "code_examples": ce,
        "hints": get_hints(ce, target) or ce.get("hints"),
        "post_solve_explanation": get_post_solve(ce, target),
        "expected_concepts": get_expected_concepts(ce, target),
        "curriculum": {
            "slot_pattern_id": showcase.get("slot_pattern_id"),
            "action": showcase.get("primary_action") or showcase.get("action"),
            "task_format": showcase.get("task_format"),
            "source_language": source,
            "target_language": target,
        },
        "transfer": transfer,
    }
    return sanitize_public_task_payload(raw)


def check_payload_nulls(payload: dict, *, needs_buggy: bool, target: str) -> list[str]:
    issues: list[str] = []
    ce = payload.get("code_examples") or {}
    curriculum = payload.get("curriculum") or payload.get("transfer") or {}
    checks = {
        "title": payload.get("title"),
        "description": payload.get("description"),
        "pattern_id": (payload.get("curriculum") or {}).get("slot_pattern_id")
        or ce.get("slot_pattern_id"),
        "action": (payload.get("curriculum") or {}).get("action"),
        "task_format": (payload.get("curriculum") or {}).get("task_format"),
        "test_cases": payload.get("test_cases"),
        "hints": payload.get("hints"),
        "post_solve_explanation": payload.get("post_solve_explanation"),
        "expected_concepts": payload.get("expected_concepts"),
        "code_examples": ce,
    }
    for field, val in checks.items():
        if val is None or val == "" or val == [] or val == {}:
            issues.append(f"null:{field}")
    if needs_buggy:
        buggy = get_lang_code(ce, target, fixed=False)
        if not buggy:
            issues.append(f"null:buggy_code[{target}]")
    return issues


def feedback_has_code_examples(text: str) -> bool:
    if not text or len(text.strip()) < 20:
        return False
    lower = text.lower()
    if any(re.search(p, lower) for p in GENERIC_FEEDBACK_PATTERNS):
        if not re.search(r"[`'\"]|//|div|readln|cin|scanf|Console|Scanner", text):
            return False
    return bool(
        re.search(r"[`'\"]|//|div|readln|cin|Console|Scanner|>=|//|%", text)
        or len(text) > 80
    )


def pitfall_carryover_code(pattern_id: str, pitfall_id: str, target: str) -> str:
    samples = {
        ("integer_division", "pascal"): "var a,b: integer;\nbegin\n  readln(a,b);\n  writeln(a / b);\nend.",
        ("integer_division", "cpp"): "#include <iostream>\nint main(){int a,b; std::cin>>a>>b; std::cout<<a/b;}",
        ("input_line_model", "pascal"): "var a,b,c: integer;\nbegin\n  readln(a);\n  readln(b);\n  readln(c);\n  writeln(a);\nend.",
        ("input_line_model", "java"): "import java.util.*;\nclass Main{public static void main(String[]a){Scanner s=new Scanner(System.in);int a=s.nextInt();int b=s.nextInt();int c=s.nextInt();System.out.println(a);}}",
    }
    return samples.get((pitfall_id, target), "")


def debug_carryover_code(debug_id: str, target: str) -> str:
    if debug_id == "filter_positive":
        if target == "pascal":
            return "var n,i,x,c:integer;\nbegin readln(n); c:=0; for i:=1 to n do begin readln(x); if x>=0 then c:=c+1; end; writeln(c); end."
        return "n=int(input())\nc=0\nfor _ in range(n):\n x=int(input())\n if x>=0: c+=1\nprint(c)"
    if debug_id == "threshold_count":
        if target == "pascal":
            return "var n,i,x,c:integer;\nbegin readln(n); c:=0; for i:=1 to n do begin readln(x); if x>50 then c:=c+1; end; writeln(c); end."
        return "n=int(input())\nc=0\nfor _ in range(n):\n x=int(input())\n if x>50: c+=1\nprint(c)"
    return ""


def audit_language_support(pattern_id: str, db_task: dict | None, action: str) -> dict[str, Any]:
    ce = (db_task or {}).get("code_examples") or {}
    needs_buggy = action == "debug"
    per_lang: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    for lang in LANGS:
        fixed = get_lang_code(ce, lang, fixed=True) or get_reference_code(pattern_id, lang)
        buggy = get_lang_code(ce, lang, fixed=False)
        hints = get_hints(ce, lang)
        post = get_post_solve(ce, lang)
        concepts = get_expected_concepts(ce, lang)
        row = {
            "fixed": bool(fixed.strip()),
            "buggy": bool(buggy.strip()) if needs_buggy else "n/a",
            "hints": len(hints) if hints else 0,
            "post_solve": bool(post),
            "expected_concepts": len(concepts) if concepts else 0,
        }
        per_lang[lang] = row
        if not row["fixed"]:
            missing.append(f"{lang}:fixed")
        if needs_buggy and not buggy.strip():
            missing.append(f"{lang}:buggy")
        if not hints:
            missing.append(f"{lang}:hints")
        if not post:
            missing.append(f"{lang}:post_solve")
        if not concepts:
            missing.append(f"{lang}:expected_concepts")
    return {"per_lang": per_lang, "missing": missing, "ok": len(missing) == 0}


def audit_mplt_pairs(pattern_id: str, meta: dict, db_task: dict | None) -> dict[str, Any]:
    pitfall_id = meta.get("pitfall_id")
    debug_id = meta.get("debug_id")
    category = str(meta.get("transfer_type") or meta.get("transfer_category") or "")
    pair_results: dict[str, dict[str, Any]] = {}
    pair_failures: list[str] = []
    for src, tgt in MPLT_PAIRS:
        key = f"{src}->{tgt}"
        tm = transfer_meta_for_language_pair(
            pattern_id, source_language=src, target_language=tgt
        )
        tt = str(tm.get("transfer_type") or "")
        proactive = (tm.get("proactive") or {}).get("text")
        expect_proactive = category in ("FCC", "AFCC", "ATCC")
        expect_algorithm = bool(debug_id)
        issues: list[str] = []
        if pitfall_id and tt != category:
            issues.append(f"transfer_type={tt}!={category}")
        if debug_id and tt != "TCC":
            issues.append(f"debug task transfer_type={tt}")
        if expect_proactive and not proactive:
            issues.append("no_proactive")
        elif not expect_proactive and not expect_algorithm and proactive:
            issues.append("unexpected_proactive")
        reactive_text = None
        reactive_ok = None
        if pitfall_id:
            code = pitfall_carryover_code(pattern_id, pitfall_id, tgt)
            if code:
                hits = detect_transfer_pitfalls(
                    pitfall_id=str(pitfall_id),
                    transfer_type=category,
                    source_language=src,
                    target_language=tgt,
                    code=code,
                    test_results=[{"status": "FAILED"}],
                )
                if hits:
                    reactive_text = hits[0].get("message") or hits[0].get("text") or ""
                    reactive_ok = feedback_has_code_examples(reactive_text)
                else:
                    issues.append("no_reactive_pitfall")
        elif debug_id:
            code = debug_carryover_code(debug_id, tgt)
            if code:
                hits = detect_algorithm_debug(
                    debug_id=str(debug_id),
                    target_language=tgt,
                    code=code,
                    test_results=[{"status": "FAILED"}],
                    buggy_code=code,
                )
                if hits:
                    reactive_text = hits[0].get("message") or hits[0].get("text") or ""
                    reactive_ok = feedback_has_code_examples(reactive_text)
                else:
                    issues.append("no_reactive_algorithm")
        if db_task:
            payload = build_public_payload(db_task, source=src, target=tgt)
            nulls = check_payload_nulls(
                payload,
                needs_buggy=str((db_task.get("curriculum_showcase") or {}).get("primary_action") or "").lower() == "debug",
                target=tgt,
            )
            if nulls:
                issues.append(f"payload:{','.join(nulls[:3])}")
        pair_results[key] = {
            "transfer_type": tt,
            "proactive": bool(proactive),
            "proactive_has_code": feedback_has_code_examples(proactive or ""),
            "reactive": reactive_ok,
            "reactive_preview": (reactive_text or "")[:120] if reactive_text else None,
            "issues": issues,
        }
        if issues:
            pair_failures.append(f"{key}:{';'.join(issues)}")
    return {
        "pairs_ok": len(pair_failures) == 0,
        "pair_failures": pair_failures[:25],
        "pair_fail_count": len(pair_failures),
        "pair_results_sample": {k: pair_results[k] for k in list(pair_results)[:4]},
    }


def detector_info(meta: dict) -> dict[str, Any]:
    pitfall_id = meta.get("pitfall_id")
    debug_id = meta.get("debug_id")
    if debug_id:
        return {
            "pitfall_or_debug_id": debug_id,
            "detector": "algorithm_debug_detector (matches_buggy + lex heuristics)",
            "method": "similarity",
            "regex_fallback": True,
            "true_positive_example": ">=0 instead of >0 for filter_positive; >50 instead of >=50 for threshold_count",
            "false_positive_example": "Correct code with coincidental substring match (low risk for threshold_count)",
        }
    if pitfall_id == "integer_division":
        return {
            "pitfall_or_debug_id": pitfall_id,
            "detector": "transfer_pitfall_detector + fcc_ast_detector",
            "method": "AST",
            "regex_fallback": True,
            "true_positive_example": "writeln(total / n) in Pascal",
            "false_positive_example": "s := 'total / n' in string literal — AST blocks",
        }
    if pitfall_id == "input_line_model":
        return {
            "pitfall_or_debug_id": pitfall_id,
            "detector": "afcc_contrast_detector (+ optional AST readln count)",
            "method": "contrast",
            "regex_fallback": False,
            "true_positive_example": "Three separate readln vs single-line input",
            "false_positive_example": "Correct multi-readln when input is line-by-line",
        }
    return {
        "pitfall_or_debug_id": pitfall_id or debug_id,
        "detector": "n/a (TCC assemble)",
        "method": "n/a",
        "regex_fallback": False,
        "true_positive_example": "n/a",
        "false_positive_example": "n/a",
    }


def audit_task(pattern_id: str) -> dict[str, Any]:
    catalog = next((r for r in _TASK_INDEX if r.get("pattern_id") == pattern_id), {})
    meta = resolve_v128_transfer_meta(pattern_id)
    db_task = load_db_task(pattern_id)
    if isinstance(db_task, dict) and db_task.get("_db_error"):
        db_available = False
        db_error = db_task["_db_error"]
        db_task = None
    else:
        db_available = db_task is not None
        db_error = None

    action = str(
        (db_task or {}).get("curriculum_showcase", {}).get("primary_action")
        or catalog.get("action")
        or ""
    ).lower()
    category = str(meta.get("transfer_type") or meta.get("transfer_category") or "")

    lang_audit = audit_language_support(pattern_id, db_task, action)
    mplt_audit = audit_mplt_pairs(pattern_id, meta, db_task)

    tests = (db_task or {}).get("test_cases") or V128_TEST_SUITES.get(pattern_id) or []
    ce = (db_task or {}).get("code_examples") or {}

    fixed_val: dict[str, Any] = {}
    buggy_val: dict[str, Any] = {}
    for lang in LANGS:
        fixed = get_lang_code(ce, lang, fixed=True) or get_reference_code(pattern_id, lang)
        fixed_val[lang] = validate_code(fixed, tests)
        if action == "debug":
            buggy = get_lang_code(ce, lang, fixed=False)
            buggy_val[lang] = validate_code(buggy, tests)

    api_nulls: dict[str, list[str]] = {}
    if db_task:
        for src, tgt in [("python", "pascal"), ("pascal", "cpp")]:
            payload = build_public_payload(db_task, source=src, target=tgt)
            api_nulls[f"{src}->{tgt}"] = check_payload_nulls(
                payload, needs_buggy=action == "debug", target=tgt
            )

    api_live = None
    if db_task and db_task.get("db_id"):
        try:
            url = f"{API}/tasks/{db_task['db_id']}?learning_language=pascal&source_language=python"
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                live = json.loads(resp.read().decode("utf-8"))
            api_live = {
                "reachable": True,
                "title": live.get("title"),
                "hints_count": len(live.get("hints") or []),
                "tests_count": len(live.get("test_cases") or []),
                "has_transfer": bool((live.get("transfer") or {}).get("proactive")),
            }
        except Exception as exc:
            api_live = {"reachable": False, "error": str(exc)[:120]}

    blockers: list[str] = []
    if not lang_audit["ok"]:
        blockers.append(f"languages:{len(lang_audit['missing'])} missing")
    if not mplt_audit["pairs_ok"]:
        blockers.append(f"mplt:{mplt_audit['pair_fail_count']} pair issues")
    if not db_available:
        blockers.append("db:task not found" if not db_error else f"db:{db_error[:60]}")
    for lang in LANGS:
        fv = fixed_val.get(lang, {})
        if fv.get("total") and fv.get("ok", 0) < fv.get("total", 0):
            blockers.append(f"fixed:{lang}={fv.get('pass')}")
    if action == "debug":
        for lang in LANGS:
            bv = buggy_val.get(lang, {})
            if bv.get("total") and bv.get("ok", 0) >= bv.get("total", 0):
                blockers.append(f"buggy:{lang} passes all (need fail)")
            notes = bv.get("notes") or []
            if any("SyntaxError" in n for n in notes):
                blockers.append(f"buggy:{lang} SyntaxError")
    for k, nulls in api_nulls.items():
        if nulls:
            blockers.append(f"api_nulls:{k}")

    return {
        "pattern_id": pattern_id,
        "title": catalog.get("title") or (db_task or {}).get("title"),
        "purpose": catalog.get("goal") or "",
        "category": category,
        "action": action,
        "catalog_format": catalog.get("format_ru"),
        "db_id": (db_task or {}).get("db_id"),
        "db_available": db_available,
        "db_error": db_error,
        "language_support": lang_audit,
        "mplt": mplt_audit,
        "detector": detector_info(meta),
        "meta": {
            "pitfall_id": meta.get("pitfall_id"),
            "debug_id": meta.get("debug_id"),
            "transfer_type": meta.get("transfer_type"),
        },
        "test_coverage": {"count": len(tests), "source": "db" if (db_task or {}).get("test_cases") else "v128_suites"},
        "fixed_validation": fixed_val,
        "buggy_validation": buggy_val if action == "debug" else "n/a",
        "api_null_checks": api_nulls,
        "api_live": api_live,
        "frontend": {
            "manual_required": True,
            "status": "NOT_CHECKED",
            "note": "Screenshots require running frontend; not verified in this audit run",
        },
        "demo_ready": len(blockers) == 0,
        "blockers": blockers,
    }


def main() -> None:
    report = {pid: audit_task(pid) for pid in AUDIT_TASKS}
    out = SCRIPTS.parent.parent / "docs" / "demo_ready_mplt_audit.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: {"demo_ready": v["demo_ready"], "blockers": v["blockers"]} for k, v in report.items()}, ensure_ascii=False, indent=2))
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
