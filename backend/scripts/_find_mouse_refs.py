"""Find reference codes with Mouse in fixed docx."""
from __future__ import annotations

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

SRC = Path(r"c:\Users\redmi\Downloads\final_course_270_tasks_with_placeholder_capstones_fixed (1).docx")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def main() -> None:
    with zipfile.ZipFile(SRC) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    paras: list[str] = []
    for para in root.iter(f"{W}p"):
        t = "".join(n.text or "" for n in para.iter(f"{W}t")).strip()
        if t:
            paras.append(t)
    hits = [i for i, p in enumerate(paras) if "Mouse" in p and "1100" in p]
    print("hits", len(hits))
    for i in hits[:3]:
        for j in range(max(0, i - 5), min(len(paras), i + 15)):
            print(f"{j+1}: {paras[j][:120]}")


if __name__ == "__main__":
    main()
