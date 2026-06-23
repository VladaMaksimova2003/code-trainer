#!/usr/bin/env python3
"""Generate backend/scripts/python_v31_tasks.py from generate_python_v31_catalog_doc.py."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

FORMAT_TO_ACTION = {
    "перевод_программы": "translate",
    "перевод_фрагмента": "translate",
    "исправление": "debug",
    "поиск_ошибки": "debug",
    "сборка_программы": "assemble",
    "сборка_фрагмента": "assemble",
    "выбор_фрагмента": "implement",
    "код_по_блок-схеме": "implement",
    "блок-схема_пo_кodu": "implement",
}


def _escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _load_pascal_by_slot() -> dict[str, tuple]:
    from pascal_v31_tasks import V31_TASKS

    return {str(row[0]): row for row in V31_TASKS}


def _overlay_from_pascal_mirror(
    slot_id: str,
    name: str,
    fmt: str,
    diff: str,
    goal: str,
    features: str,
    pas_by_slot: dict[str, tuple],
) -> tuple[str, str, str, str, str]:
    from application.curriculum.mirror.curriculum_slot_mirror_map import (
        is_python_only_slot,
        python_to_pascal_slot,
    )
    from application.curriculum.python.catalog.python_mirror_content import (
        neutral_goal_from_mirror,
        neutral_title_for_mirror,
    )

    if is_python_only_slot(slot_id):
        return name, fmt, diff, goal, features

    pas_id = python_to_pascal_slot(slot_id)
    if not pas_id:
        return name, fmt, diff, goal, features
    pas = pas_by_slot.get(pas_id)
    if not pas:
        return name, fmt, diff, goal, features

    _sid, _ch, pas_title, pas_fmt, _act, _pat, pas_goal, pas_features, pas_diff, _leg = pas
    name = neutral_title_for_mirror(slot_id, pas_title or name)
    goal = neutral_goal_from_mirror(slot_id, pas_goal or goal)
    fmt = str(pas_fmt or fmt)
    diff = str(pas_diff or diff)
    if not str(features or "").strip() and str(pas_features or "").strip():
        features = str(pas_features)
    return name, fmt, diff, goal, features


def main() -> int:
    import generate_python_v31_catalog_doc as cat

    for _key, _title, _mirror, tasks in cat.CHAPTERS:
        for _slot_id, _name, fmt, *_rest in tasks:
            FORMAT_TO_ACTION.setdefault(fmt, "implement")

    pas_by_slot = _load_pascal_by_slot()
    out = Path(__file__).resolve().parent / "python_v31_tasks.py"
    lines = [
        '"""Python Course v1 task catalog — language-neutral metadata only."""',
        "from __future__ import annotations",
        "",
        "TaskRow = tuple[str, str, str, str, str, str, str, str, str, str]",
        "",
        "V311_CORE_TASK_COUNT = 0  # set after _extend blocks",
        "",
        "V31_TASKS: list[TaskRow] = []",
        "",
        "",
        "def _extend(chapter: str, rows: list[tuple]) -> None:",
        "    for row in rows:",
        '        padded = row + ("",) * (10 - len(row))',
        "        V31_TASKS.append((padded[0], chapter, *padded[1:9]))  # type: ignore[misc]",
        "",
    ]

    chapter_titles: dict[str, str] = {}
    for key, title, _mirror, tasks in cat.CHAPTERS:
        chapter_titles[key] = title.split(". ", 1)[-1] if ". " in title else title
        lines.append(f"# {title}")
        lines.append(f'_extend("{key}", [')
        for slot_id, name, fmt, diff, goal, features in tasks:
            name, fmt, diff, goal, features = _overlay_from_pascal_mirror(
                slot_id, name, fmt, diff, goal, features, pas_by_slot
            )
            action = FORMAT_TO_ACTION[fmt]
            pattern = f"py_{slot_id}"
            lines.append(
                f'    ("{slot_id}", "{_escape(name)}", "{fmt}", "{action}", '
                f'"{pattern}", "{_escape(goal)}", "{_escape(features)}", "{diff}"),'
            )
        lines.append("])")
        lines.append("")

    core_count = sum(len(ch[3]) for ch in cat.CHAPTERS)
    lines.extend(
        [
            "from application.curriculum.python.catalog.python_v311_capstone_catalog import (  # noqa: E402",
            "    capstone_count,",
            "    capstone_task_rows,",
            ")",
            "",
            "V311_CORE_TASK_COUNT = " + str(core_count),
            "",
            "V31_TASKS.extend(capstone_task_rows())",
            "",
            f"assert len(V31_TASKS) == V311_CORE_TASK_COUNT + capstone_count(), len(V31_TASKS)",
            "",
            "V31_CHAPTER_TITLES = {",
        ]
    )
    chapter_titles["capstones"] = "Capstone (мета-блоки)"
    for key, title in chapter_titles.items():
        lines.append(f'    "{key}": "{_escape(title)}",')
    lines.append("}")
    lines.append("")

    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out} ({core_count} core tasks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
