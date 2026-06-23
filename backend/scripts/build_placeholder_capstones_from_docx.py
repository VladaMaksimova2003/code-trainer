#!/usr/bin/env python3
"""Parse placeholder capstone section (tasks 271+) from course docx."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
SRC_DEFAULT = Path(
    r"c:\Users\redmi\Downloads\final_course_270_tasks_with_placeholder_capstones_fixed (1).docx"
)
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
EXTRA_TASK = re.compile(r"^Задача\s+(\d{3})\.")
CHAPTER_ANCHOR = re.compile(r"добавить после задачи\s+(\d+)", re.I)
LANGS = ["Pascal", "Python", "C++", "C#", "Java"]
LANG_KEYS = ["pascal", "python", "cpp", "csharp", "java"]
LANG_MAP = {
    "Pascal": "pascal",
    "Python": "python",
    "C++": "cpp",
    "C#": "csharp",
    "Java": "java",
}
PLACEHOLDER_HEADER = re.compile(r"^Код с плейсхолдерами \((Pascal|Python|C\+\+|C#|Java)\):$")
BLOCKS_HEADER = re.compile(r"^Блоки для вставки \((Pascal|Python|C\+\+|C#|Java)\):\s*(.+)$")


def paras(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    out: list[str] = []
    for para in root.iter(f"{W}p"):
        t = "".join(n.text or "" for n in para.iter(f"{W}t")).strip()
        if t:
            out.append(t)
    return out


def _clean_title(raw: str) -> str:
    text = str(raw or "").strip()
    text = re.sub(r"^[A-Z0-9]+-P\d+\.\s*", "", text)
    return text.strip()


def _parse_test_cases(lines: list[str], start: int) -> tuple[list[dict[str, str]], int]:
    cases: list[dict[str, str]] = []
    i = start
    while i < len(lines) and lines[i] in {"№", "Вход / данные", "Ожидаемый вывод / результат"}:
        i += 1
    while i < len(lines):
        line = lines[i]
        if (
            line.startswith("Код с плейсхолдерами")
            or line == "Корректные реализации на 5 языках:"
            or EXTRA_TASK.match(line)
            or CHAPTER_ANCHOR.search(line)
        ):
            break
        if line.isdigit():
            i += 1
            if i >= len(lines):
                break
            inputs = lines[i]
            i += 1
            if i >= len(lines):
                break
            output = lines[i]
            cases.append({"inputs": inputs, "output": output})
        i += 1
    return cases, i


def _parse_reference_codes(lines: list[str], start: int) -> tuple[dict[str, str], int]:
    codes: dict[str, str] = {}
    i = start
    if i < len(lines) and lines[i] == "Корректные реализации на 5 языках:":
        i += 1
    if i + 4 < len(lines) and lines[i : i + 5] == LANGS:
        i += 5
        for lang_key in LANG_KEYS:
            if i < len(lines) and lines[i] not in LANGS and not EXTRA_TASK.match(lines[i]):
                codes[lang_key] = lines[i]
                i += 1
            else:
                break
    return codes, i


def parse_placeholder_capstones(lines: list[str]) -> list[dict]:
    start = next((i for i, ln in enumerate(lines) if "Дополнительные жирные задания" in ln), None)
    if start is None:
        return []

    tasks: list[dict] = []
    chapter_after: int | None = None
    i = start

    while i < len(lines):
        anchor = CHAPTER_ANCHOR.search(lines[i])
        if anchor:
            chapter_after = int(anchor.group(1))
            i += 1
            continue

        m = EXTRA_TASK.match(lines[i])
        if not m or int(m.group(1)) < 271:
            i += 1
            continue

        task_num = int(m.group(1))
        raw_title = lines[i].split(".", 1)[1].strip() if "." in lines[i] else lines[i]
        title = _clean_title(raw_title)
        i += 1

        short_goal = ""
        detailed = ""
        concepts: list[str] = []
        placeholder_codes: dict[str, str] = {}
        placeholder_blocks: dict[str, list[str]] = {}
        test_cases: list[dict[str, str]] = []
        reference_codes: dict[str, str] = {}

        while i < len(lines):
            if EXTRA_TASK.match(lines[i]) and int(EXTRA_TASK.match(lines[i]).group(1)) != task_num:
                break
            if CHAPTER_ANCHOR.search(lines[i]):
                break

            line = lines[i]
            if line.startswith("Краткое условие:"):
                short_goal = line.split(":", 1)[1].strip()
            elif line.startswith("Подробное условие:"):
                detailed = line.split(":", 1)[1].strip()
            elif line.startswith("Ожидаемые конструкции:"):
                concepts = [c.strip() for c in line.split(":", 1)[1].split(",") if c.strip()]
            elif line == "Тест-кейсы:":
                test_cases, i = _parse_test_cases(lines, i + 1)
                continue
            elif ph := PLACEHOLDER_HEADER.match(line):
                lang = LANG_MAP[ph.group(1)]
                i += 1
                if i < len(lines):
                    placeholder_codes[lang] = lines[i]
            elif bl := BLOCKS_HEADER.match(line):
                lang = LANG_MAP[bl.group(1)]
                placeholder_blocks[lang] = [b.strip() for b in bl.group(2).split(",") if b.strip()]
            elif line == "Корректные реализации на 5 языках:":
                reference_codes, i = _parse_reference_codes(lines, i)
                continue
            i += 1

        slot_id = f"plh_{task_num:03d}"
        tasks.append(
            {
                "task_num": task_num,
                "slot_id": slot_id,
                "title": title,
                "raw_title": raw_title,
                "short_goal": short_goal,
                "detailed_description": detailed or short_goal or title,
                "goal": detailed or short_goal or title,
                "after_task": chapter_after,
                "expected_concepts": concepts,
                "test_cases": test_cases,
                "placeholder_codes": placeholder_codes,
                "placeholder_blocks": placeholder_blocks,
                "reference_codes": reference_codes,
            }
        )
    return tasks


def emit_tasks_module(tasks: list[dict], out_path: Path) -> None:
    lines = [
        '"""Placeholder capstone tasks (271+) — generated from docx."""',
        "from __future__ import annotations",
        "",
        "TaskRow = tuple[str, str, str, str, str, str, str, str, str, str]",
        "",
        "PLACEHOLDER_CAPSTONE_TASKS: list[TaskRow] = [",
    ]
    for task in tasks:
        slot = task["slot_id"]
        title = str(task["title"]).replace('"', "'")
        goal = str(task["goal"]).replace('"', "'")
        features = "; ".join(task.get("expected_concepts") or ["stdout_write"])
        after = int(task.get("after_task") or 0)
        lines.append(
            f'    ("{slot}", "{title}", "сборка_фрагмента", "assemble", "{slot}", '
            f'"{goal}", "{features}", "hard", "{slot}"),  # after {after}'
        )
    lines.append("]")
    lines.append("")
    lines.append("PLACEHOLDER_CAPSTONE_META: dict[str, dict] = {")
    for task in tasks:
        slot = task["slot_id"]
        meta = {
            "task_num": task["task_num"],
            "raw_title": task.get("raw_title"),
            "title": task.get("title"),
            "short_goal": task.get("short_goal"),
            "detailed_description": task.get("detailed_description"),
            "after_task": task.get("after_task"),
            "test_cases": task.get("test_cases") or [],
            "expected_concepts": task.get("expected_concepts") or [],
            "placeholder_codes": task.get("placeholder_codes") or {},
            "placeholder_blocks": task.get("placeholder_blocks") or {},
            "reference_codes": task.get("reference_codes") or {},
        }
        lines.append(f'    "{slot}": {json.dumps(meta, ensure_ascii=False)},')
    lines.append("}")
    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docx", type=Path, default=SRC_DEFAULT)
    parser.add_argument("--out-json", type=Path, default=BACKEND_ROOT / "_placeholder_capstones.json")
    parser.add_argument(
        "--out-py",
        type=Path,
        default=BACKEND_ROOT / "scripts" / "placeholder_capstone_tasks.py",
    )
    args = parser.parse_args()
    lines = paras(args.docx)
    tasks = parse_placeholder_capstones(lines)
    args.out_json.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
    emit_tasks_module(tasks, args.out_py)
    sample = tasks[0] if tasks else {}
    print(f"parsed {len(tasks)} placeholder capstones -> {args.out_json}")
    if sample:
        print("sample title:", sample.get("title"))
        print("sample desc:", (sample.get("detailed_description") or "")[:80])
        print("sample langs:", list((sample.get("placeholder_codes") or {}).keys()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
