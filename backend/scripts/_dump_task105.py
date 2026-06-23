from scripts.build_algorithm_syntax_course_from_docx import paras, parse_course
from pathlib import Path

DOCX = Path(
    r"c:\Users\redmi\Downloads\algorithm_syntax_course_5_languages_128_tasks_TC42_FULL_REWORKED (1).docx"
)
lines = paras(DOCX)
tasks, _, _ = parse_course(lines)
t = next(x for x in tasks if x["task_num"] == 105)
pas = t["implementations"]["pascal"]
print("blocks:", pas.get("assembly_blocks"))
print("ref:", t["reference_codes"]["pascal"][:200])
