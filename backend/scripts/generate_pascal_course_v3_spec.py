#!/usr/bin/env python3
"""Generate Pascal Course v3 audit + full task catalog (markdown + CSV)."""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"

# --- Audit of existing 102 tasks -------------------------------------------------

AUDIT_102: list[dict] = [
    # variables_and_io
    {"old_id": "vai_s01", "verdict": "изменить", "reason": "Фокус на echo числа, а не на program/begin/end/Readln"},
    {"old_id": "vai_s02", "verdict": "изменить", "reason": "Сводится к сложению двух чисел"},
    {"old_id": "vai_s03", "verdict": "удалить", "reason": "Implement «a-b» без особенностей Pascal"},
    {"old_id": "vai_s04", "verdict": "удалить", "reason": "Чистая арифметика x²+y²"},
    {"old_id": "vai_s05", "verdict": "оставить", "reason": "Типичная ошибка Readln — Pascal I/O"},
    {"old_id": "vai_s06", "verdict": "удалить", "reason": "Writeln суммы без синтаксической цели"},
    {"old_id": "vai_s07", "verdict": "удалить", "reason": "analyze — предсказание вывода"},
    {"old_id": "vai_s08", "verdict": "изменить", "reason": "analyze → выбор фрагмента div/mod (уникально для Pascal)"},
    {"old_id": "vai_s09", "verdict": "удалить", "reason": "analyze присваивания"},
    {"old_id": "vai_s10", "verdict": "удалить", "reason": "analyze арифметики"},
    {"old_id": "vai_s11", "verdict": "удалить", "reason": "analyze Readln"},
    {"old_id": "vai_s12", "verdict": "удалить", "reason": "analyze Writeln"},
    # conditions
    {"old_id": "cond_s01", "verdict": "оставить", "reason": "Перевод if then else"},
    {"old_id": "cond_s02", "verdict": "оставить", "reason": "Сборка if из блоков"},
    {"old_id": "cond_s03", "verdict": "изменить", "reason": "Implement → код по блок-схеме else if"},
    {"old_id": "cond_s04", "verdict": "оставить", "reason": "Перевод switch → case of"},
    {"old_id": "cond_s05", "verdict": "изменить", "reason": "analyze → перевод тернарного оператора в if then else"},
    {"old_id": "cond_s06", "verdict": "оставить", "reason": "Ошибка and/or в условии"},
    {"old_id": "cond_s07", "verdict": "удалить", "reason": "analyze цепочки if"},
    {"old_id": "cond_s08", "verdict": "удалить", "reason": "analyze case of"},
    {"old_id": "cond_s09", "verdict": "оставить", "reason": "Пропущенная ветка case"},
    {"old_id": "cond_s10", "verdict": "оставить", "reason": "if-then-else вместо abs — синтаксис Pascal"},
    {"old_id": "cond_s11", "verdict": "оставить", "reason": "Сборка цепочки if"},
    {"old_id": "cond_s12", "verdict": "удалить", "reason": "analyze классификации знака"},
    # loops
    {"old_id": "loop_s01", "verdict": "оставить", "reason": "Перевод for"},
    {"old_id": "loop_s02", "verdict": "оставить", "reason": "Сборка for"},
    {"old_id": "loop_s03", "verdict": "изменить", "reason": "Implement → код по блок-схеме while"},
    {"old_id": "loop_s04", "verdict": "изменить", "reason": "analyze → блок-схема repeat until по коду"},
    {"old_id": "loop_s05", "verdict": "оставить", "reason": "Break/Continue в Pascal"},
    {"old_id": "loop_s06", "verdict": "удалить", "reason": "Таблица умножения — алгоритмика"},
    {"old_id": "loop_s07", "verdict": "оставить", "reason": "Перебор строки for char"},
    {"old_id": "loop_s08", "verdict": "удалить", "reason": "analyze суммы 1..n"},
    {"old_id": "loop_s09", "verdict": "удалить", "reason": "analyze while"},
    {"old_id": "loop_s10", "verdict": "удалить", "reason": "analyze перебора"},
    {"old_id": "loop_s11", "verdict": "удалить", "reason": "analyze вложенных циклов"},
    {"old_id": "loop_s12", "verdict": "удалить", "reason": "analyze continue"},
    {"old_id": "loop_s13", "verdict": "оставить", "reason": "Ошибка until в repeat"},
    {"old_id": "loop_s14", "verdict": "изменить", "reason": "Implement → акцент Length, 1-based, For char"},
    # functions
    {"old_id": "fn_s01", "verdict": "удалить", "reason": "analyze Sq(5)"},
    {"old_id": "fn_s02", "verdict": "оставить", "reason": "Перевод вызова функции"},
    {"old_id": "fn_s03", "verdict": "удалить", "reason": "analyze Max2"},
    {"old_id": "fn_s04", "verdict": "оставить", "reason": "Ошибка в function ... : type"},
    {"old_id": "fn_s05", "verdict": "удалить", "reason": "Implement сумма квадратов"},
    {"old_id": "fn_s06", "verdict": "оставить", "reason": "Result и ветвление для нуля"},
    {"old_id": "fn_s07", "verdict": "удалить", "reason": "analyze Sq(3)"},
    # arrays
    {"old_id": "arr_s01", "verdict": "удалить", "reason": "Перевод суммы трёх — алгоритм"},
    {"old_id": "arr_s02", "verdict": "удалить", "reason": "analyze максимум"},
    {"old_id": "arr_s03", "verdict": "изменить", "reason": "Debug → границы Low/High, не алгоритм подсчёта"},
    {"old_id": "arr_s04", "verdict": "удалить", "reason": "analyze динамического массива"},
    # strings
    {"old_id": "str_s01", "verdict": "изменить", "reason": "Перевод Length + индекс 1..Length"},
    {"old_id": "str_s02", "verdict": "изменить", "reason": "analyze → выбор s[1] vs s[0]"},
    {"old_id": "str_s03", "verdict": "оставить", "reason": "Length(s) для последнего символа"},
    # records
    {"old_id": "rec_s01", "verdict": "оставить", "reason": "Перевод record"},
    {"old_id": "rec_s02", "verdict": "удалить", "reason": "analyze поля"},
    {"old_id": "rec_s03", "verdict": "оставить", "reason": "with / обмен полей record"},
    # files
    {"old_id": "fil_s01", "verdict": "удалить", "reason": "analyze чтения"},
    {"old_id": "fil_s02", "verdict": "удалить", "reason": "analyze квадрата"},
    {"old_id": "fil_s03", "verdict": "оставить", "reason": "Порядок Readln/Writeln"},
    {"old_id": "fil_s04", "verdict": "удалить", "reason": "analyze echo"},
    # procedures
    {"old_id": "pp_s01", "verdict": "изменить", "reason": "analyze → debug var-параметра Swap"},
    {"old_id": "pp_s02", "verdict": "оставить", "reason": "Потеря значения без var"},
    # modules
    {"old_id": "mod_s01", "verdict": "оставить", "reason": "import → uses"},
    {"old_id": "mod_s02", "verdict": "удалить", "reason": "analyze суммы"},
    {"old_id": "mod_s03", "verdict": "изменить", "reason": "Implement → unit interface/implementation"},
    {"old_id": "mod_s04", "verdict": "оставить", "reason": "Uses и видимость"},
    {"old_id": "mod_s05", "verdict": "удалить", "reason": "Implement удвоение без unit-контекста"},
    {"old_id": "mod_s06", "verdict": "удалить", "reason": "analyze SignValue"},
    {"old_id": "mod_s07", "verdict": "удалить", "reason": "analyze Add"},
    {"old_id": "mod_s08", "verdict": "оставить", "reason": "Неверное имя после uses"},
    # recursion
    {"old_id": "recu_s01", "verdict": "оставить", "reason": "Перевод recursive function"},
    {"old_id": "recu_s02", "verdict": "изменить", "reason": "Implement → сборка/перевод forward declaration"},
    {"old_id": "recu_s03", "verdict": "оставить", "reason": "Базовый случай рекурсии"},
    {"old_id": "recu_s04", "verdict": "удалить", "reason": "analyze SumTo"},
    # algorithms (section removed)
    {"old_id": "alg_s01", "verdict": "удалить", "reason": "Раздел «алгоритмы» — не Pascal-синтаксис"},
    {"old_id": "alg_s02", "verdict": "удалить", "reason": "analyze фильтрации"},
    {"old_id": "alg_s03", "verdict": "удалить", "reason": "Перевод fold/sum abs"},
    {"old_id": "alg_s04", "verdict": "изменить", "reason": "→ обмен через temp в Pascal vs Python swap"},
    {"old_id": "alg_s05", "verdict": "удалить", "reason": "analyze min/max"},
    {"old_id": "alg_s06", "verdict": "удалить", "reason": "analyze среднее"},
    {"old_id": "alg_s07", "verdict": "удалить", "reason": "analyze contains"},
    # data_structures (section reworked)
    {"old_id": "ds_s01", "verdict": "удалить", "reason": "Абстрактный стек без Pascal-типа"},
    {"old_id": "ds_s02", "verdict": "изменить", "reason": "→ record-узел, не «linked list»"},
    {"old_id": "ds_s03", "verdict": "удалить", "reason": "Дерево как алгоритм, не синтаксис"},
    {"old_id": "ds_s04", "verdict": "удалить", "reason": "Граф — алгоритмика"},
    {"old_id": "ds_s05", "verdict": "удалить", "reason": "Очередь — абстракция"},
    {"old_id": "ds_s06", "verdict": "удалить", "reason": "analyze глубины"},
    {"old_id": "ds_s07", "verdict": "удалить", "reason": "analyze стека"},
    {"old_id": "ds_s08", "verdict": "удалить", "reason": "analyze узла"},
    {"old_id": "ds_s09", "verdict": "изменить", "reason": "→ with record.field доступ"},
    {"old_id": "ds_s10", "verdict": "удалить", "reason": "Граф n+m"},
    {"old_id": "ds_s11", "verdict": "удалить", "reason": "analyze рёбер"},
    # oop
    {"old_id": "oop_s01", "verdict": "оставить", "reason": "Перевод class → Pascal OOP"},
    {"old_id": "oop_s02", "verdict": "удалить", "reason": "analyze площади"},
    {"old_id": "oop_s03", "verdict": "изменить", "reason": "Implement → method + Self/Result в классе"},
    {"old_id": "oop_s04", "verdict": "оставить", "reason": "inherited / override вызов"},
    {"old_id": "oop_s05", "verdict": "удалить", "reason": "Implement сумма полей"},
    {"old_id": "oop_s06", "verdict": "удалить", "reason": "analyze Sign.Eval"},
    {"old_id": "oop_s07", "verdict": "удалить", "reason": "analyze суммы полей"},
    {"old_id": "oop_s08", "verdict": "изменить", "reason": "Debug → property read/write"},
    {"old_id": "oop_s09", "verdict": "оставить", "reason": "Тело метода класса"},
    {"old_id": "oop_s10", "verdict": "удалить", "reason": "analyze наследования"},
    {"old_id": "oop_s11", "verdict": "удалить", "reason": "Capstone сумма координат"},
]

# Детали переработки (19 задач с verdict=изменить)
REWORK_DETAILS: dict[str, dict] = {
    "vai_s01": {
        "weak": "Echo числа — не учит каркас program/begin/end",
        "new": "psk_01: перевод каркаса program … begin … end из Python/C#",
        "feature": "program; begin; end.",
    },
    "vai_s02": {
        "weak": "Readln двух чисел и сложение — чистая арифметика",
        "new": "typ_01: перевод секции var x: integer из C#/Java",
        "feature": "var; явные типы; :=",
    },
    "vai_s08": {
        "weak": "analyze «что выведет» для div/mod",
        "new": "exp_01: MCQ — выбор фрагмента с div/mod vs /",
        "feature": "div; mod; целочисленное деление",
    },
    "cond_s03": {
        "weak": "implement else-if без акцента на then/begin",
        "new": "cnd_03 + cnd_04: перевод else if и код по блок-схеме",
        "feature": "if then else; begin/end в ветках",
    },
    "cond_s05": {
        "weak": "analyze тернарного оператора",
        "new": "cnd_05: перевод C# ? : → if then else",
        "feature": "нет тернарного; if then else",
    },
    "loop_s03": {
        "weak": "implement while без визуальной структуры",
        "new": "lop_04: код по блок-схеме while do",
        "feature": "while do; begin/end",
    },
    "loop_s04": {
        "weak": "analyze repeat until — предсказание итераций",
        "new": "lop_05: блок-схема по коду repeat until",
        "feature": "repeat until; post-test цикл",
    },
    "loop_s14": {
        "weak": "implement подсчёт гласных — алгоритмика",
        "new": "lop_10 + str_07: for char с Length, 1-based",
        "feature": "for char; Length; индекс 1..Length",
    },
    "arr_s03": {
        "weak": "debug подсчёта >0 — алгоритм, не синтаксис",
        "new": "arr_02 + arr_09: MCQ Low/High и debug границ",
        "feature": "array; Low; High; for to",
    },
    "str_s01": {
        "weak": "перевод без акцента на 1-based индекс",
        "new": "str_01: перевод Length(s) и s[i] для i:=1 to Length(s)",
        "feature": "string; Length; 1-based",
    },
    "str_s02": {
        "weak": "analyze «какой символ s[0]»",
        "new": "str_02: MCQ s[1] vs s[0] — первый символ",
        "feature": "string indexing 1-based",
    },
    "pp_s01": {
        "weak": "analyze Swap без var — предсказание",
        "new": "prc_06: сопоставление C# ref → var",
        "feature": "procedure; var parameter",
    },
    "mod_s03": {
        "weak": "implement функции без unit-контекста",
        "new": "unt_02 + unt_08: unit interface/implementation",
        "feature": "unit; interface; implementation",
    },
    "recu_s02": {
        "weak": "implement факториала — алгоритм",
        "new": "fn_05: перевод forward declaration",
        "feature": "forward; procedure/function",
    },
    "alg_s04": {
        "weak": "раздел algorithms удалён",
        "new": "xlg_10: перевод Python a,b=b,a → temp через var",
        "feature": "var; обмен без tuple swap",
    },
    "ds_s02": {
        "weak": "linked list как абстракция DS",
        "new": "rec_06: record-узел с указателем ^ и New/Dispose",
        "feature": "record; ^ pointer; new",
    },
    "ds_s09": {
        "weak": "implement обход дерева — алгоритм",
        "new": "rec_10: with Node.field — область видимости with",
        "feature": "with; record.field",
    },
    "oop_s03": {
        "weak": "implement Sum полей — алгоритм в классе",
        "new": "oop_16: перевод метода с Self и Result",
        "feature": "Self; method; Result in class",
    },
    "oop_s08": {
        "weak": "debug без фокуса на property",
        "new": "oop_07: перевод C# property → Pascal property read/write",
        "feature": "property; read; write",
    },
}

# --- New course v3: 200 tasks --------------------------------------------------

@dataclass(frozen=True)
class TaskSpec:
    slot_id: str
    chapter: str
    title: str
    format: str
    primary_action: str
    exercise_pattern: str
    goal: str
    pascal_features: str
    difficulty: str
    legacy_ref: str = ""  # old slot if reworked


def _t(
    slot_id: str,
    chapter: str,
    title: str,
    fmt: str,
    action: str,
    pattern: str,
    goal: str,
    features: str,
    diff: str,
    legacy: str = "",
) -> TaskSpec:
    return TaskSpec(slot_id, chapter, title, fmt, action, pattern, goal, features, diff, legacy)


def build_v3_tasks() -> list[TaskSpec]:
    tasks: list[TaskSpec] = []

    def add(chapter: str, items: list[tuple]):
        for item in items:
            tasks.append(_t(*item))

    # 1. Каркас программы (12)
    add("program_skeleton", [
        ("psk_01", "program_skeleton", "Каркас program … begin … end.", "перевод_программы", "translate", "tr_program_skeleton", "Узнать обязательную структуру Pascal-программы", "program; begin; end.; точка", "easy", "vai_s01"),
        ("psk_02", "program_skeleton", "Точка с запятой перед end", "исправление", "debug", "dbg_semicolon_end", "Типичная ошибка лишней ; перед end", "точка с запятой", "easy"),
        ("psk_03", "program_skeleton", "Соберите каркас из блоков", "сборка_программы", "assemble", "asm_program_skeleton", "Порядок program / var / begin / end", "program; begin; end", "easy"),
        ("psk_04", "program_skeleton", "Python if __name__ → Pascal program", "сопоставление", "translate", "match_entry_point", "Сопоставить точку входа языков", "program vs main", "easy"),
        ("psk_05", "program_skeleton", "Блок-схема → каркас program", "код_по_блок-схеме", "implement", "flow_skeleton_to_code", "Схема структуры → код", "begin/end", "easy"),
        ("psk_06", "program_skeleton", "Код → блок-схема каркаса", "блок-схема_по_коду", "implement", "flow_skeleton_from_code", "Чтение структуры программы", "program/begin/end", "easy"),
        ("psk_07", "program_skeleton", "Выберите верный program … end.", "выбор_фрагмента", "implement", "mcq_program_end", "Отличить валидный каркас", "end. vs end", "easy"),
        ("psk_08", "program_skeleton", "Uses в program vs implementation", "сопоставление", "translate", "match_uses_placement", "Где пишется uses", "uses clause", "medium"),
        ("psk_09", "program_skeleton", "Комментарии { } и (* *)", "перевод_фрагмента", "translate", "tr_comments", "Синтаксис комментариев Pascal", "комментарии", "easy"),
        ("psk_10", "program_skeleton", "Label и goto — найдите ошибку", "поиск_ошибки", "debug", "dbg_goto_label", "Устаревший, но читаемый синтаксис", "label; goto", "hard"),
        ("psk_11", "program_skeleton", "Разделы var / const / type", "сборка_фрагмента", "assemble", "asm_declaration_sections", "Порядок секций в program", "var; const; type", "medium"),
        ("psk_12", "program_skeleton", "C# Main → Pascal program", "перевод_программы", "translate", "tr_csharp_main", "Перенос точки входа", "program/begin/end", "easy"),
    ])

    # 2. Переменные и типы (10)
    add("typed_variables", [
        ("typ_01", "typed_variables", "var x: integer — перевод из C#", "перевод_фрагмента", "translate", "tr_var_section", "Явные типы в var", "var; integer", "easy", "vai_s02"),
        ("typ_02", "typed_variables", "Присваивание := vs =", "исправление", "debug", "dbg_assign_colon_eq", "Оператор :=", ":=", "easy", "vai_s03"),
        ("typ_03", "typed_variables", "Real vs Double / float", "сопоставление", "translate", "match_real_types", "Имена типов Pascal", "real; double", "easy"),
        ("typ_04", "typed_variables", "Boolean и сравнение", "перевод_фрагмента", "translate", "tr_boolean", "true/false в Pascal", "boolean", "easy"),
        ("typ_05", "typed_variables", "Char vs string[1]", "выбор_фрагмента", "implement", "mcq_char_string", "Символ vs строка", "char; string", "medium"),
        ("typ_06", "typed_variables", "Константы const", "сборка_фрагмента", "assemble", "asm_const", "const в program", "const", "easy"),
        ("typ_07", "typed_variables", "Диапазон 1..10 в типе", "перевод_фрагмента", "translate", "tr_subrange_type", "Subrange types", "1..N", "medium"),
        ("typ_08", "typed_variables", "Ord / Chr / Pred / Succ", "перевод_фрагмента", "translate", "tr_ord_chr", "Встроенные для ordinal", "ord; chr", "medium"),
        ("typ_09", "typed_variables", "Приведение типов trunc/round", "исправление", "debug", "dbg_trunc_round", "Целочисленное деление vs /", "div; trunc", "medium"),
        ("typ_10", "typed_variables", "Java int → Pascal integer", "сопоставление", "translate", "match_java_int", "Сопоставление типов", "integer", "easy"),
    ])

    # 3. Ввод-вывод (10)
    add("io", [
        ("io_01", "io", "Readln без второго параметра", "исправление", "debug", "dbg_readln", "Синтаксис Readln", "readln", "easy", "vai_s05"),
        ("io_02", "io", "Writeln с несколькими аргументами", "перевод_фрагмента", "translate", "tr_writeln_args", "Writeln(a, b)", "writeln", "easy"),
        ("io_03", "io", "Readln(x) vs Readln; x", "выбор_фрагмента", "implement", "mcq_readln_form", "Формы Readln", "readln", "easy"),
        ("io_04", "io", "Format / Write с форматом", "перевод_фрагмента", "translate", "tr_format", "Форматированный вывод", "format; write", "medium"),
        ("io_05", "io", "Val для разбора строки", "перевод_фрагмента", "translate", "tr_val", "Val vs int.Parse", "val", "medium"),
        ("io_06", "io", "Соберите Readln/Writeln", "сборка_фрагмента", "assemble", "asm_readln_writeln", "Порядок ввода-вывода", "readln; writeln", "easy", "fil_s03"),
        ("io_07", "io", "Python input/print → Pascal", "перевод_программы", "translate", "tr_python_io", "I/O mapping", "readln; writeln", "easy", "vai_s01"),
        ("io_08", "io", "Console.ReadLine → Readln", "сопоставление", "translate", "match_csharp_io", "C# I/O", "readln", "easy"),
        ("io_09", "io", "Порядок Writeln до Readln", "исправление", "debug", "dbg_io_order", "Логика I/O", "readln; writeln", "easy", "fil_s03"),
        ("io_10", "io", "Eof и Readln в цикле", "перевод_фрагмента", "translate", "tr_eof_readln", "Чтение до EOF stdin", "eof", "medium"),
    ])

    # 4. Операторы и выражения (10)
    add("expressions", [
        ("exp_01", "expressions", "div и mod vs / и %", "выбор_фрагмента", "implement", "mcq_div_mod", "Целочисленное деление Pascal", "div; mod", "easy", "vai_s08"),
        ("exp_02", "expressions", "Перевод a // b (Python) → div", "перевод_фрагмента", "translate", "tr_python_div", "Оператор // → div", "div", "easy"),
        ("exp_03", "expressions", "Shl / Shr / and / or / xor", "перевод_фрагмента", "translate", "tr_bitwise", "Битовые операторы", "shl; shr", "medium"),
        ("exp_04", "expressions", "In для множества/set", "перевод_фрагмента", "translate", "tr_set_in", "Set membership", "set of; in", "hard"),
        ("exp_05", "expressions", "Приоритет and/or vs C/Java &&", "сопоставление", "translate", "match_logic_ops", "Логические операторы", "and; or", "easy"),
        ("exp_06", "expressions", "Ошибка: mod от real", "поиск_ошибки", "debug", "dbg_mod_real", "mod только integer", "mod", "medium"),
        ("exp_07", "expressions", "Inc/Dec vs i := i + 1", "перевод_фрагмента", "translate", "tr_inc_dec", "Inc Dec", "inc; dec", "easy"),
        ("exp_08", "expressions", "Сборка выражения с div/mod", "сборка_фрагмента", "assemble", "asm_div_mod_expr", "Синтаксис выражения", "div; mod", "easy"),
        ("exp_09", "expressions", "Math.Pow → ** или Power", "сопоставление", "translate", "match_power", "Степень в Pascal", "**", "medium"),
        ("exp_10", "expressions", "Short-circuit? — and/or Pascal", "выбор_фрагмента", "implement", "mcq_short_circuit", "Особенность вычисления", "and; or", "hard"),
    ])

    # 5. Условия (14)
    add("conditions", [
        ("cnd_01", "conditions", "if then else — перевод Python", "перевод_программы", "translate", "tr_if_else", "Синтаксис if", "if then else", "easy", "cond_s01"),
        ("cnd_02", "conditions", "Соберите if/else из блоков", "сборка_программы", "assemble", "asm_if_blocks", "Блоки if", "if then else", "easy", "cond_s02"),
        ("cnd_03", "conditions", "else if → else if в Pascal", "перевод_фрагмента", "translate", "tr_elseif", "Цепочка условий", "else if", "easy", "cond_s03"),
        ("cnd_04", "conditions", "Код по блок-схеме else if", "код_по_блок-схеме", "implement", "flow_if_chain_code", "Схема → код", "if then else", "easy", "cond_s03"),
        ("cnd_05", "conditions", "switch → case of", "перевод_программы", "translate", "tr_case_of", "case of синтаксис", "case of", "medium", "cond_s04"),
        ("cnd_06", "conditions", "Тернарный ? : → if then else", "перевод_фрагмента", "translate", "tr_ternary_to_if", "Нет ? : в Pascal", "if then else", "medium", "cond_s05"),
        ("cnd_07", "conditions", "and vs or в условии", "исправление", "debug", "dbg_logic_and", "Логика условия", "and; or", "medium", "cond_s06"),
        ("cnd_08", "conditions", "Пропущенная ветка case", "исправление", "debug", "dbg_case_branch", "case of ветки", "case of", "medium", "cond_s09"),
        ("cnd_09", "conditions", "if-then-else для abs", "исправление", "debug", "dbg_if_abs", "Условное присваивание", "if then else", "medium", "cond_s10"),
        ("cnd_10", "conditions", "Сборка case of", "сборка_фрагмента", "assemble", "asm_case_of", "Структура case", "case of", "medium"),
        ("cnd_11", "conditions", "Блок-схема if → код", "код_по_блок-схеме", "implement", "flow_if_to_code", "Схема → Pascal", "if then else", "easy"),
        ("cnd_12", "conditions", "Код if → блок-схема", "блок-схема_по_коду", "implement", "flow_if_from_code", "Код → схема", "if then else", "easy"),
        ("cnd_13", "conditions", "Точка с запятой перед else", "поиск_ошибки", "debug", "dbg_semicolon_else", "Классическая ошибка Pascal", "else", "easy"),
        ("cnd_14", "conditions", "Java switch → case of", "сопоставление", "translate", "match_java_switch", "Сопоставление switch", "case of", "medium"),
    ])

    # 6. Циклы (16)
    add("loops", [
        ("lop_01", "loops", "for i := 1 to n do", "перевод_программы", "translate", "tr_for_to", "for/to/do", "for to do", "easy", "loop_s01"),
        ("lop_02", "loops", "Соберите for из блоков", "сборка_программы", "assemble", "asm_for_blocks", "for блоки", "for to do", "easy", "loop_s02"),
        ("lop_03", "loops", "for downto", "перевод_фрагмента", "translate", "tr_for_downto", "downto", "for downto", "easy"),
        ("lop_04", "loops", "while do — код по схеме", "код_по_блок-схеме", "implement", "flow_while_code", "while синтаксис", "while do", "easy", "loop_s03"),
        ("lop_05", "loops", "repeat until — схема по коду", "блок-схема_по_коду", "implement", "flow_repeat_from_code", "repeat until", "repeat until", "medium", "loop_s04"),
        ("lop_06", "loops", "repeat until — код по схеме", "код_по_блок-схеме", "implement", "flow_repeat_to_code", "until условие", "repeat until", "medium"),
        ("lop_07", "loops", "Неверное until в repeat", "исправление", "debug", "dbg_repeat_until", "Условие выхода", "repeat until", "medium", "loop_s13"),
        ("lop_08", "loops", "Break / Continue", "исправление", "debug", "dbg_break_continue", "Управление циклом", "break; continue", "medium", "loop_s05"),
        ("lop_09", "loops", "for char in string (Python) → for i", "перевод_программы", "translate", "tr_string_for", "Перебор строки", "for; length", "medium", "loop_s07"),
        ("lop_10", "loops", "for с char — Length и индекс", "перевод_фрагмента", "translate", "tr_for_char_index", "1-based индекс", "for; length", "medium", "loop_s14"),
        ("lop_11", "loops", "C# foreach → for", "сопоставление", "translate", "match_foreach", "Итерация", "for to do", "medium"),
        ("lop_12", "loops", "Вложенный for — синтаксис", "сборка_фрагмента", "assemble", "asm_nested_for", "begin/end во вложенном", "for; begin", "medium"),
        ("lop_13", "loops", "while vs repeat until — выбор", "выбор_фрагмента", "implement", "mcq_while_repeat", "Различие циклов", "while; repeat", "medium"),
        ("lop_14", "loops", "Ошибка: i := 1 to 10", "поиск_ошибки", "debug", "dbg_for_assign", "for не присваивание", "for to", "easy"),
        ("lop_15", "loops", "Exit из процедуры в цикле", "перевод_фрагмента", "translate", "tr_exit_loop", "exit vs break", "exit; break", "hard"),
        ("lop_16", "loops", "Java while → Pascal while", "перевод_фрагмента", "translate", "tr_java_while", "while do", "while do", "easy"),
    ])

    # 7. Функции (12)
    add("functions", [
        ("fn_01", "functions", "function … : integer", "перевод_фрагмента", "translate", "tr_function_decl", "Объявление function", "function", "easy", "fn_s02"),
        ("fn_02", "functions", "Result := …", "перевод_фрагмента", "translate", "tr_result", "Result vs return", "result", "easy"),
        ("fn_03", "functions", "Ошибка в function … : type", "исправление", "debug", "dbg_function_header", "Заголовок функции", "function", "medium", "fn_s04"),
        ("fn_04", "functions", "Result для нуля", "исправление", "debug", "dbg_result_zero", "Result в ветках", "result", "medium", "fn_s06"),
        ("fn_05", "functions", "Forward declaration", "перевод_фрагмента", "translate", "tr_forward", "forward", "forward", "hard", "recu_s02"),
        ("fn_06", "functions", "Соберите function/end", "сборка_фрагмента", "assemble", "asm_function_body", "begin/end function", "function; begin", "easy"),
        ("fn_07", "functions", "C# return → Result", "сопоставление", "translate", "match_return_result", "Возврат значения", "result", "easy"),
        ("fn_08", "functions", "Вложенные функции — нельзя", "поиск_ошибки", "debug", "dbg_nested_function", "Ограничение Pascal", "function", "hard"),
        ("fn_09", "functions", "Exit из function", "перевод_фрагмента", "translate", "tr_exit_function", "exit vs result", "exit; result", "medium"),
        ("fn_10", "functions", "Inline (если доступно) — выбор", "выбор_фрагмента", "implement", "mcq_inline", "inline hint", "inline", "hard"),
        ("fn_11", "functions", "Java static int f → function", "перевод_фрагмента", "translate", "tr_java_function", "Статическая функция", "function", "easy"),
        ("fn_12", "functions", "Recursive function — перевод", "перевод_программы", "translate", "tr_recursive_fn", "Рекурсивная function", "function", "medium", "recu_s01"),
    ])

    # 8. Процедуры и параметры (12)
    add("procedures", [
        ("prc_01", "procedures", "procedure без Result", "перевод_фрагмента", "translate", "tr_procedure", "procedure vs function", "procedure", "easy"),
        ("prc_02", "procedures", "var-параметр Swap", "исправление", "debug", "dbg_var_param", "var передача", "var", "medium", "pp_s02"),
        ("prc_03", "procedures", "const-параметр", "перевод_фрагмента", "translate", "tr_const_param", "const в параметрах", "const", "medium"),
        ("prc_04", "procedures", "Open array parameter", "перевод_фрагмента", "translate", "tr_open_array", "array of T", "array of", "hard"),
        ("prc_05", "procedures", "Default parameters — нет в classic", "выбор_фрагмента", "implement", "mcq_no_default", "Отличие от C#", "procedure", "medium"),
        ("prc_06", "procedures", "C# ref → var", "сопоставление", "translate", "match_ref_var", "ref/out mapping", "var", "medium", "pp_s01"),
        ("prc_07", "procedures", "Соберите procedure с var", "сборка_фрагмента", "assemble", "asm_proc_var", "var в заголовке", "var", "medium"),
        ("prc_08", "procedures", "Out-параметр через var + локальная", "перевод_фрагмента", "translate", "tr_out_pattern", "Имитация out", "var", "hard"),
        ("prc_09", "procedures", "Procedure внутри program", "исправление", "debug", "dbg_proc_placement", "Объявление до begin", "procedure", "easy"),
        ("prc_10", "procedures", "Nested procedure (FPC/Delphi)", "перевод_фрагмента", "translate", "tr_nested_proc", "Вложенная procedure", "procedure", "hard"),
        ("prc_11", "procedures", "Python def без return → procedure", "сопоставление", "translate", "match_def_procedure", "def mapping", "procedure", "easy"),
        ("prc_12", "procedures", "Value vs var — найдите ошибку", "поиск_ошибки", "debug", "dbg_value_vs_var", "Семантика параметров", "var", "medium"),
    ])

    # 9. Статические массивы (10)
    add("static_arrays", [
        ("arr_01", "static_arrays", "array[1..N] of integer", "перевод_фрагмента", "translate", "tr_static_array", "Статический массив", "array of; 1..", "easy"),
        ("arr_02", "static_arrays", "Low/High/Length массива", "выбор_фрагмента", "implement", "mcq_low_high", "Границы массива", "low; high", "medium", "arr_s03"),
        ("arr_03", "static_arrays", "Индекс 0 vs 1", "исправление", "debug", "dbg_array_index", "1-based индекс", "array", "easy"),
        ("arr_04", "static_arrays", "for i := Low to High", "перевод_фрагмента", "translate", "tr_for_low_high", "Обход массива", "low; high", "easy"),
        ("arr_05", "static_arrays", "Многомерный array", "перевод_фрагмента", "translate", "tr_multidim_array", "array[x..y, a..b]", "array", "medium"),
        ("arr_06", "static_arrays", "Сборка объявления array", "сборка_фрагмента", "assemble", "asm_array_decl", "Синтаксис array", "array", "easy"),
        ("arr_07", "static_arrays", "C# int[] → array", "сопоставление", "translate", "match_csharp_array", "Массив C#", "array", "easy"),
        ("arr_08", "static_arrays", "Copy/Fill для array", "перевод_фрагмента", "translate", "tr_array_copy", "Copy функция", "copy", "medium"),
        ("arr_09", "static_arrays", "Static array bounds error", "поиск_ошибки", "debug", "dbg_bounds", "Выход за границы", "array", "medium", "arr_s03"),
        ("arr_10", "static_arrays", "Set of char vs array of char", "сопоставление", "translate", "match_set_array", "Set vs array", "set of", "hard"),
    ])

    # 10. Динамические массивы (10)
    add("dynamic_arrays", [
        ("dyn_01", "dynamic_arrays", "dynamic array + SetLength", "перевод_фрагмента", "translate", "tr_setlength", "SetLength", "setlength", "medium"),
        ("dyn_02", "dynamic_arrays", "Length после SetLength", "исправление", "debug", "dbg_setlength", "SetLength(n)", "setlength; length", "medium"),
        ("dyn_03", "dynamic_arrays", "List<T> → dynamic array", "сопоставление", "translate", "match_list_dynamic", "C# List", "setlength", "medium"),
        ("dyn_04", "dynamic_arrays", "Append через SetLength+1", "перевод_фрагмента", "translate", "tr_dyn_append", "Рост массива", "setlength", "medium"),
        ("dyn_05", "dynamic_arrays", "Сборка SetLength блоков", "сборка_фрагмента", "assemble", "asm_setlength", "SetLength синтаксис", "setlength", "easy"),
        ("dyn_06", "dynamic_arrays", "new int[n] → SetLength", "перевод_фрагмента", "translate", "tr_java_new_array", "Java массив", "setlength", "medium"),
        ("dyn_07", "dynamic_arrays", "Finalize dynamic array", "перевод_фрагмента", "translate", "tr_finalize", "Управление памятью", "finalize", "hard"),
        ("dyn_08", "dynamic_arrays", "Copy для dynamic", "перевод_фрагмента", "translate", "tr_dyn_copy", "Copy dynamic", "copy", "medium"),
        ("dyn_09", "dynamic_arrays", "Ошибка: array[0..n]", "поиск_ошибки", "debug", "dbg_dyn_decl", "Dynamic vs static decl", "array", "medium"),
        ("dyn_10", "dynamic_arrays", "Python list.append → SetLength", "сопоставление", "translate", "match_python_list", "list mapping", "setlength", "medium"),
    ])

    # 11. Строки (10)
    add("strings", [
        ("str_01", "strings", "string и Length(s)", "перевод_фрагмента", "translate", "tr_string_length", "Length", "string; length", "easy", "str_s01"),
        ("str_02", "strings", "s[1] vs s[0] — выбор", "выбор_фрагмента", "implement", "mcq_string_index", "1-based string", "string index", "easy", "str_s02"),
        ("str_03", "strings", "Последний символ s[Length(s)]", "исправление", "debug", "dbg_last_char", "Length индекс", "length", "medium", "str_s03"),
        ("str_04", "strings", "Copy(s, i, count)", "перевод_фрагмента", "translate", "tr_copy", "Substring → Copy", "copy", "medium"),
        ("str_05", "strings", "Concat / + для string", "сопоставление", "translate", "match_string_concat", "Конкатенация", "concat", "easy"),
        ("str_06", "strings", "AnsiString vs UnicodeString", "выбор_фрагмента", "implement", "mcq_ansistring", "Типы строк Delphi", "string", "hard"),
        ("str_07", "strings", "char in string loop", "перевод_фрагмента", "translate", "tr_string_char_loop", "for i := 1 to Length", "for; length", "medium", "loop_s14"),
        ("str_08", "strings", "Insert/Delete для string", "перевод_фрагмента", "translate", "tr_insert_delete", "Insert Delete", "insert; delete", "medium"),
        ("str_09", "strings", "Java charAt → s[i]", "сопоставление", "translate", "match_charat", "charAt mapping", "string", "easy"),
        ("str_10", "strings", "Trim / TrimLeft", "перевод_фрагмента", "translate", "tr_trim", "Trim функции", "trim", "easy"),
    ])

    # 12. Records (10)
    add("records", [
        ("rec_01", "records", "record с полями", "перевод_программы", "translate", "tr_record", "record syntax", "record", "medium", "rec_s01"),
        ("rec_02", "records", "with r do field", "перевод_фрагмента", "translate", "tr_with_record", "with statement", "with", "medium"),
        ("rec_03", "records", "Обмен полей record", "исправление", "debug", "dbg_record_swap", "Поля record", "record", "medium", "rec_s03"),
        ("rec_04", "records", "C# struct → record", "сопоставление", "translate", "match_struct_record", "struct mapping", "record", "medium"),
        ("rec_05", "records", "Variant record (case)", "перевод_фрагмента", "translate", "tr_variant_record", "case in record", "case", "hard"),
        ("rec_06", "records", "Указатель ^ на record", "перевод_фрагмента", "translate", "tr_record_ptr", "New/Dispose", "new; dispose", "hard", "ds_s02"),
        ("rec_07", "records", "Сборка record/end", "сборка_фрагмента", "assemble", "asm_record", "record/end", "record", "easy"),
        ("rec_08", "records", "Packed record", "выбор_фрагмента", "implement", "mcq_packed", "packed", "packed", "hard"),
        ("rec_09", "records", "Python dataclass → record", "сопоставление", "translate", "match_dataclass", "dataclass", "record", "medium"),
        ("rec_10", "records", "with — область видимости", "поиск_ошибки", "debug", "dbg_with_scope", "with end", "with", "medium", "ds_s09"),
    ])

    # 13. Файлы (8)
    add("files", [
        ("fil_01", "files", "Assign/Reset/Readln file", "перевод_фрагмента", "translate", "tr_textfile_read", "TextFile чтение", "assign; reset", "medium"),
        ("fil_02", "files", "Rewrite/WriteLn file", "перевод_фрагмента", "translate", "tr_textfile_write", "Запись файла", "rewrite; writeln", "medium"),
        ("fil_03", "files", "CloseFile после работы", "исправление", "debug", "dbg_closefile", "CloseFile", "closefile", "medium"),
        ("fil_04", "files", "Eof(f) цикл чтения", "перевод_фрагмента", "translate", "tr_eof_file", "Eof для файла", "eof", "medium"),
        ("fil_05", "files", "C# StreamReader → TextFile", "сопоставление", "translate", "match_streamreader", "File I/O mapping", "textfile", "medium"),
        ("fil_06", "files", "Append vs Rewrite", "выбор_фрагмента", "implement", "mcq_rewrite_append", "Rewrite/Append", "rewrite", "medium"),
        ("fil_07", "files", "Reset без Assign", "поиск_ошибки", "debug", "dbg_assign_reset", "Assign обязателен", "assign", "easy"),
        ("fil_08", "files", "Сборка блоков TextFile", "сборка_фрагмента", "assemble", "asm_textfile", "Assign/Reset/Readln", "textfile", "medium"),
    ])

    # 14. Units (12)
    add("units", [
        ("unt_01", "units", "import → uses", "перевод_фрагмента", "translate", "tr_uses", "uses clause", "uses", "medium", "mod_s01"),
        ("unt_02", "units", "unit interface / implementation", "перевод_фрагмента", "translate", "tr_unit_sections", "Структура unit", "interface; implementation", "medium", "mod_s03"),
        ("unt_03", "units", "Ошибка uses в implementation", "исправление", "debug", "dbg_uses_access", "Видимость uses", "uses", "medium", "mod_s04"),
        ("unt_04", "units", "Экспорт procedure из unit", "перевод_фрагмента", "translate", "tr_unit_export", "interface exports", "interface", "medium"),
        ("unt_05", "units", "initialization/finalization", "перевод_фрагмента", "translate", "tr_unit_init", "Unit init", "initialization", "hard"),
        ("unt_06", "units", "Circular uses — найдите", "поиск_ошибки", "debug", "dbg_circular_uses", "Циклические uses", "uses", "hard"),
        ("unt_07", "units", "Python module → unit", "сопоставление", "translate", "match_python_module", "module mapping", "unit", "medium"),
        ("unt_08", "units", "Сборка unit interface", "сборка_фрагмента", "assemble", "asm_unit_interface", "interface section", "interface", "medium"),
        ("unt_09", "units", "Неверное имя после uses", "исправление", "debug", "dbg_wrong_symbol", "Uses symbol", "uses", "easy", "mod_s08"),
        ("unt_10", "units", "SysUtils в uses", "выбор_фрагмента", "implement", "mcq_sysutils", "Стандартные units", "uses", "easy"),
        ("unt_11", "units", "C# namespace → unit", "сопоставление", "translate", "match_namespace_unit", "namespace", "unit", "medium"),
        ("unt_12", "units", "Forward в interface", "перевод_фрагмента", "translate", "tr_interface_forward", "Forward in interface", "forward", "hard"),
    ])

    # 15. Рекурсия (8)
    add("recursion", [
        ("rcu_01", "recursion", "factorial — перевод", "перевод_программы", "translate", "tr_factorial", "Recursive function", "function", "medium", "recu_s01"),
        ("rcu_02", "recursion", "Базовый случай — исправление", "исправление", "debug", "dbg_rec_base", "Base case", "function", "medium", "recu_s03"),
        ("rcu_03", "recursion", "Forward + recursive", "сборка_фрагмента", "assemble", "asm_forward_rec", "forward decl", "forward", "hard", "recu_s02"),
        ("rcu_04", "recursion", "Python recursion → Pascal", "сопоставление", "translate", "match_python_rec", "def recursive", "function", "medium"),
        ("rcu_05", "recursion", "Stack overflow pattern — debug", "поиск_ошибки", "debug", "dbg_infinite_rec", "Бесконечная рекурсия", "function", "medium"),
        ("rcu_06", "recursion", "Tail recursion — перевод", "перевод_фрагмента", "translate", "tr_tail_rec", "Хвостовая рекурсия", "function", "hard"),
        ("rcu_07", "recursion", "Mutual recursion forward", "перевод_фрагмента", "translate", "tr_mutual_forward", "Взаимная рекурсия", "forward", "hard"),
        ("rcu_08", "recursion", "Блок-схема recursion → код", "код_по_блок-схеме", "implement", "flow_recursion_code", "Схема → function", "function", "medium"),
    ])

    # 16. ООП (16)
    add("oop", [
        ("oop_01", "oop", "class → Pascal OOP", "перевод_программы", "translate", "tr_class", "class syntax", "class", "medium", "oop_s01"),
        ("oop_02", "oop", "constructor Create", "перевод_фрагмента", "translate", "tr_constructor", "constructor", "constructor", "medium"),
        ("oop_03", "oop", "destructor Destroy", "перевод_фрагмента", "translate", "tr_destructor", "destructor", "destructor", "medium"),
        ("oop_04", "oop", "inherited вызов", "исправление", "debug", "dbg_inherited", "inherited", "inherited", "medium", "oop_s04"),
        ("oop_05", "oop", "virtual / override", "перевод_фрагмента", "translate", "tr_virtual_override", "virtual override", "virtual; override", "hard"),
        ("oop_06", "oop", "abstract class", "перевод_фрагмента", "translate", "tr_abstract", "abstract", "abstract", "hard"),
        ("oop_07", "oop", "property read/write", "перевод_фрагмента", "translate", "tr_property", "property", "property", "medium", "oop_s08"),
        ("oop_08", "oop", "Self vs this", "сопоставление", "translate", "match_self_this", "Self", "self", "easy"),
        ("oop_09", "oop", "Тело метода — исправление", "исправление", "debug", "dbg_method_body", "method body", "class", "medium", "oop_s09"),
        ("oop_10", "oop", "C# class → Pascal class", "сопоставление", "translate", "match_csharp_class", "class mapping", "class", "medium"),
        ("oop_11", "oop", "override без virtual", "поиск_ошибки", "debug", "dbg_override_virtual", "override требует virtual", "override", "medium"),
        ("oop_12", "oop", "object vs class (legacy)", "выбор_фрагмента", "implement", "mcq_object_class", "object type", "object; class", "hard"),
        ("oop_13", "oop", "Сборка class/end", "сборка_фрагмента", "assemble", "asm_class", "class structure", "class", "easy"),
        ("oop_14", "oop", "interface in Pascal", "перевод_фрагмента", "translate", "tr_interface_oop", "interface type", "interface", "hard"),
        ("oop_15", "oop", "Java extends → class(TBase)", "сопоставление", "translate", "match_java_extends", "inheritance syntax", "class", "medium"),
        ("oop_16", "oop", "Method + Self — перевод", "перевод_фрагмента", "translate", "tr_method_self", "method dispatch", "self", "medium", "oop_s03"),
    ])

    # 17. Типичные ошибки Pascal (10)
    add("pascal_pitfalls", [
        ("pit_01", "pascal_pitfalls", "Точка с запятой перед else", "исправление", "debug", "dbg_pit_else", "else semicolon myth", "else", "easy", "cnd_13"),
        ("pit_02", "pascal_pitfalls", "Присваивание := vs =", "исправление", "debug", "dbg_pit_assign", ":= vs =", ":=", "easy", "typ_02"),
        ("pit_03", "pascal_pitfalls", "String index 0", "исправление", "debug", "dbg_pit_string0", "1-based strings", "string", "easy", "str_02"),
        ("pit_04", "pascal_pitfalls", "For loop variable mutation", "поиск_ошибки", "debug", "dbg_pit_for_var", "for var read-only", "for to", "medium"),
        ("pit_05", "pascal_pitfalls", "case без else — выбор", "выбор_фрагмента", "implement", "mcq_case_else", "case else", "case of", "medium"),
        ("pit_06", "pascal_pitfalls", "Writeln без writeln", "исправление", "debug", "dbg_pit_writeln_case", "Writeln case", "writeln", "easy"),
        ("pit_07", "pascal_pitfalls", "Unit name ≠ file name", "поиск_ошибки", "debug", "dbg_pit_unit_name", "unit file", "unit", "medium"),
        ("pit_08", "pascal_pitfalls", "Result до присваивания", "исправление", "debug", "dbg_pit_result", "Result undefined", "result", "medium"),
        ("pit_09", "pascal_pitfalls", "SetLength в цикле perf", "выбор_фрагмента", "implement", "mcq_setlength_loop", "SetLength anti-pattern", "setlength", "medium"),
        ("pit_10", "pascal_pitfalls", "with — двойное применение", "исправление", "debug", "dbg_pit_with", "with nesting", "with", "medium"),
    ])

    # 18. Сопоставление языков (10)
    add("cross_language", [
        ("xlg_01", "cross_language", "Python list comp → for", "сопоставление", "translate", "match_list_comp", "Comprehension", "for to", "medium"),
        ("xlg_02", "cross_language", "C# properties → property", "сопоставление", "translate", "match_csharp_property", "property", "property", "medium"),
        ("xlg_03", "cross_language", "Java interface → Pascal interface", "сопоставление", "translate", "match_java_interface", "interface", "interface", "hard"),
        ("xlg_04", "cross_language", "Python None → nil", "сопоставление", "translate", "match_nil", "nil pointer", "nil", "medium"),
        ("xlg_05", "cross_language", "C# event → ?", "выбор_фрагмента", "implement", "mcq_no_events", "Нет events в classic", "class", "hard"),
        ("xlg_06", "cross_language", "Python with → with record", "сопоставление", "translate", "match_python_with", "with mapping", "with", "medium"),
        ("xlg_07", "cross_language", "Java package → unit", "сопоставление", "translate", "match_java_package", "package", "unit", "medium"),
        ("xlg_08", "cross_language", "C# lambda → anonymous proc", "перевод_фрагмента", "translate", "tr_anonymous", "Procedural type", "procedure of", "hard"),
        ("xlg_09", "cross_language", "Python pass → ; empty", "сопоставление", "translate", "match_empty_stmt", "Empty statement", "begin end", "easy"),
        ("xlg_10", "cross_language", "Swap tuple Python → temp", "перевод_фрагмента", "translate", "tr_swap_temp", "a,b=b,a нет", "var temp", "easy", "alg_s04"),
    ])

    assert 150 <= len(tasks) <= 200, len(tasks)
    return tasks


CHAPTER_TITLES = {
    "program_skeleton": "1. Каркас программы",
    "typed_variables": "2. Переменные и типы",
    "io": "3. Ввод-вывод",
    "expressions": "4. Операторы и выражения",
    "conditions": "5. Условия",
    "loops": "6. Циклы",
    "functions": "7. Функции",
    "procedures": "8. Процедуры и параметры",
    "static_arrays": "9. Статические массивы",
    "dynamic_arrays": "10. Динамические массивы",
    "strings": "11. Строки",
    "records": "12. Записи (record)",
    "files": "13. Файлы",
    "units": "14. Модули (unit)",
    "recursion": "15. Рекурсия",
    "oop": "16. ООП",
    "pascal_pitfalls": "17. Типичные ошибки Pascal",
    "cross_language": "18. Сопоставление Python/C#/Java",
}


def write_audit_csv(path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["old_slot_id", "verdict", "reason"], delimiter=";")
        w.writeheader()
        w.writerows(
            {"old_slot_id": r["old_id"], "verdict": r["verdict"], "reason": r["reason"]} for r in AUDIT_102
        )


def write_tasks_csv(path: Path, tasks: list[TaskSpec]) -> None:
    fields = [
        "slot_id",
        "chapter_key",
        "chapter_title",
        "title",
        "task_format",
        "primary_action",
        "exercise_pattern_id",
        "educational_goal",
        "pascal_features",
        "difficulty",
        "legacy_slot_id",
        "collection_key",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter=";")
        w.writeheader()
        for t in tasks:
            w.writerow(
                {
                    "slot_id": t.slot_id,
                    "chapter_key": t.chapter,
                    "chapter_title": CHAPTER_TITLES[t.chapter],
                    "title": t.title,
                    "task_format": t.format,
                    "primary_action": t.primary_action,
                    "exercise_pattern_id": t.exercise_pattern,
                    "educational_goal": t.goal,
                    "pascal_features": t.pascal_features,
                    "difficulty": t.difficulty,
                    "legacy_slot_id": t.legacy_ref,
                    "collection_key": t.chapter,
                }
            )


def write_markdown(path: Path, tasks: list[TaskSpec]) -> None:
    lines: list[str] = []
    lines.append("# Pascal Course v3 — спецификация курса\n")
    lines.append("> Целевая аудитория: программисты, знающие Python/C#/Java. ")
    lines.append("> Фокус: синтаксис и особенности Pascal, не алгоритмика.\n")

    # Summary stats
    verdict_counts = {}
    for r in AUDIT_102:
        verdict_counts[r["verdict"]] = verdict_counts.get(r["verdict"], 0) + 1
    lines.append("## Сводка аудита v2 (102 задачи)\n")
    lines.append(f"- **Оставить без существенных изменений:** {verdict_counts.get('оставить', 0)}")
    lines.append(f"- **Изменить:** {verdict_counts.get('изменить', 0)}")
    lines.append(f"- **Удалить:** {verdict_counts.get('удалить', 0)}")
    lines.append(f"- **Новый курс v3:** {len(tasks)} задач\n")

    lines.append("## Новая структура курса\n")
    lines.append("| № | Раздел (chapter_key) | Задач |")
    lines.append("|---|----------------------|-------|")
    for i, (key, title) in enumerate(CHAPTER_TITLES.items(), 1):
        count = sum(1 for t in tasks if t.chapter == key)
        lines.append(f"| {i} | {title} (`{key}`) | {count} |")
    lines.append(f"| | **Итого** | **{len(tasks)}** |\n")

    lines.append("## Форматы заданий (маппинг)\n")
    lines.append("| task_format | primary_action | builder (рекомендация) |")
    lines.append("|-------------|----------------|------------------------|")
    fmt_map = {
        "перевод_программы": ("translate", "translation_to_pascal"),
        "перевод_фрагмента": ("translate", "translation_snippet_to_pascal"),
        "исправление": ("debug", "pascal_debug_starter"),
        "поиск_ошибки": ("debug", "pascal_debug_starter"),
        "сборка_программы": ("assemble", "block_reorder_pascal"),
        "сборка_фрагмента": ("assemble", "block_reorder_pascal"),
        "код_по_блок-схеме": ("implement", "flowchart_to_code"),
        "блок-схема_по_коду": ("implement", "code_to_flowchart"),
        "выбор_фрагмента": ("implement", "mcq_pascal_fragment"),
        "сопоставление": ("translate", "lang_construction_match"),
    }
    for fmt, (act, bld) in fmt_map.items():
        lines.append(f"| {fmt} | {act} | {bld} |")
    lines.append("\n> **Запрещено:** `primary_action=analyze` (предсказание вывода), кроме MCQ на уникальную особенность Pascal.\n")

    lines.append("## Аудит существующих 102 задач\n")
    lines.append("| old_slot_id | Вердикт | Причина |")
    lines.append("|-------------|---------|---------|")
    for r in AUDIT_102:
        lines.append(f"| `{r['old_id']}` | {r['verdict']} | {r['reason']} |")
    lines.append("")

    deleted = [r for r in AUDIT_102 if r["verdict"] == "удалить"]
    lines.append(f"## Удалённые задачи ({len(deleted)})\n")
    for r in deleted:
        lines.append(f"- `{r['old_id']}` — {r['reason']}")
    lines.append("")

    changed = [r for r in AUDIT_102 if r["verdict"] == "изменить"]
    lines.append(f"## Переработанные задачи ({len(changed)})\n")
    for r in changed:
        legacy = r["old_id"]
        detail = REWORK_DETAILS.get(legacy, {})
        new = [t for t in tasks if t.legacy_ref == legacy]
        new_ids = ", ".join(f"`{t.slot_id}`" for t in new) or detail.get("new", "→ см. раздел v3")
        lines.append(f"### `{legacy}`\n")
        lines.append(f"- **Проблема v2:** {detail.get('weak', r['reason'])}")
        lines.append(f"- **Новая версия:** {new_ids} — {detail.get('new', r['reason'])}")
        lines.append(f"- **Особенность Pascal:** {detail.get('feature', '—')}")
        lines.append("")

    lines.append("## Полный каталог задач v3\n")
    current_ch = None
    for t in tasks:
        if t.chapter != current_ch:
            current_ch = t.chapter
            lines.append(f"\n### {CHAPTER_TITLES[t.chapter]}\n")
        lines.append(f"#### `{t.slot_id}` — {t.title}\n")
        lines.append(f"- **Формат:** {t.format}")
        lines.append(f"- **primary_action:** `{t.primary_action}` · **pattern:** `{t.exercise_pattern}`")
        lines.append(f"- **Цель:** {t.goal}")
        lines.append(f"- **Pascal:** {t.pascal_features}")
        lines.append(f"- **Сложность:** {t.difficulty}")
        if t.legacy_ref:
            lines.append(f"- **Наследие v2:** `{t.legacy_ref}`")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def write_json(path: Path, tasks: list[TaskSpec]) -> None:
    payload = {
        "version": 3,
        "total_tasks": len(tasks),
        "chapters": [
            {"key": k, "title": CHAPTER_TITLES[k], "count": sum(1 for t in tasks if t.chapter == k)}
            for k in CHAPTER_TITLES
        ],
        "audit_102": AUDIT_102,
        "rework_details": REWORK_DETAILS,
        "tasks": [
            {
                "slot_id": t.slot_id,
                "chapter_key": t.chapter,
                "title": t.title,
                "task_format": t.format,
                "primary_action": t.primary_action,
                "exercise_pattern_id": t.exercise_pattern,
                "educational_goal": t.goal,
                "pascal_features": t.pascal_features,
                "difficulty": t.difficulty,
                "legacy_slot_id": t.legacy_ref or None,
            }
            for t in tasks
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    tasks = build_v3_tasks()
    write_audit_csv(DOCS / "PASCAL_COURSE_V3_AUDIT_102.csv")
    write_tasks_csv(DOCS / "PASCAL_COURSE_V3_TASKS.csv", tasks)
    write_markdown(DOCS / "PASCAL_COURSE_V3_SPEC.md", tasks)
    write_json(DOCS / "PASCAL_COURSE_V3_TASKS.json", tasks)
    print(f"Generated {len(tasks)} tasks in {DOCS}")


if __name__ == "__main__":
    main()
