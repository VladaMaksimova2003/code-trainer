from scripts.build_algorithm_syntax_course_from_docx import parse_course, paras
from pathlib import Path

lines = paras(
    Path(
        r"c:\Users\redmi\Downloads\algorithm_syntax_course_5_languages_128_tasks_TC42_FULL_REWORKED (1).docx"
    )
)
tasks, _, _ = parse_course(lines)
t = next(x for x in tasks if x["task_num"] == 2)
py = t["implementations"]["python"]
print("ph:", py["placeholder_code"])
print("gaps:", py["gaps"])
print("ref:", t["reference_codes"]["python"])
