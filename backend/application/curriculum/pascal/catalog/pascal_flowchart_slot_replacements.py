"""Replace 11 pedagogical slots with flowchart-based tasks (102 total unchanged)."""

from __future__ import annotations

from application.curriculum.pascal.catalog.pascal_flowchart_diagrams import (
    diagram_case_code,
    diagram_for_sum_n,
    diagram_grade_chain,
    diagram_if_n_pos,
    diagram_if_parity,
    diagram_linear_search,
    diagram_multi_branch_score,
    diagram_nested_sum_products,
    diagram_pow2_recursion,
    diagram_while_countdown,
)
from application.curriculum.pascal.catalog.pascal_pedagogical_slot import PedagogicalSlotSpec
from application.curriculum.pascal.catalog.pascal_v2_slot_factories import (
    code_to_flowchart_slot,
    flowchart_to_blocks_slot,
    flowchart_to_code_slot,
)

_ALLOWED_BLOCKS = [
    "start",
    "input",
    "process",
    "decision",
    "loop",
    "output",
    "end",
]

_COND_IF_REF = (
    "program PosCheck;\nvar n: integer;\nbegin\n  readln(n);\n  if n > 0 then\n    writeln('pos')\n"
    "  else\n    writeln('nonpos');\nend."
)

_LOOP_FOR_REF = (
    "program SumN;\nvar i, n, s: integer;\nbegin\n  readln(n);\n  s := 0;\n  for i := 1 to n do\n"
    "    s := s + i;\n  writeln(s);\nend."
)

_ALG_SEARCH_REF = (
    "program Contains3;\nvar a, b, c, t: integer;\nbegin\n  readln(a);\n  readln(b);\n  readln(c);\n"
    "  readln(t);\n  if (a = t) or (b = t) or (c = t) then writeln('yes') else writeln('no');\nend."
)

_LOOP_NESTED_REF = (
    "program NestedSum;\nvar i, j, n, m, s: integer;\nbegin\n  readln(n);\n  readln(m);\n  s := 0;\n"
    "  for i := 1 to n do\n    for j := 1 to m do\n      s := s + i * j;\n  writeln(s);\nend."
)

_RECU_POW2_REF = (
    "function Pow2(n: integer): integer;\nbegin\n  if n = 0 then Pow2 := 1\n"
    "  else Pow2 := 2 * Pow2(n - 1);\nend;\nvar n: integer;\nbegin\n  readln(n);\n  writeln(Pow2(n));\nend."
)

_COND_CASE_REF = (
    "program CaseCode;\nvar code: integer;\nbegin\n  readln(code);\n  case code of\n    1: writeln('one');\n"
    "    2: writeln('two');\n  else writeln('other');\n  end;\nend."
)

_LOOP_WHILE_REF = (
    "program Countdown;\nvar n: integer;\nbegin\n  readln(n);\n  while n > 0 do\n  begin\n    writeln(n);\n"
    "    n := n - 1;\n  end;\nend."
)

_COND_GRADE_REF = (
    "program Grade;\nvar score: integer;\nbegin\n  readln(score);\n  if score >= 90 then writeln('A')\n"
    "  else if score >= 70 then writeln('B')\n  else writeln('C');\nend."
)


def flowchart_slot_replacements() -> dict[str, PedagogicalSlotSpec]:
    return {
        "alg_s01": flowchart_to_code_slot(
            slot_id="alg_s01",
            collection_key="algorithms",
            target_tc="search_find",
            slug="alg_search_find_imp_text_contains",
            title_suffix="Поиск: напишите код по схеме",
            short_instruction="По блок-схеме слева напишите Pascal-программу линейного поиска.",
            description=(
                "Слева — блок-схема: проверка a = t, b = t, c = t.\n\n"
                "Справа напишите программу на Pascal: считайте a, b, c, t и выведите `yes`, "
                "если t совпадает с одним из чисел, иначе `no`."
            ),
            difficulty="easy",
            diagram=diagram_linear_search(),
            reference_solution_pascal=_ALG_SEARCH_REF,
            test_cases=[
                {"inputs": "1\n5\n9\n5", "output": "yes"},
                {"inputs": "2\n3\n4\n1", "output": "no"},
            ],
        ),
        "loop_s06": flowchart_to_code_slot(
            slot_id="loop_s06",
            collection_key="loops",
            target_tc="nested_iteration",
            slug="nested_iteration_io",
            title_suffix="Вложенные циклы: код по схеме",
            short_instruction="Реализуйте двойной цикл по блок-схеме.",
            description=(
                "Слева — блок-схема вложенных циклов i и j с накоплением s := s + i * j.\n\n"
                "Справа напишите Pascal: считайте n и m, выведите сумму произведений."
            ),
            difficulty="hard",
            diagram=diagram_nested_sum_products(),
            reference_solution_pascal=_LOOP_NESTED_REF,
            test_cases=[
                {"inputs": "2\n3", "output": "18"},
                {"inputs": "1\n1", "output": "1"},
            ],
        ),
        "recu_s02": flowchart_to_code_slot(
            slot_id="recu_s02",
            collection_key="recursion",
            target_tc="recursion",
            slug="recu_recursion_imp_text_pow2",
            title_suffix="Рекурсия Pow2: код по схеме",
            short_instruction="Напишите рекурсивную функцию по блок-схеме.",
            description=(
                "Слева — блок-схема Pow2(n): базовый случай n = 0 → 1, иначе 2 * Pow2(n-1).\n\n"
                "Справа напишите Pascal-программу, считывающую n и выводящую 2^n."
            ),
            difficulty="hard",
            diagram=diagram_pow2_recursion(),
            reference_solution_pascal=_RECU_POW2_REF,
            test_cases=[
                {"inputs": "0", "output": "1"},
                {"inputs": "5", "output": "32"},
            ],
        ),
        "cond_s08": flowchart_to_code_slot(
            slot_id="cond_s08",
            collection_key="conditions",
            target_tc="switch_selection",
            slug="cond_s08",
            title_suffix="Case of: код по схеме",
            short_instruction="Напишите case of по блок-схеме веток.",
            description=(
                "Слева — блок-схема выбора: code = 1 → one, code = 2 → two, иначе other.\n\n"
                "Справа напишите Pascal с `case code of` и тестами ввода."
            ),
            difficulty="hard",
            diagram=diagram_case_code(),
            reference_solution_pascal=_COND_CASE_REF,
            test_cases=[
                {"inputs": "1", "output": "one"},
                {"inputs": "2", "output": "two"},
                {"inputs": "9", "output": "other"},
            ],
        ),
        "loop_s03": flowchart_to_code_slot(
            slot_id="loop_s03",
            collection_key="loops",
            target_tc="pre_condition_loop",
            slug="pre_condition_imp_text",
            title_suffix="Цикл while: код по схеме",
            short_instruction="Реализуйте while по блок-схеме обратного отсчёта.",
            description=(
                "Слева — блок-схема: пока n > 0, выводите n и уменьшайте на 1.\n\n"
                "Справа напишите Pascal с циклом while."
            ),
            difficulty="easy",
            diagram=diagram_while_countdown(),
            reference_solution_pascal=_LOOP_WHILE_REF,
            test_cases=[
                {"inputs": "3", "output": "3\n2\n1"},
                {"inputs": "1", "output": "1"},
                {"inputs": "0", "output": ""},
            ],
        ),
        "cond_s03": flowchart_to_code_slot(
            slot_id="cond_s03",
            collection_key="conditions",
            target_tc="multi_branch",
            slug="multi_branch_imp_text",
            title_suffix="Оценки: код по схеме",
            short_instruction="Реализуйте цепочку if по блок-схеме.",
            description=(
                "Слева — блок-схема цепочки if для score → A/B/C.\n\n"
                "Справа напишите Pascal: readln(score) и буква по правилам из схемы."
            ),
            difficulty="easy",
            diagram=diagram_multi_branch_score(),
            reference_solution_pascal=_COND_GRADE_REF,
            test_cases=[
                {"inputs": "95", "output": "A"},
                {"inputs": "75", "output": "B"},
                {"inputs": "50", "output": "C"},
            ],
        ),
        "loop_s02": flowchart_to_blocks_slot(
            slot_id="loop_s02",
            collection_key="loops",
            target_tc="counted_loop",
            slug="counted_loop_asm_blocks",
            title_suffix="Цикл for: соберите из блоков по схеме",
            short_instruction="Слева схема for — справа соберите Pascal-блоки.",
            description=(
                "Слева — блок-схема цикла for: s := 0, i := 1 to n, s := s + i.\n\n"
                "Справа расставьте Pascal-блоки в программе-сумматоре."
            ),
            difficulty="easy",
            diagram=diagram_for_sum_n(),
            original_code=(
                "program Sum;\nvar i, n, s: integer;\nbegin\n  readln(n);\n  s := 0;\n"
                "  for i := 1 to n do\n    s := s + i;\n  writeln(s);\nend."
            ),
            template=(
                "program Sum;\nvar i, n, s: integer;\nbegin\n  readln(n);\n  s := 0;\n  {0}\n    {1}\n  writeln(s);\nend."
            ),
            blocks=["for i := 1 to n do", "s := s + i;"],
            correct_order=[0, 1],
            test_cases=[
                {"inputs": "4", "output": "10"},
                {"inputs": "1", "output": "1"},
            ],
        ),
        "cond_s02": flowchart_to_blocks_slot(
            slot_id="cond_s02",
            collection_key="conditions",
            target_tc="simple_branch",
            slug="simple_branch_asm_blocks",
            title_suffix="If: соберите блоки по схеме",
            short_instruction="Слева схема if n mod 2 — справа блоки Pascal.",
            description=(
                "Слева — блок-схема: n mod 2 = 0 ? → even / odd.\n\n"
                "Справа соберите Pascal-блоки if/else/writeln."
            ),
            difficulty="easy",
            diagram=diagram_if_parity(),
            original_code=(
                "program Parity;\nvar n: integer;\nbegin\n  readln(n);\n  if n mod 2 = 0 then\n"
                "    writeln('even')\n  else\n    writeln('odd');\nend."
            ),
            template=(
                "program Parity;\nvar n: integer;\nbegin\n  readln(n);\n  {0}\n    {1}\n  {2}\n    {3}\nend."
            ),
            blocks=[
                "if n mod 2 = 0 then",
                "writeln('even')",
                "else",
                "writeln('odd');",
            ],
            correct_order=[0, 1, 2, 3],
            test_cases=[
                {"inputs": "4", "output": "even"},
                {"inputs": "7", "output": "odd"},
            ],
        ),
        "cond_s11": flowchart_to_blocks_slot(
            slot_id="cond_s11",
            collection_key="conditions",
            target_tc="multi_branch",
            slug="cond_s11",
            title_suffix="Цепочка if: блоки по схеме",
            short_instruction="Соберите блоки оценок по схеме score ≥ 90 / 70.",
            description=(
                "Слева — блок-схема цепочки if для score.\n\n"
                "Справа соберите Pascal-блоки программы оценок."
            ),
            difficulty="easy",
            diagram=diagram_grade_chain(),
            original_code=(
                "program Grade;\nvar score: integer;\nbegin\n  readln(score);\n  if score >= 90 then\n"
                "    writeln('A')\n  else if score >= 70 then\n    writeln('B')\n  else\n    writeln('C');\nend."
            ),
            template=(
                "program Grade;\nvar score: integer;\nbegin\n  readln(score);\n  {0}\n    {1}\n  {2}\n    {3}\n  {4}\n    {5};\nend."
            ),
            blocks=[
                "if score >= 90 then",
                "writeln('A')",
                "else if score >= 70 then",
                "writeln('B')",
                "else",
                "writeln('C')",
            ],
            correct_order=[0, 1, 2, 3, 4, 5],
            test_cases=[
                {"inputs": "95", "output": "A"},
                {"inputs": "75", "output": "B"},
            ],
        ),
        "loop_s01": code_to_flowchart_slot(
            slot_id="loop_s01",
            collection_key="loops",
            target_tc="counted_loop",
            slug="counted_loop_tr_python",
            title_suffix="Цикл for: постройте схему по коду",
            short_instruction="По Pascal-коду слева нарисуйте блок-схему for.",
            description=(
                "Слева — Pascal-программа суммы 1..n.\n\n"
                "Справа постройте блок-схему: s := 0, цикл i := 1 to n, s := s + i, вывод s."
            ),
            difficulty="easy",
            reference_code_pascal=_LOOP_FOR_REF,
            flow_spec={
                "student_reference_languages": ["pascal"],
                "allowed_blocks": _ALLOWED_BLOCKS,
                "required_sequence": ["start", "input", "process", "loop", "process", "output", "end"],
                "required_text_checks": [
                    {"type": "input", "contains_any": ["readln", "n"]},
                    {"type": "process", "contains_any": ["s := 0", "s=0", "s :=0"]},
                    {"type": "loop", "contains_any": ["1 to n", "i := 1", "for i"]},
                    {"type": "process", "contains_any": ["s + i", "s:=s", "s := s"]},
                    {"type": "output", "contains_any": ["writeln", "s"]},
                ],
                "require_loop_back_edge": True,
                "allow_extra_nodes": False,
            },
        ),
        "cond_s01": code_to_flowchart_slot(
            slot_id="cond_s01",
            collection_key="conditions",
            target_tc="simple_branch",
            slug="simple_branch_tr_python",
            title_suffix="If: постройте схему по коду",
            short_instruction="По Pascal-коду слева нарисуйте блок-схему if.",
            description=(
                "Слева — Pascal-программа: if n > 0 then pos else nonpos.\n\n"
                "Справа постройте блок-схему с условием **n > 0 ?** и двумя ветками вывода."
            ),
            difficulty="easy",
            reference_code_pascal=_COND_IF_REF,
            flow_spec={
                "student_reference_languages": ["pascal"],
                "allowed_blocks": _ALLOWED_BLOCKS,
                "required_sequence": ["start", "input", "decision", "output", "output", "end"],
                "required_text_checks": [
                    {"type": "input", "contains_any": ["readln", "n"]},
                    {"type": "decision", "contains_any": ["> 0", "n > 0", ">0"]},
                    {"type": "output", "contains_any": ["pos"]},
                    {"type": "output", "contains_any": ["nonpos"]},
                ],
                "allow_extra_nodes": False,
            },
        ),
    }


FLOWCHART_SLOT_BY_ID: dict[str, PedagogicalSlotSpec] = flowchart_slot_replacements()

assert len(FLOWCHART_SLOT_BY_ID) == 11

