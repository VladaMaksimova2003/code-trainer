"""Pascal / LC conditions — showcase task definitions (curriculum v2)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from shared.enums import AssignmentType

from application.curriculum.pascal.catalog.pascal_transfer_presets import (
    COND_IF_ASSEMBLE,
    COND_SIMPLE_BRANCH,
    COND_SWITCH,
    LOOP_COLLECTION,
    LOOP_COUNTED,
    LOOP_FOR_ASSEMBLE,
)

SHOWCASE_GROUP = "pascal_curriculum_conditions_v1"
TITLE_PREFIX = "[Pascal Conditions Showcase] "
LANGUAGE = "pascal"
LEARNING_CONCEPT_ID = "conditions"


@dataclass(frozen=True)
class ConditionsShowcaseTaskSpec:
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


def conditions_showcase_specs() -> tuple[ConditionsShowcaseTaskSpec, ...]:
    return (
        ConditionsShowcaseTaskSpec(
            slug="simple_branch_tr_python",
            title_suffix="Условие if",
            description=(
                "Перенесите знакомую программу на Pascal (Free Pascal).\n\n"
                "Программа считывает целое n и выводит `pos`, если n > 0, иначе `nonpos`."
            ),
            difficulty="easy",
            technical_concept_id="simple_branch",
            exercise_pattern_id="tr_python_to_pascal_code",
            assignment_type=AssignmentType.TASK_TRANSLATE_SNIPPET.value,
            builder_key="translation_to_pascal",
            extra={
                "known_language_variants": COND_SIMPLE_BRANCH,
                "source_language": "python",
                "source_code": COND_SIMPLE_BRANCH["python"]["source_code"],
                "test_cases": [
                    {"inputs": "5", "output": "pos"},
                    {"inputs": "0", "output": "nonpos"},
                    {"inputs": "-3", "output": "nonpos"},
                ],
            },
        ),
        ConditionsShowcaseTaskSpec(
            slug="simple_branch_asm_blocks",
            title_suffix="Условие if: соберите из блоков",
            description="Слева — знакомый if на вашем языке. Справа — соберите эквивалент на Pascal.",
            difficulty="easy",
            technical_concept_id="simple_branch",
            exercise_pattern_id="asm_blocks_to_code_pascal",
            assignment_type=AssignmentType.TASK_BUILD_FROM_BLOCKS.value,
            builder_key="block_reorder_pascal",
            extra={
                "language": "pascal",
                "known_language_variants": COND_IF_ASSEMBLE,
                "original_code": (
                    "program Parity;\n"
                    "var n: integer;\n"
                    "begin\n"
                    "  readln(n);\n"
                    "  if n mod 2 = 0 then\n"
                    "    writeln('even')\n"
                    "  else\n"
                    "    writeln('odd');\n"
                    "end."
                ),
                "template": (
                    "program Parity;\n"
                    "var n: integer;\n"
                    "begin\n"
                    "  readln(n);\n"
                    "  {0}\n"
                    "    {1}\n"
                    "  {2}\n"
                    "    {3}\n"
                    "end."
                ),
                "blocks": [
                    "if n mod 2 = 0 then",
                    "writeln('even')",
                    "else",
                    "writeln('odd');",
                ],
                "correct_order": [0, 1, 2, 3],
                "test_cases": [
                    {"inputs": "4", "output": "even"},
                    {"inputs": "7", "output": "odd"},
                ],
            },
        ),
        ConditionsShowcaseTaskSpec(
            slug="multi_branch_imp_text",
            title_suffix="Несколько ветвей: напишите программу",
            description=(
                "Напишите программу на Pascal по условию.\n\n"
                "Считывается целое score (0..100). Выведите одну букву:\n"
                "- `A`, если score ≥ 90;\n"
                "- `B`, если score ≥ 70 (и < 90);\n"
                "- `C` в остальных случаях."
            ),
            difficulty="easy",
            technical_concept_id="multi_branch",
            exercise_pattern_id="imp_text_spec_to_pascal",
            assignment_type=AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
            builder_key="pascal_io_program",
            extra={
                "test_cases": [
                    {"inputs": "95", "output": "A"},
                    {"inputs": "75", "output": "B"},
                    {"inputs": "50", "output": "C"},
                ],
            },
        ),
        ConditionsShowcaseTaskSpec(
            slug="switch_selection_tr_cpp",
            title_suffix="Case of",
            description=(
                "Перенесите знакомую программу на Pascal.\n\n"
                "Программа считывает code и выводит `one`, `two` или `other`."
            ),
            difficulty="medium",
            technical_concept_id="switch_selection",
            exercise_pattern_id="tr_cpp_to_pascal_code",
            assignment_type=AssignmentType.TASK_TRANSLATE_SNIPPET.value,
            builder_key="translation_to_pascal",
            extra={
                "known_language_variants": COND_SWITCH,
                "source_language": "cpp",
                "source_code": COND_SWITCH["cpp"]["source_code"],
                "test_cases": [
                    {"inputs": "1", "output": "one"},
                    {"inputs": "2", "output": "two"},
                    {"inputs": "9", "output": "other"},
                ],
            },
        ),
        ConditionsShowcaseTaskSpec(
            slug="conditional_expression_analyze",
            title_suffix="Условное выражение: предскажите результат",
            description=(
                "В C/Java/C# часто пишут тернарный оператор:\n"
                "`result = (n >= 0) ? n : -n;`\n\n"
                "В Pascal нет такого оператора — эквивалент записывают через `if … then … else`.\n\n"
                "Изучите фрагмент Pascal ниже (абсолютное значение n при n=5) и напишите "
                "минимальную программу с тем же выводом.\n\n"
                "```pascal\n"
                "var n, result: integer;\n"
                "begin\n"
                "  n := 5;\n"
                "  if n >= 0 then\n"
                "    result := n\n"
                "  else\n"
                "    result := -n;\n"
                "  writeln(result);\n"
                "end.\n"
                "```"
            ),
            difficulty="medium",
            technical_concept_id="conditional_expression",
            exercise_pattern_id="ana_pascal_code_predict_output",
            assignment_type=AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
            builder_key="pascal_io_program",
            extra={
                "code_examples_pascal": (
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
                "test_cases": [
                    {"inputs": "", "output": "5"},
                ],
            },
        ),
        ConditionsShowcaseTaskSpec(
            slug="simple_branch_debug_logic",
            title_suffix="Логическое условие: исправьте ошибку",
            description=(
                "В программе Pascal ошибка в условии: должны выводиться числа, "
                "которые **положительны и чётны**, но сейчас проверка написана с `or` вместо `and`. "
                "Исправьте условие."
            ),
            difficulty="medium",
            technical_concept_id="simple_branch",
            exercise_pattern_id="dbg_pascal_code_fix",
            assignment_type=AssignmentType.TASK_TRANSLATE_FULL_PROGRAM.value,
            builder_key="pascal_debug_starter",
            extra={
                "starter_pascal": (
                    "program PosEven;\n"
                    "var n: integer;\n"
                    "begin\n"
                    "  readln(n);\n"
                    "  if (n > 0) or (n mod 2 = 0) then\n"
                    "    writeln('yes')\n"
                    "  else\n"
                    "    writeln('no');\n"
                    "end."
                ),
                "test_cases": [
                    {"inputs": "4", "output": "yes"},
                    {"inputs": "3", "output": "no"},
                    {"inputs": "-2", "output": "no"},
                    {"inputs": "7", "output": "no"},
                ],
            },
        ),
    )

