import sys
from pathlib import Path
BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from application.curriculum.pascal.catalog.pascal_v311_known_code import get_known_code
from application.curriculum.content.algo_syntax_task_extra import algo_assembly_payload, algo_reference_code

lines = []
for sid in ["pas_001", "pas_003", "pas_030", "pas_002"]:
    k = get_known_code(sid)
    lines.append(f"{sid} known py: {(k[0][:60] if k else 'NONE')}")
    ref = algo_reference_code(sid, "pascal")
    lines.append(f"  pascal ref: {ref[:80].replace(chr(10),' ')}")
    o, t, b, ord_ = algo_assembly_payload(sid, "pascal", task_format="сборка_программы")
    lines.append(f"  blocks ({len(b)}): {b[:3]}")
    o2, t2, b2, ord2 = algo_assembly_payload(sid, "pascal", task_format="сборка_фрагмента")
    lines.append(f"  ph blocks ({len(b2)}): {b2[:5]}")

Path(BACKEND / "_quick_check.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok")
