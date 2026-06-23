#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from infrastructure.db.models.task.registry import load_models

load_models()
from infrastructure.db.session import SessionLocal
from application.curriculum.mirror.pedagogical_task_store import iter_showcase_tasks
from application.curriculum.content.v4_assembly_builder import assembly_payload_for_format

s = SessionLocal()
rows = []
for row, sh in iter_showcase_tasks(s):
    if str(sh.get("collection_key") or "") != "algo_basics":
        continue
    num = int(sh.get("task_num") or 0)
    if not 1 <= num <= 8:
        continue
    ex = row.code_examples or {}
    hints = ex.get("hints") or []
    buggy_py = str(ex.get("buggy_pascal") or "")[:80]
    pattern = str(sh.get("slot_pattern_id") or sh.get("exercise_pattern_id") or "")
    fmt = str(sh.get("task_format") or "")
    # fragment template check
    frag_gaps = None
    if fmt == "сборка_фрагмента" and pattern:
        code = str(ex.get("pascal") or "")
        if code:
            _, tmpl, blocks, _ = assembly_payload_for_format(
                fmt, "pascal", code, pattern_id=pattern
            )
            frag_gaps = tmpl.count("{0}") + tmpl.count("{1}") + tmpl.count("{2}")
    rows.append(
        {
            "num": num,
            "id": row.id,
            "title": row.title,
            "pattern": pattern,
            "format": fmt,
            "hints_n": len(hints),
            "hints": hints,
            "buggy_snip": buggy_py.replace("\n", " "),
            "frag_gaps": frag_gaps,
        }
    )
s.close()
for r in sorted(rows, key=lambda x: x["num"]):
    print(f"#{r['num']} id={r['id']} {r['pattern']} fmt={r['format']} hints={r['hints_n']} gaps={r['frag_gaps']}")
    for h in r["hints"]:
        print(f"   - {h}")
    if r["buggy_snip"]:
        print(f"   buggy: {r['buggy_snip']}...")
