#!/usr/bin/env python3
"""P0 DEMO_READY verification for task_004 (AlgorithmDebug) and task_053 (Assemble).

Usage:
  cd backend
  poetry run python scripts/demo_p0_verify.py
  poetry run python scripts/demo_p0_verify.py --json docs/demo_p0_report.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

SCRIPTS = Path(__file__).resolve().parent
BACKEND = SCRIPTS.parent
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(SCRIPTS))

import psycopg2

from application.execution.pipeline_runner import WorkerPipelineRunner
from application.tasks.services.block_reorder_helpers import build_entity_from_db
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.task.task import Task
from infrastructure.db.session import SessionLocal
from infrastructure.execution.execution_guard import mark_worker_context

DB = dict(
    host="localhost",
    port=5433,
    dbname="code_trainer",
    user="code_trainer",
    password="change_me",
)
API = "http://127.0.0.1:9000"
LANGS = ("pascal", "python", "cpp", "csharp", "java")

TASK_004_ID = 5
TASK_053_ID = 77


def parse_json(val: Any) -> Any:
    if isinstance(val, str):
        return json.loads(val)
    return val


def http_get_task(task_id: int, *, lang: str = "pascal") -> dict[str, Any]:
    url = f"{API}/tasks/{task_id}?learning_language={lang}&source_language=python"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def guest_submit(task_id: int, language: str, code: str, *, pause: float = 2.0) -> dict[str, Any]:
    body = json.dumps({"task_id": task_id, "language": language, "code": code}).encode()
    req = urllib.request.Request(
        f"{API}/guest/check",
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                queued = json.loads(resp.read().decode())
            break
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < 7:
                time.sleep(5 * (attempt + 1))
                continue
            raise
    job_id = str(queued.get("job_id") or "")
    for _ in range(240):
        with urllib.request.urlopen(f"{API}/guest/check/{job_id}", timeout=120) as resp:
            result = json.loads(resp.read().decode())
        if str(result.get("status")) in {"SUCCESS", "FAILED"}:
            if pause > 0:
                time.sleep(pause)
            return result
        time.sleep(0.5)
    return {"status": "TIMEOUT"}


def test_stats(result: dict[str, Any]) -> tuple[int, int]:
    tests = result.get("test_results") or []
    passed = sum(1 for t in tests if str(t.get("status")).upper() == "PASSED")
    return passed, len(tests)


def algo_feedback(result: dict[str, Any]) -> list[dict]:
    return [
        e
        for e in (result.get("pattern_errors") or [])
        if str(e.get("type")).upper() == "ALGORITHM"
    ]


def feedback_has_code(text: str) -> bool:
    t = str(text or "")
    return bool(
        "count := 0" in t
        or "count = 0" in t
        or "count := 1" in t
        or "amount > 0" in t
        or "> 0" in t
    )


def load_ce(task_id: int) -> dict[str, Any]:
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("select code_examples from task where id=%s", (task_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return parse_json(row[0]) if row else {}


def lang_fixed(ce: dict, lang: str) -> str:
    impl = (ce.get("implementations") or {}).get(lang) or {}
    return str(ce.get(lang) or impl.get("fixed_code") or impl.get("reference_code") or "").strip()


def lang_buggy(ce: dict, lang: str) -> str:
    impl = (ce.get("implementations") or {}).get(lang) or {}
    return str(ce.get(f"buggy_{lang}") or impl.get("buggy_code") or "").strip()


def run_pipeline(task_id: int, language: str, code: str) -> dict[str, Any]:
    runner = WorkerPipelineRunner()
    return runner.run_submission(task_id, code, language)


def assembled_from_blocks(task_id: int, lang: str) -> str:
    session = SessionLocal()
    try:
        task = session.get(Task, task_id)
        if not task or not task.block_reorder_task:
            return ""
        entity = build_entity_from_db(task, task.block_reorder_task)
        variant = entity._get_variant(lang)
        order = list(variant.get("correct_order") or entity.correct_order or [])
        blocks = list(variant.get("blocks") or entity.blocks or [])
        if not order or not blocks:
            return ""
        return entity.build_code(order, lang)
    finally:
        session.close()


def ui_before_task004() -> dict[str, Any]:
    try:
        payload = http_get_task(TASK_004_ID, lang="pascal")
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200]}
    transfer = payload.get("transfer") or {}
    hints = payload.get("hints") or []
    curriculum = payload.get("curriculum") or {}
    return {
        "ok": bool(payload.get("title") and len(hints) >= 3),
        "title": payload.get("title"),
        "hints_count": len(hints),
        "hints_sample": hints[:2],
        "post_solve_present": bool(payload.get("post_solve_explanation")),
        "post_solve_preview": (payload.get("post_solve_explanation") or "")[:120],
        "debug_id": transfer.get("debug_id") or curriculum.get("debug_id"),
        "algorithm_hint": (transfer.get("algorithm_proactive") or {}).get("text")
        or transfer.get("debug_meta", {}).get("hint_ru")
        or (hints[0] if hints else None),
        "expected_concepts_count": len(payload.get("expected_concepts") or []),
        "buggy_starter": bool(curriculum.get("buggy_pascal") or (payload.get("code_examples") or {}).get("buggy_pascal")),
    }


def ui_before_task053() -> dict[str, Any]:
    try:
        payload = http_get_task(TASK_053_ID, lang="pascal")
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200]}
    hints = payload.get("hints") or []
    blocks = payload.get("blocks") or []
    curriculum = payload.get("curriculum") or {}
    return {
        "ok": bool(payload.get("title") and len(hints) >= 3 and len(blocks) >= 8),
        "title": payload.get("title"),
        "action": curriculum.get("action"),
        "format": curriculum.get("task_format"),
        "hints_count": len(hints),
        "blocks_count": len(blocks),
        "blocks_sample": blocks[:3],
        "post_solve_present": bool(payload.get("post_solve_explanation")),
        "post_solve_preview": (payload.get("post_solve_explanation") or "")[:120],
        "original_code_head": (payload.get("original_code") or "")[:80],
        "is_palindrome": "palindrome" in str(payload.get("original_code") or "").lower()
        or "IsPalindrome" in str(payload.get("original_code") or ""),
    }


def verify_task_004(*, use_api: bool, pause: float = 3.0) -> dict[str, Any]:
    ce = load_ce(TASK_004_ID)
    lang_rows: dict[str, dict[str, Any]] = {}
    all_fixed_ok = True
    all_buggy_ok = True
    bad_submit_sample: dict[str, Any] | None = None
    fixed_submit_sample: dict[str, Any] | None = None

    def submit(task_id: int, lang: str, code: str) -> dict[str, Any]:
        if use_api:
            return guest_submit(task_id, lang, code, pause=pause)
        return run_pipeline(task_id, lang, code)

    submit_fn = submit

    for lang in LANGS:
        fixed = lang_fixed(ce, lang)
        buggy = lang_buggy(ce, lang)
        row: dict[str, Any] = {"fixed_present": bool(fixed), "buggy_present": bool(buggy)}
        if fixed:
            fr = submit_fn(TASK_004_ID, lang, fixed)
            fp, ft = test_stats(fr)
            row["fixed"] = f"{fp}/{ft}"
            row["fixed_ok"] = ft > 0 and fp == ft
            if not row["fixed_ok"]:
                all_fixed_ok = False
            if lang == "pascal" and row["fixed_ok"]:
                fixed_submit_sample = {
                    "language": lang,
                    "tests": row["fixed"],
                    "success": fr.get("success"),
                    "post_solve_in_api": ui_before_task004().get("post_solve_present"),
                }
        if buggy:
            br = submit_fn(TASK_004_ID, lang, buggy)
            bp, bt = test_stats(br)
            algo = algo_feedback(br)
            fb_text = algo[0].get("text", "") if algo else ""
            row["buggy"] = f"{bp}/{bt} pass"
            row["buggy_fails_tests"] = bt > 0 and bp < bt
            row["algorithm_feedback"] = bool(algo)
            row["feedback_has_code"] = feedback_has_code(fb_text)
            if not row["buggy_fails_tests"] or not row["algorithm_feedback"]:
                all_buggy_ok = False
            if lang == "pascal" and not bad_submit_sample:
                bad_submit_sample = {
                    "language": lang,
                    "tests": row["buggy"],
                    "algorithm_feedback": fb_text[:240],
                    "feedback_has_code": row["feedback_has_code"],
                }
        lang_rows[lang] = row

    ui = ui_before_task004()
    demo_ready = (
        all(lang_rows.get(l, {}).get("fixed_ok") for l in LANGS)
        and all(lang_rows.get(l, {}).get("buggy_fails_tests") for l in LANGS)
        and all(lang_rows.get(l, {}).get("algorithm_feedback") for l in LANGS)
        and all(lang_rows.get(l, {}).get("feedback_has_code") for l in LANGS)
        and ui.get("ok")
        and bool(bad_submit_sample and bad_submit_sample.get("feedback_has_code"))
    )
    return {
        "pattern_id": "task_004",
        "db_id": TASK_004_ID,
        "languages_validated": lang_rows,
        "ui_before": ui,
        "bad_submit": bad_submit_sample,
        "fixed_submit": fixed_submit_sample,
        "demo_ready": demo_ready,
    }


def verify_task_053(*, use_api: bool, pause: float = 3.0) -> dict[str, Any]:
    ce = load_ce(TASK_053_ID)
    lang_rows: dict[str, dict[str, Any]] = {}
    all_ref_ok = True
    all_blocks_ok = True
    fixed_submit_sample: dict[str, Any] | None = None

    def submit(task_id: int, lang: str, code: str) -> dict[str, Any]:
        if use_api:
            return guest_submit(task_id, lang, code, pause=pause)
        return run_pipeline(task_id, lang, code)

    submit_fn = submit

    for lang in LANGS:
        ref = lang_fixed(ce, lang)
        assembled = assembled_from_blocks(TASK_053_ID, lang)
        row: dict[str, Any] = {
            "ref_present": bool(ref),
            "blocks_present": bool(assembled),
            "blocks_is_palindrome": "palindrome" in assembled.lower() or "IsPalindrome" in assembled,
        }
        if ref:
            rr = submit_fn(TASK_053_ID, lang, ref)
            rp, rt = test_stats(rr)
            row["reference"] = f"{rp}/{rt}"
            row["reference_ok"] = rt > 0 and rp == rt
            if not row["reference_ok"]:
                all_ref_ok = False
        if assembled:
            ar = submit_fn(TASK_053_ID, lang, assembled)
            ap, at = test_stats(ar)
            row["assembled"] = f"{ap}/{at}"
            row["assembled_ok"] = at > 0 and ap == at
            if not row["assembled_ok"]:
                all_blocks_ok = False
            if lang == "pascal" and row["assembled_ok"]:
                fixed_submit_sample = {"language": lang, "tests": row["assembled"], "via": "blocks"}
        lang_rows[lang] = row

    ui = ui_before_task053()
    demo_ready = all_ref_ok and all_blocks_ok and ui.get("ok")
    return {
        "pattern_id": "task_053",
        "db_id": TASK_053_ID,
        "languages_validated": lang_rows,
        "ui_before": ui,
        "bad_submit": "n/a (assemble)",
        "fixed_submit": fixed_submit_sample,
        "post_solve": ui.get("post_solve_present"),
        "demo_ready": demo_ready,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", default="", help="Write full report JSON")
    parser.add_argument("--api", action="store_true", help="Use guest API instead of WorkerPipelineRunner")
    parser.add_argument("--pause", type=float, default=3.0, help="Pause seconds between guest submits")
    args = parser.parse_args()

    mark_worker_context()
    load_models()

    use_api = args.api
    if not use_api:
        try:
            urllib.request.urlopen(f"{API}/tasks/{TASK_004_ID}", timeout=5)
            use_api = True
        except Exception:
            use_api = False
    else:
        use_api = True

    report = {
        "mode": "guest_api" if use_api else "worker_pipeline",
        "task_004": verify_task_004(use_api=use_api, pause=args.pause),
        "task_053": verify_task_053(use_api=use_api, pause=args.pause),
    }

    table = []
    for key in ("task_004", "task_053"):
        r = report[key]
        langs = r.get("languages_validated") or {}
        fixed_summary = ", ".join(
            f"{l}:{langs[l].get('fixed') or langs[l].get('reference') or langs[l].get('assembled') or '—'}"
            for l in LANGS
        )
        table.append(
            {
                "task": r["pattern_id"],
                "languages validated": fixed_summary,
                "UI before": "OK" if (r.get("ui_before") or {}).get("ok") else "FAIL",
                "bad submit": "OK" if key == "task_004" and (r.get("bad_submit") or {}).get("feedback_has_code") else ("n/a" if key == "task_053" else "FAIL"),
                "fixed submit": "OK" if (r.get("fixed_submit") or {}).get("tests") else "FAIL",
                "post_solve": "OK" if (r.get("ui_before") or {}).get("post_solve_present") else "FAIL",
                "DEMO_READY": "YES" if r.get("demo_ready") else "NO",
            }
        )
    report["summary_table"] = table

    out_json = args.json or str(BACKEND.parent / "docs" / "demo_p0_report.json")
    Path(out_json).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(table, ensure_ascii=False, indent=2))
    print(f"\nWrote {out_json}")
    return 0 if all(r["DEMO_READY"] == "YES" for r in table) else 1


if __name__ == "__main__":
    raise SystemExit(main())
