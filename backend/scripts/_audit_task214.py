#!/usr/bin/env python3
import json
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
data = json.loads((BACKEND / "algo_syntax_course.json").read_text(encoding="utf-8"))

print("=== strings chapter placeholder tasks ===")
for t in data:
    if t.get("chapter_key") == "strings" and t.get("format_ru") == "сборка_фрагмента":
        n = t["task_num"]
        impl = t.get("implementations", {}).get("pascal", {})
        print(n, t.get("title"))
        print("  short:", t.get("short_goal"))
        print("  desc:", t.get("detailed_description"))
        print("  ph:", (impl.get("placeholder_code") or "")[:100])

print("\n=== weak / missing placeholder audit ===")
weak = []
for t in data:
    desc = str(t.get("detailed_description") or "").strip()
    short = str(t.get("short_goal") or "").strip()
    title = str(t.get("title") or "").strip()
    fmt = t.get("format_ru")
    impl = t.get("implementations", {}).get("pascal", {})
    ph = str(impl.get("placeholder_code") or "").strip()
    gaps = impl.get("gaps") or []
    bad_desc = (
        not desc
        or desc == title
        or (desc == short and len(desc) < 30)
        or (len(desc) < 20)
    )
    missing_ph = fmt == "сборка_фрагмента" and (not ph or "___" not in ph)
    missing_gaps = fmt == "сборка_фрагмента" and not gaps
    if bad_desc or missing_ph or missing_gaps:
        weak.append(
            {
                "n": t["task_num"],
                "title": title[:50],
                "fmt": fmt,
                "bad_desc": bad_desc,
                "missing_ph": missing_ph,
                "desc_len": len(desc),
            }
        )
print("issues:", len(weak))
for w in weak:
    print(w)
