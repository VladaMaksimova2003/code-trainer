import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from scripts.build_algorithm_syntax_course_from_docx import paras, parse_course
from application.curriculum.content.algo_syntax_task_extra import algo_assembly_payload

docx = Path(
    r"c:\Users\redmi\Downloads\algorithm_syntax_course_5_languages_128_tasks_TC42_FULL_REWORKED (1).docx"
)
lines = paras(docx)
tasks, _, failures = parse_course(lines)

out = []
for n in [1, 5]:
    t = next(x for x in tasks if x["task_num"] == n)
    out.append(f"=== TASK {n}: {t['title']} ({t['format_ru']}) ===")
    out.append(f"DOCX TC (raw parse): {t['test_cases']}")
    py = t["implementations"]["python"]
    out.append(f"py assembly_blocks: {py.get('assembly_blocks')}")
    out.append(f"py ref: {t['reference_codes'].get('python', '')[:250]}")
    o, tpl, blocks, order = algo_assembly_payload(
        f"py_{n:03d}", "python", task_format=t["format_ru"]
    )
    out.append(f"runtime blocks: {blocks}")
    out.append("")

# also check JSON on disk
data = json.loads((BACKEND / "algo_syntax_course.json").read_text(encoding="utf-8"))
for n in [1, 5]:
    t = next(x for x in data if x["task_num"] == n)
    out.append(f"=== JSON task {n} TC ===")
    out.append(str(t["test_cases"]))
    out.append("")

Path(BACKEND / "_t1_t5_dump.txt").write_text("\n".join(out), encoding="utf-8")
print("written")
