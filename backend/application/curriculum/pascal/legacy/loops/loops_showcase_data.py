"""Pascal / LC loops — showcase task definitions (curriculum v2)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from shared.enums import AssignmentType

from application.curriculum.pascal.catalog.pascal_transfer_presets import (
    LOOP_COLLECTION,
    LOOP_COUNTED,
    LOOP_FOR_ASSEMBLE,
)

SHOWCASE_GROUP = "pascal_curriculum_loops_v1"
TITLE_PREFIX = "[Pascal Loops Showcase] "
LANGUAGE = "pascal"
LEARNING_CONCEPT_ID = "loops"


@dataclass(frozen=True)
class LoopsShowcaseTaskSpec:
    slug: str
    title_suffix: str
    description: str
    difficulty: str
    technical_concept_id: str
    exercise_pattern_id: str
    assignment_type: str
    builder_key: str
    extra: dict[str, Any] | None = None
    primary_action: str | None = None

    @property
    def title(self) -> str:
        return f"{TITLE_PREFIX}{self.title_suffix}"


def loops_showcase_specs() -> tuple[LoopsShowcaseTaskSpec, ...]:
    return (
        LoopsShowcaseTaskSpec(
            slug="counted_loop_tr_python",
            title_suffix="Цикл for: перевод с Python на Pascal",
            description=(
                "Перенесите знакомую программу на Pascal (Free Pascal).\n\n"
                "Программа считывает n и выводит сумму чисел от 1 до n."
            ),
            difficulty="easy",
            technical_concept_id="counted_loop",
            exercise_pattern_id="tr_python_to_pascal_code",
            assignment_type=AssignmentType.TASK_TRANSLATE_SNIPPET.value,
            builder_key="translation_python_to_pascal",
            extra={
                "known_language_variants": LOOP_COUNTED,
                "source_language": "python",
                "source_code": LOOP_COUNTED["python"]["source_code"],
                "test_cases": [
                    {"inputs": "5", "output": "15"},
                    {"inputs": "1", "output": "1"},
                    {"inputs": "10", "output": "55"},
                ],
            },
        ),
        LoopsShowcaseTaskSpec(
            slug="counted_loop_asm_blocks",
            title_suffix="Цикл for: соберите из блоков",
            description="Слева — знакомый цикл for. Справа — соберите эквивалент на Pascal.",
            difficulty="easy",
            technical_concept_id="counted_loop",
            exercise_pattern_id="asm_blocks_to_code_pascal",
            assignment_type=AssignmentType.TASK_BUILD_FROM_BLOCKS.value,
            builder_key="block_reorder_pascal",
            extra={
                "language": "pascal",
                "known_language_variants": LOOP_FOR_ASSEMBLE,
                "original_code": (
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
                "template": (
                    "program Sum;\n"
                    "var i, n, s: integer;\n"
                    "begin\n"
                    "  readln(n);\n"
                    "  s := 0;\n"
                    "  {0}\n"
                    "    {1}\n"
                    "  writeln(s);\n"
                    "end."
                ),
                "blocks": [
                    "for i := 1 to n do",
                    "s := s + i;",
                ],
                "correct_order": [0, 1],
                "test_cases": [
                    {"inputs": "4", "output": "10"},
                    {"inputs": "1", "output": "1"},
                ],
            },
        ),
        LoopsShowcaseTaskSpec(
            slug="pre_condition_imp_text",
            title_suffix="Цикл while: напишите программу по условию",
            description=(
                "Напишите программу на Pascal по условию.\n\n"
                "Считывается целое n (n ≥ 0). Пока n > 0, выводите n и уменьшайте его на 1. "
                "Когда n станет 0, программа завершается."
            ),
            difficulty="easy",
            technical_concept_id="pre_condition_loop",
            exercise_pattern_id="imp_text_spec_to_pascal",
            assignment_type=AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
            builder_key="pascal_io_program",
            extra={
                "test_cases": [
                    {"inputs": "3", "output": "3\n2\n1"},
                    {"inputs": "1", "output": "1"},
                    {"inputs": "0", "output": ""},
                ],
            },
        ),
        LoopsShowcaseTaskSpec(
            slug="post_condition_analyze_output",
            title_suffix="Цикл repeat-until: предскажите вывод",
            description=(
                "Изучите фрагмент Pascal с `repeat … until` и определите вывод.\n\n"
                "Напишите минимальную программу Pascal, которая выводит тот же результат, "
                "что и фрагмент при n=3 (три строки: 3, 2, 1).\n\n"
                "```pascal\n"
                "var n: integer;\n"
                "begin\n"
                "  n := 3;\n"
                "  repeat\n"
                "    writeln(n);\n"
                "    n := n - 1;\n"
                "  until n = 0;\n"
                "end.\n"
                "```"
            ),
            difficulty="medium",
            technical_concept_id="post_condition_loop",
            exercise_pattern_id="ana_pascal_code_predict_output",
            assignment_type=AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
            builder_key="pascal_io_program",
            extra={
                "code_examples_pascal": (
                    "var n: integer;\n"
                    "begin\n"
                    "  n := 3;\n"
                    "  repeat\n"
                    "    writeln(n);\n"
                    "    n := n - 1;\n"
                    "  until n = 0;\n"
                    "end."
                ),
                "test_cases": [
                    {"inputs": "", "output": "3\n2\n1"},
                ],
            },
        ),
        LoopsShowcaseTaskSpec(
            slug="loop_control_debug_logic",
            title_suffix="Break/Continue: исправьте ошибку",
            description=(
                "В программе Pascal ошибка: в цикл попадают чётные числа и суммируются, "
                "а нечётные пропускаются. Исправьте код так, чтобы при входе n выводилась "
                "сумма нечётных чисел от 1 до n."
            ),
            difficulty="medium",
            technical_concept_id="loop_control",
            exercise_pattern_id="dbg_pascal_logic_fix",
            assignment_type=AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
            builder_key="pascal_debug_starter",
            extra={
                "starter_pascal": (
                    "program OddSum;\n"
                    "var i, n, s: integer;\n"
                    "begin\n"
                    "  readln(n);\n"
                    "  s := 0;\n"
                    "  for i := 1 to n do\n"
                    "  begin\n"
                    "    if i mod 2 = 0 then\n"
                    "      s := s + i\n"
                    "    else\n"
                    "      continue;\n"
                    "  end;\n"
                    "  writeln(s);\n"
                    "end."
                ),
                "test_cases": [
                    {"inputs": "5", "output": "9"},
                    {"inputs": "1", "output": "1"},
                    {"inputs": "6", "output": "9"},
                ],
            },
        ),
        LoopsShowcaseTaskSpec(
            slug="nested_iteration_io",
            title_suffix="Вложенные циклы: таблица умножения",
            description=(
                "Напишите программу Pascal: считываются два целых a и b (1..9). "
                "Выведите произведение a×b (как в таблице умножения)."
            ),
            difficulty="hard",
            technical_concept_id="nested_iteration",
            exercise_pattern_id="imp_io_tests_pascal",
            assignment_type=AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
            builder_key="pascal_io_program",
            extra={
                "test_cases": [
                    {"inputs": "3\n4", "output": "12"},
                    {"inputs": "2\n2", "output": "4"},
                    {"inputs": "9\n9", "output": "81"},
                ],
            },
        ),
        LoopsShowcaseTaskSpec(
            slug="collection_iteration_tr_python",
            title_suffix="Перебор строки",
            description=(
                "Перенесите знакомую программу на Pascal.\n\n"
                "Программа считывает строку s и выводит количество символов 'a'."
            ),
            difficulty="medium",
            technical_concept_id="collection_iteration",
            exercise_pattern_id="tr_python_to_pascal_code",
            assignment_type=AssignmentType.TASK_TRANSLATE_SNIPPET.value,
            builder_key="translation_python_to_pascal",
            extra={
                "known_language_variants": LOOP_COLLECTION,
                "source_language": "python",
                "source_code": LOOP_COLLECTION["python"]["source_code"],
                "test_cases": [
                    {"inputs": "abaca", "output": "3"},
                    {"inputs": "xyz", "output": "0"},
                    {"inputs": "a", "output": "1"},
                ],
            },
        ),
    )

