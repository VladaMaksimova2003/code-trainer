"""Pascal curriculum v2 — single source of truth for pedagogical slots (~102)."""

from __future__ import annotations

from dataclasses import replace

from application.curriculum.pascal.legacy.conditions.conditions_showcase_data import conditions_showcase_specs
from application.curriculum.pascal.legacy.conditions.conditions_showcase_reference_solutions import (
    REFERENCE_SOLUTIONS as CONDITIONS_REFERENCE,
)
from application.curriculum.pascal.legacy.loops.loops_showcase_data import loops_showcase_specs
from application.curriculum.pascal.legacy.loops.loops_showcase_reference_solutions import (
    REFERENCE_SOLUTIONS as LOOPS_REFERENCE,
)
from application.curriculum.pascal.catalog.pascal_transfer_presets import (
    ALG_SUM_ABS,
    ARR_SUM3,
    COND_IF_ASSEMBLE,
    COND_MULTI_BRANCH,
    COND_SIMPLE_BRANCH,
    COND_SWITCH,
    DS_NODE,
    DS_TREE,
    FN_INVOCATION,
    LOOP_COLLECTION,
    LOOP_COUNTED,
    LOOP_FOR_ASSEMBLE,
    MOD_IMPORT,
    OOP_POINT,
    REC_PAIR,
    RECU_FACT,
    STR_LEN,
    VAI_ASSIGNMENT,
    VAI_ARITHMETIC_OPS,
    VAI_PROGRAM_ENTRY,
    VAI_STDIN_READ,
    VAI_STDOUT_WRITE,
    VAI_TYPED_DECLARATION,
)
from application.curriculum.pascal.catalog.pascal_flowchart_slot_replacements import FLOWCHART_SLOT_BY_ID
from application.curriculum.pascal.catalog.pascal_pedagogical_slot import PedagogicalSlotSpec
from application.curriculum.pascal.showcase.pascal_showcase_core import PascalShowcaseTaskSpec
from application.curriculum.pascal.catalog.pascal_v2_slot_factories import (
    analyze_slot,
    assemble_slot,
    debug_slot,
    io_slot,
    task_spec_to_slot,
    translate_slot,
)
from shared.enums import AssignmentType

COLLECTION_TARGETS: dict[str, int] = {
    "variables_and_io": 12,
    "conditions": 12,
    "loops": 14,
    "functions": 7,
    "arrays": 4,
    "strings": 3,
    "records": 3,
    "files": 4,
    "procedures_and_parameters": 2,
    "modules": 8,
    "recursion": 4,
    "algorithms": 7,
    "data_structures": 11,
    "oop": 11,
}


def _normalize_builder(builder_key: str) -> str:
    if builder_key == "translation_python_to_pascal":
        return "translation_to_pascal"
    return builder_key


def _adapt_legacy_specs(collection_key: str, specs: tuple[object, ...]) -> tuple[PascalShowcaseTaskSpec, ...]:
    adapted: list[PascalShowcaseTaskSpec] = []
    for spec in specs:
        adapted.append(
            PascalShowcaseTaskSpec(
                collection_key=collection_key,
                slug=spec.slug,
                title_suffix=spec.title_suffix,
                description=spec.description,
                difficulty=spec.difficulty,
                technical_concept_id=spec.technical_concept_id,
                exercise_pattern_id=spec.exercise_pattern_id,
                assignment_type=spec.assignment_type,
                builder_key=_normalize_builder(spec.builder_key),
                extra=spec.extra,
            )
        )
    return tuple(adapted)


def _first_line(text: str) -> str:
    return (text or "").strip().split("\n")[0].strip()


def _primary_action_from_spec(spec: PascalShowcaseTaskSpec) -> str:
    pattern = spec.exercise_pattern_id or ""
    if pattern.startswith("tr_"):
        return "translate"
    if pattern.startswith("asm_"):
        return "assemble"
    if pattern.startswith("imp_"):
        return "implement"
    if pattern.startswith("ana_"):
        return "analyze"
    if pattern.startswith("dbg_"):
        return "debug"
    return {
        "translation_to_pascal": "translate",
        "translation_python_to_pascal": "translate",
        "block_reorder_pascal": "assemble",
        "pascal_io_program": "implement",
        "pascal_debug_starter": "debug",
    }.get(spec.builder_key, "implement")


def _with_reference(extra: dict | None, slug: str, refs: dict[str, str]) -> dict:
    merged = dict(extra or {})
    if "reference_solution_pascal" not in merged and slug in refs:
        merged["reference_solution_pascal"] = refs[slug]
    return merged


def _legacy_specs_to_slots(
    *,
    collection_key: str,
    specs: tuple[object, ...],
    prefix: str,
    refs: dict[str, str],
) -> tuple[PedagogicalSlotSpec, ...]:
    slots: list[PedagogicalSlotSpec] = []
    for index, raw in enumerate(_adapt_legacy_specs(collection_key, specs), start=1):
        extra = _with_reference(raw.extra, raw.slug, refs)
        spec = raw if extra == (raw.extra or {}) else replace(raw, extra=extra)
        slots.append(
            task_spec_to_slot(
                spec,
                slot_id=f"{prefix}_s{index:02d}",
                primary_action=_primary_action_from_spec(spec),
                short_instruction=_first_line(spec.description),
            )
        )
    return tuple(slots)


def _spec_to_slot(
    spec: PascalShowcaseTaskSpec,
    *,
    slot_id: str,
    primary_action: str | None = None,
    secondary_actions: tuple[str, ...] = (),
    short_instruction: str | None = None,
) -> PedagogicalSlotSpec:
    return task_spec_to_slot(
        spec,
        slot_id=slot_id,
        primary_action=primary_action or _primary_action_from_spec(spec),
        secondary_actions=secondary_actions,
        short_instruction=short_instruction or _first_line(spec.description),
    )


def _io_spec(
    *,
    collection_key: str,
    slug: str,
    title_suffix: str,
    description: str,
    difficulty: str,
    technical_concept_id: str,
    test_cases: list[dict[str, str]],
    reference_solution_pascal: str,
    exercise_pattern_id: str = "imp_text_spec_to_pascal",
    known_language_variants: dict | None = None,
) -> PascalShowcaseTaskSpec:
    extra: dict = {
        "test_cases": test_cases,
        "reference_solution_pascal": reference_solution_pascal,
    }
    if known_language_variants:
        extra["known_language_variants"] = known_language_variants
    return PascalShowcaseTaskSpec(
        collection_key=collection_key,
        slug=slug,
        title_suffix=title_suffix,
        description=description,
        difficulty=difficulty,
        technical_concept_id=technical_concept_id,
        exercise_pattern_id=exercise_pattern_id,
        assignment_type=AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
        builder_key="pascal_io_program",
        extra=extra,
    )


def _translation_spec(
    *,
    collection_key: str,
    slug: str,
    title_suffix: str,
    description: str,
    difficulty: str,
    technical_concept_id: str,
    known_language_variants: dict,
    test_cases: list[dict[str, str]],
    reference_solution_pascal: str,
    exercise_pattern_id: str = "tr_python_to_pascal_code",
) -> PascalShowcaseTaskSpec:
    from application.curriculum.pascal.catalog.pascal_known_language import default_source_code, default_source_language

    lang = default_source_language(known_language_variants)
    return PascalShowcaseTaskSpec(
        collection_key=collection_key,
        slug=slug,
        title_suffix=title_suffix,
        description=description,
        difficulty=difficulty,
        technical_concept_id=technical_concept_id,
        exercise_pattern_id=exercise_pattern_id,
        assignment_type=AssignmentType.TASK_TRANSLATE_SNIPPET.value,
        builder_key="translation_to_pascal",
        extra={
            "known_language_variants": known_language_variants,
            "source_language": lang,
            "source_code": default_source_code(known_language_variants, lang=lang),
            "test_cases": test_cases,
            "reference_solution_pascal": reference_solution_pascal,
        },
    )


def _debug_spec(
    *,
    collection_key: str,
    slug: str,
    title_suffix: str,
    description: str,
    difficulty: str,
    technical_concept_id: str,
    starter_pascal: str,
    test_cases: list[dict[str, str]],
    reference_solution_pascal: str,
    exercise_pattern_id: str = "dbg_pascal_code_fix",
    known_language_variants: dict | None = None,
) -> PascalShowcaseTaskSpec:
    extra: dict = {
        "starter_pascal": starter_pascal,
        "test_cases": test_cases,
        "reference_solution_pascal": reference_solution_pascal,
    }
    if known_language_variants:
        extra["known_language_variants"] = known_language_variants
    return PascalShowcaseTaskSpec(
        collection_key=collection_key,
        slug=slug,
        title_suffix=title_suffix,
        description=description,
        difficulty=difficulty,
        technical_concept_id=technical_concept_id,
        exercise_pattern_id=exercise_pattern_id,
        assignment_type=AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
        builder_key="pascal_debug_starter",
        extra=extra,
    )


def _variables_and_io_slots() -> tuple[PedagogicalSlotSpec, ...]:
    legacy = (
        _translation_spec(
            collection_key="variables_and_io",
            slug="vai_program_entry_tr_python",
            title_suffix="Точка входа программы",
            description="Перенесите знакомую программу на Pascal: считайте число и выведите его.",
            difficulty="easy",
            technical_concept_id="program_entry",
            known_language_variants=VAI_PROGRAM_ENTRY,
            test_cases=[{"inputs": "7", "output": "7"}, {"inputs": "-3", "output": "-3"}],
            reference_solution_pascal="var n: integer;\nbegin\n  readln(n);\n  writeln(n);\nend.",
        ),
        _translation_spec(
            collection_key="variables_and_io",
            slug="vai_typed_declaration_tr_cpp",
            title_suffix="Типизированные переменные",
            description="Перенесите программу с явными типами на Pascal: сложите два целых числа.",
            difficulty="easy",
            technical_concept_id="typed_declaration",
            known_language_variants=VAI_TYPED_DECLARATION,
            test_cases=[{"inputs": "2\n5", "output": "7"}, {"inputs": "-1\n1", "output": "0"}],
            reference_solution_pascal=(
                "program Sum;\nvar a, b: integer;\nbegin\n  readln(a);\n  readln(b);\n  writeln(a + b);\nend."
            ),
        ),
        _io_spec(
            collection_key="variables_and_io",
            slug="vai_assignment_imp_text",
            title_suffix="Присваивание: напишите программу",
            description="Считайте a и b. Присвойте переменной result разность a - b и выведите result.",
            difficulty="easy",
            technical_concept_id="assignment",
            known_language_variants=VAI_ASSIGNMENT,
            test_cases=[{"inputs": "9\n4", "output": "5"}, {"inputs": "4\n9", "output": "-5"}],
            reference_solution_pascal=(
                "program Diff;\nvar a, b, result: integer;\nbegin\n  readln(a);\n  readln(b);\n"
                "  result := a - b;\n  writeln(result);\nend."
            ),
        ),
        _io_spec(
            collection_key="variables_and_io",
            slug="vai_arithmetic_ops_imp_io",
            title_suffix="Арифметика: сумма квадратов",
            description="Считайте x и y, выведите x*x + y*y.",
            difficulty="easy",
            technical_concept_id="arithmetic_ops",
            known_language_variants=VAI_ARITHMETIC_OPS,
            test_cases=[{"inputs": "3\n4", "output": "25"}, {"inputs": "1\n2", "output": "5"}],
            reference_solution_pascal=(
                "program SqSum;\nvar x, y: integer;\nbegin\n  readln(x);\n  readln(y);\n"
                "  writeln(x * x + y * y);\nend."
            ),
        ),
        _debug_spec(
            collection_key="variables_and_io",
            slug="vai_stdin_read_dbg_fix",
            title_suffix="Readln: исправьте ввод данных",
            description="В коде ошибка чтения: второе число не считывается. Исправьте программу.",
            difficulty="easy",
            technical_concept_id="stdin_read",
            known_language_variants=VAI_STDIN_READ,
            starter_pascal=(
                "program InputBug;\nvar a, b: integer;\nbegin\n  readln(a);\n  a := b;\n  writeln(a + b);\nend."
            ),
            test_cases=[{"inputs": "2\n3", "output": "5"}, {"inputs": "10\n-2", "output": "8"}],
            reference_solution_pascal=(
                "program InputBug;\nvar a, b: integer;\nbegin\n  readln(a);\n  readln(b);\n  writeln(a + b);\nend."
            ),
        ),
        _io_spec(
            collection_key="variables_and_io",
            slug="vai_stdout_write_imp_text",
            title_suffix="Writeln: форматированный вывод суммы",
            description="Считайте два числа и выведите только их сумму.",
            difficulty="easy",
            technical_concept_id="stdout_write",
            known_language_variants=VAI_STDOUT_WRITE,
            test_cases=[{"inputs": "6\n7", "output": "13"}, {"inputs": "0\n5", "output": "5"}],
            reference_solution_pascal=(
                "program OutSum;\nvar a, b: integer;\nbegin\n  readln(a);\n  readln(b);\n  writeln(a + b);\nend."
            ),
        ),
    )
    slots = [
        _spec_to_slot(spec, slot_id=f"vai_s{index:02d}")
        for index, spec in enumerate(legacy, start=1)
    ]
    slots.extend(
        (
            analyze_slot(
                slot_id="vai_s07",
                collection_key="variables_and_io",
                target_tc="program_entry",
                title_suffix="Точка входа: предскажите вывод readln/writeln",
                short_instruction="Определите вывод фрагмента при n=4.",
                description="Изучите фрагмент с readln и writeln и воспроизведите вывод.",
                difficulty="easy",
                code_examples_pascal="var n: integer;\nbegin\n  n := 4;\n  writeln(n);\nend.",
                expected_output="4",
            ),
            analyze_slot(
                slot_id="vai_s08",
                collection_key="variables_and_io",
                target_tc="typed_declaration",
                title_suffix="Типы: предскажите остаток и частное",
                short_instruction="Определите a div b и a mod b для a=17, b=5.",
                description="Изучите целочисленное деление и остаток в Pascal.",
                difficulty="medium",
                code_examples_pascal=(
                    "var a, b: integer;\nbegin\n  a := 17;\n  b := 5;\n  writeln(a div b);\n"
                    "  writeln(a mod b);\nend."
                ),
                expected_output="3\n2",
            ),
            analyze_slot(
                slot_id="vai_s09",
                collection_key="variables_and_io",
                target_tc="assignment",
                title_suffix="Присваивание: предскажите result := a - b",
                short_instruction="Определите result для a=9, b=4.",
                description="Изучите присваивание с оператором := и вывод result.",
                difficulty="easy",
                code_examples_pascal=(
                    "var a, b, result: integer;\nbegin\n  a := 9;\n  b := 4;\n  result := a - b;\n  writeln(result);\nend."
                ),
                expected_output="5",
            ),
            analyze_slot(
                slot_id="vai_s10",
                collection_key="variables_and_io",
                target_tc="arithmetic_ops",
                title_suffix="Арифметика: предскажите сумму квадратов",
                short_instruction="Определите x*x + y*y для x=3, y=4.",
                description="Изучите выражение с арифметическими операциями.",
                difficulty="easy",
                code_examples_pascal=(
                    "var x, y: integer;\nbegin\n  x := 3;\n  y := 4;\n  writeln(x * x + y * y);\nend."
                ),
                expected_output="25",
            ),
            analyze_slot(
                slot_id="vai_s11",
                collection_key="variables_and_io",
                target_tc="stdin_read",
                title_suffix="Readln: предскажите сумму после ввода",
                short_instruction="Определите a+b после readln(a) и readln(b) при вводе 8 и -3.",
                description="Изучите фрагмент с двумя readln и сложением результатов.",
                difficulty="hard",
                code_examples_pascal=(
                    "var a, b: integer;\nbegin\n  readln(a);\n  readln(b);\n  writeln(a + b);\nend."
                ),
                expected_output="5",
            ),
            analyze_slot(
                slot_id="vai_s12",
                collection_key="variables_and_io",
                target_tc="stdout_write",
                title_suffix="Writeln: предскажите две строки вывода",
                short_instruction="Определите обе строки для x=3, y=4.",
                description="Изучите фрагмент с двумя writeln и промежуточным присваиванием.",
                difficulty="medium",
                code_examples_pascal=(
                    "var x, y, s: integer;\nbegin\n  x := 3;\n  y := 4;\n  s := x * y;\n"
                    "  writeln('product=', s);\n  writeln('sum=', x + y);\nend."
                ),
                expected_output="product= 12\nsum= 7",
            ),
        )
    )
    return tuple(slots)


def _conditions_slots() -> tuple[PedagogicalSlotSpec, ...]:
    legacy = _legacy_specs_to_slots(
        collection_key="conditions",
        specs=conditions_showcase_specs(),
        prefix="cond",
        refs=CONDITIONS_REFERENCE,
    )
    new = (
        analyze_slot(
            slot_id="cond_s07",
            collection_key="conditions",
            target_tc="multi_branch",
            title_suffix="Цепочка if: предскажите букву оценки",
            short_instruction="Определите букву для score=85 по цепочке if.",
            description="Изучите фрагмент с if / else if и воспроизведите вывод для score=85.",
            difficulty="easy",
            code_examples_pascal=(
                "var score: integer;\nbegin\n  score := 85;\n  if score >= 90 then\n    writeln('A')\n"
                "  else if score >= 70 then\n    writeln('B')\n  else\n    writeln('C');\nend."
            ),
            expected_output="B",
        ),
        analyze_slot(
            slot_id="cond_s08",
            collection_key="conditions",
            target_tc="switch_selection",
            title_suffix="Case of: предскажите метку ветки",
            short_instruction="Определите вывод case для code=2.",
            description="Изучите фрагмент case of и воспроизведите вывод для code=2.",
            difficulty="hard",
            code_examples_pascal=(
                "var code: integer;\nbegin\n  code := 2;\n  case code of\n    1: writeln('one');\n"
                "    2: writeln('two');\n  else writeln('other');\n  end;\nend."
            ),
            expected_output="two",
        ),
        debug_slot(
            slot_id="cond_s09",
            collection_key="conditions",
            target_tc="switch_selection",
            title_suffix="Case of: исправьте пропущенную ветку",
            short_instruction="Исправьте case, чтобы code=2 выводил two.",
            description="В case of отсутствует корректная обработка значения 2.",
            difficulty="medium",
            starter_pascal=(
                "program CaseBug;\nvar code: integer;\nbegin\n  readln(code);\n  case code of\n"
                "    1: writeln('one');\n  else writeln('other');\n  end;\nend."
            ),
            test_cases=[
                {"inputs": "1", "output": "one"},
                {"inputs": "2", "output": "two"},
                {"inputs": "9", "output": "other"},
            ],
            reference_solution_pascal=(
                "program CaseBug;\nvar code: integer;\nbegin\n  readln(code);\n  case code of\n"
                "    1: writeln('one');\n    2: writeln('two');\n  else writeln('other');\n  end;\nend."
            ),
        ),
        debug_slot(
            slot_id="cond_s10",
            collection_key="conditions",
            target_tc="conditional_expression",
            title_suffix="Условное выражение: исправьте знак результата",
            short_instruction="Исправьте if-then-else для абсолютного значения.",
            description="Фрагмент должен давать модуль n, но для отрицательных n результат неверный.",
            difficulty="medium",
            starter_pascal=(
                "program AbsBug;\nvar n, result: integer;\nbegin\n  readln(n);\n  if n >= 0 then\n"
                "    result := n\n  else\n    result := n;\n  writeln(result);\nend."
            ),
            test_cases=[{"inputs": "5", "output": "5"}, {"inputs": "-3", "output": "3"}],
            reference_solution_pascal=(
                "program AbsBug;\nvar n, result: integer;\nbegin\n  readln(n);\n  if n >= 0 then\n"
                "    result := n\n  else\n    result := -n;\n  writeln(result);\nend."
            ),
        ),
        assemble_slot(
            slot_id="cond_s11",
            collection_key="conditions",
            target_tc="multi_branch",
            title_suffix="Цепочка if: соберите программу оценок",
            short_instruction="Расставьте блоки цепочки if для букв A/B/C.",
            description="Соберите программу, выводящую A, B или C по значению score.",
            difficulty="easy",
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
            test_cases=[{"inputs": "95", "output": "A"}, {"inputs": "75", "output": "B"}],
            known_language_variants=COND_MULTI_BRANCH,
        ),
        analyze_slot(
            slot_id="cond_s12",
            collection_key="conditions",
            target_tc="simple_branch",
            title_suffix="If then else: предскажите классификацию знака",
            short_instruction="Определите вывод для n=5 при if n>0.",
            description="Изучите простую ветку if then else для классификации числа.",
            difficulty="easy",
            code_examples_pascal=(
                "var n: integer;\nbegin\n  n := 5;\n  if n > 0 then\n    writeln('pos')\n  else\n    writeln('nonpos');\nend."
            ),
            expected_output="pos",
        ),
    )
    return legacy + new


def _loops_slots() -> tuple[PedagogicalSlotSpec, ...]:
    legacy = _legacy_specs_to_slots(
        collection_key="loops",
        specs=loops_showcase_specs(),
        prefix="loop",
        refs=LOOPS_REFERENCE,
    )
    new = (
        analyze_slot(
            slot_id="loop_s08",
            collection_key="loops",
            target_tc="counted_loop",
            title_suffix="For: предскажите сумму 1..n",
            short_instruction="Определите вывод цикла for при n=4.",
            description="Изучите фрагмент с for i := 1 to n и воспроизведите сумму.",
            difficulty="easy",
            code_examples_pascal=(
                "var i, n, s: integer;\nbegin\n  n := 4;\n  s := 0;\n  for i := 1 to n do\n"
                "    s := s + i;\n  writeln(s);\nend."
            ),
            expected_output="10",
        ),
        analyze_slot(
            slot_id="loop_s09",
            collection_key="loops",
            target_tc="pre_condition_loop",
            title_suffix="While: предскажите обратный отсчёт",
            short_instruction="Определите строки вывода while при n=2.",
            description="Изучите while-цикл с уменьшением n.",
            difficulty="easy",
            code_examples_pascal=(
                "var n: integer;\nbegin\n  n := 2;\n  while n > 0 do\n  begin\n    writeln(n);\n"
                "    n := n - 1;\n  end;\nend."
            ),
            expected_output="2\n1",
        ),
        analyze_slot(
            slot_id="loop_s10",
            collection_key="loops",
            target_tc="collection_iteration",
            title_suffix="Перебор строки: предскажите count символов a",
            short_instruction="Определите count для s='aba'.",
            description="Изучите цикл по символам строки.",
            difficulty="medium",
            code_examples_pascal=(
                "var s: string;\n    i, count: integer;\nbegin\n  s := 'aba';\n  count := 0;\n"
                "  for i := 1 to length(s) do\n    if s[i] = 'a' then\n      count := count + 1;\n"
                "  writeln(count);\nend."
            ),
            expected_output="2",
        ),
        analyze_slot(
            slot_id="loop_s11",
            collection_key="loops",
            target_tc="nested_iteration",
            title_suffix="Вложенные циклы: предскажите сумму произведений",
            short_instruction="Определите s после двойного цикла for.",
            description="Изучите вложенные циклы for и накопление суммы i*j.",
            difficulty="hard",
            code_examples_pascal=(
                "var i, j, s: integer;\nbegin\n  s := 0;\n  for i := 1 to 2 do\n"
                "    for j := 1 to 3 do\n      s := s + i * j;\n  writeln(s);\nend."
            ),
            expected_output="18",
        ),
        analyze_slot(
            slot_id="loop_s12",
            collection_key="loops",
            target_tc="loop_control",
            title_suffix="Continue: предскажите сумму нечётных",
            short_instruction="Определите сумму нечётных от 1 до 4.",
            description="Изучите цикл с continue для чётных i.",
            difficulty="medium",
            code_examples_pascal=(
                "var i, s: integer;\nbegin\n  s := 0;\n  for i := 1 to 4 do\n  begin\n"
                "    if i mod 2 = 0 then continue;\n    s := s + i;\n  end;\n  writeln(s);\nend."
            ),
            expected_output="4",
        ),
        debug_slot(
            slot_id="loop_s13",
            collection_key="loops",
            target_tc="post_condition_loop",
            title_suffix="Repeat-until: исправьте условие выхода",
            short_instruction="Исправьте until, чтобы цикл останавливался при n=0.",
            description="Repeat-цикл не завершается из-за неверного условия until.",
            difficulty="medium",
            starter_pascal=(
                "program RepeatBug;\nvar n: integer;\nbegin\n  readln(n);\n  repeat\n    writeln(n);\n"
                "    n := n - 1;\n  until n = 1;\nend."
            ),
            test_cases=[{"inputs": "3", "output": "3\n2\n1"}, {"inputs": "1", "output": "1"}],
            reference_solution_pascal=(
                "program RepeatBug;\nvar n: integer;\nbegin\n  readln(n);\n  repeat\n    writeln(n);\n"
                "    n := n - 1;\n  until n = 0;\nend."
            ),
        ),
        io_slot(
            slot_id="loop_s14",
            collection_key="loops",
            target_tc="collection_iteration",
            primary_action="implement",
            title_suffix="Перебор: подсчёт символов x в строке",
            short_instruction="Считайте s и выведите число символов x.",
            description="Капstone: прочитайте строку и посчитайте вхождения символа x.",
            difficulty="medium",
            test_cases=[
                {"inputs": "abxax\nx", "output": "2"},
                {"inputs": "abc\nz", "output": "0"},
            ],
            reference_solution_pascal=(
                "program CountChar;\nvar s: string;\n    ch: char;\n    i, c: integer;\nbegin\n"
                "  readln(s);\n  readln(ch);\n  c := 0;\n  for i := 1 to length(s) do\n"
                "    if s[i] = ch then\n      c := c + 1;\n  writeln(c);\nend."
            ),
        ),
    )
    return legacy + new


def _functions_slots() -> tuple[PedagogicalSlotSpec, ...]:
    return (
        analyze_slot(
            slot_id="fn_s01",
            collection_key="functions",
            target_tc="function_definition",
            title_suffix="Функция: предскажите Sq(5)",
            short_instruction="Определите вывод writeln(Sq(5)) для функции квадрата.",
            description="Изучите определение функции Sq и её вызов.",
            difficulty="easy",
            code_examples_pascal=(
                "function Sq(x: integer): integer;\nbegin\n  Sq := x * x;\nend;\nbegin\n  writeln(Sq(5));\nend."
            ),
            expected_output="25",
        ),
        _spec_to_slot(
            _translation_spec(
                collection_key="functions",
                slug="fn_function_invocation_tr_cpp",
                title_suffix="Вызов функции",
                description="Перенесите программу с вызовом функции add на Pascal.",
                difficulty="easy",
                technical_concept_id="function_invocation",
                known_language_variants=FN_INVOCATION,
                test_cases=[{"inputs": "2\n8", "output": "10"}, {"inputs": "-1\n1", "output": "0"}],
                reference_solution_pascal=(
                    "function Add(a, b: integer): integer;\nbegin\n  Add := a + b;\nend;\nvar x, y: integer;\n"
                    "begin\n  readln(x);\n  readln(y);\n  writeln(Add(x, y));\nend."
                ),
            ),
            slot_id="fn_s02",
        ),
        analyze_slot(
            slot_id="fn_s03",
            collection_key="functions",
            target_tc="return_flow",
            title_suffix="Возврат значения: предскажите Max2(3, 9)",
            short_instruction="Определите Max2(3, 9) для функции максимума.",
            description="Изучите функцию Max2 и её возвращаемое значение.",
            difficulty="easy",
            code_examples_pascal=(
                "function Max2(a, b: integer): integer;\nbegin\n  if a > b then Max2 := a else Max2 := b;\nend;\n"
                "begin\n  writeln(Max2(3, 9));\nend."
            ),
            expected_output="9",
        ),
        _spec_to_slot(
            _debug_spec(
                collection_key="functions",
                slug="fn_function_definition_dbg_fix",
                title_suffix="Функция: исправьте ошибку в определении",
                description="Функция должна возвращать удвоенное число, но сейчас работает неверно.",
                difficulty="medium",
                technical_concept_id="function_definition",
                starter_pascal=(
                    "function DoubleValue(x: integer): integer;\nbegin\n  DoubleValue := x;\nend;\n"
                    "var n: integer;\nbegin\n  readln(n);\n  writeln(DoubleValue(n));\nend."
                ),
                test_cases=[{"inputs": "6", "output": "12"}, {"inputs": "-4", "output": "-8"}],
                reference_solution_pascal=(
                    "function DoubleValue(x: integer): integer;\nbegin\n  DoubleValue := x * 2;\nend;\n"
                    "var n: integer;\nbegin\n  readln(n);\n  writeln(DoubleValue(n));\nend."
                ),
            ),
            slot_id="fn_s04",
        ),
        _spec_to_slot(
            _io_spec(
                collection_key="functions",
                slug="fn_function_invocation_imp_io",
                title_suffix="Вызов подпрограммы: сумма квадратов",
                description="Реализуйте функцию Sq и используйте её при вычислении суммы квадратов.",
                difficulty="hard",
                technical_concept_id="function_invocation",
                test_cases=[{"inputs": "2\n3", "output": "13"}, {"inputs": "1\n1", "output": "2"}],
                reference_solution_pascal=(
                    "function Sq(x: integer): integer;\nbegin\n  Sq := x * x;\nend;\nvar a, b: integer;\n"
                    "begin\n  readln(a);\n  readln(b);\n  writeln(Sq(a) + Sq(b));\nend."
                ),
            ),
            slot_id="fn_s05",
        ),
        _spec_to_slot(
            _debug_spec(
                collection_key="functions",
                slug="fn_return_flow_dbg_fix_sign",
                title_suffix="Return: исправьте знак для нуля",
                description="Sign3 должна возвращать 0 для n=0, но сейчас возвращает -1.",
                difficulty="medium",
                technical_concept_id="return_flow",
                starter_pascal=(
                    "function Sign3(n: integer): integer;\nbegin\n  if n > 0 then Sign3 := 1 else Sign3 := -1;\nend;\n"
                    "var n: integer;\nbegin\n  readln(n);\n  writeln(Sign3(n));\nend."
                ),
                test_cases=[{"inputs": "0", "output": "0"}, {"inputs": "5", "output": "1"}],
                reference_solution_pascal=(
                    "function Sign3(n: integer): integer;\nbegin\n  if n > 0 then Sign3 := 1\n"
                    "  else if n < 0 then Sign3 := -1\n  else Sign3 := 0;\nend;\nvar n: integer;\n"
                    "begin\n  readln(n);\n  writeln(Sign3(n));\nend."
                ),
            ),
            slot_id="fn_s06",
        ),
        analyze_slot(
            slot_id="fn_s07",
            collection_key="functions",
            target_tc="function_invocation",
            title_suffix="Вызов функции: предскажите результат Sq(3)",
            short_instruction="Определите вывод writeln(Sq(3)) для функции квадрата.",
            description="Изучите определение функции и её вызов.",
            difficulty="easy",
            code_examples_pascal=(
                "function Sq(x: integer): integer;\nbegin\n  Sq := x * x;\nend;\nbegin\n  writeln(Sq(3));\nend."
            ),
            expected_output="9",
        ),
    )


def _arrays_slots() -> tuple[PedagogicalSlotSpec, ...]:
    return (
        _spec_to_slot(
            _translation_spec(
                collection_key="arrays",
                slug="arr_indexed_sequence_tr_python_sum3",
                title_suffix="Массив: сумма трёх элементов",
                description="Перенесите программу: введите три числа и выведите их сумму.",
                difficulty="easy",
                technical_concept_id="indexed_sequence",
                known_language_variants=ARR_SUM3,
                test_cases=[{"inputs": "1\n2\n3", "output": "6"}, {"inputs": "5\n-1\n4", "output": "8"}],
                reference_solution_pascal=(
                    "program ArrSum3;\nvar a: array[1..3] of integer;\nbegin\n  readln(a[1]);\n  readln(a[2]);\n"
                    "  readln(a[3]);\n  writeln(a[1] + a[2] + a[3]);\nend."
                ),
            ),
            slot_id="arr_s01",
        ),
        analyze_slot(
            slot_id="arr_s02",
            collection_key="arrays",
            target_tc="indexed_sequence",
            title_suffix="Массив: предскажите максимум из трёх",
            short_instruction="Определите max для a=[5,7,1].",
            description="Изучите поиск максимума в массиве из трёх элементов.",
            difficulty="medium",
            code_examples_pascal=(
                "var a: array[1..3] of integer;\n    m: integer;\nbegin\n  a[1] := 5; a[2] := 7; a[3] := 1;\n"
                "  m := a[1];\n  if a[2] > m then m := a[2];\n  if a[3] > m then m := a[3];\n  writeln(m);\nend."
            ),
            expected_output="7",
        ),
        _spec_to_slot(
            _debug_spec(
                collection_key="arrays",
                slug="arr_dynamic_array_dbg_fix_count_positive",
                title_suffix="Массив: исправьте подсчёт положительных",
                description="Программа должна считать количество положительных среди трёх чисел.",
                difficulty="hard",
                technical_concept_id="dynamic_array",
                starter_pascal=(
                    "program PosCnt;\nvar a: array[1..3] of integer;\n    i, c: integer;\nbegin\n"
                    "  readln(a[1]);\n  readln(a[2]);\n  readln(a[3]);\n  c := 0;\n  for i := 1 to 3 do\n"
                    "    if a[i] < 0 then c := c + 1;\n  writeln(c);\nend."
                ),
                test_cases=[{"inputs": "1\n2\n-4", "output": "2"}, {"inputs": "-1\n-2\n-3", "output": "0"}],
                reference_solution_pascal=(
                    "program PosCnt;\nvar a: array[1..3] of integer;\n    i, c: integer;\nbegin\n"
                    "  readln(a[1]);\n  readln(a[2]);\n  readln(a[3]);\n  c := 0;\n  for i := 1 to 3 do\n"
                    "    if a[i] > 0 then c := c + 1;\n  writeln(c);\nend."
                ),
            ),
            slot_id="arr_s03",
        ),
        analyze_slot(
            slot_id="arr_s04",
            collection_key="arrays",
            target_tc="dynamic_array",
            title_suffix="Динамический массив: предскажите сумму n чисел",
            short_instruction="Определите сумму для n=3 и чисел 5, -2, 1.",
            description="Изучите цикл чтения n чисел и накопление суммы.",
            difficulty="medium",
            code_examples_pascal=(
                "var n, i, x, s: integer;\nbegin\n  n := 3;\n  s := 0;\n  x := 5; s := s + x;\n"
                "  x := -2; s := s + x;\n  x := 1; s := s + x;\n  writeln(s);\nend."
            ),
            expected_output="4",
        ),
    )


def _strings_slots() -> tuple[PedagogicalSlotSpec, ...]:
    return (
        _spec_to_slot(
            _translation_spec(
                collection_key="strings",
                slug="str_string_sequence_tr_python_len",
                title_suffix="Строка: длина текста",
                description="Перенесите программу подсчёта длины строки на Pascal.",
                difficulty="easy",
                technical_concept_id="string_sequence",
                known_language_variants=STR_LEN,
                test_cases=[{"inputs": "abc", "output": "3"}, {"inputs": "hello", "output": "5"}],
                reference_solution_pascal=(
                    "program StrLen;\nvar s: string;\nbegin\n  readln(s);\n  writeln(length(s));\nend."
                ),
            ),
            slot_id="str_s01",
        ),
        analyze_slot(
            slot_id="str_s02",
            collection_key="strings",
            target_tc="string_sequence",
            title_suffix="Строка: предскажите первый символ",
            short_instruction="Определите s[1] для s='pascal'.",
            description="Изучите доступ к символу строки по индексу.",
            difficulty="easy",
            code_examples_pascal="var s: string;\nbegin\n  s := 'pascal';\n  writeln(s[1]);\nend.",
            expected_output="p",
        ),
        _spec_to_slot(
            _debug_spec(
                collection_key="strings",
                slug="str_string_sequence_dbg_fix_last_char",
                title_suffix="Строка: исправьте вывод последнего символа",
                description="Программа должна печатать последний символ строки.",
                difficulty="hard",
                technical_concept_id="string_sequence",
                starter_pascal="program LastChar;\nvar s: string;\nbegin\n  readln(s);\n  writeln(s[1]);\nend.",
                test_cases=[{"inputs": "abc", "output": "c"}, {"inputs": "k", "output": "k"}],
                reference_solution_pascal=(
                    "program LastChar;\nvar s: string;\nbegin\n  readln(s);\n  writeln(s[length(s)]);\nend."
                ),
            ),
            slot_id="str_s03",
        ),
    )


def _records_slots() -> tuple[PedagogicalSlotSpec, ...]:
    return (
        _spec_to_slot(
            _translation_spec(
                collection_key="records",
                slug="rec_key_value_map_tr_python_pair_sum",
                title_suffix="Запись record",
                description="Перенесите программу с парой полей и суммой на Pascal.",
                difficulty="medium",
                technical_concept_id="key_value_map",
                known_language_variants=REC_PAIR,
                test_cases=[{"inputs": "4\n6", "output": "10"}, {"inputs": "-3\n1", "output": "-2"}],
                reference_solution_pascal=(
                    "program PairSum;\ntype TItem = record\n  x: integer;\n  y: integer;\nend;\nvar item: TItem;\n"
                    "begin\n  readln(item.x);\n  readln(item.y);\n  writeln(item.x + item.y);\nend."
                ),
            ),
            slot_id="rec_s01",
        ),
        analyze_slot(
            slot_id="rec_s02",
            collection_key="records",
            target_tc="key_value_map",
            title_suffix="Запись: предскажите значение поля grade",
            short_instruction="Определите s.grade после присваивания.",
            description="Изучите доступ к полю записи через точку.",
            difficulty="medium",
            code_examples_pascal=(
                "type TStudent = record\n  age: integer;\n  grade: integer;\nend;\nvar s: TStudent;\n"
                "begin\n  s.age := 15;\n  s.grade := 4;\n  writeln(s.grade);\nend."
            ),
            expected_output="4",
        ),
        _spec_to_slot(
            _debug_spec(
                collection_key="records",
                slug="rec_key_value_map_dbg_fix_swap",
                title_suffix="Запись: исправьте обмен полей",
                description="В программе неверно меняются местами два поля записи.",
                difficulty="hard",
                technical_concept_id="key_value_map",
                starter_pascal=(
                    "program RecordSwap;\ntype TPair = record\n  a: integer;\n  b: integer;\nend;\nvar p: TPair;\n"
                    "begin\n  readln(p.a);\n  readln(p.b);\n  p.a := p.b;\n  p.b := p.a;\n  writeln(p.a);\n"
                    "  writeln(p.b);\nend."
                ),
                test_cases=[{"inputs": "2\n9", "output": "9\n2"}, {"inputs": "7\n1", "output": "1\n7"}],
                reference_solution_pascal=(
                    "program RecordSwap;\ntype TPair = record\n  a: integer;\n  b: integer;\nend;\nvar p: TPair;\n"
                    "    t: integer;\nbegin\n  readln(p.a);\n  readln(p.b);\n  t := p.a;\n  p.a := p.b;\n"
                    "  p.b := t;\n  writeln(p.a);\n  writeln(p.b);\nend."
                ),
            ),
            slot_id="rec_s03",
        ),
    )


def _files_slots() -> tuple[PedagogicalSlotSpec, ...]:
    return (
        analyze_slot(
            slot_id="fil_s01",
            collection_key="files",
            target_tc="file_read",
            title_suffix="Чтение: предскажите сумму двух чисел",
            short_instruction="Определите вывод после readln(a) и readln(b) при a=1, b=9.",
            description="Изучите фрагмент чтения двух значений и вывод их суммы.",
            difficulty="hard",
            code_examples_pascal=(
                "var a, b: integer;\nbegin\n  a := 1;\n  b := 9;\n  writeln(a + b);\nend."
            ),
            expected_output="10",
        ),
        analyze_slot(
            slot_id="fil_s02",
            collection_key="files",
            target_tc="file_write",
            title_suffix="Запись: предскажите квадрат числа",
            short_instruction="Определите вывод writeln(x * x) при x=6.",
            description="Изучите фрагмент вычисления и вывода результата.",
            difficulty="medium",
            code_examples_pascal="var x: integer;\nbegin\n  x := 6;\n  writeln(x * x);\nend.",
            expected_output="36",
        ),
        _spec_to_slot(
            _debug_spec(
                collection_key="files",
                slug="fil_stdin_read_dbg_fix_order",
                title_suffix="Ввод/вывод: исправьте порядок операций",
                description="Исправьте программу: результат выводится до чтения второго числа.",
                difficulty="easy",
                technical_concept_id="stdin_read",
                starter_pascal=(
                    "program InputOrder;\nvar a, b: integer;\nbegin\n  readln(a);\n  writeln(a + b);\n  readln(b);\nend."
                ),
                test_cases=[{"inputs": "3\n4", "output": "7"}, {"inputs": "8\n1", "output": "9"}],
                reference_solution_pascal=(
                    "program InputOrder;\nvar a, b: integer;\nbegin\n  readln(a);\n  readln(b);\n  writeln(a + b);\nend."
                ),
            ),
            slot_id="fil_s03",
        ),
        analyze_slot(
            slot_id="fil_s04",
            collection_key="files",
            target_tc="stdout_write",
            title_suffix="Writeln: предскажите echo числа",
            short_instruction="Определите вывод writeln(n) при n=12.",
            description="Изучите фрагмент echo через stdout.",
            difficulty="easy",
            code_examples_pascal="var n: integer;\nbegin\n  n := 12;\n  writeln(n);\nend.",
            expected_output="12",
        ),
    )


def _procedures_slots() -> tuple[PedagogicalSlotSpec, ...]:
    return (
        analyze_slot(
            slot_id="pp_s01",
            collection_key="procedures_and_parameters",
            target_tc="parameter_passing",
            title_suffix="Параметры var: предскажите результат Swap",
            short_instruction="Определите a и b после Swap(2, 9).",
            description="Изучите процедуру Swap с параметрами var и обмен значений.",
            difficulty="medium",
            code_examples_pascal=(
                "procedure Swap(var x, y: integer);\nvar t: integer;\nbegin\n  t := x;\n  x := y;\n  y := t;\nend;\n"
                "var a, b: integer;\nbegin\n  a := 2;\n  b := 9;\n  Swap(a, b);\n  writeln(a);\n  writeln(b);\nend."
            ),
            expected_output="9\n2",
        ),
        _spec_to_slot(
            _debug_spec(
                collection_key="procedures_and_parameters",
                slug="pp_parameter_passing_dbg_fix",
                title_suffix="Параметры: исправьте потерю значения",
                description="Процедура должна менять переменную по ссылке, но сейчас это не происходит.",
                difficulty="hard",
                technical_concept_id="parameter_passing",
                starter_pascal=(
                    "procedure IncByTwo(x: integer);\nbegin\n  x := x + 2;\nend;\nvar n: integer;\n"
                    "begin\n  readln(n);\n  IncByTwo(n);\n  writeln(n);\nend."
                ),
                test_cases=[{"inputs": "5", "output": "7"}, {"inputs": "-1", "output": "1"}],
                reference_solution_pascal=(
                    "procedure IncByTwo(var x: integer);\nbegin\n  x := x + 2;\nend;\nvar n: integer;\n"
                    "begin\n  readln(n);\n  IncByTwo(n);\n  writeln(n);\nend."
                ),
            ),
            slot_id="pp_s02",
        ),
    )


def _modules_slots() -> tuple[PedagogicalSlotSpec, ...]:
    legacy = (
        _spec_to_slot(
            _translation_spec(
                collection_key="modules",
                slug="mod_import_dependency_tr_python",
                title_suffix="Модули uses",
                description="Перенесите идею локальной функции и её вызова на Pascal.",
                difficulty="medium",
                technical_concept_id="import_dependency",
                known_language_variants=MOD_IMPORT,
                test_cases=[{"inputs": "5\n6", "output": "11"}, {"inputs": "0\n3", "output": "3"}],
                reference_solution_pascal=(
                    "program UsesLike;\nfunction Add(a, b: integer): integer;\nbegin\n  Add := a + b;\nend;\n"
                    "var a, b: integer;\nbegin\n  readln(a);\n  readln(b);\n  writeln(Add(a, b));\nend."
                ),
            ),
            slot_id="mod_s01",
        ),
        analyze_slot(
            slot_id="mod_s02",
            collection_key="modules",
            target_tc="module_namespace",
            title_suffix="Пространство имён: предскажите сумму",
            short_instruction="Определите writeln(a + b) для a=2, b=2.",
            description="Изучите фрагмент с двумя переменными и выводом их суммы.",
            difficulty="medium",
            code_examples_pascal="var a, b: integer;\nbegin\n  a := 2;\n  b := 2;\n  writeln(a + b);\nend.",
            expected_output="4",
        ),
        _spec_to_slot(
            _io_spec(
                collection_key="modules",
                slug="mod_symbol_visibility_imp_text",
                title_suffix="Видимость символов: публичная функция",
                description="Реализуйте функцию внутри программы и используйте её в основном блоке.",
                difficulty="medium",
                technical_concept_id="symbol_visibility",
                test_cases=[{"inputs": "4", "output": "16"}, {"inputs": "-3", "output": "9"}],
                reference_solution_pascal=(
                    "function Sq(x: integer): integer;\nbegin\n  Sq := x * x;\nend;\nvar n: integer;\n"
                    "begin\n  readln(n);\n  writeln(Sq(n));\nend."
                ),
            ),
            slot_id="mod_s03",
        ),
        _spec_to_slot(
            _debug_spec(
                collection_key="modules",
                slug="mod_import_dependency_dbg_fix_uses",
                title_suffix="Uses: исправьте ошибку доступа",
                description="Исправьте программу: функция должна вызываться корректно из основного блока.",
                difficulty="medium",
                technical_concept_id="import_dependency",
                starter_pascal=(
                    "function Inc1(x: integer): integer;\nbegin\n  Inc1 := x + 1;\nend;\nvar n: integer;\n"
                    "begin\n  readln(n);\n  writeln(Inc(n));\nend."
                ),
                test_cases=[{"inputs": "5", "output": "6"}, {"inputs": "-1", "output": "0"}],
                reference_solution_pascal=(
                    "function Inc1(x: integer): integer;\nbegin\n  Inc1 := x + 1;\nend;\nvar n: integer;\n"
                    "begin\n  readln(n);\n  writeln(Inc1(n));\nend."
                ),
                exercise_pattern_id="dbg_pascal_logic_fix",
            ),
            slot_id="mod_s04",
        ),
        _spec_to_slot(
            _io_spec(
                collection_key="modules",
                slug="mod_module_namespace_imp_io_double",
                title_suffix="Модульная организация: функция удвоения",
                description="Создайте функцию DoubleIt и выведите её результат.",
                difficulty="hard",
                technical_concept_id="module_namespace",
                test_cases=[{"inputs": "8", "output": "16"}, {"inputs": "-2", "output": "-4"}],
                reference_solution_pascal=(
                    "function DoubleIt(x: integer): integer;\nbegin\n  DoubleIt := x * 2;\nend;\nvar n: integer;\n"
                    "begin\n  readln(n);\n  writeln(DoubleIt(n));\nend."
                ),
            ),
            slot_id="mod_s05",
        ),
        analyze_slot(
            slot_id="mod_s06",
            collection_key="modules",
            target_tc="symbol_visibility",
            title_suffix="Видимость: предскажите SignValue(3)",
            short_instruction="Определите вывод функции SignValue для n=3.",
            description="Изучите функцию SignValue и её вызов.",
            difficulty="medium",
            code_examples_pascal=(
                "function SignValue(n: integer): integer;\nbegin\n  if n > 0 then SignValue := 1\n"
                "  else if n < 0 then SignValue := -1\n  else SignValue := 0;\nend;\nbegin\n"
                "  writeln(SignValue(3));\nend."
            ),
            expected_output="1",
        ),
    )
    new = (
        analyze_slot(
            slot_id="mod_s07",
            collection_key="modules",
            target_tc="import_dependency",
            title_suffix="Uses: предскажите сумму через Add",
            short_instruction="Определите вывод Add(2,3).",
            description="Изучите локальную функцию Add и её вызов.",
            difficulty="easy",
            code_examples_pascal=(
                "function Add(a, b: integer): integer;\nbegin\n  Add := a + b;\nend;\nbegin\n  writeln(Add(2, 3));\nend."
            ),
            expected_output="5",
        ),
        debug_slot(
            slot_id="mod_s08",
            collection_key="modules",
            target_tc="module_namespace",
            title_suffix="Модуль: исправьте вызов DoubleIt",
            short_instruction="Исправьте имя функции в writeln.",
            description="Функция объявлена как DoubleIt, но вызывается с другим именем.",
            difficulty="easy",
            starter_pascal=(
                "function DoubleIt(x: integer): integer;\nbegin\n  DoubleIt := x * 2;\nend;\nvar n: integer;\n"
                "begin\n  readln(n);\n  writeln(Double(n));\nend."
            ),
            test_cases=[{"inputs": "8", "output": "16"}, {"inputs": "-2", "output": "-4"}],
            reference_solution_pascal=(
                "function DoubleIt(x: integer): integer;\nbegin\n  DoubleIt := x * 2;\nend;\nvar n: integer;\n"
                "begin\n  readln(n);\n  writeln(DoubleIt(n));\nend."
            ),
        ),
    )
    return legacy + new


def _recursion_slots() -> tuple[PedagogicalSlotSpec, ...]:
    return (
        _spec_to_slot(
            _translation_spec(
                collection_key="recursion",
                slug="recu_recursion_tr_python_fact",
                title_suffix="Рекурсия",
                description="Перенесите рекурсивный factorial на Pascal.",
                difficulty="medium",
                technical_concept_id="recursion",
                known_language_variants=RECU_FACT,
                test_cases=[{"inputs": "5", "output": "120"}, {"inputs": "1", "output": "1"}],
                reference_solution_pascal=(
                    "function Fact(n: integer): integer;\nbegin\n  if n <= 1 then Fact := 1\n"
                    "  else Fact := n * Fact(n - 1);\nend;\nvar n: integer;\nbegin\n  readln(n);\n  writeln(Fact(n));\nend."
                ),
            ),
            slot_id="recu_s01",
        ),
        _spec_to_slot(
            _io_spec(
                collection_key="recursion",
                slug="recu_recursion_imp_text_pow2",
                title_suffix="Рекурсия: степень двойки",
                description="Рекурсивно вычислите 2^n для n >= 0.",
                difficulty="hard",
                technical_concept_id="recursion",
                test_cases=[{"inputs": "0", "output": "1"}, {"inputs": "5", "output": "32"}],
                reference_solution_pascal=(
                    "function Pow2(n: integer): integer;\nbegin\n  if n = 0 then Pow2 := 1\n"
                    "  else Pow2 := 2 * Pow2(n - 1);\nend;\nvar n: integer;\nbegin\n  readln(n);\n  writeln(Pow2(n));\nend."
                ),
            ),
            slot_id="recu_s02",
        ),
        _spec_to_slot(
            _debug_spec(
                collection_key="recursion",
                slug="recu_recursion_dbg_fix_base_case",
                title_suffix="Рекурсия: исправьте базовый случай",
                description="Исправьте ошибку в базовом случае рекурсивной функции.",
                difficulty="medium",
                technical_concept_id="recursion",
                starter_pascal=(
                    "function Fact(n: integer): integer;\nbegin\n  if n = 0 then Fact := 0\n"
                    "  else Fact := n * Fact(n - 1);\nend;\nvar n: integer;\nbegin\n  readln(n);\n  writeln(Fact(n));\nend."
                ),
                test_cases=[{"inputs": "0", "output": "1"}, {"inputs": "4", "output": "24"}],
                reference_solution_pascal=(
                    "function Fact(n: integer): integer;\nbegin\n  if n = 0 then Fact := 1\n"
                    "  else Fact := n * Fact(n - 1);\nend;\nvar n: integer;\nbegin\n  readln(n);\n  writeln(Fact(n));\nend."
                ),
            ),
            slot_id="recu_s03",
        ),
        analyze_slot(
            slot_id="recu_s04",
            collection_key="recursion",
            target_tc="recursion",
            title_suffix="Рекурсия: предскажите SumTo(4)",
            short_instruction="Определите SumTo(4) для суммы 1..n.",
            description="Изучите рекурсивную функцию SumTo.",
            difficulty="medium",
            code_examples_pascal=(
                "function SumTo(n: integer): integer;\nbegin\n  if n <= 0 then SumTo := 0\n"
                "  else SumTo := n + SumTo(n - 1);\nend;\nbegin\n  writeln(SumTo(4));\nend."
            ),
            expected_output="10",
        ),
    )


def _algorithms_slots() -> tuple[PedagogicalSlotSpec, ...]:
    return (
        _spec_to_slot(
            _io_spec(
                collection_key="algorithms",
                slug="alg_search_find_imp_text_contains",
                title_suffix="Поиск: есть ли элемент",
                description="Считайте три числа и target. Выведите yes, если target равен одному из трёх.",
                difficulty="easy",
                technical_concept_id="search_find",
                test_cases=[{"inputs": "1\n5\n9\n5", "output": "yes"}, {"inputs": "2\n3\n4\n1", "output": "no"}],
                reference_solution_pascal=(
                    "program Contains3;\nvar a, b, c, t: integer;\nbegin\n  readln(a);\n  readln(b);\n  readln(c);\n"
                    "  readln(t);\n  if (a = t) or (b = t) or (c = t) then writeln('yes') else writeln('no');\nend."
                ),
            ),
            slot_id="alg_s01",
        ),
        analyze_slot(
            slot_id="alg_s02",
            collection_key="algorithms",
            target_tc="filter_select",
            title_suffix="Фильтрация: предскажите число чётных",
            short_instruction="Определите c для массива 2, 3, 4.",
            description="Изучите подсчёт чётных элементов среди трёх чисел.",
            difficulty="easy",
            code_examples_pascal=(
                "var a: array[1..3] of integer;\n    i, c: integer;\nbegin\n"
                "  a[1] := 2; a[2] := 3; a[3] := 4;\n  c := 0;\n  for i := 1 to 3 do\n"
                "    if a[i] mod 2 = 0 then c := c + 1;\n  writeln(c);\nend."
            ),
            expected_output="2",
        ),
        _spec_to_slot(
            _translation_spec(
                collection_key="algorithms",
                slug="alg_fold_aggregate_tr_cpp_sum_abs",
                title_suffix="Агрегация fold",
                description="Перенесите сумму модулей двух чисел на Pascal.",
                difficulty="medium",
                technical_concept_id="fold_aggregate",
                known_language_variants=ALG_SUM_ABS,
                test_cases=[{"inputs": "-3\n4", "output": "7"}, {"inputs": "-2\n-5", "output": "7"}],
                reference_solution_pascal=(
                    "program SumAbs;\nvar a, b: integer;\nbegin\n  readln(a);\n  readln(b);\n  if a < 0 then a := -a;\n"
                    "  if b < 0 then b := -b;\n  writeln(a + b);\nend."
                ),
            ),
            slot_id="alg_s03",
        ),
        _spec_to_slot(
            _debug_spec(
                collection_key="algorithms",
                slug="alg_sort_order_dbg_fix_swap",
                title_suffix="Сортировка: исправьте обмен двух чисел",
                description="Программа должна выводить два числа по возрастанию.",
                difficulty="hard",
                technical_concept_id="sort_order",
                starter_pascal=(
                    "program Sort2;\nvar a, b, t: integer;\nbegin\n  readln(a);\n  readln(b);\n  if a > b then\n"
                    "  begin\n    t := a;\n    a := b;\n    b := a;\n  end;\n  writeln(a);\n  writeln(b);\nend."
                ),
                test_cases=[{"inputs": "7\n2", "output": "2\n7"}, {"inputs": "1\n5", "output": "1\n5"}],
                reference_solution_pascal=(
                    "program Sort2;\nvar a, b, t: integer;\nbegin\n  readln(a);\n  readln(b);\n  if a > b then\n"
                    "  begin\n    t := a;\n    a := b;\n    b := t;\n  end;\n  writeln(a);\n  writeln(b);\nend."
                ),
            ),
            slot_id="alg_s04",
        ),
        analyze_slot(
            slot_id="alg_s05",
            collection_key="algorithms",
            target_tc="sort_order",
            title_suffix="Сортировка: предскажите min и max из трёх",
            short_instruction="Определите min и max для 5, 2, 9.",
            description="Изучите поиск минимума и максимума среди трёх чисел.",
            difficulty="medium",
            code_examples_pascal=(
                "var a, b, c, mn, mx: integer;\nbegin\n  a := 5; b := 2; c := 9;\n"
                "  mn := a; mx := a;\n  if b < mn then mn := b;\n  if c < mn then mn := c;\n"
                "  if b > mx then mx := b;\n  if c > mx then mx := c;\n  writeln(mn);\n  writeln(mx);\nend."
            ),
            expected_output="2\n9",
        ),
        analyze_slot(
            slot_id="alg_s06",
            collection_key="algorithms",
            target_tc="fold_aggregate",
            title_suffix="Агрегация: предскажите среднее двух чисел",
            short_instruction="Определите (a+b) div 2 для a=4, b=8.",
            description="Изучите вычисление целочисленного среднего двух чисел.",
            difficulty="easy",
            code_examples_pascal=(
                "var a, b: integer;\nbegin\n  a := 4;\n  b := 8;\n  writeln((a + b) div 2);\nend."
            ),
            expected_output="6",
        ),
        analyze_slot(
            slot_id="alg_s07",
            collection_key="algorithms",
            target_tc="search_find",
            title_suffix="Поиск: предскажите результат contains",
            short_instruction="Определите yes/no для target=5 среди 1,5,9.",
            description="Изучите проверку вхождения target в три значения.",
            difficulty="easy",
            code_examples_pascal=(
                "var a, b, c, t: integer;\nbegin\n  a := 1; b := 5; c := 9; t := 5;\n"
                "  if (a = t) or (b = t) or (c = t) then writeln('yes') else writeln('no');\nend."
            ),
            expected_output="yes",
        ),
    )


def _data_structures_slots() -> tuple[PedagogicalSlotSpec, ...]:
    legacy = (
        _spec_to_slot(
            _io_spec(
                collection_key="data_structures",
                slug="ds_stack_queue_imp_text_stack_top",
                title_suffix="Стек: верхний элемент после двух push",
                description="Считайте a и b как два push в стек. Выведите top.",
                difficulty="medium",
                technical_concept_id="stack_queue",
                test_cases=[{"inputs": "3\n7", "output": "7"}, {"inputs": "10\n1", "output": "1"}],
                reference_solution_pascal=(
                    "program StackTop;\nvar a, b: integer;\nbegin\n  readln(a);\n  readln(b);\n  writeln(b);\nend."
                ),
            ),
            slot_id="ds_s01",
        ),
        _spec_to_slot(
            _translation_spec(
                collection_key="data_structures",
                slug="ds_linked_node_tr_python_pair",
                title_suffix="Связный узел",
                description="Перенесите идею узла с двумя значениями на Pascal.",
                difficulty="medium",
                technical_concept_id="linked_node",
                known_language_variants=DS_NODE,
                test_cases=[{"inputs": "5\n8", "output": "8"}, {"inputs": "1\n2", "output": "2"}],
                reference_solution_pascal=(
                    "program NodePair;\nvar first, second: integer;\nbegin\n  readln(first);\n  readln(second);\n  writeln(second);\nend."
                ),
            ),
            slot_id="ds_s02",
        ),
        _spec_to_slot(
            _translation_spec(
                collection_key="data_structures",
                slug="ds_tree_hierarchy_tr_cpp_parent_child",
                title_suffix="Дерево tree",
                description="Перенесите parent-child логику на Pascal.",
                difficulty="medium",
                technical_concept_id="tree_hierarchy",
                known_language_variants=DS_TREE,
                test_cases=[{"inputs": "9\n4", "output": "9"}, {"inputs": "1\n2", "output": "1"}],
                reference_solution_pascal=(
                    "program TreeParent;\nvar p, c: integer;\nbegin\n  readln(p);\n  readln(c);\n  writeln(p);\nend."
                ),
            ),
            slot_id="ds_s03",
        ),
        _spec_to_slot(
            _debug_spec(
                collection_key="data_structures",
                slug="ds_graph_edges_dbg_fix_count",
                title_suffix="Граф: исправьте подсчёт рёбер",
                description="Программа должна выводить количество рёбер m, а не число вершин n.",
                difficulty="hard",
                technical_concept_id="graph_edges",
                starter_pascal=(
                    "program EdgeCount;\nvar n, m: integer;\nbegin\n  readln(n);\n  readln(m);\n  writeln(n);\nend."
                ),
                test_cases=[{"inputs": "5\n7", "output": "7"}, {"inputs": "3\n0", "output": "0"}],
                reference_solution_pascal=(
                    "program EdgeCount;\nvar n, m: integer;\nbegin\n  readln(n);\n  readln(m);\n  writeln(m);\nend."
                ),
            ),
            slot_id="ds_s04",
        ),
        debug_slot(
            slot_id="ds_s05",
            collection_key="data_structures",
            target_tc="stack_queue",
            title_suffix="Очередь: исправьте front",
            short_instruction="Исправьте вывод: front — первое число.",
            description="Очередь FIFO: после enqueue a и b front равен a, не b.",
            difficulty="medium",
            starter_pascal=(
                "program QueueBug;\nvar a, b: integer;\nbegin\n  readln(a);\n  readln(b);\n  writeln(b);\nend."
            ),
            test_cases=[{"inputs": "4\n9", "output": "4"}, {"inputs": "7\n1", "output": "7"}],
            reference_solution_pascal=(
                "program QueueBug;\nvar a, b: integer;\nbegin\n  readln(a);\n  readln(b);\n  writeln(a);\nend."
            ),
        ),
        analyze_slot(
            slot_id="ds_s06",
            collection_key="data_structures",
            target_tc="tree_hierarchy",
            title_suffix="Дерево: предскажите глубину узла",
            short_instruction="Определите глубину 1 для child первого уровня.",
            description="Изучите модель дерева с корнем и потомком первого уровня.",
            difficulty="easy",
            code_examples_pascal=(
                "var root, child: integer;\nbegin\n  root := 10;\n  child := 11;\n  writeln(1);\nend."
            ),
            expected_output="1",
        ),
    )
    new = (
        analyze_slot(
            slot_id="ds_s07",
            collection_key="data_structures",
            target_tc="stack_queue",
            title_suffix="Стек: предскажите top после push",
            short_instruction="Определите top после push 3 и push 7.",
            description="Изучите поведение стека LIFO.",
            difficulty="easy",
            code_examples_pascal="var a, b: integer;\nbegin\n  a := 3;\n  b := 7;\n  writeln(b);\nend.",
            expected_output="7",
        ),
        analyze_slot(
            slot_id="ds_s08",
            collection_key="data_structures",
            target_tc="linked_node",
            title_suffix="Узел: предскажите second",
            short_instruction="Определите second после first=5, second=8.",
            description="Изучите пару значений как связный узел.",
            difficulty="easy",
            code_examples_pascal=(
                "var first, second: integer;\nbegin\n  first := 5;\n  second := 8;\n  writeln(second);\nend."
            ),
            expected_output="8",
        ),
        debug_slot(
            slot_id="ds_s09",
            collection_key="data_structures",
            target_tc="linked_node",
            title_suffix="Узел: исправьте порядок полей",
            short_instruction="Исправьте вывод: нужен second, не first.",
            description="Программа должна выводить second, но печатает first.",
            difficulty="medium",
            starter_pascal=(
                "program NodeBug;\nvar first, second: integer;\nbegin\n  readln(first);\n  readln(second);\n"
                "  writeln(first);\nend."
            ),
            test_cases=[{"inputs": "5\n8", "output": "8"}, {"inputs": "1\n2", "output": "2"}],
            reference_solution_pascal=(
                "program NodeBug;\nvar first, second: integer;\nbegin\n  readln(first);\n  readln(second);\n"
                "  writeln(second);\nend."
            ),
        ),
        debug_slot(
            slot_id="ds_s10",
            collection_key="data_structures",
            target_tc="graph_edges",
            title_suffix="Граф: исправьте сумму n и m",
            short_instruction="Исправьте вывод: нужна сумма n+m, не m.",
            description="Программа должна выводить n+m, но печатает только m.",
            difficulty="medium",
            starter_pascal=(
                "program EdgeSum;\nvar n, m: integer;\nbegin\n  readln(n);\n  readln(m);\n  writeln(m);\nend."
            ),
            test_cases=[{"inputs": "5\n7", "output": "12"}, {"inputs": "3\n0", "output": "3"}],
            reference_solution_pascal=(
                "program EdgeSum;\nvar n, m: integer;\nbegin\n  readln(n);\n  readln(m);\n  writeln(n + m);\nend."
            ),
        ),
        analyze_slot(
            slot_id="ds_s11",
            collection_key="data_structures",
            target_tc="graph_edges",
            title_suffix="Граф: предскажите число рёбер",
            short_instruction="Определите вывод m при n=3, m=0.",
            description="Изучите чтение параметров графа и вывод m.",
            difficulty="easy",
            code_examples_pascal=(
                "var n, m: integer;\nbegin\n  n := 3;\n  m := 0;\n  writeln(m);\nend."
            ),
            expected_output="0",
        ),
    )
    return legacy + new


def _oop_slots() -> tuple[PedagogicalSlotSpec, ...]:
    legacy = (
        _spec_to_slot(
            _translation_spec(
                collection_key="oop",
                slug="oop_class_type_tr_python_point_sum",
                title_suffix="Класс: сумма координат точки",
                description="Перенесите объект с полями x, y и суммой на Pascal.",
                difficulty="medium",
                technical_concept_id="class_type",
                known_language_variants=OOP_POINT,
                test_cases=[{"inputs": "2\n3", "output": "5"}, {"inputs": "-1\n5", "output": "4"}],
                reference_solution_pascal=(
                    "program OopPoint;\ntype TPoint = class\n  x: integer;\n  y: integer;\nend;\nvar p: TPoint;\n"
                    "begin\n  p := TPoint.Create;\n  readln(p.x);\n  readln(p.y);\n  writeln(p.x + p.y);\n  p.Free;\nend."
                ),
            ),
            slot_id="oop_s01",
        ),
        analyze_slot(
            slot_id="oop_s02",
            collection_key="oop",
            target_tc="object_instance",
            title_suffix="Экземпляр объекта: предскажите площадь",
            short_instruction="Определите r.w * r.h для w=3, h=4.",
            description="Изучите объект с полями w и h и вывод произведения.",
            difficulty="medium",
            code_examples_pascal=(
                "type TRect = class\n  w: integer;\n  h: integer;\nend;\nvar r: TRect;\nbegin\n"
                "  r := TRect.Create;\n  r.w := 3;\n  r.h := 4;\n  writeln(r.w * r.h);\n  r.Free;\nend."
            ),
            expected_output="12",
        ),
        _spec_to_slot(
            _io_spec(
                collection_key="oop",
                slug="oop_method_dispatch_imp_text_double",
                title_suffix="Метод объекта: удвоение значения",
                description="Реализуйте класс с методом DoubleValue и выведите результат.",
                difficulty="medium",
                technical_concept_id="method_dispatch",
                test_cases=[{"inputs": "6", "output": "12"}, {"inputs": "-2", "output": "-4"}],
                reference_solution_pascal=(
                    "type TCalc = class\n  function DoubleValue(x: integer): integer;\nend;\n"
                    "function TCalc.DoubleValue(x: integer): integer;\nbegin\n  DoubleValue := x * 2;\nend;\n"
                    "var c: TCalc;\n    n: integer;\nbegin\n  c := TCalc.Create;\n  readln(n);\n"
                    "  writeln(c.DoubleValue(n));\n  c.Free;\nend."
                ),
            ),
            slot_id="oop_s03",
        ),
        _spec_to_slot(
            _debug_spec(
                collection_key="oop",
                slug="oop_inheritance_hierarchy_dbg_fix",
                title_suffix="Наследование: исправьте вызов метода",
                description="В коде ошибка: создаётся базовый класс вместо потомка.",
                difficulty="hard",
                technical_concept_id="inheritance_hierarchy",
                starter_pascal=(
                    "type TBase = class\n  function Value: integer; virtual;\nend;\n"
                    "function TBase.Value: integer;\nbegin\n  Value := 1;\nend;\n"
                    "type TChild = class(TBase)\n  function Value: integer; override;\nend;\n"
                    "function TChild.Value: integer;\nbegin\n  Value := 2;\nend;\n"
                    "var b: TBase;\nbegin\n  b := TBase.Create;\n  writeln(b.Value);\n  b.Free;\nend."
                ),
                test_cases=[{"inputs": "", "output": "2"}],
                reference_solution_pascal=(
                    "type TBase = class\n  function Value: integer; virtual;\nend;\n"
                    "function TBase.Value: integer;\nbegin\n  Value := 1;\nend;\n"
                    "type TChild = class(TBase)\n  function Value: integer; override;\nend;\n"
                    "function TChild.Value: integer;\nbegin\n  Value := 2;\nend;\n"
                    "var b: TBase;\nbegin\n  b := TChild.Create;\n  writeln(b.Value);\n  b.Free;\nend."
                ),
            ),
            slot_id="oop_s04",
        ),
        _spec_to_slot(
            _io_spec(
                collection_key="oop",
                slug="oop_object_instance_imp_io_sum_fields",
                title_suffix="Объект: сумма полей",
                description="Создайте объект с полями a и b, выведите сумму полей.",
                difficulty="medium",
                technical_concept_id="object_instance",
                test_cases=[{"inputs": "9\n1", "output": "10"}, {"inputs": "-2\n7", "output": "5"}],
                reference_solution_pascal=(
                    "type TPair = class\n  a: integer;\n  b: integer;\nend;\nvar p: TPair;\nbegin\n"
                    "  p := TPair.Create;\n  readln(p.a);\n  readln(p.b);\n  writeln(p.a + p.b);\n  p.Free;\nend."
                ),
            ),
            slot_id="oop_s05",
        ),
        analyze_slot(
            slot_id="oop_s06",
            collection_key="oop",
            target_tc="method_dispatch",
            title_suffix="Метод: предскажите Sign.Eval(-3)",
            short_instruction="Определите результат метода Eval для n=-3.",
            description="Изучите метод объекта, возвращающий знак числа.",
            difficulty="medium",
            code_examples_pascal=(
                "type TSign = class\n  function Eval(n: integer): integer;\nend;\n"
                "function TSign.Eval(n: integer): integer;\nbegin\n  if n > 0 then Eval := 1\n"
                "  else if n < 0 then Eval := -1\n  else Eval := 0;\nend;\n"
                "var s: TSign;\nbegin\n  s := TSign.Create;\n  writeln(s.Eval(-3));\n  s.Free;\nend."
            ),
            expected_output="-1",
        ),
    )
    new = (
        analyze_slot(
            slot_id="oop_s07",
            collection_key="oop",
            target_tc="class_type",
            title_suffix="Класс: предскажите сумму полей Point",
            short_instruction="Определите p.x + p.y для x=2, y=3.",
            description="Изучите объект с полями x и y.",
            difficulty="easy",
            code_examples_pascal=(
                "type TPoint = class\n  x: integer;\n  y: integer;\nend;\nvar p: TPoint;\nbegin\n"
                "  p := TPoint.Create;\n  p.x := 2;\n  p.y := 3;\n  writeln(p.x + p.y);\n  p.Free;\nend."
            ),
            expected_output="5",
        ),
        debug_slot(
            slot_id="oop_s08",
            collection_key="oop",
            target_tc="object_instance",
            title_suffix="Объект: исправьте умножение полей",
            short_instruction="Исправьте формулу площади w*h.",
            description="Прямоугольник должен выводить произведение w и h.",
            difficulty="medium",
            starter_pascal=(
                "type TRect = class\n  w: integer;\n  h: integer;\nend;\nvar r: TRect;\nbegin\n"
                "  r := TRect.Create;\n  readln(r.w);\n  readln(r.h);\n  writeln(r.w + r.h);\n  r.Free;\nend."
            ),
            test_cases=[{"inputs": "3\n4", "output": "12"}, {"inputs": "2\n5", "output": "10"}],
            reference_solution_pascal=(
                "type TRect = class\n  w: integer;\n  h: integer;\nend;\nvar r: TRect;\nbegin\n"
                "  r := TRect.Create;\n  readln(r.w);\n  readln(r.h);\n  writeln(r.w * r.h);\n  r.Free;\nend."
            ),
        ),
        debug_slot(
            slot_id="oop_s09",
            collection_key="oop",
            target_tc="method_dispatch",
            title_suffix="Метод: исправьте тело DoubleValue",
            short_instruction="Исправьте метод: нужно x * 2, не x.",
            description="Метод DoubleValue должен удваивать аргумент, но возвращает его без изменений.",
            difficulty="medium",
            starter_pascal=(
                "type TCalc = class\n  function DoubleValue(x: integer): integer;\nend;\n"
                "function TCalc.DoubleValue(x: integer): integer;\nbegin\n  DoubleValue := x;\nend;\n"
                "var c: TCalc;\n    n: integer;\nbegin\n  c := TCalc.Create;\n  readln(n);\n"
                "  writeln(c.DoubleValue(n));\n  c.Free;\nend."
            ),
            test_cases=[{"inputs": "6", "output": "12"}, {"inputs": "-2", "output": "-4"}],
            reference_solution_pascal=(
                "type TCalc = class\n  function DoubleValue(x: integer): integer;\nend;\n"
                "function TCalc.DoubleValue(x: integer): integer;\nbegin\n  DoubleValue := x * 2;\nend;\n"
                "var c: TCalc;\n    n: integer;\nbegin\n  c := TCalc.Create;\n  readln(n);\n"
                "  writeln(c.DoubleValue(n));\n  c.Free;\nend."
            ),
        ),
        analyze_slot(
            slot_id="oop_s10",
            collection_key="oop",
            target_tc="inheritance_hierarchy",
            title_suffix="Наследование: предскажите Value у TChild",
            short_instruction="Определите b.Value при b := TChild.Create.",
            description="Изучите полиморный вызов переопределённого метода.",
            difficulty="medium",
            code_examples_pascal=(
                "type TBase = class\n  function Value: integer; virtual;\nend;\n"
                "function TBase.Value: integer;\nbegin\n  Value := 1;\nend;\n"
                "type TChild = class(TBase)\n  function Value: integer; override;\nend;\n"
                "function TChild.Value: integer;\nbegin\n  Value := 2;\nend;\n"
                "var b: TBase;\nbegin\n  b := TChild.Create;\n  writeln(b.Value);\n  b.Free;\nend."
            ),
            expected_output="2",
        ),
        io_slot(
            slot_id="oop_s11",
            collection_key="oop",
            target_tc="class_type",
            primary_action="implement",
            title_suffix="Класс: капstone — сумма координат Point",
            short_instruction="Создайте TPoint, прочитайте x и y, выведите сумму.",
            description="Капstone: класс TPoint с полями x, y и выводом их суммы.",
            difficulty="medium",
            test_cases=[{"inputs": "2\n3", "output": "5"}, {"inputs": "-1\n5", "output": "4"}],
            reference_solution_pascal=(
                "program OopCapstone;\ntype TPoint = class\n  x: integer;\n  y: integer;\nend;\nvar p: TPoint;\n"
                "begin\n  p := TPoint.Create;\n  readln(p.x);\n  readln(p.y);\n  writeln(p.x + p.y);\n  p.Free;\nend."
            ),
        ),
    )
    return legacy + new


_COLLECTION_BUILDERS = (
    _variables_and_io_slots,
    _conditions_slots,
    _loops_slots,
    _functions_slots,
    _arrays_slots,
    _strings_slots,
    _records_slots,
    _files_slots,
    _procedures_slots,
    _modules_slots,
    _recursion_slots,
    _algorithms_slots,
    _data_structures_slots,
    _oop_slots,
)


def all_pedagogical_slots() -> tuple[PedagogicalSlotSpec, ...]:
    slots: list[PedagogicalSlotSpec] = []
    for builder in _COLLECTION_BUILDERS:
        for slot in builder():
            slots.append(FLOWCHART_SLOT_BY_ID.get(slot.slot_id, slot))
    return tuple(slots)


def slots_by_collection() -> dict[str, tuple[PedagogicalSlotSpec, ...]]:
    grouped: dict[str, list[PedagogicalSlotSpec]] = {}
    for slot in all_pedagogical_slots():
        grouped.setdefault(slot.collection_key, []).append(slot)
    return {key: tuple(items) for key, items in grouped.items()}


assert len(all_pedagogical_slots()) == 102
for _collection_key, _target in COLLECTION_TARGETS.items():
    assert len(slots_by_collection()[_collection_key]) == _target



