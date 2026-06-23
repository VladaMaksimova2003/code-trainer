"""Validate user Pascal code against per-task expected_concept_ids."""

from __future__ import annotations

import re
from typing import Callable

from application.curriculum.display.pascal_tc_pedagogy import PEDAGOGY_CARDS

ConceptCheck = tuple[str, Callable[[str], bool]]

# Regex/heuristic checks aligned with student UI highlighting.
_CONCEPT_CHECKS: dict[str, ConceptCheck] = {
    "program_entry": (
        "Точка входа программы",
        lambda code: bool(re.search(r"\b(program|begin)\b", code, re.I)),
    ),
    "block_scope": (
        "Блок begin/end",
        lambda code: bool(re.search(r"\bbegin\b", code, re.I)),
    ),
    "typed_declaration": (
        "Объявление переменных",
        lambda code: bool(
            re.search(r"\b(var|const|type)\b", code, re.I)
            or re.search(
                r":\s*(integer|real|extended|double|boolean|char|string|byte|word|longint|single)",
                code,
                re.I,
            )
        ),
    ),
    "assignment": (
        "Присваивание",
        lambda code: ":=" in code,
    ),
    "arithmetic_ops": (
        "Арифметика",
        lambda code: bool(
            re.search(r"\b(div|mod)\b", code, re.I) or re.search(r"[+\-*/]", code)
        ),
    ),
    "stdin_read": (
        "Ввод с клавиатуры",
        lambda code: bool(re.search(r"\b(readln|read)\s*\(", code, re.I)),
    ),
    "stdout_write": (
        "Вывод на экран",
        lambda code: bool(re.search(r"\b(writeln|write)\b", code, re.I)),
    ),
    "simple_branch": (
        "Условие if",
        lambda code: bool(re.search(r"\bif\b.+\bthen\b", code, re.I | re.S)),
    ),
    "multi_branch": (
        "Цепочка условий",
        lambda code: bool(re.search(r"\belse\s+if\b|\belseif\b", code, re.I)),
    ),
    "switch_selection": (
        "Выбор case",
        lambda code: bool(re.search(r"\bcase\b.+\bof\b", code, re.I | re.S)),
    ),
    "conditional_expression": (
        "Условие в выражении",
        lambda code: bool(re.search(r"\bif\b.+\bthen\b.+\belse\b", code, re.I | re.S)),
    ),
    "counted_loop": (
        "Счётный цикл for",
        lambda code: bool(re.search(r"\bfor\s+\w+\s*:=", code, re.I)),
    ),
    "pre_condition_loop": (
        "Цикл while",
        lambda code: bool(re.search(r"\bwhile\b", code, re.I)),
    ),
    "post_condition_loop": (
        "Цикл repeat/until",
        lambda code: bool(re.search(r"\brepeat\b", code, re.I)),
    ),
    "loop_control": (
        "Управление циклом",
        lambda code: bool(re.search(r"\b(break|continue|exit)\b", code, re.I)),
    ),
    "nested_iteration": (
        "Вложенные циклы",
        lambda code: len(re.findall(r"\b(for|while|repeat)\b", code, re.I)) >= 2,
    ),
    "collection_iteration": (
        "Обход коллекции",
        lambda code: bool(re.search(r"\bfor\b.+\b(array|downto|to)\b", code, re.I | re.S)),
    ),
    "function_definition": (
        "Функция",
        lambda code: bool(re.search(r"\bfunction\s+\w+", code, re.I)),
    ),
    "parameter_passing": (
        "Параметры процедуры",
        lambda code: bool(re.search(r"\bprocedure\s+\w+\s*\(", code, re.I)),
    ),
    "return_flow": (
        "Возврат из функции",
        lambda code: bool(re.search(r"\bResult\s*:=", code, re.I)),
    ),
    "function_invocation": (
        "Вызов функции",
        lambda code: bool(re.search(r"\w+\s*\([^)]*\)", code)),
    ),
    "indexed_sequence": (
        "Массив",
        lambda code: bool(re.search(r"\barray\b|\[\s*\d", code, re.I)),
    ),
    "dynamic_array": (
        "Динамический массив",
        lambda code: bool(re.search(r"\bSetLength\b|\barray\s+of\b", code, re.I)),
    ),
    "string_sequence": (
        "Строки",
        lambda code: bool(re.search(r"\b(string|Length|Copy|Pos)\b", code, re.I)),
    ),
    "key_value_map": (
        "Запись (record)",
        lambda code: bool(re.search(r"\brecord\b|\.\w+\s*:=", code, re.I)),
    ),
    "file_read": (
        "Чтение файла",
        lambda code: bool(re.search(r"\b(Assign|Reset|Rewrite|CloseFile)\b", code, re.I)),
    ),
    "import_dependency": (
        "Подключение unit",
        lambda code: bool(re.search(r"\buses\b", code, re.I)),
    ),
    "recursion": (
        "Рекурсия",
        lambda code: bool(re.search(r"\bfunction\s+(\w+)[\s\S]*?\1\s*\(", code, re.I)),
    ),
    "class_type": (
        "Класс",
        lambda code: bool(re.search(r"\btype\s+\w+\s*=\s*class\b|\bclass\b", code, re.I)),
    ),
    "object_instance": (
        "Объект",
        lambda code: bool(re.search(r"\.Create\b|\bobject\b", code, re.I)),
    ),
    "method_dispatch": (
        "Метод",
        lambda code: bool(re.search(r"\bprocedure\s+\w+\.\w+|\bfunction\s+\w+\.\w+", code, re.I)),
    ),
    "inheritance_hierarchy": (
        "Наследование",
        lambda code: bool(re.search(r"\bclass\s*\(\s*\w+\s*\)", code, re.I)),
    ),
    "pascal_comment": (
        "Комментарии",
        lambda code: bool(re.search(r"\{|\(\*", code)),
    ),
    "search_find": (
        "Поиск",
        lambda code: bool(
            re.search(r"\b(in|find|pos|index)\b", code, re.I)
            or (
                re.search(r"\bif\b", code, re.I)
                and re.search(r"\bfor\b", code, re.I)
                and re.search(r"(==|!=|<=|>=|<|>|=|:=)", code)
            )
        ),
    ),
    "filter_select": (
        "Фильтрация",
        lambda code: bool(re.search(r"\bif\b", code, re.I) and re.search(r"\bfor\b", code, re.I)),
    ),
    "fold_aggregate": (
        "Накопление",
        lambda code: bool(
            re.search(r":=\s*\w+\s*[+\-]", code)
            or re.search(r"\b(\+=|-=)\b", code)
        ),
    ),
    "sort_order": (
        "Сортировка",
        lambda code: bool(re.search(r"\bSort\b|<|>", code, re.I)),
    ),
    "stack_queue": (
        "Стек или очередь",
        lambda code: bool(re.search(r"\b(Push|Pop|Enqueue|Dequeue|Stack|Queue)\b", code, re.I)),
    ),
    "linked_node": (
        "Связный узел",
        lambda code: bool(re.search(r"\bnext\b|\^Node", code, re.I)),
    ),
    "tree_hierarchy": (
        "Дерево",
        lambda code: bool(re.search(r"\b(left|right|children)\b", code, re.I)),
    ),
    "graph_edges": (
        "Граф",
        lambda code: bool(re.search(r"\b(edge|adj|graph)\b", code, re.I)),
    ),
    "file_write": (
        "Запись файла",
        lambda code: bool(re.search(r"\b(Rewrite|WriteLn|Write)\b", code, re.I)),
    ),
    "module_namespace": (
        "Модуль",
        lambda code: bool(re.search(r"\bunit\b", code, re.I)),
    ),
    "symbol_visibility": (
        "Видимость",
        lambda code: bool(re.search(r"\b(public|private|protected)\b", code, re.I)),
    ),
    "field_access": (
        "Поле",
        lambda code: bool(re.search(r"\.\w+\b(?!\s*\()", code)),
    ),
}


def _label_for(concept_id: str, fallback: str) -> str:
    from application.curriculum.validation.technical_concept_registry import tc_concept_label_ru

    return tc_concept_label_ru(concept_id, fallback)


def missing_expected_concept_messages(
    code: str,
    expected_concept_ids: list[str],
) -> list[str]:
    """Return human-readable CONSTRUCTION errors for missing concepts."""
    from application.curriculum.validation.expected_concept_checker import (
        missing_expected_concept_messages as missing_for_language,
    )

    return missing_for_language(code, expected_concept_ids, language="pascal")
