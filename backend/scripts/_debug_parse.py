import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from scripts.build_algorithm_syntax_course_from_docx import (
    _format_type_key,
    _parse_language_impl,
    _parse_numbered_blocks,
    paras,
    parse_course,
    TASK_HEADER,
)

DOCX = Path(
    r"c:\Users\redmi\Downloads\algorithm_syntax_course_5_languages_128_tasks_TC42_FULL_REWORKED (1).docx"
)

lines = paras(DOCX)
start = next(i for i, ln in enumerate(lines) if ln.startswith("Задача 1."))
fmt_ru = ""
for j in range(start, start + 40):
    if lines[j].startswith("Тип реализации:"):
        fmt_ru = lines[j].split(":", 1)[1].strip()
    if lines[j] == "Pascal:":
        print("fmt_ru", repr(fmt_ru), "key", _format_type_key(fmt_ru))
        blocks, ni = _parse_numbered_blocks(lines, j + 1)
        print("numbered blocks", len(blocks), blocks[:2])
        impl, ni2 = _parse_language_impl(lines, j + 1, _format_type_key(fmt_ru))
        print("impl blocks", len(impl.get("assembly_blocks") or []))
        break

tasks, _, failures = parse_course(lines)
t1 = next(t for t in tasks if t["task_num"] == 1)
print("failures task1", [f for f in failures if f.startswith("task 1")])
print("pas blocks", t1["implementations"]["pascal"].get("assembly_blocks", [])[:2])
