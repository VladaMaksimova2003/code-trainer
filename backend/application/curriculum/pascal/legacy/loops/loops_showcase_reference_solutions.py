"""Reference Pascal solutions for Pascal loops curriculum showcase E2E checks."""

from __future__ import annotations

REFERENCE_SOLUTIONS: dict[str, str] = {
    "counted_loop_tr_python": (
        "var n, i, total: integer;\n"
        "begin\n"
        "  readln(n);\n"
        "  total := 0;\n"
        "  for i := 1 to n do\n"
        "    total := total + i;\n"
        "  writeln(total);\n"
        "end."
    ),
    "pre_condition_imp_text": (
        "program Countdown;\n"
        "var n: integer;\n"
        "begin\n"
        "  readln(n);\n"
        "  while n > 0 do\n"
        "  begin\n"
        "    writeln(n);\n"
        "    n := n - 1;\n"
        "  end;\n"
        "end."
    ),
    "post_condition_analyze_output": (
        "program RepeatDemo;\n"
        "var n: integer;\n"
        "begin\n"
        "  n := 3;\n"
        "  repeat\n"
        "    writeln(n);\n"
        "    n := n - 1;\n"
        "  until n = 0;\n"
        "end."
    ),
    "loop_control_debug_logic": (
        "program OddSum;\n"
        "var i, n, s: integer;\n"
        "begin\n"
        "  readln(n);\n"
        "  s := 0;\n"
        "  for i := 1 to n do\n"
        "  begin\n"
        "    if i mod 2 = 0 then\n"
        "      continue;\n"
        "    s := s + i;\n"
        "  end;\n"
        "  writeln(s);\n"
        "end."
    ),
    "nested_iteration_io": (
        "program Product;\n"
        "var a, b: integer;\n"
        "begin\n"
        "  readln(a);\n"
        "  readln(b);\n"
        "  writeln(a * b);\n"
        "end."
    ),
    "collection_iteration_tr_python": (
        "program CountA;\n"
        "var s: string;\n"
        "    i, count, len: integer;\n"
        "    ch: char;\n"
        "begin\n"
        "  readln(s);\n"
        "  count := 0;\n"
        "  len := length(s);\n"
        "  for i := 1 to len do\n"
        "  begin\n"
        "    ch := s[i];\n"
        "    if ch = 'a' then\n"
        "      count := count + 1;\n"
        "  end;\n"
        "  writeln(count);\n"
        "end."
    ),
}

BLOCK_REORDER_SOLUTIONS: dict[str, dict] = {
    "counted_loop_asm_blocks": {
        "order": [0, 1],
        "assembled_code": (
            "program Sum;\n"
            "var i, n, s: integer;\n"
            "begin\n"
            "  readln(n);\n"
            "  s := 0;\n"
            "  for i := 1 to n do\n"
            "    s := s + i;\n"
            "  writeln(s);\n"
            "end."
        ),
    },
}
