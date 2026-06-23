import importlib
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

import scripts.build_algorithm_syntax_course_from_docx as mod

importlib.reload(mod)

code = "var n, i, code, target, ___: integer;begin  readln(n, target);  position := 0;  for i := 1 to n do  begin    readln(code);    if (code = target) and (position = 0) then ___ := i;  end;  writeln(position);end."
gaps = [
    {"id": "p1", "correct": "position"},
    {"id": "p2", "correct": "position"},
]
print(mod._normalize_placeholder_markers(code, gaps))
print(mod._fill_placeholders(mod._normalize_placeholder_markers(code, gaps), gaps))
