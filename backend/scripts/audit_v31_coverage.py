#!/usr/bin/env python3
"""Coverage audit for Pascal Course v3.1."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = ROOT / "docs" / "PASCAL_COURSE_V3_1_1_TASKS.json"

TRANSLATE = {"перевод_фрагмента", "перевод_программы"}
ACTIVE = {
    "сборка_фрагмента", "сборка_программы", "исправление", "поиск_ошибки",
    "код_по_блок-схеме", "блок-схема_по_коду", "выбор_фрагмента",
}

FOCUS_TOPICS = [
    "begin/end", "semicolon", "compiler diagnostics", "unit", "interface",
    "implementation", "forward", "record", "pointers", "property",
    "constructor", "destructor", "virtual", "override", "inherited",
    "setlength", "pitfalls",
]

TOPIC_PATTERNS: dict[str, re.Pattern] = {
    "begin/end": re.compile(r"begin|end\.|end;|begin/end", re.I),
    "semicolon": re.compile(r"semicolon|точка с запятой|;\s*перед|dbg_semicolon|cdg_semicolon", re.I),
    "compiler diagnostics": re.compile(r"^cdg_|compiler|identifier not found|type mismatch|begin expected", re.I),
    "unit": re.compile(r"\bunit\b|uses", re.I),
    "interface": re.compile(r"\binterface\b", re.I),
    "implementation": re.compile(r"\bimplementation\b", re.I),
    "forward": re.compile(r"\bforward\b", re.I),
    "record": re.compile(r"\brecord\b", re.I),
    "pointers": re.compile(r"\^|new; dispose|pointer|tr_record_ptr", re.I),
    "property": re.compile(r"\bproperty\b|asm_property|tr_property", re.I),
    "constructor": re.compile(r"\bconstructor\b|asm_constructor|tr_constructor", re.I),
    "destructor": re.compile(r"\bdestructor\b|tr_destructor", re.I),
    "virtual": re.compile(r"\bvirtual\b", re.I),
    "override": re.compile(r"\boverride\b|dbg_override", re.I),
    "inherited": re.compile(r"\binherited\b", re.I),
    "setlength": re.compile(r"setlength|asm_setlength|asm_dyn", re.I),
    "pitfalls": re.compile(r"^pit_|pascal_pitfalls", re.I),
    "Result": re.compile(r"\bresult\b", re.I),
    "var parameter": re.compile(r"var parameter|var-параметр|asm_proc_var|dbg_var_param|dbg_pit_swap", re.I),
    "case of": re.compile(r"case of|asm_case", re.I),
    "repeat until": re.compile(r"repeat until|asm_repeat", re.I),
    "textfile": re.compile(r"textfile|assign|reset|rewrite|eof\(f\)", re.I),
}


def blob(t: dict) -> str:
    return " ".join(
        str(t.get(k, "")) for k in ("slot_id", "title", "educational_goal", "pascal_features", "exercise_pattern_id", "chapter_key")
    )


def max_consecutive_run(tasks: list[dict], key: str = "task_format") -> tuple[int, str]:
    if not tasks:
        return 0, ""
    best_n, best_v = 1, tasks[0][key]
    n, v = 1, tasks[0][key]
    for t in tasks[1:]:
        if t[key] == v:
            n += 1
            if n > best_n:
                best_n, best_v = n, v
        else:
            n, v = 1, t[key]
    return best_n, best_v


def topic_hits(tasks: list[dict]) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = defaultdict(list)
    for t in tasks:
        b = blob(t)
        for topic, pat in TOPIC_PATTERNS.items():
            if pat.search(b):
                hits[topic].append(t["slot_id"])
    return hits


def main() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    tasks = data["tasks"]
    by_ch: dict[str, list[dict]] = defaultdict(list)
    for t in tasks:
        by_ch[t["chapter_key"]].append(t)

    global_hits = topic_hits(tasks)
    print(f"TOTAL={len(tasks)}")
    print("\n=== FOCUS TOPIC COVERAGE (global) ===")
    for topic in FOCUS_TOPICS:
        ids = global_hits.get(topic, [])
        print(f"{topic}: {len(ids)} -> {', '.join(ids[:8])}{'...' if len(ids)>8 else ''}")

    print("\n=== PER CHAPTER ===")
    for ch in data["chapters"]:
        key = ch["key"]
        ts = by_ch[key]
        fmt = Counter(t["task_format"] for t in ts)
        tr = sum(fmt.get(f, 0) for f in TRANSLATE)
        act = sum(fmt.get(f, 0) for f in ACTIVE)
        run, run_fmt = max_consecutive_run(ts)
        dom = fmt.most_common(1)[0] if fmt else ("?", 0)
        ch_hits = topic_hits(ts)
        print(f"\n{key} n={len(ts)} translate={tr} active={act} tr%={100*tr/len(ts):.0f}% dom={dom[0]}:{dom[1]} max_run={run}x{run_fmt}")
        if run >= 4:
            print(f"  WARNING consecutive {run_fmt} x{run}")

    print("\n=== GLOBAL FORMAT ===")
    for k, v in data["format_stats"].items():
        print(f"  {k}: {v}")
    tr_total = sum(data["format_stats"].get(f, 0) for f in TRANSLATE)
    print(f"translate total: {tr_total} ({100*tr_total/len(tasks):.0f}%)")


if __name__ == "__main__":
    main()
