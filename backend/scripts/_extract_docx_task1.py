from pathlib import Path
from scripts.build_algorithm_syntax_course_from_docx import paras

docx = Path(
    r"c:\Users\redmi\Downloads\algorithm_syntax_course_5_languages_128_tasks_TC42_FULL_REWORKED (1).docx"
)
lines = paras(docx)
start = next(i for i, l in enumerate(lines) if l.startswith("Задача 1."))
end = next(i for i, l in enumerate(lines) if l.startswith("Задача 2."))
chunk = lines[start:end]
out = Path(__file__).resolve().parents[1] / "_docx_task1.txt"
out.write_text("\n".join(chunk), encoding="utf-8")
print("written", len(chunk), "lines to", out)
