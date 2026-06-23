#!/usr/bin/env python3
"""Import per-language expected TC from final_course_270_tasks_corrected_language_TC.docx."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SRC = Path(r"c:\Users\redmi\Downloads\final_course_270_tasks_corrected_language_TC.docx")
OUT_JSON = ROOT / "scripts" / "course_270_expected_concepts_from_docx.json"

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
LANG_HEADERS = ["Pascal", "Python", "C++", "C#", "Java"]
LANG_KEYS = ["pascal", "python", "cpp", "csharp", "java"]
SLOT_PREFIX = {
    "pascal": "pas",
    "python": "py",
    "cpp": "cpp",
    "csharp": "cs",
    "java": "java",
}
TASK_HEADER = re.compile(r"^Задача\s+(\d+)\.\s*(.*)$")
TC_TOKEN = re.compile(r"^[a-z][a-z0-9_]*$")

TARGETS: dict[str, tuple[str, str]] = {
    "pascal": (
        ROOT / "application/curriculum/pascal/catalog/pascal_v311_expected_concepts.py",
        "SLOT_EXPECTED_CONCEPT_OVERRIDES: dict[str, list[str]] = {",
    ),
    "python": (
        ROOT / "application/curriculum/python/catalog/python_v311_expected_concepts.py",
        "_V4_SLOT_OVERRIDES: dict[str, list[str]] = {",
    ),
    "cpp": (
        ROOT / "application/curriculum/cpp/catalog/cpp_v311_expected_concepts.py",
        "_V4_SLOT_OVERRIDES: dict[str, list[str]] = {",
    ),
    "csharp": (
        ROOT / "application/curriculum/csharp/catalog/csharp_v311_expected_concepts.py",
        "_V4_SLOT_OVERRIDES: dict[str, list[str]] = {",
    ),
    "java": (
        ROOT / "application/curriculum/java/catalog/java_v311_expected_concepts.py",
        "_V4_SLOT_OVERRIDES: dict[str, list[str]] = {",
    ),
}


def paragraphs_from_docx(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    paras: list[str] = []
    for para in root.iter(f"{W_NS}p"):
        parts: list[str] = []
        for node in para.iter(f"{W_NS}t"):
            if node.text:
                parts.append(node.text)
        text = "".join(parts).strip()
        if text:
            paras.append(text)
    return paras


def parse_tc_line(line: str) -> list[str]:
    items: list[str] = []
    for part in re.split(r"[,;]", line):
        token = part.strip().split("(", 1)[0].strip()
        if TC_TOKEN.match(token):
            items.append(token)
    return items


def is_lang_header_block(paras: list[str], index: int) -> bool:
    if index + 10 > len(paras):
        return False
    if paras[index : index + 5] != LANG_HEADERS:
        return False
    return all(parse_tc_line(paras[index + 5 + offset]) for offset in range(5))


def parse_docx(paras: list[str]) -> dict[int, dict[str, list[str]]]:
    by_task: dict[int, dict[str, list[str]]] = {}
    current_task: int | None = None

    for index, line in enumerate(paras):
        task_match = TASK_HEADER.match(line)
        if task_match:
            current_task = int(task_match.group(1))
            by_task.setdefault(current_task, {})
            continue
        if current_task is None:
            continue
        if not is_lang_header_block(paras, index):
            continue
        for offset, lang in enumerate(LANG_KEYS):
            concepts = parse_tc_line(paras[index + 5 + offset])
            if concepts:
                by_task[current_task][lang] = concepts

    return by_task


def slot_id(lang: str, task_num: int) -> str:
    return f"{SLOT_PREFIX[lang]}_{task_num:03d}"


def render_slot_dict(mapping: dict[str, list[str]]) -> str:
    lines = ["{"]
    for slot in sorted(mapping.keys(), key=lambda item: int(item.rsplit("_", 1)[-1])):
        ids = mapping[slot]
        quoted = ", ".join(f'"{item}"' for item in ids)
        lines.append(f'    "{slot}": [{quoted}],')
    lines.append("}")
    return "\n".join(lines)


def patch_dict_in_file(path: Path, marker: str, slot_mapping: dict[str, list[str]]) -> None:
    text = path.read_text(encoding="utf-8")
    start = text.index(marker)
    dict_start = start + len(marker)
    depth = 1
    pos = dict_start
    while pos < len(text) and depth:
        char = text[pos]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        pos += 1
    if depth != 0:
        raise RuntimeError(f"Unbalanced braces in {path}")
    new_text = text[:dict_start] + "\n" + render_slot_dict(slot_mapping)[1:-1] + "\n" + text[pos - 1 :]
    path.write_text(new_text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docx", type=Path, default=DEFAULT_SRC)
    parser.add_argument("--write", action="store_true", help="Patch catalog python files")
    args = parser.parse_args()

    if not args.docx.is_file():
        print(json.dumps({"error": f"docx not found: {args.docx}"}, ensure_ascii=False))
        return 1

    by_task = parse_docx(paragraphs_from_docx(args.docx))
    per_lang: dict[str, dict[str, list[str]]] = {lang: {} for lang in LANG_KEYS}
    for task_num, langs in sorted(by_task.items()):
        for lang, concepts in langs.items():
            per_lang[lang][slot_id(lang, task_num)] = concepts

    OUT_JSON.write_text(
        json.dumps({"by_task": by_task, "by_slot": per_lang}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    summary = {
        "tasks_parsed": len(by_task),
        "per_language": {lang: len(slots) for lang, slots in per_lang.items()},
        "sample_task_1": by_task.get(1),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if args.write:
        for lang, (path, marker) in TARGETS.items():
            patch_dict_in_file(path, marker, per_lang[lang])
            print(f"patched {path.name} ({lang})")

    return 0 if len(by_task) >= 250 else 1


if __name__ == "__main__":
    raise SystemExit(main())
