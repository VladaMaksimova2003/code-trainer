#!/usr/bin/env python3
"""Final implementation-readiness audit for Pascal Course v3.1.1."""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = ROOT / "docs" / "PASCAL_COURSE_V3_1_1_TASKS.csv"

DIFF = {"easy": 1, "medium": 2, "hard": 3}
TRANSLATE = {"перевод_фрагмента", "перевод_программы"}

CHAPTER_ORDER = [
    "program_skeleton", "typed_variables", "io", "expressions", "conditions", "loops",
    "functions", "procedures", "static_arrays", "dynamic_arrays", "strings", "records",
    "files", "units", "recursion", "oop", "pascal_pitfalls", "compiler_diagnostics",
]

CHAPTER_DEPS: dict[str, list[str]] = {
    "program_skeleton": [],
    "typed_variables": ["program_skeleton"],
    "io": ["program_skeleton", "typed_variables"],
    "expressions": ["typed_variables"],
    "conditions": ["expressions", "io"],
    "loops": ["conditions", "expressions"],
    "functions": ["conditions", "loops", "typed_variables"],
    "procedures": ["functions"],
    "static_arrays": ["loops", "typed_variables"],
    "dynamic_arrays": ["static_arrays", "procedures"],
    "strings": ["loops", "static_arrays"],
    "records": ["typed_variables", "static_arrays"],
    "files": ["loops", "io"],
    "units": ["functions", "procedures"],
    "recursion": ["functions", "forward"],
    "oop": ["records", "units", "procedures", "functions"],
    "pascal_pitfalls": ["*prior*"],
    "compiler_diagnostics": ["*prior*"],
}

FEATURE_PATTERNS: dict[str, re.Pattern] = {
    "program": re.compile(r"\bprogram\b", re.I),
    "begin/end": re.compile(r"begin|end\.|begin/end", re.I),
    ";": re.compile(r"semicolon|точка с запятой|;\s*перед|dbg_semicolon|cdg_semicolon", re.I),
    "if then else": re.compile(r"if then else|else if|dbg_if|tr_if|asm_if|flow_if", re.I),
    "case of": re.compile(r"case of|asm_case|flow_case|mcq_case", re.I),
    "for": re.compile(r"for to|for to do|asm_for|tr_for|flow_for|dbg_for|cdg_for", re.I),
    "downto": re.compile(r"downto|flow_downto|asm_for_downto", re.I),
    "while": re.compile(r"while do|flow_while|mcq_while", re.I),
    "repeat until": re.compile(r"repeat until|asm_repeat|flow_repeat|dbg_repeat|dbg_pit_until", re.I),
    "function": re.compile(r"\bfunction\b|asm_function|tr_function|dbg_function|dbg_rec", re.I),
    "Result": re.compile(r"\bresult\b|dbg_result|cdg_result|dbg_pit_result|dbg_pit_exit", re.I),
    "Exit": re.compile(r"\bexit\b|tr_exit", re.I),
    "forward": re.compile(r"\bforward\b|asm_forward|mcq_forward|cdg_forward|dbg_forward", re.I),
    "procedure": re.compile(r"\bprocedure\b|tr_procedure|asm_proc|dbg_proc|dbg_pit_proc", re.I),
    "var parameter": re.compile(r"\bvar\b.*param|dbg_var|asm_proc_var|dbg_pit_swap|dbg_value_vs_var|tr_byref", re.I),
    "const parameter": re.compile(r"const param|tr_const_param|const;", re.I),
    "array": re.compile(r"\barray\b|asm_array|tr_static|tr_fixed|dbg_bounds|dbg_dyn|dbg_pit_dyn", re.I),
    "Low/High": re.compile(r"\blow\b|\bhigh\b|mcq_low_high|dbg_pit_low", re.I),
    "dynamic array": re.compile(r"setlength|dynamic|finalize|asm_dyn|tr_setlength|mcq_setlength", re.I),
    "SetLength": re.compile(r"setlength|asm_setlength|mcq_setlength|dbg_setlength|flow_setlength|dbg_pit_setlength", re.I),
    "string": re.compile(r"\bstring\b|str_|asm_string|tr_string|mcq_string|dbg_pit_string", re.I),
    "Copy": re.compile(r"\bcopy\b|asm_dyn_copy|asm_string_copy|tr_copy|tr_array_copy", re.I),
    "record": re.compile(r"\brecord\b|asm_record|tr_variant|dbg_record", re.I),
    "with": re.compile(r"\bwith\b|asm_with|tr_with|dbg_with|dbg_pit_with", re.I),
    "pointer (^)": re.compile(r"\^|pointer|dbg_ptr|dbg_pit_nil", re.I),
    "nil": re.compile(r"\bnil\b|dbg_pit_nil", re.I),
    "New": re.compile(r"\bnew\b|asm_new|dbg_pit_dispose", re.I),
    "Dispose": re.compile(r"\bdispose\b|asm_new_dispose|dbg_pit_dispose", re.I),
    "TextFile": re.compile(r"textfile|asm_textfile|tr_textfile|fil_", re.I),
    "Assign": re.compile(r"\bassign\b|dbg_assign", re.I),
    "Reset": re.compile(r"\breset\b|asm_textfile", re.I),
    "Rewrite": re.compile(r"\brewrite\b|mcq_rewrite|asm_textfile_write", re.I),
    "unit": re.compile(r"\bunit\b|unt_|dbg_pit_unit|cdg_unit", re.I),
    "uses": re.compile(r"\buses\b|mcq_uses|tr_uses|dbg_circular", re.I),
    "interface": re.compile(r"\binterface\b|mcq_interface|asm_unit_interface|pit_13|oop_14", re.I),
    "implementation": re.compile(r"\bimplementation\b|asm_unit_implementation|asm_unit_full", re.I),
    "initialization": re.compile(r"initialization|dbg_unit_init", re.I),
    "finalization": re.compile(r"finalization|dbg_unit_init", re.I),
    "class": re.compile(r"\bclass\b|asm_class|oop_|cdg_class|dbg_class", re.I),
    "constructor": re.compile(r"\bconstructor\b|asm_constructor|tr_constructor", re.I),
    "destructor": re.compile(r"\bdestructor\b|asm_destructor", re.I),
    "inherited": re.compile(r"\binherited\b|dbg_inherited", re.I),
    "Self": re.compile(r"\bself\b|asm_method_self", re.I),
    "virtual": re.compile(r"\bvirtual\b|asm_virtual|cdg_virtual|dbg_virtual", re.I),
    "override": re.compile(r"\boverride\b|dbg_inherited_override|cdg_virtual", re.I),
    "property": re.compile(r"\bproperty\b|asm_property|dbg_property|cdg_property|pit_24", re.I),
}

FORMAT_BUILDER = {
    "перевод_программы": ("translate", "translation_to_pascal", True),
    "перевод_фрагмента": ("translate", "translation_snippet_to_pascal", False),
    "исправление": ("debug", "pascal_debug_starter", True),
    "поиск_ошибки": ("debug", "pascal_debug_starter", True),
    "сборка_программы": ("assemble", "block_reorder_pascal", True),
    "сборка_фрагмента": ("assemble", "block_reorder_pascal", True),
    "код_по_блок-схеме": ("implement", "flowchart_pascal", True),
    "блок-схема_по_коду": ("implement", "flowchart_pascal", True),
    "выбор_фрагмента": ("implement", "mcq_pascal_fragment", False),
}

EXISTING_BUILDERS = {
    "translation_to_pascal", "translation_python_to_pascal",
    "block_reorder_pascal", "flowchart_pascal",
    "pascal_io_program", "pascal_debug_starter",
}


def load_tasks() -> list[dict]:
    with open(CSV_PATH, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))


def blob(t: dict) -> str:
    return " ".join(
        str(t.get(k, ""))
        for k in ("slot_id", "title", "educational_goal", "pascal_features", "exercise_pattern_id", "chapter_key")
    )


def max_consecutive(tasks: list[dict], key: str = "task_format") -> tuple[int, str]:
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


def chapter_index(ch: str) -> int:
    try:
        return CHAPTER_ORDER.index(ch)
    except ValueError:
        return 999


def feature_hits(tasks: list[dict]) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = defaultdict(list)
    for t in tasks:
        b = blob(t)
        for feat, pat in FEATURE_PATTERNS.items():
            if pat.search(b):
                hits[feat].append(t["slot_id"])
    return hits


def normalize_dup_key(t: dict) -> str:
    feats = re.sub(r"\s+", " ", t.get("pascal_features", "").lower().strip())
    fmt = t["task_format"]
    action = t["primary_action"]
    # cluster by core feature + action family
    core = feats.split(";")[0].strip() if feats else t["title"][:30].lower()
    return f"{core}|{action}|{fmt}"


def main() -> None:
    tasks = load_tasks()
    by_ch: dict[str, list[dict]] = defaultdict(list)
    for t in tasks:
        by_ch[t["collection_key"]].append(t)

    print("=" * 72)
    print("PASCAL COURSE v3.1.1 — IMPLEMENTATION READINESS AUDIT")
    print("=" * 72)
    print(f"Tasks: {len(tasks)}  Chapters: {len(CHAPTER_ORDER)}")

    # Part 1: progression
    print("\n## PART 1 — DIFFICULTY PROGRESSION\n")
    jumps: list[tuple[str, str, str, str, str]] = []
    new_topic_hard: list[tuple[str, str, str]] = []
    for ch in CHAPTER_ORDER:
        ch_tasks = by_ch[ch]
        diffs = [t["difficulty"] for t in ch_tasks]
        seq = " -> ".join(f"{t['slot_id']}({t['difficulty'][0]})" for t in ch_tasks)
        print(f"### {ch} ({len(ch_tasks)} tasks)")
        print(seq)
        for i in range(1, len(ch_tasks)):
            prev, cur = ch_tasks[i - 1], ch_tasks[i]
            dp, dc = DIFF[prev["difficulty"]], DIFF[cur["difficulty"]]
            if dc - dp >= 2:
                jumps.append((ch, prev["slot_id"], cur["slot_id"], prev["difficulty"], cur["difficulty"]))
            if dc == 3 and dp <= 1:
                # first hard without medium in same feature?
                pf_prev = set(re.split(r"[;,/]", prev.get("pascal_features", "").lower()))
                pf_cur = set(re.split(r"[;,/]", cur.get("pascal_features", "").lower()))
                if not pf_prev & pf_cur and i < 3:
                    new_topic_hard.append((ch, cur["slot_id"], cur["pascal_features"]))
        print()

    print("### Sharp jumps (easy->hard or +2 levels)")
    for ch, a, b, da, db in jumps:
        print(f"  {ch}: {a}({da}) -> {b}({db})  -> swap {b} after easier tasks on same topic")
    if not jumps:
        print("  (none +2 level jumps within consecutive pairs)")
    print("\n### New topic first as hard (early in section)")
    for ch, sid, feat in new_topic_hard:
        print(f"  {ch}: {sid} hard on '{feat}'")

    # Part 2: dependencies
    print("\n## PART 2 — DEPENDENCY GRAPH\n")
    for ch in CHAPTER_ORDER:
        deps = CHAPTER_DEPS.get(ch, [])
        print(f"  {ch} <- {', '.join(deps) if deps else '(entry)'}")
    print("\n### Forward-reference risks (feature appears before chapter teaches it)")
    risks: list[tuple[str, str, str, str]] = []
    feature_first_ch: dict[str, str] = {}
    for ch in CHAPTER_ORDER:
        for t in by_ch[ch]:
            b = blob(t)
            for feat, pat in FEATURE_PATTERNS.items():
                if pat.search(b):
                    if feat not in feature_first_ch:
                        feature_first_ch[feat] = ch
    teach_ch = {
        "forward": "functions", "SetLength": "dynamic_arrays", "New": "records",
        "class": "oop", "unit": "units", "property": "oop", "TextFile": "files",
    }
    for ch in CHAPTER_ORDER:
        for t in by_ch[ch]:
            b = blob(t)
            for feat, teach in teach_ch.items():
                if FEATURE_PATTERNS[feat].search(b) and chapter_index(ch) < chapter_index(teach):
                    risks.append((t["slot_id"], ch, feat, teach))
    for r in risks[:25]:
        print(f"  {r[0]} in {r[1]} uses {r[2]} before {r[3]}")
    if len(risks) > 25:
        print(f"  ... +{len(risks)-25} more")
    print(f"\nTotal forward-reference flags: {len(risks)} (many OK for transfer course)")

    # Part 3: coverage matrix
    print("\n## PART 3 — COVERAGE MATRIX\n")
    hits = feature_hits(tasks)
    print(f"{'Feature':<22} {'Count':>5}  {'Verdict':<12}  Chapters")
    for feat in FEATURE_PATTERNS:
        sids = hits.get(feat, [])
        n = len(sids)
        chs = sorted({t["collection_key"] for t in tasks if t["slot_id"] in sids}, key=chapter_index)
        if n == 0:
            v = "MISSING"
        elif n == 1:
            v = "weak"
        elif n <= 3:
            v = "OK"
        elif n <= 8:
            v = "good"
        else:
            v = "excess"
        ch_short = ", ".join(chs[:4]) + ("…" if len(chs) > 4 else "")
        print(f"{feat:<22} {n:>5}  {v:<12}  {ch_short}")

    # Part 4: duplicates
    print("\n## PART 4 — HIDDEN DUPLICATES\n")
    clusters: dict[str, list[dict]] = defaultdict(list)
    for t in tasks:
        key = normalize_dup_key(t)
        clusters[key].append(t)
    dup_groups = [(k, v) for k, v in clusters.items() if len(v) >= 2]
    dup_groups.sort(key=lambda x: -len(x[1]))
    semantic_groups = [
        ("SetLength", re.compile(r"setlength", re.I)),
        ("Result", re.compile(r"\bresult\b", re.I)),
        ("override/virtual", re.compile(r"override|virtual", re.I)),
        ("property", re.compile(r"property", re.I)),
        ("forward", re.compile(r"forward", re.I)),
        ("; before else", re.compile(r"else|semicolon_else|pit_else", re.I)),
    ]
    for label, pat in semantic_groups:
        matched = [t["slot_id"] for t in tasks if pat.search(blob(t))]
        if len(matched) >= 2:
            print(f"  {label} ({len(matched)}): {', '.join(matched)}")

    # Part 5: formats
    print("\n## PART 5 — FORMAT AUDIT BY CHAPTER\n")
    fmt_global = Counter(t["task_format"] for t in tasks)
    tr_total = sum(fmt_global[f] for f in TRANSLATE)
    print(f"Global translate: {tr_total} ({100*tr_total/len(tasks):.1f}%)")
    warn = []
    for ch in CHAPTER_ORDER:
        ct = by_ch[ch]
        fc = Counter(t["task_format"] for t in ct)
        tr = sum(fc[f] for f in TRANSLATE)
        mr, mv = max_consecutive(ct)
        parts = ", ".join(f"{k}={v}" for k, v in sorted(fc.items(), key=lambda x: -x[1]))
        line = f"  {ch} n={len(ct)} tr={100*tr/len(ct):.0f}% max_run={mr}x{mv[:12]}"
        print(line)
        print(f"    {parts}")
        if mr >= 4:
            warn.append((ch, mr, mv))
        if tr / len(ct) > 0.5:
            warn.append((ch, "translate-heavy", f"{100*tr/len(ct):.0f}%"))
    print("\nWarnings:", warn if warn else "none critical")

    # Part 6: patterns / builders
    print("\n## PART 6 — PATTERN / BUILDER READINESS\n")
    patterns: dict[str, list[dict]] = defaultdict(list)
    missing_pattern = []
    for t in tasks:
        pid = t.get("exercise_pattern_id", "").strip()
        if not pid:
            missing_pattern.append(t["slot_id"])
        patterns[pid].append(t)
    print(f"Unique pattern_ids: {len(patterns)}")
    print(f"Tasks without pattern_id: {missing_pattern or 'none'}")
    multi_fmt: list[tuple[str, set]] = []
    for pid, ts in patterns.items():
        fmts = {t["task_format"] for t in ts}
        if len(fmts) > 1:
            multi_fmt.append((pid, fmts))
    print(f"Patterns used with multiple task_formats: {len(multi_fmt)}")
    for pid, fmts in sorted(multi_fmt)[:10]:
        print(f"  {pid}: {fmts}")

    print("\nBuilder summary by task_format:")
    for fmt, (act, bld, exists) in FORMAT_BUILDER.items():
        n = fmt_global.get(fmt, 0)
        status = "EXISTS" if exists and bld in EXISTING_BUILDERS else "NEEDS NEW"
        print(f"  {fmt}: n={n} builder={bld} [{status}]")

    new_patterns = len(patterns)
    print(f"\nAll {new_patterns} pattern_ids need content payloads at seed time.")
    print("Reuse: same builder + different extra payload per pattern_id.")

    # export json summary
    out = ROOT / "docs" / "PASCAL_COURSE_V3_1_1_IMPLEMENTATION_AUDIT.json"
    summary = {
        "tasks": len(tasks),
        "chapters": len(CHAPTER_ORDER),
        "translate_percent": round(100 * tr_total / len(tasks), 1),
        "sharp_jumps": [{"chapter": j[0], "from": j[1], "to": j[2]} for j in jumps],
        "forward_reference_flags": len(risks),
        "unique_patterns": len(patterns),
        "builders_needed_new": ["translation_snippet_to_pascal", "mcq_pascal_fragment"],
        "builders_existing": sorted(EXISTING_BUILDERS),
        "format_warnings": [{"chapter": w[0], "issue": str(w[1])} for w in warn],
        "coverage": {f: len(hits.get(f, [])) for f in FEATURE_PATTERNS},
    }
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
