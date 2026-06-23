from scripts.build_algorithm_syntax_course_from_docx import paras
from pathlib import Path

lines = paras(
    Path(
        r"c:\Users\redmi\Downloads\algorithm_syntax_course_5_languages_128_tasks_TC42_FULL_REWORKED (1).docx"
    )
)
start = next(i for i, ln in enumerate(lines) if ln.startswith("Задача 2."))
for j in range(start, start + 55):
    if j > start and lines[j].startswith("Задача 3."):
        break
    print(j, lines[j][:180])
