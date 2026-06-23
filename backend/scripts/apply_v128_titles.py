#!/usr/bin/env python3
"""Apply v128_task_titles to algo_v128_catalog._TASK_INDEX."""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from algo_v128_catalog import (  # noqa: E402
    V128_CHAPTER_ORDER,
    V128_CHAPTER_TITLES,
    V128_CORE_TASK_COUNT,
    _TASK_INDEX,
)
from v128_task_titles import V128_TASK_TITLES  # noqa: E402

FORMAT_PRODUCT = {
    "сборка_фрагмента": "Собрать",
    "сборка_программы": "Собрать",
    "перевод_программы": "Написать",
    "перевод_фрагмента": "Написать",
    "исправление": "Исправить",
    "поиск_ошибки": "Исправить",
}


def _py_literal(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def apply_titles_to_catalog(*, dry_run: bool = False) -> int:
    catalog_path = _SCRIPTS / "algo_v128_catalog.py"
    text = catalog_path.read_text(encoding="utf-8")
    changed = 0
    for item in _TASK_INDEX:
        num = int(item["task_num"])
        new_title = V128_TASK_TITLES[num]
        old_title = str(item["title"])
        if old_title == new_title:
            continue
        pattern = (
            rf'(\{{"task_num": {num}, "chapter_key": "[^"]+", "title": )'
            + re.escape(json.dumps(old_title, ensure_ascii=False))
            + r"(,)"
        )
        replacement = rf"\1{_py_literal(new_title)}\2"
        new_text, n = re.subn(pattern, replacement, text, count=1)
        if n != 1:
            raise RuntimeError(f"Failed to patch task {num}: {old_title!r} -> {new_title!r}")
        text = new_text
        changed += 1
    if not dry_run and changed:
        catalog_path.write_text(text, encoding="utf-8")
    return changed


def export_task_list(task_index, out_json: Path, out_md: Path) -> None:
    rows = []
    md_lines = ["# Курс v128 — 128 заданий (заголовки согласованы с goal)\n"]
    by_ch: dict[str, list] = {k: [] for k in V128_CHAPTER_ORDER}
    for item in task_index:
        num = int(item["task_num"])
        title = V128_TASK_TITLES[num]
        by_ch[item["chapter_key"]].append((num, title, item))

    for ch_i, ch_key in enumerate(V128_CHAPTER_ORDER, 1):
        md_lines.append(f"\n## {ch_i}. {V128_CHAPTER_TITLES[ch_key]}\n")
        md_lines.append("| № | Slot | Формат | Название |")
        md_lines.append("|---:|---|---|---|")
        for num, title, item in by_ch[ch_key]:
            fmt = FORMAT_PRODUCT.get(item["format_ru"], item["format_ru"])
            rows.append(
                {
                    "num": num,
                    "chapter": ch_i,
                    "chapter_title": V128_CHAPTER_TITLES[ch_key],
                    "chapter_key": ch_key,
                    "slot_pascal": f"pas_{num:03d}",
                    "slot_python": f"py_{num:03d}",
                    "title": title,
                    "format_ru": item["format_ru"],
                    "format_product": fmt,
                    "action": item["action"],
                    "difficulty": item["difficulty"],
                    "pattern_id": item["pattern_id"],
                    "goal": item["goal"],
                    "features": item["features"],
                }
            )
            md_lines.append(f"| {num} | pas_{num:03d} | {fmt} | {title} |")

    out_json.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")


def main() -> None:
    # reload after potential patch — first apply
    changed = apply_titles_to_catalog()
    print(f"catalog_titles_updated: {changed}")

    docs = _SCRIPTS.parents[1] / "docs"
    # re-import fresh index
    import importlib
    import algo_v128_catalog as mod

    importlib.reload(mod)
    export_task_list(
        mod._TASK_INDEX,
        docs / "_v128_tasks_export.json",
        docs / "v128_task_list.md",
    )
    print(f"exported: {docs / 'v128_task_list.md'}")


if __name__ == "__main__":
    main()
