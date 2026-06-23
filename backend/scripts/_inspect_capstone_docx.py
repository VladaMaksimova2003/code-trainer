"""Inspect capstone placeholder docx."""
from __future__ import annotations

import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

SRC = Path(r"c:\Users\redmi\Downloads\final_course_270_tasks_with_placeholder_capstones.docx")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def main() -> None:
    with zipfile.ZipFile(SRC) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    paras: list[str] = []
    for para in root.iter(f"{W}p"):
        text = "".join(node.text or "" for node in para.iter(f"{W}t")).strip()
        if text:
            paras.append(text)

    out = Path(__file__).resolve().parents[1] / "_capstone_docx_dump.txt"
    with out.open("w", encoding="utf-8") as fh:
        fh.write(f"total={len(paras)}\n\n")
        for i, line in enumerate(paras):
            if re.search(
                r"placeholder|плейс|capstone|проверочн|сборк.*фраг|placeholder_capstone|PLACEHOLDER",
                line,
                re.I,
            ):
                fh.write(f"\n=== hit {i+1} ===\n")
                for j in range(max(0, i - 3), min(len(paras), i + 25)):
                    fh.write(f"{j+1}: {paras[j]}\n")

    # also dump last 30 tasks (capstones often at chapter ends)
    with out.open("a", encoding="utf-8") as fh:
        fh.write("\n\n=== LAST TASKS ===\n")
        task_idxs = [i for i, l in enumerate(paras) if re.match(r"^Задача\s+\d+\.", l)]
        for i in task_idxs[-15:]:
            fh.write(f"\n--- {paras[i]} ---\n")
            for j in range(i, min(len(paras), i + 20)):
                fh.write(f"{j+1}: {paras[j]}\n")

    print("wrote", out)


if __name__ == "__main__":
    main()
