#!/usr/bin/env python3
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

DOCX = Path(r"c:\Users\redmi\Downloads\algorithm_syntax_course_5_languages_128_tasks_TC42_REWORKED.docx")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
TASK = re.compile(r"^Задача\s+(\d+)\.")
OUT = Path(__file__).resolve().parents[1] / "_algo_docx_dump.txt"


def paras(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    out: list[str] = []
    for para in root.iter(f"{W}p"):
        t = "".join(n.text or "" for n in para.iter(f"{W}t")).strip()
        if t:
            out.append(t)
    return out


def main() -> None:
    lines = paras(DOCX)
    tasks = [i for i, ln in enumerate(lines) if TASK.match(ln)]
    OUT.write_text("\n".join(f"{i}: {ln}" for i, ln in enumerate(lines)), encoding="utf-8")
    print("paras", len(lines), "tasks", len(tasks))
    for idx in tasks[:5]:
        print("---", lines[idx][:120])
        for j in range(idx + 1, min(idx + 25, len(lines))):
            if TASK.match(lines[j]) and j != idx:
                break
            print(f"  {lines[j][:120]}")
    if len(tasks) >= 2:
        last = tasks[-1]
        print("LAST", lines[last][:120])


if __name__ == "__main__":
    main()
