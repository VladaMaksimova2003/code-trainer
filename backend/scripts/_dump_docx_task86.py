#!/usr/bin/env python3
"""Dump docx task 86 section."""
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
path = Path(r"C:\Users\redmi\Downloads\algorithm_syntax_course_5_languages_128_tasks_TC42_FULL_REWORKED (1).docx")
with zipfile.ZipFile(path) as zf:
    root = ET.fromstring(zf.read("word/document.xml"))
lines = []
for para in root.iter(f"{W}p"):
    t = "".join(n.text or "" for n in para.iter(f"{W}t")).strip()
    if t:
        lines.append(t)

for i, line in enumerate(lines):
    if re.match(r"^Задача\s+86\.", line):
        for j in range(i, min(i + 100, len(lines))):
            print(lines[j])
        break
