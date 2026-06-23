#!/usr/bin/env python3
"""Extract docx table rows to debug condition parsing."""
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

DOCX = Path(r"c:\Users\redmi\Downloads\algorithm_syntax_course_5_languages_128_tasks_TC42_REWORKED.docx")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
TASK = re.compile(r"^Задача\s+(\d+)\.")


def cell_text(tc) -> str:
    parts = []
    for t in tc.iter(f"{W}t"):
        if t.text:
            parts.append(t.text)
    return "".join(parts).strip()


def main() -> None:
    with zipfile.ZipFile(DOCX) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))

    body = root.find(f"{W}body")
    current_task = None
    for child in body:
        tag = child.tag.split("}")[-1]
        if tag == "p":
            text = "".join(t.text or "" for t in child.iter(f"{W}t")).strip()
            m = TASK.match(text)
            if m:
                current_task = int(m.group(1))
                print(f"\n=== TASK {current_task}: {text} ===")
        elif tag == "tbl" and current_task in {1, 2, 4, 6, 66}:
            print(f"--- table for task {current_task} ---")
            for tr in child.iter(f"{W}tr"):
                cells = [cell_text(tc) for tc in tr.findall(f"{W}tc")]
                cells = [c for c in cells if c]
                if cells:
                    print(" | ".join(c[:80] for c in cells))


if __name__ == "__main__":
    main()
