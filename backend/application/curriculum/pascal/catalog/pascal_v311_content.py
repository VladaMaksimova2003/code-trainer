"""Seed payloads for Pascal Course v3.1.1 tasks (content, not catalog metadata)."""
from __future__ import annotations

import re
from typing import Any

from application.curriculum.pascal.catalog.pascal_flowchart_diagrams import (
    diagram_if_n_pos,
    empty_diagram,
)
from application.curriculum.pascal.catalog.pascal_known_language import (
    build_known_language_variants,
    code_examples_from_variants,
)
from application.curriculum.pascal.catalog.pascal_v311_known_code import get_known_code

from application.curriculum.pascal.catalog.pascal_v311_capstone_catalog import (
    capstone_reference_pascal,
    capstone_starter_pascal,
    capstone_test_cases,
)
from application.curriculum.pascal.catalog.pascal_v311_test_case_resolver import derive_test_cases
from application.curriculum.pascal.catalog.pascal_v32_delta_content import (
    V32_ASSEMBLY,
    V32_DEBUG_STARTER,
    V32_REFERENCE,
    V32_TEST_CASES,
)

try:
    from application.curriculum.pascal.catalog.pascal_v311_measured_outputs import (
        MEASURED_OUTPUTS,
    )
except ImportError:
    MEASURED_OUTPUTS = {}

TaskRow = tuple[str, str, str, str, str, str, str, str, str, str]

_PASCAL_PROGRAM = (
    "program Demo;\n"
    "var\n"
    "  x, y: integer;\n"
    "begin\n"
    "  x := 1;\n"
    "  y := x + 1;\n"
    "  writeln(y);\n"
    "end.\n"
)

_PASCAL_SNIPPET = "x := 1;\ny := x + 1;"

_ASSEMBLE_BLOCKS = ["x := 1;", "y := x + 1;", "writeln(y);"]
_ASSEMBLE_TEMPLATE = "var\n  x, y: integer;\nbegin\n  ___\nend."

# Placeholder assembly: (placeholder_code, gaps, test_cases)
_SLOT_PLACEHOLDER: dict[str, tuple[str, list[dict[str, Any]], list[dict[str, str]]]] = {
    "str_07": (
        "program Demo;\nvar\n  s, sub, result: string;\nbegin\n  readln(s);\n  ___p1___\n  ___p2___\n  writeln(result);\nend.",
        [
            {
                "id": "p1",
                "label": "выделить первые 3 символа строки",
                "answer": "sub := Copy(s, 1, 3);",
                "variants": [
                    "sub := Copy(s, 1, 3);",
                    "sub := Copy(s, 1, 5);",
                    "Copy(sub, s);",
                    "sub := s;",
                ],
            },
            {
                "id": "p2",
                "label": "добавить ! к подстроке",
                "answer": "result := Concat(sub, '!');",
                "variants": [
                    "result := Concat(sub, '!');",
                    "result := sub + '!';",
                    "Concat(result, sub);",
                    "result := Copy(sub, 1, 1);",
                ],
            },
        ],
        [{"inputs": "Hello\n", "output": "Hel!"}],
    ),
}

_SLOT_DESCRIPTIONS: dict[str, str] = {
    "str_07": (
        "Дана строка s. Возьмите первые 3 символа функцией Copy и добавьте к ним "
        "восклицательный знак функцией Concat. Выведите result."
    ),
}

# Per-slot assembly content: (original_code, template, blocks, correct_order, test_cases)
# template="___" means free-form assembly (FreeBlockAssemblyView)
# correct_order: indices of blocks in correct order
_SLOT_ASSEMBLY: dict[str, tuple[str, str, list[str], list[int], list[dict[str, str]]]] = {
    # ── program_skeleton ──────────────────────────────────────────────────────
    "psk_03": (
        "program Demo;\nbegin\n  writeln('done');\nend.",
        "___",
        ["program Demo;", "begin", "  writeln('done');", "end."],
        [0, 1, 2, 3],
        [{"inputs": "", "output": "done"}],
    ),
    "psk_11": (
        "const\n  MAX = 100;\nvar\n  n: integer;",
        "___",
        ["const", "  MAX = 100;", "var", "  n: integer;"],
        [0, 1, 2, 3],
        [],
    ),
    "psk_12": (
        "begin\nend",
        "___",
        ["begin", "end"],
        [0, 1],
        [{"inputs": "", "output": "ok"}],
    ),
    # ── typed_variables ───────────────────────────────────────────────────────
    "typ_06": (
        "const\n  PI = 3.14;\n  MAX = 100;",
        "___",
        ["const", "  PI = 3.14;", "  MAX = 100;"],
        [0, 1, 2],
        [],
    ),
    # ── io ────────────────────────────────────────────────────────────────────
    "io_06": (
        "readln(n);\nwriteln(n);",
        "___",
        ["readln(n);", "writeln(n);"],
        [0, 1],
        [],
    ),
    "io_07": (
        "program Demo;\nvar n: integer;\nbegin\n  readln(n);\n  writeln(n);\nend.",
        "___",
        ["program Demo;", "var n: integer;", "begin", "  readln(n);", "  writeln(n);", "end."],
        [0, 1, 2, 3, 4, 5],
        [{"inputs": "5\n", "output": "5"}],
    ),
    # ── expressions ───────────────────────────────────────────────────────────
    "exp_04": (
        "var S: set of char;\nS := ['a'..'z'];\nif 'a' in S then writeln('yes');",
        "___",
        ["var S: set of char;", "S := ['a'..'z'];", "if 'a' in S then writeln('yes');"],
        [0, 1, 2],
        [],
    ),
    "exp_08": (
        "q := a div b;\nr := a mod b;",
        "___",
        ["q := a div b;", "r := a mod b;"],
        [0, 1],
        [],
    ),
    # ── conditions ────────────────────────────────────────────────────────────
    "cnd_02": (
        "program Demo;\nvar x: integer;\nbegin\n  readln(x);\n  if x > 0 then\n    writeln('positive')\n  else\n    writeln('non-positive');\nend.",
        "___",
        ["program Demo;", "var x: integer;", "begin", "  readln(x);",
         "  if x > 0 then", "    writeln('positive')", "  else",
         "    writeln('non-positive');", "end."],
        [0, 1, 2, 3, 4, 5, 6, 7, 8],
        [{"inputs": "5\n", "output": "positive"}],
    ),
    "cnd_05": (
        "program Demo;\nvar x: integer;\nbegin\n  readln(x);\n  case x of\n    1: writeln('one');\n    2: writeln('two');\n  else\n    writeln('other');\n  end;\nend.",
        "___",
        ["program Demo;", "var x: integer;", "begin", "  readln(x);",
         "  case x of", "    1: writeln('one');", "    2: writeln('two');",
         "  else", "    writeln('other');", "  end;", "end."],
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        [{"inputs": "1\n", "output": "one"}],
    ),
    "cnd_10": (
        "case x of\n  1: writeln('one');\n  2: writeln('two');\nend;",
        "___",
        ["case x of", "  1: writeln('one');", "  2: writeln('two');", "end;"],
        [0, 1, 2, 3],
        [],
    ),
    # ── loops ─────────────────────────────────────────────────────────────────
    "lop_01": (
        "program Demo;\nvar i, n: integer;\nbegin\n  readln(n);\n  for i := 1 to n do\n    writeln(i);\nend.",
        "___",
        ["program Demo;", "var i, n: integer;", "begin", "  readln(n);",
         "  for i := 1 to n do", "    writeln(i);", "end."],
        [0, 1, 2, 3, 4, 5, 6],
        [{"inputs": "5\n", "output": "1\n2\n3\n4\n5"}],
    ),
    "lop_02": (
        "program Demo;\nvar i, n, s: integer;\nbegin\n  readln(n);\n  s := 0;\n  for i := 1 to n do\n    s := s + i;\n  writeln(s);\nend.",
        "___",
        ["program Demo;", "var i, n, s: integer;", "begin", "  readln(n);",
         "  s := 0;", "  for i := 1 to n do", "    s := s + i;", "  writeln(s);", "end."],
        [0, 1, 2, 3, 4, 5, 6, 7, 8],
        [{"inputs": "5\n", "output": "15"}],
    ),
    "lop_03": (
        "for i := n downto 1 do\n  writeln(i);",
        "___",
        ["for i := n downto 1 do", "  writeln(i);"],
        [0, 1],
        [],
    ),
    "lop_07": (
        "program Demo;\nvar n, s: integer;\nbegin\n  s := 0;\n  repeat\n    readln(n);\n    s := s + n;\n  until n = 0;\n  writeln(s);\nend.",
        "___",
        ["program Demo;", "var n, s: integer;", "begin", "  s := 0;",
         "  repeat", "    readln(n);", "    s := s + n;", "  until n = 0;",
         "  writeln(s);", "end."],
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [{"inputs": "3\n2\n0\n", "output": "5"}],
    ),
    "lop_12": (
        "for i := 1 to n do\nbegin\n  for j := 1 to m do\n    write(i * j, ' ');\n  writeln;\nend;",
        "___",
        ["for i := 1 to n do", "begin", "  for j := 1 to m do",
         "    write(i * j, ' ');", "  writeln;", "end;"],
        [0, 1, 2, 3, 4, 5],
        [],
    ),
    # ── functions ─────────────────────────────────────────────────────────────
    "fn_06": (
        "function Add(a, b: integer): integer;\nbegin\n  Result := a + b;\nend;",
        "___",
        ["function Add(a, b: integer): integer;", "begin", "  Result := a + b;", "end;"],
        [0, 1, 2, 3],
        [],
    ),
    "fn_12": (
        "program Demo;\nfunction Square(n: integer): integer;\nbegin\n  Result := n * n;\nend;\nvar x: integer;\nbegin\n  readln(x);\n  writeln(Square(x));\nend.",
        "___",
        ["program Demo;", "function Square(n: integer): integer;", "begin",
         "  Result := n * n;", "end;", "var x: integer;", "begin",
         "  readln(x);", "  writeln(Square(x));", "end."],
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [{"inputs": "4\n", "output": "16"}],
    ),
    "fn_07": (
        "function Fact(n: integer): integer; forward;\nfunction Fact(n: integer): integer;\nbegin\n  if n <= 1 then Result := 1\n  else Result := n * Fact(n - 1);\nend;",
        "___",
        ["function Fact(n: integer): integer; forward;",
         "function Fact(n: integer): integer;",
         "begin", "  if n <= 1 then Result := 1",
         "  else Result := n * Fact(n - 1);", "end;"],
        [0, 1, 2, 3, 4, 5],
        [],
    ),
    # ── procedures ────────────────────────────────────────────────────────────
    "prc_07": (
        "procedure Swap(var a, b: integer);\nvar t: integer;\nbegin\n  t := a; a := b; b := t;\nend;",
        "___",
        ["procedure Swap(var a, b: integer);", "var t: integer;", "begin",
         "  t := a; a := b; b := t;", "end;"],
        [0, 1, 2, 3, 4],
        [],
    ),
    "prc_10": (
        "procedure Greet(name: string);\nbegin\n  writeln('Hello, ', name, '!');\nend;",
        "___",
        ["procedure Greet(name: string);", "begin",
         "  writeln('Hello, ', name, '!');", "end;"],
        [0, 1, 2, 3],
        [],
    ),
    "prc_13": (
        "program Demo;\nprocedure SayHello;\nbegin\n  writeln('Hello!');\nend;\nbegin\n  SayHello;\nend.",
        "___",
        ["program Demo;", "procedure SayHello;", "begin",
         "  writeln('Hello!');", "end;", "begin", "  SayHello;", "end."],
        [0, 1, 2, 3, 4, 5, 6, 7],
        [{"inputs": "", "output": "Hello!"}],
    ),
    # ── arrays ────────────────────────────────────────────────────────────────
    "arr_06": (
        "var a: array[1..10] of integer;",
        "___",
        ["var", "a: array[1..10] of integer;"],
        [0, 1],
        [],
    ),
    # ── dynamic arrays ────────────────────────────────────────────────────────
    "dyn_05": (
        "SetLength(a, 5);\na[0] := 1;\na[1] := 2;",
        "___",
        ["SetLength(a, 5);", "a[0] := 1;", "a[1] := 2;"],
        [0, 1, 2],
        [],
    ),
    "dyn_04": (
        "program Demo;\nvar a: array of integer;\nn: integer;\nbegin\n  readln(n);\n  SetLength(a, n + 1);\n  a[n] := n;\n  writeln(a[n]);\nend.",
        "___",
        ["program Demo;", "var a: array of integer;", "  n: integer;", "begin",
         "  readln(n);", "  SetLength(a, n + 1);", "  a[n] := n;",
         "  writeln(a[n]);", "end."],
        [0, 1, 2, 3, 4, 5, 6, 7, 8],
        [{"inputs": "3\n", "output": "3"}],
    ),
    "dyn_06": (
        "SetLength(a, 0);",
        "___",
        ["SetLength(a, 0);"],
        [0],
        [],
    ),
    "dyn_08": (
        "b := Copy(a, i, count);",
        "___",
        ["b := Copy(a, i, count);"],
        [0],
        [],
    ),
    # ── strings ───────────────────────────────────────────────────────────────
    "str_09": (
        "for i := 1 to Length(s) do\n  write(s[i]);",
        "___",
        ["for i := 1 to Length(s) do", "  write(s[i]);"],
        [0, 1],
        [],
    ),
    # ── records ───────────────────────────────────────────────────────────────
    "rec_01": (
        "program Demo;\ntype\n  TPerson = record\n    Name: string;\n    Age: integer;\n  end;\nvar p: TPerson;\nbegin\n  p.Name := 'Alice';\n  p.Age := 20;\n  writeln(p.Name, ' ', p.Age);\nend.",
        "___",
        ["program Demo;", "type", "  TPerson = record", "    Name: string;",
         "    Age: integer;", "  end;", "var p: TPerson;", "begin",
         "  p.Name := 'Alice';", "  p.Age := 20;",
         "  writeln(p.Name, ' ', p.Age);", "end."],
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        [{"inputs": "", "output": "Alice 20"}],
    ),
    "rec_07": (
        "type\n  TPoint = record\n    x, y: integer;\n  end;",
        "___",
        ["type", "  TPoint = record", "    x, y: integer;", "  end;"],
        [0, 1, 2, 3],
        [],
    ),
    "rec_06": (
        "New(p);\np^.x := 10;\nDispose(p);",
        "___",
        ["New(p);", "p^.x := 10;", "Dispose(p);"],
        [0, 1, 2],
        [],
    ),
    "rec_11": (
        "with p do\nbegin\n  Name := 'Bob';\n  Age := 25;\nend;",
        "___",
        ["with p do", "begin", "  Name := 'Bob';", "  Age := 25;", "end;"],
        [0, 1, 2, 3, 4],
        [],
    ),
    # ── files ─────────────────────────────────────────────────────────────────
    "fil_02": (
        "AssignFile(f, 'out.txt');\nRewrite(f);\nWriteLn(f, 'data');\nCloseFile(f);",
        "___",
        ["AssignFile(f, 'out.txt');", "Rewrite(f);", "WriteLn(f, 'data');", "CloseFile(f);"],
        [0, 1, 2, 3],
        [],
    ),
    "fil_08": (
        "AssignFile(f, 'in.txt');\nReset(f);\nReadLn(f, s);\nCloseFile(f);",
        "___",
        ["AssignFile(f, 'in.txt');", "Reset(f);", "ReadLn(f, s);", "CloseFile(f);"],
        [0, 1, 2, 3],
        [],
    ),
    # ── units ─────────────────────────────────────────────────────────────────
    "unt_08": (
        "unit MyUnit;\ninterface\n  procedure Hello;\nimplementation",
        "___",
        ["unit MyUnit;", "interface", "  procedure Hello;", "implementation"],
        [0, 1, 2, 3],
        [],
    ),
    "unt_11": (
        "implementation\nprocedure Hello;\nbegin\n  writeln('Hello!');\nend;",
        "___",
        ["implementation", "procedure Hello;", "begin", "  writeln('Hello!');", "end;"],
        [0, 1, 2, 3, 4],
        [],
    ),
    "unt_13": (
        "unit MyUnit;\ninterface\n  procedure Hello;\nimplementation\nprocedure Hello;\nbegin\n  writeln('Hi!');\nend;\nend.",
        "___",
        ["unit MyUnit;", "interface", "  procedure Hello;", "implementation",
         "procedure Hello;", "begin", "  writeln('Hi!');", "end;", "end."],
        [0, 1, 2, 3, 4, 5, 6, 7, 8],
        [],
    ),
    # ── recursion ─────────────────────────────────────────────────────────────
    "rcu_01": (
        "program Demo;\nfunction Fact(n: integer): integer;\nbegin\n  if n <= 1 then Result := 1\n  else Result := n * Fact(n - 1);\nend;\nvar x: integer;\nbegin\n  readln(x);\n  writeln(Fact(x));\nend.",
        "___",
        ["program Demo;", "function Fact(n: integer): integer;", "begin",
         "  if n <= 1 then Result := 1",
         "  else Result := n * Fact(n - 1);", "end;", "var x: integer;",
         "begin", "  readln(x);", "  writeln(Fact(x));", "end."],
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        [{"inputs": "5\n", "output": "120"}],
    ),
    "rcu_03": (
        "procedure Foo(n: integer); forward;\nprocedure Foo(n: integer);\nbegin\n  if n > 0 then Foo(n - 1);\n  writeln(n);\nend;",
        "___",
        ["procedure Foo(n: integer); forward;",
         "procedure Foo(n: integer);", "begin",
         "  if n > 0 then Foo(n - 1);", "  writeln(n);", "end;"],
        [0, 1, 2, 3, 4, 5],
        [],
    ),
    # ── OOP ───────────────────────────────────────────────────────────────────
    "oop_01": (
        "program Demo;\ntype\n  TAnimal = class\n    Name: string;\n    procedure Speak; virtual;\n  end;\nvar a: TAnimal;\nbegin\n  a := TAnimal.Create;\n  a.Name := 'Cat';\n  a.Free;\nend.",
        "___",
        ["program Demo;", "type", "  TAnimal = class", "    Name: string;",
         "    procedure Speak; virtual;", "  end;", "var a: TAnimal;", "begin",
         "  a := TAnimal.Create;", "  a.Name := 'Cat';", "  a.Free;", "end."],
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        [],
    ),
    "oop_03": (
        "destructor TMyClass.Destroy;\nbegin\n  inherited Destroy;\nend;",
        "___",
        ["destructor TMyClass.Destroy;", "begin", "  inherited Destroy;", "end;"],
        [0, 1, 2, 3],
        [],
    ),
    "oop_13": (
        "type\n  TMyClass = class\n    x: integer;\n  end;",
        "___",
        ["type", "  TMyClass = class", "    x: integer;", "  end;"],
        [0, 1, 2, 3],
        [],
    ),
    "oop_06": (
        "type\n  TBase = class\n    procedure Hello; virtual;\n  end;\n  TChild = class(TBase)\n    procedure Hello; override;\n  end;",
        "___",
        ["type", "  TBase = class", "    procedure Hello; virtual;", "  end;",
         "  TChild = class(TBase)", "    procedure Hello; override;", "  end;"],
        [0, 1, 2, 3, 4, 5, 6],
        [],
    ),
    "oop_16": (
        "procedure TMyClass.SetX(val: integer);\nbegin\n  Self.FX := val;\nend;",
        "___",
        ["procedure TMyClass.SetX(val: integer);", "begin",
         "  Self.FX := val;", "end;"],
        [0, 1, 2, 3],
        [],
    ),
    "oop_17": (
        "constructor TMyClass.Create(val: integer);\nbegin\n  inherited Create;\n  FX := val;\nend;",
        "___",
        ["constructor TMyClass.Create(val: integer);", "begin",
         "  inherited Create;", "  FX := val;", "end;"],
        [0, 1, 2, 3, 4],
        [],
    ),
    "oop_18": (
        "property X: integer read FX write SetX;",
        "___",
        ["property X: integer", "read FX", "write SetX;"],
        [0, 1, 2],
        [],
    ),
    # ── pitfalls ──────────────────────────────────────────────────────────────
    "pit_12": (
        "if x > 0 then\nbegin\n  writeln('pos');\n  writeln('ok');\nend;",
        "___",
        ["if x > 0 then", "begin", "  writeln('pos');", "  writeln('ok');", "end;"],
        [0, 1, 2, 3, 4],
        [],
    ),
}

# Fallback when slot not in lookup table
_FALLBACK = (
    "print('Hello, World!')",
    '#include <iostream>\nusing namespace std;\nint main() {\n    cout << "Hello!" << endl;\n    return 0;\n}',
    'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello!");\n    }\n}',
    'using System;\nclass Program {\n    static void Main() {\n        Console.WriteLine("Hello!");\n    }\n}',
)


def _make_variants(slot_id: str, *, slot_pattern_id: str | None = None) -> dict[str, Any]:
    """Return known_language_variants for slot_id using the per-task lookup table."""
    from application.curriculum.content.algo_syntax_task_extra import (
        algo_reference_code,
        is_algo_syntax_slot,
    )

    if is_algo_syntax_slot(slot_id):
        python = algo_reference_code(slot_id, "python", slot_pattern_id=slot_pattern_id)
        cpp = algo_reference_code(slot_id, "cpp", slot_pattern_id=slot_pattern_id)
        java = algo_reference_code(slot_id, "java", slot_pattern_id=slot_pattern_id)
        csharp = algo_reference_code(slot_id, "csharp", slot_pattern_id=slot_pattern_id)
        if any(str(code).strip() for code in (python, cpp, java, csharp)):
            return build_known_language_variants(
                python=python,
                cpp=cpp,
                java=java,
                csharp=csharp,
            )
    codes = get_known_code(slot_id) or _FALLBACK
    python, cpp, java, csharp = codes
    return build_known_language_variants(python=python, cpp=cpp, java=java, csharp=csharp)


def _known_language_extra(slot_id: str, **fields: Any) -> dict[str, Any]:
    """Every v3.1.1 task exposes «Я знаю» with task-specific code snippets."""
    slot_pattern_id = str(fields.get("slot_pattern_id") or "").strip() or None
    variants = _make_variants(slot_id, slot_pattern_id=slot_pattern_id)
    payload: dict[str, Any] = {
        "known_language_variants": variants,
        "assemble_context": code_examples_from_variants(variants),
    }
    payload.update(fields)
    return payload


def _attach_expected_concepts(
    extra: dict[str, Any],
    *,
    slot_id: str,
    chapter_key: str,
    pascal_features: str,
    task_format: str,
    slot_pattern_id: str | None = None,
) -> dict[str, Any]:
    from application.curriculum.content.algo_syntax_showcase_meta import (
        attach_expected_concepts_to_extra,
    )
    from application.curriculum.content.algo_syntax_task_extra import is_algo_syntax_slot
    from application.curriculum.pascal.catalog.pascal_v311_expected_concepts import (
        expected_concept_ids_for_row,
    )

    pattern = slot_pattern_id or str(extra.get("slot_pattern_id") or "").strip() or None
    if is_algo_syntax_slot(slot_id):
        enriched = attach_expected_concepts_to_extra(
            extra,
            slot_id=slot_id,
            slot_pattern_id=pattern,
        )
        if enriched.get("expected_concepts"):
            return enriched

    extra["expected_concept_ids"] = expected_concept_ids_for_row(
        slot_id=slot_id,
        chapter_key=chapter_key,
        pascal_features=pascal_features,
        task_format=task_format,
    )
    return extra


_SLOT_REFERENCE: dict[str, str] = {
    "psk_01": "program Demo;\nbegin\n  writeln('Hello, World!');\nend.",
    "psk_02": "program Demo;\nvar x: integer;\nbegin\n  x := 1;\n  writeln(x);\nend.",
    "psk_04": "program Demo;\nbegin\nend.",
    "psk_06": (
        "program Demo;\n"
        "begin\n"
        "  Writeln('start');\n"
        "  Writeln('finish');\n"
        "end."
    ),
    "psk_09": "{ Однострочный }\n(* Многострочный *)",
    "pit_01": (
        "program Demo;\n"
        "var\n"
        "  x: integer;\n"
        "begin\n"
        "  Readln(x);\n"
        "  if x > 0 then\n"
        "    Writeln('positive')\n"
        "  else\n"
        "    Writeln('negative');\n"
        "end.\n"
    ),
    "pit_02": (
        "program Demo;\n"
        "var\n"
        "  p: ^integer;\n"
        "begin\n"
        "  New(p);\n"
        "  p^ := 1;\n"
        "  Writeln(p^);\n"
        "  Dispose(p);\n"
        "end.\n"
    ),
    "pit_03": (
        "program Demo;\n"
        "var\n"
        "  s: string;\n"
        "begin\n"
        "  s := 'Hello';\n"
        "  Writeln(s[1]);\n"
        "end.\n"
    ),
    "pit_04": (
        "program Demo;\n"
        "var\n"
        "  i: integer;\n"
        "begin\n"
        "  for i := 1 to 5 do\n"
        "    Writeln(i);\n"
        "end.\n"
    ),
    "pit_07": (
        "unit source;\n"
        "\n"
        "interface\n"
        "\n"
        "implementation\n"
        "\n"
        "end.\n"
    ),
    "pit_08": (
        "program Demo;\n"
        "\n"
        "function DoubleValue(n: integer): integer;\n"
        "begin\n"
        "  Result := 0;\n"
        "  Result := n * 2;\n"
        "end;\n"
        "\n"
        "begin\n"
        "  Writeln(DoubleValue(3));\n"
        "end.\n"
    ),
    "pit_10": (
        "program Demo;\n"
        "type\n"
        "  TPoint = record\n"
        "    x, y: integer;\n"
        "  end;\n"
        "var\n"
        "  p: TPoint;\n"
        "begin\n"
        "  p.x := 1;\n"
        "  p.y := 2;\n"
        "  with p do\n"
        "    Writeln(x);\n"
        "end.\n"
    ),
    "pit_13": (
        "unit MyUtils;\n"
        "\n"
        "interface\n"
        "\n"
        "procedure Hello;\n"
        "\n"
        "implementation\n"
        "\n"
        "procedure Hello;\n"
        "begin\n"
        "  Writeln('ok');\n"
        "end;\n"
        "\n"
        "end.\n"
    ),
    "pit_14": (
        "program Demo;\n"
        "var\n"
        "  p: ^integer;\n"
        "begin\n"
        "  New(p);\n"
        "  p^ := 1;\n"
        "  Dispose(p);\n"
        "end.\n"
    ),
    "pit_15": (
        "program Demo;\n"
        "var\n"
        "  a: array[1..5] of integer;\n"
        "  i: integer;\n"
        "begin\n"
        "  for i := Low(a) to High(a) do\n"
        "    a[i] := i;\n"
        "  for i := Low(a) to High(a) do\n"
        "    Writeln(a[i]);\n"
        "end.\n"
    ),
    "pit_16": (
        "program Demo;\n"
        "\n"
        "procedure Swap(var a, b: integer);\n"
        "var\n"
        "  tmp: integer;\n"
        "begin\n"
        "  tmp := a;\n"
        "  a := b;\n"
        "  b := tmp;\n"
        "end;\n"
        "\n"
        "var\n"
        "  x, y: integer;\n"
        "begin\n"
        "  x := 1;\n"
        "  y := 2;\n"
        "  Swap(x, y);\n"
        "  Writeln(x);\n"
        "end.\n"
    ),
    "pit_17": (
        "program Demo;\n"
        "\n"
        "function Triple(n: integer): integer;\n"
        "begin\n"
        "  Result := n * 3;\n"
        "end;\n"
        "\n"
        "begin\n"
        "  Writeln(Triple(1));\n"
        "end.\n"
    ),
    "pit_18": (
        "program Demo;\n"
        "var\n"
        "  a: array of integer;\n"
        "  n: integer;\n"
        "begin\n"
        "  Readln(n);\n"
        "  SetLength(a, n);\n"
        "  if n > 0 then\n"
        "    Writeln(a[n - 1]);\n"
        "end.\n"
    ),
    "pit_19": (
        "program Demo;\n"
        "type\n"
        "  TRec = record\n"
        "    x: integer;\n"
        "  end;\n"
        "var\n"
        "  r: TRec;\n"
        "  x: integer;\n"
        "begin\n"
        "  r.x := 5;\n"
        "  x := 1;\n"
        "  with r do\n"
        "    r.x := 9;\n"
        "  Writeln(r.x);\n"
        "end.\n"
    ),
    "pit_21": (
        "program Demo;\n"
        "\n"
        "function Sum(a, b: integer): integer;\n"
        "begin\n"
        "  Result := a + b;\n"
        "end;\n"
        "\n"
        "begin\n"
        "  Writeln(Sum(2, 3));\n"
        "end.\n"
    ),
    "pit_22": (
        "program Demo;\n"
        "var\n"
        "  a: array of integer;\n"
        "  i: integer;\n"
        "begin\n"
        "  SetLength(a, 10);\n"
        "  for i := 0 to 9 do\n"
        "    a[i] := i + 1;\n"
        "  Writeln(a[0]);\n"
        "end.\n"
    ),
    "pit_23": (
        "program Demo;\n"
        "var\n"
        "  n: integer;\n"
        "begin\n"
        "  n := 0;\n"
        "  repeat\n"
        "    Inc(n);\n"
        "    Writeln(n);\n"
        "  until n >= 3;\n"
        "end.\n"
    ),
    "pit_24": (
        "program Demo;\n"
        "type\n"
        "  TBox = class\n"
        "  private\n"
        "    FX: integer;\n"
        "  public\n"
        "    property X: integer read FX write FX;\n"
        "  end;\n"
        "\n"
        "var\n"
        "  b: TBox;\n"
        "begin\n"
        "  b := TBox.Create;\n"
        "  b.X := 1;\n"
        "  Writeln(b.X);\n"
        "end.\n"
    ),
}
_SLOT_REFERENCE["str_07"] = (
    "program Demo;\n"
    "var\n"
    "  s, sub, result: string;\n"
    "begin\n"
    "  readln(s);\n"
    "  sub := Copy(s, 1, 3);\n"
    "  result := Concat(sub, '!');\n"
    "  writeln(result);\n"
    "end."
)
_SLOT_REFERENCE.update(V32_REFERENCE)
_SLOT_REFERENCE.update(capstone_reference_pascal())

_CAPSTONE_STARTER = capstone_starter_pascal()

_SLOT_DEBUG_STARTER: dict[str, str] = {
    "psk_02": (
        "program Demo;\n"
        "var\n"
        "  x: integer;\n"
        "begin\n"
        "  x := 1\n"
        "  writeln(x);\n"
        "end.\n"
    ),
    "cdg_06": (
        "program Demo;\n"
        "var\n"
        "  n: integer;\n"
        "begin\n"
        "  n := 1\n"
        "  Writeln(n);\n"
        "end.\n"
    ),
    "pit_01": (
        "program Demo;\n"
        "var\n"
        "  x: integer;\n"
        "begin\n"
        "  Readln(x);\n"
        "  if x > 0 then\n"
        "    Writeln('positive');\n"
        "  ;\n"
        "  else\n"
        "    Writeln('negative');\n"
        "end.\n"
    ),
    "pit_02": (
        "program Demo;\n"
        "var\n"
        "  p: ^integer;\n"
        "begin\n"
        "  Writeln(p^);\n"
        "end.\n"
    ),
    "pit_03": (
        "program Demo;\n"
        "var\n"
        "  s: string;\n"
        "begin\n"
        "  s := 'Hello';\n"
        "  Writeln(s[0]);\n"
        "end.\n"
    ),
    "pit_04": (
        "program Demo;\n"
        "var\n"
        "  i: integer;\n"
        "begin\n"
        "  for i := 1 to 5 do\n"
        "  begin\n"
        "    i := i + 1;\n"
        "    Writeln(i);\n"
        "  end;\n"
        "end.\n"
    ),
    "pit_07": (
        "unit MyUtils;\n"
        "\n"
        "interface\n"
        "\n"
        "implementation\n"
        "\n"
        "end.\n"
    ),
    "pit_08": (
        "program Demo;\n"
        "\n"
        "function DoubleValue(n: integer): integer;\n"
        "begin\n"
        "  Writeln(Result);\n"
        "  Result := n * 2;\n"
        "end;\n"
        "\n"
        "begin\n"
        "  Writeln(DoubleValue(3));\n"
        "end.\n"
    ),
    "pit_10": (
        "program Demo;\n"
        "type\n"
        "  TPoint = record\n"
        "    x, y: integer;\n"
        "  end;\n"
        "var\n"
        "  p: TPoint;\n"
        "begin\n"
        "  p.x := 1;\n"
        "  p.y := 2;\n"
        "  with p do\n"
        "    with p do\n"
        "      Writeln(x);\n"
        "end.\n"
    ),
    "pit_13": (
        "unit MyUtils;\n"
        "\n"
        "interface\n"
        "\n"
        "procedure Hello;\n"
        "begin\n"
        "  Writeln('ok');\n"
        "end;\n"
        "\n"
        "implementation\n"
        "\n"
        "end.\n"
    ),
    "pit_14": (
        "program Demo;\n"
        "var\n"
        "  p: ^integer;\n"
        "begin\n"
        "  Dispose(p);\n"
        "end.\n"
    ),
    "pit_15": (
        "program Demo;\n"
        "var\n"
        "  a: array[1..5] of integer;\n"
        "  i: integer;\n"
        "begin\n"
        "  for i := Low(a) to High(a) do\n"
        "    a[i] := i;\n"
        "  for i := Low(a) to High(a) do\n"
        "    Writeln(a[Low(a)]);\n"
        "end.\n"
    ),
    "pit_16": (
        "program Demo;\n"
        "\n"
        "procedure Swap(a, b: integer);\n"
        "var\n"
        "  tmp: integer;\n"
        "begin\n"
        "  tmp := a;\n"
        "  a := b;\n"
        "  b := tmp;\n"
        "end;\n"
        "\n"
        "var\n"
        "  x, y: integer;\n"
        "begin\n"
        "  x := 1;\n"
        "  y := 2;\n"
        "  Swap(x, y);\n"
        "  Writeln(x);\n"
        "end.\n"
    ),
    "pit_17": (
        "program Demo;\n"
        "\n"
        "function Triple(n: integer): integer;\n"
        "begin\n"
        "  exit(n * 3);\n"
        "end;\n"
        "\n"
        "begin\n"
        "  Writeln(Triple(1));\n"
        "end.\n"
    ),
    "pit_18": (
        "program Demo;\n"
        "var\n"
        "  a: array of integer;\n"
        "  n: integer;\n"
        "begin\n"
        "  Readln(n);\n"
        "  SetLength(a, n);\n"
        "  Writeln(a[n]);\n"
        "end.\n"
    ),
    "pit_19": (
        "program Demo;\n"
        "type\n"
        "  TRec = record\n"
        "    x: integer;\n"
        "  end;\n"
        "var\n"
        "  r: TRec;\n"
        "  x: integer;\n"
        "begin\n"
        "  r.x := 5;\n"
        "  x := 1;\n"
        "  with r do\n"
        "    x := 9;\n"
        "  Writeln(r.x);\n"
        "end.\n"
    ),
    "pit_21": (
        "program Demo;\n"
        "\n"
        "procedure Sum(a, b: integer): integer;\n"
        "begin\n"
        "  Result := a + b;\n"
        "end;\n"
        "\n"
        "begin\n"
        "  Writeln(Sum(2, 3));\n"
        "end.\n"
    ),
    "pit_22": (
        "program Demo;\n"
        "var\n"
        "  a: array[1..10] of integer;\n"
        "  i: integer;\n"
        "begin\n"
        "  SetLength(a, 10);\n"
        "  for i := 1 to 10 do\n"
        "    a[i] := i;\n"
        "  Writeln(a[1]);\n"
        "end.\n"
    ),
    "pit_23": (
        "program Demo;\n"
        "var\n"
        "  n: integer;\n"
        "begin\n"
        "  n := 0;\n"
        "  repeat\n"
        "    Inc(n);\n"
        "    Writeln(n);\n"
        "  until n > 3;\n"
        "end.\n"
    ),
    "pit_24": (
        "program Demo;\n"
        "type\n"
        "  TBox = class\n"
        "  public\n"
        "    property X: integer read GetX write SetX;\n"
        "  end;\n"
        "\n"
        "var\n"
        "  b: TBox;\n"
        "begin\n"
        "  b := TBox.Create;\n"
        "  b.X := 1;\n"
        "  Writeln(b.X);\n"
        "end.\n"
    ),
}
_SLOT_DEBUG_STARTER.update(V32_DEBUG_STARTER)
_SLOT_ASSEMBLY.update(V32_ASSEMBLY)


def reference_solution_for_slot(slot_id: str, *, slot_pattern_id: str | None = None) -> str:
    """Public Pascal reference fragment for a curriculum slot (mirror «Я знаю» source)."""
    if slot_id in _SLOT_REFERENCE:
        return _SLOT_REFERENCE[slot_id]
    assembly = _SLOT_ASSEMBLY.get(slot_id)
    if assembly:
        return str(assembly[0]).strip()
    return _reference_solution(slot_id, "", slot_pattern_id=slot_pattern_id)


def _reference_solution(slot_id: str, features: str, *, slot_pattern_id: str | None = None) -> str:
    from application.curriculum.content.algo_syntax_task_extra import (
        algo_reference_code,
        is_algo_syntax_slot,
        resolve_slot_pattern_key,
    )

    if is_algo_syntax_slot(slot_id):
        ref = algo_reference_code(slot_id, "pascal", slot_pattern_id=slot_pattern_id)
        if ref:
            return ref
    if slot_id in _SLOT_REFERENCE:
        return _SLOT_REFERENCE[slot_id]
    try:
        from application.curriculum.content.v4_reference_code import get_reference_code

        pattern = resolve_slot_pattern_key(slot_id, slot_pattern_id=slot_pattern_id)
        code = get_reference_code(slot_id, "pascal", pattern_key=pattern)
        if code:
            return code
    except ImportError:
        pass
    return _PASCAL_SNIPPET


def _debug_starter(slot_id: str) -> str:
    from application.curriculum.content.algo_syntax_task_extra import (
        algo_debug_starter,
        is_algo_syntax_slot,
    )

    if is_algo_syntax_slot(slot_id):
        starter = algo_debug_starter(slot_id, "pascal")
        if starter:
            return starter
    if slot_id in _SLOT_DEBUG_STARTER:
        return _SLOT_DEBUG_STARTER[slot_id]
    if slot_id in _CAPSTONE_STARTER:
        return _CAPSTONE_STARTER[slot_id]
    return (
        "program Demo;\n"
        "var x: integer;\n"
        "begin\n"
        "  x = 1;\n"
        "  writeln(x);\n"
        "end.\n"
    )


def _debug_solution(slot_id: str) -> str:
    from application.curriculum.content.algo_syntax_task_extra import (
        algo_debug_solution,
        is_algo_syntax_slot,
    )

    if is_algo_syntax_slot(slot_id):
        fixed = algo_debug_solution(slot_id, "pascal")
        if fixed:
            return fixed
    if slot_id in _SLOT_REFERENCE:
        return _SLOT_REFERENCE[slot_id]
    return (
        "program Demo;\n"
        "var x: integer;\n"
        "begin\n"
        "  x := 1;\n"
        "  writeln(x);\n"
        "end.\n"
    )


def _mcq_options(slot_id: str, features: str) -> tuple[list[str], int, str]:
    slot_mcq: dict[str, tuple[list[str], int, str]] = {
        "psk_07": (
            [
                "program Demo;\nbegin\n  writeln('ok');\nend.",
                "program Demo;\nbegin\n  writeln('ok');\nend",
                "program Demo;\n  begin\n  writeln('ok');\nend.",
                "begin\n  writeln('ok');\nend.",
            ],
            0,
            "Каркас Pascal завершайте точкой после end: end., а не end.",
        ),
        "psk_08": (
            [
                "program Demo;\nuses SysUtils;\nbegin\nend.",
                "program Demo;\nbegin\nuses SysUtils;\nend.",
                "uses SysUtils;\nprogram Demo;\nbegin\nend.",
                "program Demo;\nbegin\nend.\nuses SysUtils;",
            ],
            0,
            "Директива uses должна стоять после program и до begin.",
        ),
    }
    if slot_id in slot_mcq:
        return slot_mcq[slot_id]

    correct = _PASCAL_SNIPPET
    distractors = [
        "x = 1;",
        "if x then y;",
        "for i in 1..10 do;",
    ]
    return [correct, *distractors], 0, "Корректный фрагмент использует синтаксис Pascal."


# Per-slot test case overrides — more specific than the format defaults.
# Each entry is a list[dict] with "inputs" and "output" keys.
_SLOT_TEST_CASES: dict[str, list[dict[str, str]]] = {
    # ── 1. program_skeleton ───────────────────────────────────────────────────
    "psk_01": [{"inputs": "", "output": "Hello, World!"}],
    "psk_02": [{"inputs": "", "output": "1"}],
    "psk_04": [{"inputs": "", "output": ""}],
    "psk_06": [{"inputs": "", "output": "start\nfinish"}],
    # flowchart: каркас program — reads n, checks n > 0
    "psk_05": [{"inputs": "3\n", "output": "positive"}, {"inputs": "-2\n", "output": "non-positive"}],
    # ── 2. typed_variables ────────────────────────────────────────────────────
    "typ_01": [{"inputs": "", "output": ""}],
    "typ_02": [{"inputs": "", "output": "1"}],
    "typ_09": [{"inputs": "", "output": "2"}],   # trunc(7/3) = 2
    "typ_10": [{"inputs": "", "output": ""}],
    # ── 3. io ─────────────────────────────────────────────────────────────────
    "io_01": [{"inputs": "5\n", "output": "5"}],
    "io_02": [{"inputs": "", "output": ""}],
    "io_09": [{"inputs": "4\n", "output": "4"}],
    # ── 4. expressions ────────────────────────────────────────────────────────
    "exp_01": [{"inputs": "", "output": ""}],
    "exp_02": [{"inputs": "", "output": "5"}],
    # поиск_ошибки: mod from real — fixed code outputs integer mod result
    "exp_06": [],
    # ── 5. conditions ─────────────────────────────────────────────────────────
    "cnd_01": [{"inputs": "5\n", "output": "positive"}, {"inputs": "-1\n", "output": "non-positive"}],
    "cnd_03": [{"inputs": "1\n", "output": "one"}, {"inputs": "2\n", "output": "two"}],
    "cnd_04": [{"inputs": "5\n", "output": "positive"}, {"inputs": "-1\n", "output": "non-positive"}],
    "cnd_07": [{"inputs": "", "output": "1"}],
    "cnd_08": [{"inputs": "1\n", "output": "one"}],
    "cnd_09": [{"inputs": "3\n", "output": "3"}, {"inputs": "-3\n", "output": "3"}],
    "cnd_11": [{"inputs": "5\n", "output": "positive"}, {"inputs": "-1\n", "output": "non-positive"}],
    "cnd_13": [],   # поиск_ошибки: spot the semicolon-before-else
    "cnd_14": [{"inputs": "1\n", "output": "one"}, {"inputs": "2\n", "output": "two"}],
    # ── 6. loops ──────────────────────────────────────────────────────────────
    "lop_03": [{"inputs": "4\n", "output": "4\n3\n2\n1"}],
    "lop_04": [{"inputs": "5\n", "output": "1\n2\n3\n4\n5"}],
    "lop_06": [{"inputs": "3\n", "output": "1\n2\n3"}],
    "lop_08": [{"inputs": "3\n2\n0\n", "output": "5"}],  # repeat until fixed
    "lop_09": [{"inputs": "10\n", "output": "1\n2\n3\n4\n5"}],  # break at 5
    "lop_14": [],   # поиск_ошибки: i := 1 to 10
    "lop_15": [{"inputs": "5\n", "output": "5\n4\n3\n2\n1"}],
    # ── 7. functions ──────────────────────────────────────────────────────────
    "fn_03": [{"inputs": "", "output": "1"}],
    "fn_04": [{"inputs": "5\n", "output": "120"}],   # factorial
    "fn_08": [],   # поиск_ошибки: nested function
    # ── 8. procedures ─────────────────────────────────────────────────────────
    "prc_02": [{"inputs": "", "output": "2\n1"}],   # swap outputs
    "prc_09": [{"inputs": "", "output": "Hello!"}],
    "prc_12": [],   # поиск_ошибки: value vs var
    # ── 9. arrays ─────────────────────────────────────────────────────────────
    "arr_03": [{"inputs": "", "output": "1"}],
    "arr_09": [],   # поиск_ошибки: out of bounds
    # ── 10. dynamic arrays ────────────────────────────────────────────────────
    "dyn_02": [{"inputs": "", "output": "1"}],
    "dyn_09": [],   # поиск_ошибки: array[0..n] for dynamic
    "dyn_10": [{"inputs": "", "output": "1"}],
    "dyn_11": [{"inputs": "3\n", "output": "3"}],   # array growth flowchart
    # ── 11. strings ───────────────────────────────────────────────────────────
    "str_03": [{"inputs": "", "output": "o"}],   # last char of 'hello'
    # ── 12. records ───────────────────────────────────────────────────────────
    "rec_03": [{"inputs": "", "output": "1"}],
    "rec_04": [{"inputs": "", "output": "1"}],
    "rec_10": [],   # поиск_ошибки: with scope
    # ── 13. files ─────────────────────────────────────────────────────────────
    "fil_03": [{"inputs": "", "output": "1"}],
    "fil_07": [],   # поиск_ошибки: Reset without Assign
    # ── 14. units ─────────────────────────────────────────────────────────────
    "unt_03": [{"inputs": "", "output": "1"}],
    "unt_05": [{"inputs": "", "output": "1"}],
    "unt_06": [],   # поиск_ошибки: circular uses
    "unt_09": [{"inputs": "", "output": "1"}],
    # ── 16. recursion ─────────────────────────────────────────────────────────
    "rcu_02": [{"inputs": "5\n", "output": "120"}],  # factorial base case fix
    "rcu_04": [],   # поиск_ошибки: infinite recursion
    "rcu_06": [],   # поиск_ошибки: forward compile error
    "rcu_07": [{"inputs": "4\n", "output": "24"}],  # recursion flowchart: factorial
    # ── 17. OOP ───────────────────────────────────────────────────────────────
    "oop_04": [{"inputs": "", "output": "1"}],
    "oop_05": [{"inputs": "", "output": "1"}],
    "oop_07": [],   # поиск_ошибки: property read/write
    "oop_08": [{"inputs": "", "output": "1"}],
    "oop_09": [{"inputs": "", "output": "1"}],
    "oop_11": [],   # поиск_ошибки: incompatible types
    "oop_15": [{"inputs": "", "output": "1"}],
    # ── 18. pitfalls ──────────────────────────────────────────────────────────
    "pit_01": [{"inputs": "", "output": "1"}],
    "pit_02": [{"inputs": "", "output": "1"}],
    "pit_03": [{"inputs": "", "output": "H"}],  # s[1] for 'Hello'
    "pit_04": [],   # поиск_ошибки: modifying for control var
    "pit_07": [],   # поиск_ошибки: unit name ≠ filename
    "pit_08": [{"inputs": "", "output": "1"}],
    "pit_10": [{"inputs": "", "output": "1"}],
    "pit_13": [],   # поиск_ошибки: procedure body in interface
    "pit_14": [],   # поиск_ошибки: Dispose without New
    "pit_15": [{"inputs": "", "output": "1"}],
    "pit_16": [{"inputs": "", "output": "1"}],
    "pit_17": [{"inputs": "", "output": "1"}],
    "pit_18": [{"inputs": "3\n", "output": "3"}],
    "pit_19": [],   # поиск_ошибки: with shadows field
    "pit_21": [],   # поиск_ошибки: function declared as procedure
    "pit_22": [{"inputs": "", "output": "1"}],
    "pit_23": [{"inputs": "", "output": "1"}],
    "pit_24": [],   # поиск_ошибки: property without backing field
    # ── compiler diagnostics ──────────────────────────────────────────────────
    "cdg_01": [{"inputs": "", "output": "1"}],
    "cdg_02": [{"inputs": "", "output": "1"}],
    "cdg_03": [],   # поиск_ошибки: incompatible types
    "cdg_04": [{"inputs": "", "output": "1"}],
    "cdg_05": [{"inputs": "", "output": "1"}],
    "cdg_06": [{"inputs": "", "output": "1"}],
    "cdg_07": [{"inputs": "", "output": "1"}],
    "cdg_09": [{"inputs": "", "output": "1"}],
    "cdg_11": [{"inputs": "", "output": "1"}],
    "cdg_12": [],   # поиск_ошибки: virtual/override
    "cdg_13": [{"inputs": "", "output": "1"}],
    "cdg_14": [{"inputs": "", "output": "1"}],
    "cdg_15": [],   # поиск_ошибки: array bounds
}
_SLOT_TEST_CASES.update(V32_TEST_CASES)
_SLOT_TEST_CASES.update(capstone_test_cases())

# Default test cases by format type
_FORMAT_DEFAULT_TEST_CASES: dict[str, list[dict[str, str]]] = {
    "перевод_программы":  [{"inputs": "", "output": "Hello, World!"}],
    "исправление":        [{"inputs": "", "output": "1"}],
    "поиск_ошибки":       [],
    "сборка_программы":   [{"inputs": "", "output": "2"}],
    "перевод_фрагмента":  [],
    "сборка_фрагмента":   [],
    "выбор_фрагмента":    [],
    "код_по_блок-схеме":  [{"inputs": "5\n", "output": "positive"}],
    "блок-схема_по_коду": [],
}

_SLOT_FLOWCHART_EXTRA: dict[str, dict[str, Any]] = {
    "psk_06": {
        "concept_patterns": [],
        "flow_spec": {
            "required_sequence": ["start", "output", "output", "end"],
            "required_text_checks": [
                {"type": "output", "contains_any": ["start", "writeln"]},
                {"type": "output", "contains_any": ["finish"]},
            ],
        },
    },
}


def _task_test_cases(slot_id: str, task_format: str, row: TaskRow | None = None) -> list[dict[str, str]]:
    from application.curriculum.content.algo_syntax_task_extra import (
        algo_test_cases,
        is_algo_syntax_slot,
    )

    slot_pattern_id = None
    if row is not None and len(row) > 5:
        slot_pattern_id = str(row[5] or "").strip() or None
    if is_algo_syntax_slot(slot_id):
        cases = algo_test_cases(slot_id, slot_pattern_id=slot_pattern_id)
        if cases:
            return cases
    if row is not None:
        return derive_test_cases(row, measured=MEASURED_OUTPUTS)
    if task_format in {"сборка_программы", "сборка_фрагмента"} and slot_id in _SLOT_ASSEMBLY:
        asm_tc = _SLOT_ASSEMBLY[slot_id][4]
        if asm_tc:
            return asm_tc
    if slot_id in _SLOT_PLACEHOLDER:
        ph_tc = _SLOT_PLACEHOLDER[slot_id][2]
        if ph_tc:
            return ph_tc
    if slot_id in _SLOT_TEST_CASES and _SLOT_TEST_CASES[slot_id]:
        return _SLOT_TEST_CASES[slot_id]
    return _FORMAT_DEFAULT_TEST_CASES.get(task_format, [{"inputs": "", "output": "ok"}])


def build_task_extra(row: TaskRow) -> dict[str, Any]:
    slot_id, chapter, title, task_format, _action, pattern, goal, features, _diff, _legacy = row
    if slot_id in _SLOT_DESCRIPTIONS:
        goal = _SLOT_DESCRIPTIONS[slot_id]
    ref = _reference_solution(slot_id, features, slot_pattern_id=pattern)
    test_cases = _task_test_cases(slot_id, task_format, row)

    def _finalize(extra: dict[str, Any]) -> dict[str, Any]:
        return _attach_expected_concepts(
            extra,
            slot_id=slot_id,
            chapter_key=chapter,
            pascal_features=features,
            task_format=task_format,
            slot_pattern_id=pattern,
        )

    if task_format in {"перевод_программы", "перевод_фрагмента"}:
        from application.curriculum.content.algo_syntax_task_extra import (
            algo_translation_starter,
            is_algo_syntax_slot,
        )

        snippet = task_format == "перевод_фрагмента"
        is_program = bool(re.search(r"\bprogram\b", ref, re.I))
        starter = _CAPSTONE_STARTER.get(slot_id, "")
        if is_algo_syntax_slot(slot_id):
            starter = algo_translation_starter(slot_id, "pascal")
        translate_extra: dict[str, Any] = dict(
            reference_solution_pascal=ref if (snippet or is_program) else _PASCAL_PROGRAM,
            test_cases=test_cases,
            slot_pattern_id=pattern,
            educational_goal=goal,
            pascal_features=features,
        )
        if starter:
            translate_extra["starter_pascal"] = starter
        return _finalize(_known_language_extra(slot_id, **translate_extra))

    if task_format in {"исправление", "поиск_ошибки"}:
        mode = "find" if task_format == "поиск_ошибки" else "fix"
        from application.curriculum.content.algo_syntax_task_extra import (
            algo_debug_assembly_payload,
            algo_multilingual_debug_assembly,
            is_algo_syntax_slot,
        )

        if is_algo_syntax_slot(slot_id):
            debug_asm = algo_debug_assembly_payload(
                slot_id, "pascal", slot_pattern_id=pattern
            )
            if debug_asm:
                extra = _known_language_extra(
                    slot_id,
                    language="pascal",
                    original_code=debug_asm["original_code"],
                    template=debug_asm["template"],
                    blocks=debug_asm["blocks"],
                    correct_order=debug_asm["correct_order"],
                    reference_solution_pascal=debug_asm["reference_solution"],
                    test_cases=test_cases,
                    debug_mode=mode,
                    slot_pattern_id=pattern,
                    educational_goal=goal,
                    pascal_features=features,
                )
                extra["language_variants"] = algo_multilingual_debug_assembly(
                    slot_id, slot_pattern_id=pattern
                )
                return _finalize(extra)

        return _finalize(_known_language_extra(
            slot_id,
            starter_pascal=_debug_starter(slot_id),
            reference_solution_pascal=_debug_solution(slot_id),
            test_cases=test_cases,
            debug_mode=mode,
            slot_pattern_id=pattern,
            educational_goal=goal,
            pascal_features=features,
        ))

    if task_format in {"сборка_программы", "сборка_фрагмента"}:
        from application.curriculum.content.algo_syntax_task_extra import (
            algo_assembly_payload,
            algo_multilingual_assembly,
            is_algo_syntax_slot,
        )
        from application.curriculum.content.v4_assembly_builder import (
            build_multilingual_assembly_variants,
        )

        if is_algo_syntax_slot(slot_id):
            asm_orig, asm_tpl, asm_blocks, asm_order = algo_assembly_payload(
                slot_id,
                "pascal",
                task_format=task_format,
                slot_pattern_id=pattern,
            )
            effective_tc = test_cases
            language_variants = algo_multilingual_assembly(
                slot_id, task_format=task_format, slot_pattern_id=pattern
            )
        elif slot_id in _SLOT_PLACEHOLDER:
            from application.curriculum.content.algo_syntax_task_extra import _placeholder_assembly

            ph_code, ph_gaps, ph_tc = _SLOT_PLACEHOLDER[slot_id]
            asm_orig, asm_tpl, asm_blocks, asm_order = _placeholder_assembly(
                ph_code,
                ph_gaps,
                language="pascal",
                reference_code=ref,
            )
            effective_tc = test_cases or ph_tc
            language_variants = None
        elif slot_id in _SLOT_ASSEMBLY:
            asm_orig, asm_tpl, asm_blocks, asm_order, asm_tc = _SLOT_ASSEMBLY[slot_id]
            effective_tc = test_cases or asm_tc
            language_variants = None
        else:
            from application.curriculum.content.v4_assembly_builder import primary_assembly_extra

            asm = primary_assembly_extra(
                slot_id,
                "pascal",
                task_format=task_format,
                reference_code=ref,
            )
            asm_orig = asm["original_code"]
            asm_tpl = asm["template"]
            asm_blocks = asm["blocks"]
            asm_order = asm["correct_order"]
            effective_tc = test_cases
            language_variants = build_multilingual_assembly_variants(slot_id, task_format=task_format) or None

        extra = _finalize(_known_language_extra(
            slot_id,
            language="pascal",
            original_code=asm_orig,
            template=asm_tpl,
            blocks=asm_blocks,
            correct_order=asm_order,
            reference_solution_pascal=ref,
            test_cases=effective_tc,
            slot_pattern_id=pattern,
            educational_goal=goal,
            pascal_features=features,
        ))
        if language_variants:
            extra["language_variants"] = language_variants
        return extra

    if task_format == "выбор_фрагмента":
        options, correct_index, explanation = _mcq_options(slot_id, features)
        return _finalize(_known_language_extra(
            slot_id,
            mcq_prompt=goal,
            mcq_options=options,
            correct_index=correct_index,
            explanation=explanation,
            reference_solution_pascal=options[correct_index],
            test_cases=test_cases,
            slot_pattern_id=pattern,
            educational_goal=goal,
            pascal_features=features,
        ))

    if task_format == "код_по_блок-схеме":
        return _finalize(_known_language_extra(
            slot_id,
            diagram=diagram_if_n_pos(),
            reference_code_pascal=ref,
            expose_reference_code=False,
            flowchart_mode="flowchart_to_code",
            test_cases=test_cases,
            slot_pattern_id=pattern,
            educational_goal=goal,
            pascal_features=features,
        ))

    if task_format == "блок-схема_по_коду":
        flow_extra = _SLOT_FLOWCHART_EXTRA.get(slot_id, {})
        flow_spec: dict[str, Any] = {"nodes": [], "edges": []}
        flow_spec.update(flow_extra.get("flow_spec") or {})
        extra_fields: dict[str, Any] = {
            "diagram": empty_diagram(),
            "reference_code_pascal": ref,
            "expose_reference_code": True,
            "flowchart_mode": "code_to_flowchart",
            "flow_spec": flow_spec,
            "test_cases": test_cases,
            "slot_pattern_id": pattern,
            "educational_goal": goal,
            "pascal_features": features,
        }
        if "concept_patterns" in flow_extra:
            extra_fields["concept_patterns"] = flow_extra["concept_patterns"]
        return _finalize(_known_language_extra(slot_id, **extra_fields))

    raise ValueError(f"Unsupported task_format for {slot_id}: {task_format}")
