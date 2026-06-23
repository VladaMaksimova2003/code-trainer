import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from scripts.build_algorithm_syntax_course_from_docx import paras, parse_course

DOCX = Path(
    r"c:\Users\redmi\Downloads\algorithm_syntax_course_5_languages_128_tasks_TC42_FULL_REWORKED (1).docx"
)

lines = paras(DOCX)
tasks, _, _ = parse_course(lines)
for n in [2, 6, 10]:
    t = next(x for x in tasks if x["task_num"] == n)
    pas = t["implementations"]["pascal"]
    print(f"\n=== task {n} ===")
    print("code:", pas.get("placeholder_code"))
    print("gaps:", pas.get("gaps"))
    print("ref:", t["reference_codes"]["pascal"][:200])
