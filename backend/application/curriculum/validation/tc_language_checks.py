"""TC42 regex checks for C-family languages (Java, C++, C#)."""

from __future__ import annotations

import re
from typing import Callable

ConceptCheck = tuple[str, Callable[[str], bool]]


def _c_assignment(code: str) -> bool:
    return bool(re.search(r"[^!<>=]=[^=]", code))


def _c_arithmetic(code: str) -> bool:
    return bool(re.search(r"[+\-*/%]", code))


def _c_simple_branch(code: str) -> bool:
    return bool(re.search(r"\bif\s*\(", code))


def _c_multi_branch(code: str) -> bool:
    return bool(re.search(r"\belse\s+if\b", code))


def _c_switch(code: str) -> bool:
    return bool(re.search(r"\bswitch\s*\(", code))


def _c_counted_loop(code: str) -> bool:
    return bool(re.search(r"\bfor\s*\(", code))


def _c_while_loop(code: str) -> bool:
    return bool(re.search(r"\bwhile\s*\(", code))


def _c_do_loop(code: str) -> bool:
    return bool(re.search(r"\bdo\s*\{", code))


def _c_loop_control(code: str) -> bool:
    return bool(re.search(r"\b(break|continue)\b", code))


def _c_nested_loops(code: str) -> bool:
    return len(re.findall(r"\b(for|while|do)\b", code, re.I)) >= 2


def _c_conditional_expression(code: str) -> bool:
    return bool(re.search(r"\?[^?]*:", code))


def _c_function_invocation(code: str) -> bool:
    return bool(re.search(r"\w+\s*\([^)]*\)", code))


def _c_return(code: str) -> bool:
    return bool(re.search(r"\breturn\b", code))


def _c_class(code: str) -> bool:
    return bool(re.search(r"\bclass\s+\w+", code))


def _c_search_find(code: str) -> bool:
    return bool(
        re.search(r"\b(in|find|index|contains|IndexOf|binarySearch)\b", code, re.I)
        or (
            re.search(r"\bif\b", code, re.I)
            and re.search(r"\bfor\b", code, re.I)
            and re.search(r"(==|!=|<=|>=|<|>|[^!<>=]=[^=])", code)
        )
    )


def _c_filter_select(code: str) -> bool:
    return bool(
        re.search(r"\bif\b", code, re.I)
        and re.search(r"\bfor\b", code, re.I)
    )


def _c_fold_aggregate(code: str) -> bool:
    return bool(
        re.search(r"\b(\+=|-=|\*=)\b", code)
        or re.search(r"=\s*\w+\s*[+\-*/]", code)
    )


def _c_indexed_sequence(code: str) -> bool:
    return bool(
        re.search(r"\[\s*\]", code)
        or re.search(r"\bnew\s+\w+\s*\[", code, re.I)
        or re.search(r"\b(array|vector|Array)\b", code, re.I)
    )


def _c_collection_iteration(code: str) -> bool:
    return bool(
        re.search(r"\bfor\s*\([^)]*:", code)
        or re.search(r"\bforeach\s*\(", code, re.I)
        or (
            re.search(r"\bfor\b", code, re.I)
            and re.search(r"\[[^\]]+\]", code)
        )
    )


def _c_dynamic_array(code: str, *, lang: str) -> bool:
    patterns = {
        "java": r"\bArrayList\b|\bnew\s+\w+\s*\[",
        "cpp": r"\bvector\s*<|\bnew\s+\w+\s*\[",
        "csharp": r"\bList\s*<|\bnew\s+\w+\s*\[",
    }
    return bool(re.search(patterns.get(lang, r"\bnew\s+\w+\s*\["), code, re.I))


def _c_string_sequence(code: str) -> bool:
    return bool(
        re.search(r"\bString\b|\bstring\b", code)
        or re.search(r"\.(length|Length|substring|Substring|charAt)\b", code, re.I)
    )


def _c_key_value_map(code: str, *, lang: str) -> bool:
    patterns = {
        "java": r"\bMap\b|\bHashMap\b",
        "cpp": r"\bmap\s*<|\bunordered_map\s*<",
        "csharp": r"\bDictionary\s*<|\bHashtable\b",
    }
    return bool(re.search(patterns.get(lang, r"\bMap\b"), code, re.I))


def _c_import(code: str) -> bool:
    return bool(re.search(r"^\s*#include\b|^\s*import\b|^\s*using\b", code, re.M))


def _c_module_namespace(code: str) -> bool:
    return bool(re.search(r"\b(namespace|package)\b", code, re.I))


def _c_symbol_visibility(code: str) -> bool:
    return bool(re.search(r"\b(public|private|protected|internal)\b", code, re.I))


def _c_object_instance(code: str) -> bool:
    return bool(re.search(r"\bnew\s+\w+", code))


def _c_method_dispatch(code: str) -> bool:
    return bool(re.search(r"\.\w+\s*\(", code))


def _c_field_access(code: str) -> bool:
    return bool(re.search(r"\.\w+\b(?!\s*\()", code))


def _c_sort_order(code: str) -> bool:
    return bool(
        re.search(r"\b(sort|Sort|Collections\.sort|std::sort|OrderBy)\b", code, re.I)
        or (re.search(r"<|>", code) and re.search(r"\bif\b", code, re.I))
    )


def _c_stack_queue(code: str) -> bool:
    return bool(
        re.search(r"\b(Stack|Queue|Deque|push|pop|enqueue|dequeue)\b", code, re.I)
    )


def _c_linked_node(code: str) -> bool:
    return bool(re.search(r"\bnext\b|\->next|\.next\b", code, re.I))


def _c_tree_hierarchy(code: str) -> bool:
    return bool(re.search(r"\b(left|right|children|Left|Right|Children)\b", code))


def _c_graph_edges(code: str) -> bool:
    return bool(re.search(r"\b(edge|adj|graph|Edge|Graph|Adj)\b", code, re.I))


def _c_file_read(code: str, *, lang: str) -> bool:
    patterns = {
        "java": r"FileReader|Files\.read|Scanner\s*\(",
        "cpp": r"ifstream|fstream|freopen",
        "csharp": r"File\.Read|StreamReader",
    }
    return bool(re.search(patterns.get(lang, r"File"), code, re.I))


def _c_file_write(code: str, *, lang: str) -> bool:
    patterns = {
        "java": r"FileWriter|Files\.write|PrintWriter",
        "cpp": r"ofstream|fstream",
        "csharp": r"File\.Write|StreamWriter",
    }
    return bool(re.search(patterns.get(lang, r"Write"), code, re.I))


def _c_recursion(code: str) -> bool:
    return bool(
        re.search(
            r"\b(?:static\s+)?\w+\s+(\w+)\s*\([^)]*\)[\s\S]*?\b\1\s*\(",
            code,
        )
    )


def _build_c_family_checks(
    *,
    lang: str,
    program_entry: ConceptCheck,
    stdin_read: ConceptCheck,
    stdout_write: ConceptCheck,
    typed_declaration: ConceptCheck,
    function_definition: ConceptCheck,
    parameter_passing: ConceptCheck,
    inheritance_hierarchy: ConceptCheck,
    post_condition_loop: ConceptCheck | None = None,
) -> dict[str, ConceptCheck]:
    do_loop = post_condition_loop or ("Цикл do-while", _c_do_loop)
    return {
        "program_entry": program_entry,
        "stdin_read": stdin_read,
        "stdout_write": stdout_write,
        "assignment": ("Присваивание", _c_assignment),
        "typed_declaration": typed_declaration,
        "arithmetic_ops": ("Арифметика", _c_arithmetic),
        "simple_branch": ("Условие if", _c_simple_branch),
        "multi_branch": ("Цепочка условий", _c_multi_branch),
        "switch_selection": ("Выбор switch", _c_switch),
        "conditional_expression": ("Условие в выражении", _c_conditional_expression),
        "counted_loop": ("Цикл for", _c_counted_loop),
        "pre_condition_loop": ("Цикл while", _c_while_loop),
        "post_condition_loop": do_loop,
        "loop_control": ("Управление циклом", _c_loop_control),
        "nested_iteration": ("Вложенные циклы", _c_nested_loops),
        "collection_iteration": ("Обход коллекции", _c_collection_iteration),
        "function_definition": function_definition,
        "parameter_passing": parameter_passing,
        "return_flow": ("Возврат", _c_return),
        "function_invocation": ("Вызов функции", _c_function_invocation),
        "recursion": ("Рекурсия", _c_recursion),
        "indexed_sequence": ("Массив", _c_indexed_sequence),
        "dynamic_array": (
            "Динамический массив",
            lambda code, language=lang: _c_dynamic_array(code, lang=language),
        ),
        "string_sequence": ("Строки", _c_string_sequence),
        "key_value_map": (
            "Словарь",
            lambda code, language=lang: _c_key_value_map(code, lang=language),
        ),
        "file_read": (
            "Чтение файла",
            lambda code, language=lang: _c_file_read(code, lang=language),
        ),
        "file_write": (
            "Запись файла",
            lambda code, language=lang: _c_file_write(code, lang=language),
        ),
        "import_dependency": ("Импорт", _c_import),
        "module_namespace": ("Модуль или namespace", _c_module_namespace),
        "symbol_visibility": ("Видимость", _c_symbol_visibility),
        "search_find": ("Поиск", _c_search_find),
        "filter_select": ("Фильтрация", _c_filter_select),
        "fold_aggregate": ("Накопление", _c_fold_aggregate),
        "sort_order": ("Сортировка", _c_sort_order),
        "stack_queue": ("Стек или очередь", _c_stack_queue),
        "linked_node": ("Связный узел", _c_linked_node),
        "tree_hierarchy": ("Дерево", _c_tree_hierarchy),
        "graph_edges": ("Граф", _c_graph_edges),
        "class_type": ("Класс", _c_class),
        "object_instance": ("Объект", _c_object_instance),
        "method_dispatch": ("Метод", _c_method_dispatch),
        "field_access": ("Поле", _c_field_access),
        "inheritance_hierarchy": inheritance_hierarchy,
    }


JAVA_CHECKS: dict[str, ConceptCheck] = _build_c_family_checks(
    lang="java",
    program_entry=(
        "Точка входа",
        lambda code: bool(re.search(r"\bpublic\s+static\s+void\s+main\s*\(", code)),
    ),
    stdin_read=("Ввод", lambda code: bool(re.search(r"\bScanner\b|\.next(?:Int|Line|Double)?\b", code))),
    stdout_write=(
        "Вывод",
        lambda code: bool(re.search(r"\bSystem\.out\.(print|println)\b", code)),
    ),
    typed_declaration=(
        "Объявление переменных",
        lambda code: bool(re.search(r"\b(int|double|float|char|boolean|String|long|byte)\b", code)),
    ),
    function_definition=(
        "Функция",
        lambda code: bool(
            re.search(r"\b(static\s+)?\w+\s+\w+\s*\([^)]*\)\s*\{", code)
            or re.search(r"\bpublic\s+\w+\s+\w+\s*\(", code)
        ),
    ),
    parameter_passing=(
        "Параметры",
        lambda code: bool(re.search(r"\b\w+\s+\w+\s*\([^)]+\)", code)),
    ),
    inheritance_hierarchy=(
        "Наследование",
        lambda code: bool(re.search(r"\bclass\s+\w+\s+extends\b", code)),
    ),
)

CPP_CHECKS: dict[str, ConceptCheck] = _build_c_family_checks(
    lang="cpp",
    program_entry=("Точка входа", lambda code: bool(re.search(r"\bmain\s*\(", code))),
    stdin_read=("Ввод", lambda code: bool(re.search(r"\bcin\b|std::cin|scanf\s*\(", code))),
    stdout_write=("Вывод", lambda code: bool(re.search(r"\bcout\b|std::cout|printf\s*\(", code))),
    typed_declaration=(
        "Объявление переменных",
        lambda code: bool(re.search(r"\b(int|double|float|char|bool|string|auto)\b", code)),
    ),
    function_definition=(
        "Функция",
        lambda code: bool(re.search(r"\b\w+\s+\w+\s*\([^)]*\)\s*\{", code)),
    ),
    parameter_passing=(
        "Параметры",
        lambda code: bool(re.search(r"\b\w+\s+\w+\s*\([^)]+\)", code)),
    ),
    inheritance_hierarchy=(
        "Наследование",
        lambda code: bool(re.search(r"\bclass\s+\w+\s*:\s*(public|private|protected)", code)),
    ),
)

CSHARP_CHECKS: dict[str, ConceptCheck] = _build_c_family_checks(
    lang="csharp",
    program_entry=(
        "Точка входа",
        lambda code: bool(re.search(r"\bstatic\s+void\s+Main\s*\(", code)),
    ),
    stdin_read=("Ввод", lambda code: bool(re.search(r"\bConsole\.Read(?:Line)?\b", code))),
    stdout_write=("Вывод", lambda code: bool(re.search(r"\bConsole\.Write(?:Line)?\b", code))),
    typed_declaration=(
        "Объявление переменных",
        lambda code: bool(re.search(r"\b(int|double|float|char|bool|string|var)\b", code)),
    ),
    function_definition=(
        "Функция",
        lambda code: bool(re.search(r"\b(static\s+)?\w+\s+\w+\s*\([^)]*\)\s*\{", code)),
    ),
    parameter_passing=(
        "Параметры",
        lambda code: bool(re.search(r"\b\w+\s+\w+\s*\([^)]+\)", code)),
    ),
    inheritance_hierarchy=(
        "Наследование",
        lambda code: bool(re.search(r"\bclass\s+\w+\s*:\s*\w+", code)),
    ),
)
