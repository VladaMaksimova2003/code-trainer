"""Inspect fixed placeholder docx structure."""
from __future__ import annotations

import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

SRC = Path(r"c:\Users\redmi\Downloads\final_course_270_tasks_with_placeholder_capstones_fixed (1).docx")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


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
    lines = paras(SRC)
    start = next((i for i, ln in enumerate(lines) if "Дополнительные жирные задания" in ln), 0)
    out = Path(__file__).resolve().parents[1] / "_placeholder_fixed_dump.txt"
    with out.open("w", encoding="utf-8") as fh:
        fh.write(f"total={len(lines)} start={start}\n\n")
        for i in range(start, min(start + 120, len(lines))):
            fh.write(f"{i+1}: {lines[i]}\n")
        fh.write("\n\n=== plh_274 area ===\n")
        for i, ln in enumerate(lines):
            if "Задача 274." in ln:
                for j in range(i, min(i + 45, len(lines))):
                    fh.write(f"{j+1}: {lines[j]}\n")
                break
    print("wrote", out)


if __name__ == "__main__":
    main()
