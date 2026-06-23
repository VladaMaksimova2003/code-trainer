#!/usr/bin/env python3
"""One-off DB probe for demo task audit."""
import json
import sys
import urllib.request
from pathlib import Path

import psycopg2

SCRIPTS = Path(__file__).resolve().parent
BACKEND = SCRIPTS.parent
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(SCRIPTS))

from application.curriculum.content.algo_syntax_showcase_meta import transfer_meta_for_language_pair  # noqa: E402

DB = dict(host="localhost", port=5433, dbname="code_trainer", user="code_trainer", password="change_me")
API = "http://127.0.0.1:9000"
LANGS = ("pascal", "python", "cpp", "csharp", "java")
PAIRS = [
    ("python", "pascal"), ("python", "cpp"), ("python", "csharp"), ("python", "java"),
    ("pascal", "python"), ("pascal", "cpp"), ("pascal", "csharp"), ("pascal", "java"),
    ("cpp", "pascal"), ("cpp", "python"), ("cpp", "csharp"), ("cpp", "java"),
    ("csharp", "pascal"), ("csharp", "python"), ("csharp", "cpp"), ("csharp", "java"),
    ("java", "pascal"), ("java", "python"), ("java", "cpp"), ("java", "csharp"),
]

def probe(pid):
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute(
        """select id, title, description, test_cases, code_examples
           from task where code_examples->'curriculum_showcase'->>'slot_pattern_id'=%s""",
        (pid,),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return {"error": "not found"}
    did, title, desc, tests, ce = row
    ce = json.loads(ce) if isinstance(ce, str) else ce
    tests = json.loads(tests) if isinstance(tests, str) else tests
    showcase = ce.get("curriculum_showcase") or {}
    impls = ce.get("implementations") or {}

    lang_detail = {}
    for lang in LANGS:
        impl = impls.get(lang) or {}
        lang_detail[lang] = {
            "fixed": bool(str(ce.get(lang) or impl.get("fixed_code") or impl.get("reference_code") or "").strip()),
            "buggy": bool(str(ce.get(f"buggy_{lang}") or impl.get("buggy_code") or "").strip()),
            "hints": len((ce.get("hints") or {}).get(lang) or ce.get("hints") or []) if isinstance(ce.get("hints"), dict) else len(ce.get("hints") or []),
            "post_solve": bool(str((ce.get("post_solve_explanation") or {}).get(lang) or ce.get("post_solve_explanation") or "").strip() if isinstance(ce.get("post_solve_explanation"), dict) else ce.get("post_solve_explanation")),
            "expected_concepts": len((ce.get("expected_concepts") or {}).get(lang) or (ce.get("expected_concepts") or {}).get("all") or []),
        }

    mplt = {}
    for src, tgt in PAIRS:
        tm = transfer_meta_for_language_pair(pid, source_language=src, target_language=tgt)
        proactive = (tm.get("proactive") or {}).get("text") or ""
        mplt[f"{src}->{tgt}"] = {
            "transfer_type": tm.get("transfer_type"),
            "proactive": bool(proactive),
            "proactive_len": len(proactive),
            "has_code_in_proactive": bool("div" in proactive or "readln" in proactive or "range" in proactive or "//" in proactive or len(proactive) > 60),
        }

    api = {}
    try:
        url = f"{API}/tasks/{did}?learning_language=pascal&source_language=python"
        with urllib.request.urlopen(url, timeout=15) as resp:
            live = json.loads(resp.read().decode())
        curriculum = live.get("curriculum") or {}
        api = {
            "title": live.get("title"),
            "description": bool(live.get("description")),
            "pattern_id": curriculum.get("slot_pattern_id"),
            "action": curriculum.get("action") or curriculum.get("primary_action"),
            "task_format": curriculum.get("task_format"),
            "test_cases": len(live.get("test_cases") or []),
            "hints": len(live.get("hints") or []),
            "post_solve": bool(live.get("post_solve_explanation")),
            "expected_concepts": len(live.get("expected_concepts") or []),
            "code_examples": bool(live.get("code_examples")),
            "blocks": len(live.get("blocks") or []),
            "transfer_proactive": bool((live.get("transfer") or {}).get("proactive", {}).get("text")),
        }
    except Exception as e:
        api = {"error": str(e)[:100]}

    return {
        "db_id": did,
        "title": title,
        "action": showcase.get("primary_action"),
        "format": showcase.get("task_format"),
        "tests_count": len(tests or []),
        "lang_detail": lang_detail,
        "mplt_summary": {
            "pairs_with_proactive": sum(1 for v in mplt.values() if v["proactive"]),
            "pairs_total": len(mplt),
            "all_transfer_type_ok": len(set(v["transfer_type"] for v in mplt.values())) == 1,
        },
        "mplt_sample": {k: mplt[k] for k in list(mplt)[:3]},
        "api": api,
        "ce_top_keys": sorted(ce.keys())[:30],
    }

if __name__ == "__main__":
    pids = sys.argv[1:] or ["task_006", "task_003", "task_053"]
    out = {p: probe(p) for p in pids}
    print(json.dumps(out, ensure_ascii=False, indent=2))
