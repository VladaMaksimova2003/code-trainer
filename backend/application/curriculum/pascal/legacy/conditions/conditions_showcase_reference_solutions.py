"""Reference Pascal solutions for Pascal conditions curriculum showcase E2E checks."""

from __future__ import annotations

REFERENCE_SOLUTIONS: dict[str, str] = {
    "simple_branch_tr_python": (
        "var n: integer;\n"
        "begin\n"
        "  readln(n);\n"
        "  if n > 0 then\n"
        "    writeln('pos')\n"
        "  else\n"
        "    writeln('nonpos');\n"
        "end."
    ),
    "multi_branch_imp_text": (
        "program Grade;\n"
        "var score: integer;\n"
        "begin\n"
        "  readln(score);\n"
        "  if score >= 90 then\n"
        "    writeln('A')\n"
        "  else if score >= 70 then\n"
        "    writeln('B')\n"
        "  else\n"
        "    writeln('C');\n"
        "end."
    ),
    "switch_selection_tr_cpp": (
        "program SwitchDemo;\n"
        "var code: integer;\n"
        "begin\n"
        "  readln(code);\n"
        "  case code of\n"
        "    1: writeln('one');\n"
        "    2: writeln('two');\n"
        "  else\n"
        "    writeln('other');\n"
        "  end;\n"
        "end."
    ),
    "conditional_expression_analyze": (
        "program AbsDemo;\n"
        "var n, result: integer;\n"
        "begin\n"
        "  n := 5;\n"
        "  if n >= 0 then\n"
        "    result := n\n"
        "  else\n"
        "    result := -n;\n"
        "  writeln(result);\n"
        "end."
    ),
    "simple_branch_debug_logic": (
        "program PosEven;\n"
        "var n: integer;\n"
        "begin\n"
        "  readln(n);\n"
        "  if (n > 0) and (n mod 2 = 0) then\n"
        "    writeln('yes')\n"
        "  else\n"
        "    writeln('no');\n"
        "end."
    ),
}

BLOCK_REORDER_SOLUTIONS: dict[str, dict[str, list[int]]] = {
    "simple_branch_asm_blocks": {"order": [0, 1, 2, 3]},
}
