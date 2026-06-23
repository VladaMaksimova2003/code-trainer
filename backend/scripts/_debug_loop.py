import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from scripts.build_algorithm_syntax_course_from_docx import (
    TASK_HEADER,
    _is_impl_boundary,
    _is_lang_line,
    _lang_from_line,
    paras,
)

DOCX = Path(
    r"c:\Users\redmi\Downloads\algorithm_syntax_course_5_languages_128_tasks_TC42_FULL_REWORKED (1).docx"
)

lines = paras(DOCX)
start = next(i for i, ln in enumerate(lines) if ln.startswith("Задача 1."))
i = start + 1
fmt_ru = ""
while i < len(lines):
    if TASK_HEADER.match(lines[i]):
        break
    line = lines[i]
    if line.startswith("Тип реализации:"):
        fmt_ru = line.split(":", 1)[1].strip()
        print("fmt_ru at", i, repr(fmt_ru))
    if line.startswith("Expected Concepts"):
        print("EC at", i, repr(line))
    if _is_impl_boundary(line):
        print("impl boundary at", i, repr(line[:50]))
    if _is_lang_line(line):
        print("lang line at", i, repr(line), "fmt_ru", repr(fmt_ru))
    if line == "Pascal:":
        print("exact Pascal: at", i)
    i += 1
