from scripts.build_algorithm_syntax_course_from_docx import paras
from pathlib import Path

lines = paras(
    Path(
        r"c:\Users\redmi\Downloads\algorithm_syntax_course_5_languages_128_tasks_TC42_FULL_REWORKED (1).docx"
    )
)
print(repr(lines[136]))
