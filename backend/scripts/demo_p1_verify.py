#!/usr/bin/env python3
"""P1 DEMO_READY verification for task_006 (FCC) and task_003 (AFCC)."""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path
from typing import Any

SCRIPTS = Path(__file__).resolve().parent
BACKEND = SCRIPTS.parent
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(SCRIPTS))

import psycopg2

from application.curriculum.content.algo_syntax_showcase_meta import transfer_meta_for_language_pair
from application.curriculum.display.pitfall_messages import (
    proactive_pitfall_message,
    reactive_pitfall_message,
)
from application.curriculum.display.transfer_pitfall_detector import detect_transfer_pitfalls
from application.tasks.services.block_reorder_helpers import build_entity_from_db
from demo_fcc_afcc_content import T003_AFCC_BAD_SUBMIT_PASCAL, T006_FCC_BAD_SUBMIT_PASCAL
from demo_p0_verify import (
    API,
    DB,
    LANGS,
    assembled_from_blocks,
    guest_submit,
    http_get_task,
    lang_buggy,
    lang_fixed,
    load_ce,
    run_pipeline,
    test_stats,
)
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal
from infrastructure.db.models.task.task import Task
from infrastructure.execution.execution_guard import mark_worker_context

TASK_006_ID = 4
TASK_003_ID = 7

MPLT_PAIRS_8 = [
    ("python", "pascal"),
    ("pascal", "python"),
    ("cpp", "pascal"),
    ("pascal", "cpp"),
    ("java", "pascal"),
    ("pascal", "java"),
    ("csharp", "pascal"),
    ("pascal", "csharp"),
]


def pitfall_errors(result: dict[str, Any]) -> list[dict]:
    return [
        e
        for e in (result.get("pattern_errors") or [])
        if str(e.get("type")).upper() == "TRANSFER_PITFALL"
    ]


def feedback_has_fcc_code(text: str) -> bool:
    t = str(text or "").lower()
    return ("div" in t or "//" in t) and ("/" in t or "total" in t)


def feedback_has_afcc_code(text: str) -> bool:
    t = str(text or "").lower()
    return ("readln" in t or "input()" in t or "split" in t) and (
        "ваш код" in t or "правильный" in t or "1 2 3" in t
    )


def ui_before(task_id: int, *, lang: str = "pascal") -> dict[str, Any]:
    try:
        payload = http_get_task(task_id, lang=lang)
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200]}
    transfer = payload.get("transfer") or {}
    hints = payload.get("hints") or []
    curriculum = payload.get("curriculum") or {}
    blocks = payload.get("blocks") or []
    proactive_obj = transfer.get("proactive") or {}
    proactive_text = str(
        proactive_obj.get("text") if isinstance(proactive_obj, dict) else proactive_obj or ""
    ).strip()
    return {
        "ok": bool(payload.get("title") and len(hints) >= 3),
        "title": payload.get("title"),
        "hints_count": len(hints),
        "hints_sample": hints[:2],
        "post_solve_present": bool(payload.get("post_solve_explanation")),
        "expected_concepts_count": len(payload.get("expected_concepts") or []),
        "blocks_count": len(blocks),
        "proactive_present": bool(proactive_text.strip()),
        "proactive_has_code": feedback_has_fcc_code(proactive_text)
        or feedback_has_afcc_code(proactive_text)
        or ("//" in proactive_text or "div" in proactive_text or "split" in proactive_text),
        "action": curriculum.get("action"),
        "format": curriculum.get("task_format"),
    }


def audit_mplt_pairs(pattern_id: str, pitfall_id: str, transfer_type: str) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    all_ok = True
    for src, tgt in MPLT_PAIRS_8:
        key = f"{src}->{tgt}"
        tm = transfer_meta_for_language_pair(pattern_id, source_language=src, target_language=tgt)
        proactive = proactive_pitfall_message(pitfall_id, source_language=src, target_language=tgt) or ""
        reactive = reactive_pitfall_message(pitfall_id, source_language=src, target_language=tgt) or ""
        ok = (
            str(tm.get("transfer_type") or "").upper() == transfer_type
            and bool(proactive.strip())
            and bool(reactive.strip())
            and not proactive.lower().startswith("в этом языке")
        )
        has_code = ("//" in proactive or "div" in proactive or "split" in proactive or "readln" in proactive)
        if pitfall_id == "integer_division":
            has_code = has_code or ("//" in proactive and "div" in proactive)
        if pitfall_id == "input_line_model":
            has_code = has_code or ("split" in proactive and "readln" in proactive)
        reactive_has = (
            feedback_has_fcc_code(reactive)
            or feedback_has_afcc_code(reactive)
            or ("readln" in reactive and ("cin" in reactive or "split" in reactive or "Scanner" in reactive))
            or ("div" in reactive and "/" in reactive)
        )
        rows[key] = {
            "transfer_type": tm.get("transfer_type"),
            "proactive_preview": proactive[:100],
            "reactive_preview": reactive[:100],
            "proactive_has_code": has_code,
            "reactive_has_code": reactive_has,
            "ok": ok and has_code and reactive_has,
        }
        if not rows[key]["ok"]:
            all_ok = False
    return {"pairs": rows, "all_ok": all_ok}


def verify_task_006(*, use_api: bool, pause: float = 8.0) -> dict[str, Any]:
    ce = load_ce(TASK_006_ID)
    lang_rows: dict[str, dict[str, Any]] = {}
    fixed_submit_sample = None
    bad_submit_sample = None

    def submit(task_id: int, lang: str, code: str) -> dict[str, Any]:
        if use_api:
            return guest_submit(task_id, lang, code, pause=pause)
        return run_pipeline(task_id, lang, code)

    for lang in LANGS:
        fixed = lang_fixed(ce, lang)
        buggy = lang_buggy(ce, lang)
        row: dict[str, Any] = {"fixed_present": bool(fixed), "buggy_present": bool(buggy)}
        if fixed:
            fr = submit(TASK_006_ID, lang, fixed)
            fp, ft = test_stats(fr)
            row["fixed"] = f"{fp}/{ft}"
            row["fixed_ok"] = ft > 0 and fp == ft
        if buggy:
            br = submit(TASK_006_ID, lang, buggy)
            bp, bt = test_stats(br)
            row["buggy"] = f"{bp}/{bt} pass"
            row["buggy_fails"] = bt > 0 and bp < bt
        if lang == "pascal":
            assembled = assembled_from_blocks(TASK_006_ID, lang)
            if assembled:
                ar = submit(TASK_006_ID, lang, assembled)
                ap, at = test_stats(ar)
                row["assembled"] = f"{ap}/{at}"
                row["assembled_ok"] = at > 0 and ap == at
                if row.get("assembled_ok"):
                    fixed_submit_sample = {"language": lang, "tests": row["assembled"], "via": "blocks"}
        lang_rows[lang] = row

    br = submit(TASK_006_ID, "pascal", T006_FCC_BAD_SUBMIT_PASCAL)
    pe = pitfall_errors(br)
    fb = str(pe[0].get("text") or pe[0].get("feedback_ru") or "") if pe else ""
    bad_submit_sample = {
        "language": "pascal",
        "fcc_feedback": fb[:240],
        "feedback_has_code": feedback_has_fcc_code(fb),
        "transfer_pitfall": bool(pe),
    }

    ui = ui_before(TASK_006_ID)
    mplt = audit_mplt_pairs("task_006", "integer_division", "FCC")
    demo_ready = (
        all(r.get("fixed_ok") for r in lang_rows.values())
        and all(r.get("buggy_fails") for r in lang_rows.values())
        and ui.get("ok")
        and ui.get("proactive_has_code")
        and bad_submit_sample.get("transfer_pitfall")
        and bad_submit_sample.get("feedback_has_code")
        and mplt.get("all_ok")
        and bool(fixed_submit_sample)
    )
    return {
        "pattern_id": "task_006",
        "db_id": TASK_006_ID,
        "languages_validated": lang_rows,
        "ui_before": ui,
        "bad_submit": bad_submit_sample,
        "fixed_submit": fixed_submit_sample,
        "post_solve": ui.get("post_solve_present"),
        "mplt_pairs_8": mplt,
        "demo_ready": demo_ready,
    }


def verify_task_003(*, use_api: bool, pause: float = 8.0) -> dict[str, Any]:
    ce = load_ce(TASK_003_ID)
    lang_rows: dict[str, dict[str, Any]] = {}
    fixed_submit_sample = None
    bad_submit_sample = None

    def submit(task_id: int, lang: str, code: str) -> dict[str, Any]:
        if use_api:
            return guest_submit(task_id, lang, code, pause=pause)
        return run_pipeline(task_id, lang, code)

    for lang in LANGS:
        fixed = lang_fixed(ce, lang)
        buggy = lang_buggy(ce, lang)
        row: dict[str, Any] = {"fixed_present": bool(fixed), "buggy_present": bool(buggy)}
        if fixed:
            fr = submit(TASK_003_ID, lang, fixed)
            fp, ft = test_stats(fr)
            row["fixed"] = f"{fp}/{ft}"
            row["fixed_ok"] = ft > 0 and fp == ft
            if lang == "pascal" and row["fixed_ok"]:
                fixed_submit_sample = {"language": lang, "tests": row["fixed"]}
        if buggy:
            br = submit(TASK_003_ID, lang, buggy)
            bp, bt = test_stats(br)
            row["buggy"] = f"{bp}/{bt} pass"
            row["buggy_fails"] = bt > 0 and bp < bt
        lang_rows[lang] = row

    br = submit(TASK_003_ID, "pascal", T003_AFCC_BAD_SUBMIT_PASCAL)
    pe = pitfall_errors(br)
    fb = str(pe[0].get("text") or pe[0].get("feedback_ru") or "") if pe else ""
    bad_submit_sample = {
        "language": "pascal",
        "afcc_feedback": fb[:240],
        "feedback_has_code": feedback_has_afcc_code(fb),
        "transfer_pitfall": bool(pe),
    }

    ui = ui_before(TASK_003_ID)
    mplt = audit_mplt_pairs("task_003", "input_line_model", "AFCC")
    demo_ready = (
        all(r.get("fixed_ok") for r in lang_rows.values())
        and all(r.get("buggy_fails") for r in lang_rows.values())
        and ui.get("ok")
        and ui.get("proactive_has_code")
        and bad_submit_sample.get("transfer_pitfall")
        and bad_submit_sample.get("feedback_has_code")
        and mplt.get("all_ok")
        and bool(fixed_submit_sample)
    )
    return {
        "pattern_id": "task_003",
        "db_id": TASK_003_ID,
        "languages_validated": lang_rows,
        "ui_before": ui,
        "bad_submit": bad_submit_sample,
        "fixed_submit": fixed_submit_sample,
        "post_solve": ui.get("post_solve_present"),
        "mplt_pairs_8": mplt,
        "demo_ready": demo_ready,
    }


def summary_row(task: dict[str, Any]) -> dict[str, str]:
    langs = task.get("languages_validated") or {}
    parts = []
    for lang in LANGS:
        r = langs.get(lang) or {}
        parts.append(f"{lang}:{r.get('fixed', '?')}")
    return {
        "task": task.get("pattern_id"),
        "languages validated": ", ".join(parts),
        "UI before": "OK" if (task.get("ui_before") or {}).get("ok") else "FAIL",
        "bad submit": "OK" if (task.get("bad_submit") or {}).get("transfer_pitfall") else "FAIL",
        "fixed submit": "OK" if task.get("fixed_submit") else "FAIL",
        "post_solve": "OK" if task.get("post_solve") else "FAIL",
        "DEMO_READY": "YES" if task.get("demo_ready") else "NO",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", default="")
    parser.add_argument("--api", action="store_true")
    parser.add_argument("--pause", type=float, default=8.0)
    args = parser.parse_args()

    mark_worker_context()
    load_models()

    use_api = args.api
    if not use_api:
        try:
            urllib.request.urlopen(f"{API}/tasks/{TASK_006_ID}", timeout=5)
            use_api = True
        except Exception:
            use_api = False

    t6 = verify_task_006(use_api=use_api, pause=args.pause)
    t3 = verify_task_003(use_api=use_api, pause=args.pause)
    report = {
        "mode": "guest_api" if use_api else "worker_pipeline",
        "task_006": t6,
        "task_003": t3,
        "summary_table": [summary_row(t6), summary_row(t3)],
    }
    print(json.dumps(report["summary_table"], ensure_ascii=False, indent=2))
    if args.json:
        Path(args.json).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote {args.json}")
    return 0 if t6.get("demo_ready") and t3.get("demo_ready") else 1


if __name__ == "__main__":
    raise SystemExit(main())
