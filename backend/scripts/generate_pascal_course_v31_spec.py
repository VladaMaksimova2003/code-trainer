#!/usr/bin/env python3
"""Generate Pascal Course v3.1.1 spec (language-neutral metadata)."""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from pascal_v31_tasks import V31_CHAPTER_TITLES, V31_TASKS
from pascal_v311_swaps import V311_SWAPS

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
V31_CSV = DOCS / "PASCAL_COURSE_V3_1_TASKS.csv"

LANG_PATTERN = re.compile(
    r"python|c#|csharp|java|console\.|dataclass|list<|charat|foreach|"
    r"namespace|streamreader|__name__|switch\s*→|→\s*pascal|/int\.parse|"
    r"math\.pow|ref/out|a,b=b,a",
    re.I,
)

PASCAL_SYNTAX_TOPICS = [
    "program", "begin", "end", "uses", "var", "const", "type", ":=", "readln", "writeln",
    "if then else", "case of", "for to", "for downto", "while", "repeat until",
    "function", "procedure", "result", "forward", "var parameter", "array", "setlength",
    "low", "high", "string", "record", "with", "unit", "interface", "implementation",
    "constructor", "destructor", "virtual", "override", "inherited", "property", "class",
    "div", "mod", "textfile", "self",
]


@dataclass(frozen=True)
class TaskSpec:
    slot_id: str
    chapter: str
    title: str
    format: str
    primary_action: str
    exercise_pattern: str
    goal: str
    pascal_features: str
    difficulty: str
    legacy_ref: str = ""


def build_tasks() -> list[TaskSpec]:
    out: list[TaskSpec] = []
    for row in V31_TASKS:
        slot_id, chapter, title, fmt, action, pattern, goal, features, diff, legacy = row
        out.append(TaskSpec(slot_id, chapter, title, fmt, action, pattern, goal, features, diff, legacy))
    assert 150 <= len(out) <= 200, len(out)
    return out


TRANSLATE_FMT = {"перевод_фрагмента", "перевод_программы"}


def format_stats(tasks: list[TaskSpec]) -> dict[str, int]:
    return dict(Counter(t.format for t in tasks))


def translate_pct(tasks: list[TaskSpec]) -> float:
    n = sum(1 for t in tasks if t.format in TRANSLATE_FMT)
    return 100 * n / len(tasks) if tasks else 0.0


def load_csv_tasks(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as f:
        return {r["slot_id"]: r for r in csv.DictReader(f, delimiter=";")}


def find_lang_refs(tasks: list[TaskSpec]) -> list[TaskSpec]:
    bad = []
    for t in tasks:
        blob = f"{t.title} {t.goal} {t.pascal_features}"
        if LANG_PATTERN.search(blob):
            bad.append(t)
    return bad


def section_analysis(tasks: list[TaskSpec]) -> list[dict]:
    by_ch: dict[str, list[TaskSpec]] = defaultdict(list)
    for t in tasks:
        by_ch[t.chapter].append(t)

    rows = []
    for key, title in V31_CHAPTER_TITLES.items():
        ch_tasks = by_ch.get(key, [])
        fmt = Counter(t.format for t in ch_tasks)
        features: set[str] = set()
        for t in ch_tasks:
            for part in re.split(r"[;,/]", t.pascal_features.lower()):
                p = part.strip()
                if p:
                    features.add(p)

        covered = [topic for topic in PASCAL_SYNTAX_TOPICS if any(topic in f for f in features)]
        weak = [topic for topic in PASCAL_SYNTAX_TOPICS if topic not in covered and _topic_in_chapter(topic, key)]

        rows.append(
            {
                "chapter_key": key,
                "chapter_title": title,
                "count": len(ch_tasks),
                "formats": dict(fmt),
                "features_covered": sorted(features),
                "weak_coverage": weak,
                "suggested_additions": _suggest_additions(key, weak, fmt),
            }
        )
    return rows


def _topic_in_chapter(topic: str, chapter: str) -> bool:
    mapping = {
        "program": "program_skeleton",
        "begin": "program_skeleton",
        "end": "program_skeleton",
        "uses": "units",
        "var": "typed_variables",
        "readln": "io",
        "if then else": "conditions",
        "case of": "conditions",
        "for to": "loops",
        "while": "loops",
        "function": "functions",
        "procedure": "procedures",
        "setlength": "dynamic_arrays",
        "record": "records",
        "property": "oop",
        "class": "oop",
    }
    return mapping.get(topic) == chapter


def _suggest_additions(chapter: str, weak: list[str], fmt: Counter) -> list[str]:
    suggestions = []
    if fmt.get("сборка_фрагмента", 0) + fmt.get("сборка_программы", 0) < 2:
        suggestions.append("Добавить сборку из блоков для ключевого синтаксиса раздела")
    if fmt.get("код_по_блок-схеме", 0) + fmt.get("блок-схема_по_коду", 0) == 0 and chapter in {
        "conditions", "loops", "recursion"
    }:
        suggestions.append("Добавить блок-схему ↔ код")
    if weak:
        suggestions.append(f"Усилить: {', '.join(weak[:3])}")
    if chapter == "compiler_diagnostics" and fmt.get("выбор_фрагмента", 0) < 2:
        suggestions.append("Добавить MCQ «выбор исправления по сообщению компилятора»")
    return suggestions


def compute_v31_changelog(v3: dict[str, dict], v31: list[TaskSpec]) -> dict:
    v31_ids = {t.slot_id for t in v31}
    v3_ids = set(v3)

    deleted = sorted(v3_ids - v31_ids)
    new = sorted(v31_ids - v3_ids)

    renamed = []
    reworked = []
    for t in v31:
        old = v3.get(t.slot_id)
        if not old:
            continue
        if old["title"] != t.title:
            renamed.append(
                {
                    "slot_id": t.slot_id,
                    "old_title": old["title"],
                    "new_title": t.title,
                    "old_format": old["task_format"],
                    "new_format": t.format,
                    "problem": _rename_reason(old),
                }
            )
        if old["task_format"] != t.format or old.get("primary_action") != t.primary_action:
            if t.slot_id not in {r["slot_id"] for r in renamed}:
                reworked.append(
                    {
                        "slot_id": t.slot_id,
                        "change": f"{old['task_format']} → {t.format}",
                        "reason": "Смена формата: меньше сопоставления, больше активных задач",
                    }
                )

    return {"deleted": deleted, "new": new, "renamed": renamed, "reworked": reworked}


def _rename_reason(old: dict) -> str:
    blob = f"{old['title']} {old.get('educational_goal', '')}"
    if LANG_PATTERN.search(blob):
        return "Убрана привязка к конкретному языку-источнику"
    if old["task_format"] == "сопоставление":
        return "Формат «сопоставление» заменён на активный (перевод/сборка/исправление)"
    return "Уточнение формулировки под концепцию, а не язык"


def write_csv(path: Path, tasks: list[TaskSpec]) -> None:
    fields = [
        "slot_id", "chapter_key", "chapter_title", "title", "task_format",
        "primary_action", "exercise_pattern_id", "educational_goal",
        "pascal_features", "difficulty", "legacy_slot_id", "collection_key",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter=";")
        w.writeheader()
        for t in tasks:
            w.writerow(
                {
                    "slot_id": t.slot_id,
                    "chapter_key": t.chapter,
                    "chapter_title": V31_CHAPTER_TITLES[t.chapter],
                    "title": t.title,
                    "task_format": t.format,
                    "primary_action": t.primary_action,
                    "exercise_pattern_id": t.exercise_pattern,
                    "educational_goal": t.goal,
                    "pascal_features": t.pascal_features,
                    "difficulty": t.difficulty,
                    "legacy_slot_id": t.legacy_ref,
                    "collection_key": t.chapter,
                }
            )


def write_json(path: Path, tasks: list[TaskSpec], sections: list[dict], before: dict | None = None) -> None:
    fmt = format_stats(tasks)
    payload = {
        "version": "3.1.1",
        "total_tasks": len(tasks),
        "language_neutral": True,
        "format_stats": fmt,
        "translate_count": sum(fmt.get(f, 0) for f in TRANSLATE_FMT),
        "translate_percent": round(translate_pct(tasks), 1),
        "chapters": [
            {"key": k, "title": V31_CHAPTER_TITLES[k], "count": sum(1 for t in tasks if t.chapter == k)}
            for k in V31_CHAPTER_TITLES
        ],
        "section_analysis": sections,
        "swaps_from_v311": list(V311_SWAPS.keys()),
        "tasks": [
            {
                "slot_id": t.slot_id,
                "chapter_key": t.chapter,
                "title": t.title,
                "task_format": t.format,
                "primary_action": t.primary_action,
                "exercise_pattern_id": t.exercise_pattern,
                "educational_goal": t.goal,
                "pascal_features": t.pascal_features,
                "difficulty": t.difficulty,
                "legacy_slot_id": t.legacy_ref or None,
            }
            for t in tasks
        ],
    }
    if before:
        payload["stats_before_v31"] = before
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_markdown(path: Path, tasks: list[TaskSpec], sections: list[dict], before_stats: dict) -> None:
    fmt = format_stats(tasks)
    asm = fmt.get("сборка_фрагмента", 0) + fmt.get("сборка_программы", 0)
    flow = fmt.get("код_по_блок-схеме", 0) + fmt.get("блок-схема_по_коду", 0)
    tr = sum(fmt.get(f, 0) for f in TRANSLATE_FMT)
    lines: list[str] = [
        "# Pascal Course v3.1.1 — спецификация курса\n",
        "> Точечная доработка v3.1 без изменения архитектуры (18 разделов, 200 задач).\n",
        f"> **Перевод:** {tr} ({translate_pct(tasks):.0f}%) · **Сборка:** {asm} · **Блок-схемы:** {flow}\n",
        "## Статистика до/после (v3.1 → v3.1.1)\n",
        "| Метрика | v3.1 | v3.1.1 |",
        "|---------|------|--------|",
        f"| Перевод | {before_stats.get('translate', '?')} ({before_stats.get('translate_pct', '?')}%) | {tr} ({translate_pct(tasks):.0f}%) |",
        f"| Сборка | {before_stats.get('assemble', '?')} | {asm} |",
        f"| Исправление | {before_stats.get('debug', '?')} | {fmt.get('исправление', 0)} |",
        f"| Поиск ошибки | {before_stats.get('find', '?')} | {fmt.get('поиск_ошибки', 0)} |",
        f"| Выбор фрагмента | {before_stats.get('mcq', '?')} | {fmt.get('выбор_фрагмента', 0)} |",
        f"| Блок-схемы | {before_stats.get('flow', '?')} | {flow} |",
        "",
        "## Замены v3.1 → v3.1.1\n",
        "| slot_id | Было | Стало | Проблема |",
        "|---------|------|-------|----------|",
    ]
    for sid, swap in sorted(V311_SWAPS.items()):
        old_t, old_f, _ = swap["old"]
        new_t, new_f, _ = swap["new"][:3]
        lines.append(f"| `{sid}` | {old_t} ({old_f}) | {new_t} ({new_f}) | {swap['problem']} |")
    lines.append("")

    lines.append("## Статистика форматов v3.1.1\n")
    lines.append("| Формат | Задач |")
    lines.append("|--------|-------|")
    for name, count in Counter(fmt).most_common():
        lines.append(f"| {name} | {count} |")
    lines.append("")

    lines.append("## Структура курса\n")
    lines.append("| № | chapter_key | Задач |")
    lines.append("|---|-------------|-------|")
    for i, (key, title) in enumerate(V31_CHAPTER_TITLES.items(), 1):
        count = sum(1 for t in tasks if t.chapter == key)
        lines.append(f"| {i} | {title} (`{key}`) | {count} |")
    lines.append("")

    lines.append("## Анализ полноты по разделам\n")
    by_ch: dict[str, list[TaskSpec]] = defaultdict(list)
    for t in tasks:
        by_ch[t.chapter].append(t)
    for s in sections:
        ch_tasks = by_ch[s["chapter_key"]]
        tr_ch = sum(1 for t in ch_tasks if t.format in TRANSLATE_FMT)
        lines.append(f"### {s['chapter_title']} — {s['count']} задач (перевод {100*tr_ch/len(ch_tasks):.0f}%)\n")
        lines.append("**Форматы:** " + ", ".join(f"{k}: {v}" for k, v in sorted(s["formats"].items())) + "\n")
        lines.append("**Pascal:** " + ", ".join(s["features_covered"][:14]) + "\n")
        if s["weak_coverage"]:
            lines.append("**Пробелы:** " + ", ".join(s["weak_coverage"][:5]) + "\n")

    lines.append("## Покрытие синтаксиса Pascal\n")
    all_features: set[str] = set()
    for t in tasks:
        for part in re.split(r"[;,/]", t.pascal_features.lower()):
            if part.strip():
                all_features.add(part.strip())
    covered = [x for x in PASCAL_SYNTAX_TOPICS if any(x in f for f in all_features)]
    missing = [x for x in PASCAL_SYNTAX_TOPICS if x not in covered]
    lines.append(f"- **Покрыто:** {len(covered)}/{len(PASCAL_SYNTAX_TOPICS)}")
    lines.append(f"- **Слабо:** {', '.join(missing) if missing else '—'}\n")

    lines.append("## Полный каталог\n")
    cur = None
    for t in tasks:
        if t.chapter != cur:
            cur = t.chapter
            lines.append(f"\n### {V31_CHAPTER_TITLES[t.chapter]}\n")
        lines.append(f"#### `{t.slot_id}` — {t.title}\n")
        lines.append(f"- **Формат:** {t.format} · **pattern:** `{t.exercise_pattern}`")
        lines.append(f"- **Цель:** {t.goal}")
        lines.append(f"- **Pascal:** {t.pascal_features} · **Сложность:** {t.difficulty}")
        if t.legacy_ref:
            lines.append(f"- **Наследие v2:** `{t.legacy_ref}`")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def _before_stats_from_csv(path: Path) -> dict:
    rows = load_csv_tasks(path)
    if not rows:
        return {}
    fmt = Counter(r["task_format"] for r in rows.values())
    tr = sum(fmt.get(f, 0) for f in TRANSLATE_FMT)
    total = len(rows)
    return {
        "translate": tr,
        "translate_pct": round(100 * tr / total, 1),
        "assemble": fmt.get("сборка_фрагмента", 0) + fmt.get("сборка_программы", 0),
        "debug": fmt.get("исправление", 0),
        "find": fmt.get("поиск_ошибки", 0),
        "mcq": fmt.get("выбор_фрагмента", 0),
        "flow": fmt.get("код_по_блок-схеме", 0) + fmt.get("блок-схема_по_коду", 0),
        "formats": dict(fmt),
    }


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    tasks = build_tasks()
    lang_refs = find_lang_refs(tasks)
    if lang_refs:
        raise SystemExit(f"Language refs in metadata: {[t.slot_id for t in lang_refs]}")

    before = _before_stats_from_csv(V31_CSV)
    sections = section_analysis(tasks)

    write_csv(DOCS / "PASCAL_COURSE_V3_1_1_TASKS.csv", tasks)
    write_json(DOCS / "PASCAL_COURSE_V3_1_1_TASKS.json", tasks, sections, before)
    write_markdown(DOCS / "PASCAL_COURSE_V3_1_1_SPEC.md", tasks, sections, before)
    tr = sum(1 for t in tasks if t.format in TRANSLATE_FMT)
    asm = sum(1 for t in tasks if t.format in {"сборка_фрагмента", "сборка_программы"})
    print(f"v3.1.1: {len(tasks)} tasks -> {DOCS}")
    print(f"  translate {before.get('translate', '?')} -> {tr} ({translate_pct(tasks):.0f}%)")
    print(f"  assemble {before.get('assemble', '?')} -> {asm}")
    print(f"  swaps={len(V311_SWAPS)}")


if __name__ == "__main__":
    main()
