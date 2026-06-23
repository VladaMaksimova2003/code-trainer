"""Pedagogical concept cards and expected-concept bundles for Pascal curriculum tasks."""

from __future__ import annotations

import re
from typing import Any

from application.curriculum.display.pascal_hint_engine import (
    KNOWN_SOURCE_LANGUAGES,
    SHOWCASE_TECHNICAL_CONCEPTS,
    build_hint_payload,
    transfer_hint_for_tc,
)
from application.curriculum.display.pascal_tc_detection import resolve_technical_concepts
from application.curriculum.validation.technical_concept_registry import (
    list_display_tc_cards,
    lookup_technical_concept_reference,
)
from application.curriculum.validation.expected_concept_checker import (
    build_display_expected_concept_cards,
    normalize_expected_display_tc_ids,
)

# Pedagogical auxiliaries — shown in UI but not separate showcase slot TCs.
AUXILIARY_CONCEPT_IDS: frozenset[str] = frozenset(
    {"field_access", "parent_class", "child_class", "block_scope"}
)

PASCAL_ONLY_CONCEPT_IDS: frozenset[str] = frozenset(
    {
        "pascal_comment",
        "block_scope",
        "switch_selection",
        "post_condition_loop",
        "module_namespace",
    }
)

PYTHON_ONLY_CONCEPT_IDS: frozenset[str] = frozenset()

LEARNING_CONCEPT_LABELS_RU: dict[str, str] = {
    "program_structure": "Структура программы",
    "data_and_variables": "Данные и переменные",
    "operators": "Операторы",
    "conditions": "Условия",
    "loops": "Циклы",
    "functions": "Функции и процедуры",
    "files": "Ввод и вывод",
    "collections": "Коллекции",
    "data_processing": "Обработка данных",
    "modules": "Модули",
    "oop": "Объектно-ориентированное программирование",
    "advanced_structures": "Структуры данных",
}

# Keywords in pascal_features that activate a given concept.
# If a task's pascal_features contains ANY of a concept's keywords, that concept is shown.
_CONCEPT_FEATURE_KEYWORDS: dict[str, list[str]] = {
    "program_entry":       ["program"],
    "block_scope":         ["begin", "end"],
    "typed_declaration":   ["var", "const", "integer", "real", "boolean", "char", "string", "type"],
    "assignment":          [":=", "присваива"],
    "arithmetic_ops":      ["+", "-", "*", "/", "div", "mod", "арифм"],
    "stdin_read":          ["readln", "read", "ввод"],
    "stdout_write":        ["writeln", "write", "вывод"],
    "simple_branch":       ["if", "then", "else", "условие", "ветвл"],
    "multi_branch":        ["if", "then", "else", "вложен", "несколько"],
    "switch_selection":    ["case", "of", "вариант"],
    "conditional_expression": ["if", "then", "else", "тернар"],
    "counted_loop":        ["for", "to", "downto", "цикл"],
    "pre_condition_loop":  ["while", "do", "цикл"],
    "post_condition_loop": ["repeat", "until", "цикл"],
    "loop_control":        ["break", "continue", "exit", "управление"],
    "nested_iteration":    ["вложен", "nested", "for", "while"],
    "collection_iteration":["for", "array", "массив"],
    "function_definition": ["function", "функц"],
    "parameter_passing":   ["procedure", "параметр", "procedure"],
    "return_flow":         ["result", "exit", "return", "функц"],
    "function_invocation": ["function", "вызов", "invoke"],
    "indexed_sequence":    ["array", "массив", "индекс"],
    "dynamic_array":       ["setlength", "dynamic", "динамич"],
    "string_sequence":     ["string", "строка", "length", "copy"],
    "key_value_map":       ["record", "запись", "field"],
    "file_read":           ["file", "assign", "reset", "rewrite", "файл"],
    "import_dependency":   ["unit", "uses", "модуль", "unit"],
    "recursion":           ["рекурс", "recursion", "function"],
    "class_type":          ["class", "object", "oop", "класс"],
}


def _filter_bundle_by_features(bundle: list[str], pascal_features: str) -> list[str]:
    """Keep only concepts whose keywords appear in pascal_features; always keep primary."""
    if not pascal_features:
        return bundle
    feat_lower = pascal_features.lower()
    result = []
    for i, concept_id in enumerate(bundle):
        if i == 0:
            result.append(concept_id)
            continue
        kws = _CONCEPT_FEATURE_KEYWORDS.get(concept_id, [])
        if any(kw in feat_lower for kw in kws):
            result.append(concept_id)
    return result if result else bundle[:1]


# Ordered bundles: what a student typically needs for this slot TC.
TASK_EXPECTED_BUNDLES: dict[str, list[str]] = {
    "program_entry": [
        "program_entry",
        "block_scope",
        "typed_declaration",
        "assignment",
        "stdin_read",
        "stdout_write",
    ],
    "typed_declaration": ["typed_declaration", "assignment", "arithmetic_ops"],
    "assignment": ["assignment", "typed_declaration", "arithmetic_ops"],
    "arithmetic_ops": ["arithmetic_ops", "assignment"],
    "stdin_read": ["stdin_read", "typed_declaration", "assignment", "stdout_write"],
    "stdout_write": ["stdout_write", "assignment", "typed_declaration"],
    "simple_branch": ["simple_branch", "assignment", "stdin_read", "stdout_write"],
    "multi_branch": ["multi_branch", "simple_branch", "assignment", "stdin_read", "stdout_write"],
    "switch_selection": ["switch_selection", "simple_branch", "assignment", "stdin_read", "stdout_write"],
    "conditional_expression": [
        "conditional_expression",
        "simple_branch",
        "assignment",
        "stdout_write",
    ],
    "counted_loop": ["counted_loop", "assignment", "stdin_read", "stdout_write"],
    "pre_condition_loop": ["pre_condition_loop", "assignment", "stdin_read", "stdout_write"],
    "post_condition_loop": ["post_condition_loop", "assignment", "stdin_read", "stdout_write"],
    "loop_control": ["loop_control", "counted_loop", "pre_condition_loop"],
    "nested_iteration": ["nested_iteration", "counted_loop", "assignment", "stdout_write"],
    "collection_iteration": [
        "collection_iteration",
        "counted_loop",
        "indexed_sequence",
        "assignment",
        "stdout_write",
    ],
    "function_definition": [
        "function_definition",
        "return_flow",
        "parameter_passing",
        "assignment",
        "stdout_write",
    ],
    "function_invocation": [
        "function_invocation",
        "function_definition",
        "assignment",
        "stdin_read",
        "stdout_write",
    ],
    "return_flow": ["return_flow", "function_definition", "assignment"],
    "indexed_sequence": [
        "indexed_sequence",
        "typed_declaration",
        "assignment",
        "stdin_read",
        "stdout_write",
    ],
    "dynamic_array": [
        "dynamic_array",
        "indexed_sequence",
        "collection_iteration",
        "assignment",
        "stdout_write",
    ],
    "string_sequence": ["string_sequence", "assignment", "stdout_write", "stdin_read"],
    "key_value_map": ["key_value_map", "typed_declaration", "assignment", "stdout_write"],
    "file_read": ["file_read", "assignment", "stdout_write"],
    "file_write": ["file_write", "assignment", "stdout_write"],
    "parameter_passing": ["parameter_passing", "function_definition", "function_invocation"],
    "import_dependency": ["import_dependency", "module_namespace"],
    "module_namespace": ["module_namespace", "import_dependency", "symbol_visibility"],
    "symbol_visibility": ["symbol_visibility", "module_namespace", "import_dependency"],
    "recursion": ["recursion", "function_definition", "return_flow", "simple_branch"],
    "search_find": ["search_find", "simple_branch", "counted_loop", "indexed_sequence"],
    "filter_select": ["filter_select", "simple_branch", "counted_loop", "indexed_sequence"],
    "fold_aggregate": ["fold_aggregate", "counted_loop", "assignment", "indexed_sequence"],
    "sort_order": ["sort_order", "simple_branch", "counted_loop", "indexed_sequence"],
    "stack_queue": ["stack_queue", "indexed_sequence", "assignment", "simple_branch"],
    "linked_node": ["linked_node", "assignment", "simple_branch"],
    "tree_hierarchy": ["tree_hierarchy", "recursion", "simple_branch", "assignment"],
    "graph_edges": ["graph_edges", "counted_loop", "simple_branch", "assignment"],
    "class_type": [
        "class_type",
        "object_instance",
        "field_access",
        "assignment",
        "stdin_read",
        "stdout_write",
    ],
    "object_instance": [
        "object_instance",
        "class_type",
        "field_access",
        "assignment",
        "stdin_read",
        "stdout_write",
    ],
    "method_dispatch": [
        "method_dispatch",
        "class_type",
        "object_instance",
        "field_access",
        "return_flow",
        "stdout_write",
    ],
    "inheritance_hierarchy": [
        "inheritance_hierarchy",
        "class_type",
        "parent_class",
        "child_class",
        "object_instance",
        "method_dispatch",
    ],
}

HIERARCHY_ORDERS: dict[str, list[str]] = {
    "inheritance_hierarchy": [
        "inheritance_hierarchy",
        "class_type",
        "parent_class",
        "child_class",
        "object_instance",
        "field_access",
        "method_dispatch",
    ],
    "class_type": [
        "class_type",
        "object_instance",
        "field_access",
        "assignment",
        "stdin_read",
        "stdout_write",
    ],
    "object_instance": [
        "object_instance",
        "class_type",
        "field_access",
        "assignment",
        "stdin_read",
        "stdout_write",
    ],
    "method_dispatch": [
        "method_dispatch",
        "class_type",
        "object_instance",
        "field_access",
        "return_flow",
    ],
}

# id → pedagogical card
PEDAGOGY_CARDS: dict[str, dict[str, str]] = {
    "program_entry": {
        "name_ru": "Точка входа программы",
        "description_ru": "Каждая программа на Pascal начинается с program и завершается end.",
        "pascal_template": "program Demo;\nbegin\n  { statements }\nend.",
        "learning_concept_id": "program_structure",
    },
    "pascal_comment": {
        "name_ru": "Комментарии",
        "description_ru": "Комментарии в коде: в Pascal — { } и (* *), в других языках — свой синтаксис.",
        "pascal_template": "{ однострочный }\n(* многострочный\n   комментарий *)",
        "learning_concept_id": "program_structure",
    },
    "block_scope": {
        "name_ru": "Блок begin/end",
        "description_ru": "Операторы группируются между begin и end.",
        "pascal_template": "begin\n  writeln('step 1');\n  writeln('step 2');\nend;",
        "learning_concept_id": "program_structure",
        "parent_id": "program_entry",
    },
    "typed_declaration": {
        "name_ru": "Объявление переменных",
        "description_ru": "Перед begin объявляют переменные с типом.",
        "pascal_template": "var\n  n: integer;\n  s: string;",
        "learning_concept_id": "data_and_variables",
    },
    "assignment": {
        "name_ru": "Присваивание",
        "description_ru": "Запись значения в переменную через оператор :=.",
        "pascal_template": "x := 10;       { константа }\nx := y + z;    { выражение }\nx := x + 1;    { накопление }",
        "learning_concept_id": "data_and_variables",
    },
    "arithmetic_ops": {
        "name_ru": "Арифметика",
        "description_ru": "Сложение, вычитание, умножение; div и mod для целых чисел.",
        "pascal_template": (
            "{ + - * — обычные операции }\n"
            "z := x + y;       { сложение }\n"
            "z := x - y;       { вычитание }\n"
            "z := x * y;       { умножение }\n\n"
            "{ div и mod — только для integer }\n"
            "z := x div y;     { целое частное }\n"
            "z := x mod y;     { остаток }"
        ),
        "learning_concept_id": "operators",
    },
    "stdin_read": {
        "name_ru": "Ввод с клавиатуры",
        "description_ru": "readln считывает значение в переменную.",
        "pascal_template": "readln(n);",
        "learning_concept_id": "files",
    },
    "stdout_write": {
        "name_ru": "Вывод на экран",
        "description_ru": "writeln печатает значения и переводит строку.",
        "pascal_template": "writeln(n);\nwriteln('answer = ', result);",
        "learning_concept_id": "files",
    },
    "simple_branch": {
        "name_ru": "Условие if",
        "description_ru": "Выбор одной из двух веток по условию.",
        "pascal_template": "if n > 0 then\n  writeln('pos')\nelse\n  writeln('nonpos');",
        "learning_concept_id": "conditions",
    },
    "multi_branch": {
        "name_ru": "Цепочка условий",
        "description_ru": "Несколько проверок подряд через else if.",
        "pascal_template": (
            "if score >= 90 then writeln('A')\n"
            "else if score >= 70 then writeln('B')\n"
            "else writeln('C');"
        ),
        "learning_concept_id": "conditions",
        "parent_id": "simple_branch",
    },
    "switch_selection": {
        "name_ru": "Выбор case",
        "description_ru": "Сравнение значения с несколькими вариантами.",
        "pascal_template": "case code of\n  1: writeln('one');\n  2: writeln('two');\nelse writeln('other');\nend;",
        "learning_concept_id": "conditions",
    },
    "conditional_expression": {
        "name_ru": "Условие в выражении",
        "description_ru": "Вместо тернарного оператора используйте if then else.",
        "pascal_template": "if n > 0 then sign := 1 else sign := -1;",
        "learning_concept_id": "conditions",
        "parent_id": "simple_branch",
    },
    "counted_loop": {
        "name_ru": "Счётный цикл for",
        "description_ru": "Цикл с известным числом повторений.",
        "pascal_template": "for i := 1 to n do\n  writeln(i);",
        "learning_concept_id": "loops",
    },
    "pre_condition_loop": {
        "name_ru": "Цикл while",
        "description_ru": "Повторение, пока условие истинно.",
        "pascal_template": "while n > 0 do\nbegin\n  writeln(n);\n  n := n - 1;\nend;",
        "learning_concept_id": "loops",
    },
    "post_condition_loop": {
        "name_ru": "Цикл repeat",
        "description_ru": "Тело выполняется минимум один раз, затем проверка until.",
        "pascal_template": "repeat\n  readln(x);\nuntil x > 0;",
        "learning_concept_id": "loops",
    },
    "loop_control": {
        "name_ru": "Управление циклом",
        "description_ru": "Досрочный выход или пропуск итерации через флаг или перестройку условия.",
        "pascal_template": "for i := 1 to n do\nbegin\n  if i = stopAt then Break;\n  writeln(i);\nend;",
        "learning_concept_id": "loops",
    },
    "nested_iteration": {
        "name_ru": "Вложенные циклы",
        "description_ru": "Цикл внутри цикла для таблиц и матриц.",
        "pascal_template": "for i := 1 to n do\n  for j := 1 to m do\n    writeln(i, ' ', j);",
        "learning_concept_id": "loops",
        "parent_id": "counted_loop",
    },
    "collection_iteration": {
        "name_ru": "Перебор коллекции",
        "description_ru": "Последовательный проход по элементам массива или строки.",
        "pascal_template": "for i := 1 to Length(arr) do\n  sum := sum + arr[i];",
        "learning_concept_id": "loops",
        "parent_id": "counted_loop",
    },
    "function_definition": {
        "name_ru": "Объявление функции",
        "description_ru": "Подпрограмма с параметрами и возвращаемым значением.",
        "pascal_template": (
            "function Sq(x: integer): integer;\nbegin\n  Sq := x * x;\nend;"
        ),
        "learning_concept_id": "functions",
    },
    "function_invocation": {
        "name_ru": "Вызов подпрограммы",
        "description_ru": "Использование функции или процедуры по имени.",
        "pascal_template": "result := Sq(n);",
        "learning_concept_id": "functions",
        "parent_id": "function_definition",
    },
    "parameter_passing": {
        "name_ru": "Параметры var/value",
        "description_ru": "var передаёт переменную по ссылке и позволяет изменить её снаружи.",
        "pascal_template": "procedure Inc(var x: integer);\nbegin\n  x := x + 1;\nend;",
        "learning_concept_id": "functions",
        "parent_id": "function_definition",
    },
    "return_flow": {
        "name_ru": "Возврат результата",
        "description_ru": "Функция возвращает значение через присвоение своему имени.",
        "pascal_template": "function Max(a, b: integer): integer;\nbegin\n  if a > b then Max := a else Max := b;\nend;",
        "learning_concept_id": "functions",
        "parent_id": "function_definition",
    },
    "recursion": {
        "name_ru": "Рекурсия",
        "description_ru": "Функция вызывает себя; нужен базовый случай.",
        "pascal_template": (
            "function Fact(n: integer): integer;\nbegin\n"
            "  if n <= 1 then Fact := 1\n  else Fact := n * Fact(n - 1);\nend;"
        ),
        "learning_concept_id": "functions",
        "parent_id": "function_definition",
    },
    "indexed_sequence": {
        "name_ru": "Массив",
        "description_ru": "Фиксированная последовательность элементов с индексом.",
        "pascal_template": "var a: array[1..3] of integer;\nbegin\n  a[1] := 1;\n  writeln(a[1] + a[2] + a[3]);\nend;",
        "learning_concept_id": "collections",
    },
    "dynamic_array": {
        "name_ru": "Динамический массив",
        "description_ru": "Размер задаётся во время выполнения через SetLength.",
        "pascal_template": "var a: array of integer;\nbegin\n  SetLength(a, n);\n  a[0] := 42;\nend;",
        "learning_concept_id": "collections",
        "parent_id": "indexed_sequence",
    },
    "string_sequence": {
        "name_ru": "Строка",
        "description_ru": "Текстовая последовательность; длина через Length.",
        "pascal_template": "var s: string;\nbegin\n  readln(s);\n  writeln(Length(s));\nend;",
        "learning_concept_id": "collections",
    },
    "key_value_map": {
        "name_ru": "Запись record",
        "description_ru": "Именованные поля в одной структуре.",
        "pascal_template": "type TPair = record\n  key: integer;\n  value: string;\nend;",
        "learning_concept_id": "collections",
    },
    "file_read": {
        "name_ru": "Чтение файла",
        "description_ru": "Открытие файла на чтение и построчное чтение.",
        "pascal_template": "var f: text;\n    line: string;\nbegin\n  Assign(f, 'input.txt');\n  Reset(f);\n  Readln(f, line);\n  CloseFile(f);\nend;",
        "learning_concept_id": "files",
    },
    "file_write": {
        "name_ru": "Запись файла",
        "description_ru": "Создание или перезапись файла.",
        "pascal_template": "var f: text;\nbegin\n  Assign(f, 'out.txt');\n  Rewrite(f);\n  Writeln(f, 'hello');\n  CloseFile(f);\nend;",
        "learning_concept_id": "files",
    },
    "import_dependency": {
        "name_ru": "Подключение модуля",
        "description_ru": "uses подключает unit с готовыми процедурами.",
        "pascal_template": "uses Math;\nbegin\n  writeln(Sqrt(16));\nend.",
        "learning_concept_id": "modules",
    },
    "module_namespace": {
        "name_ru": "Unit interface/implementation",
        "description_ru": (
            "Модуль (unit) делится на две части: interface — публичные объявления "
            "(procedure Hello; без begin/end) и implementation — реализация с телами процедур."
        ),
        "pascal_template": (
            "unit MyUtils;\n"
            "interface\n"
            "  procedure Hello;\n"
            "implementation\n"
            "  procedure Hello;\n"
            "  begin\n"
            "    Writeln('hi');\n"
            "  end;\n"
            "end."
        ),
        "learning_concept_id": "modules",
        "parent_id": "import_dependency",
    },
    "symbol_visibility": {
        "name_ru": "Видимость символов",
        "description_ru": (
            "В interface экспортируются только заголовки процедур и функций. "
            "Код с begin/end всегда пишется в implementation."
        ),
        "pascal_template": (
            "interface\n"
            "  procedure PublicProc;\n"
            "implementation\n"
            "  procedure PublicProc;\n"
            "  begin\n"
            "  end;"
        ),
        "learning_concept_id": "modules",
        "parent_id": "module_namespace",
    },
    "search_find": {
        "name_ru": "Линейный поиск",
        "description_ru": "Поиск элемента проходом по массиву.",
        "pascal_template": "for i := 1 to n do\n  if a[i] = key then found := true;",
        "learning_concept_id": "data_processing",
    },
    "filter_select": {
        "name_ru": "Отбор по условию",
        "description_ru": "Выбор элементов, удовлетворяющих условию.",
        "pascal_template": "for i := 1 to n do\n  if a[i] > 0 then cnt := cnt + 1;",
        "learning_concept_id": "data_processing",
    },
    "fold_aggregate": {
        "name_ru": "Сумма / агрегация",
        "description_ru": "Накопление результата в цикле.",
        "pascal_template": "sum := 0;\nfor i := 1 to n do\n  sum := sum + a[i];",
        "learning_concept_id": "data_processing",
    },
    "sort_order": {
        "name_ru": "Сортировка",
        "description_ru": "Упорядочивание элементов массива.",
        "pascal_template": "for i := 1 to n - 1 do\n  for j := i + 1 to n do\n    if a[j] < a[i] then Swap(a[i], a[j]);",
        "learning_concept_id": "data_processing",
    },
    "stack_queue": {
        "name_ru": "Стек / очередь",
        "description_ru": "LIFO/FIFO на базе массива и индексов.",
        "pascal_template": "stack[top] := x;\ntop := top + 1;",
        "learning_concept_id": "advanced_structures",
    },
    "linked_node": {
        "name_ru": "Связный список",
        "description_ru": "Узлы со ссылкой на следующий элемент.",
        "pascal_template": "type PNode = ^Node;\n     Node = record\n  value: integer;\n  next: PNode;\nend;",
        "learning_concept_id": "advanced_structures",
    },
    "tree_hierarchy": {
        "name_ru": "Дерево",
        "description_ru": "Иерархия узлов с дочерними ссылками.",
        "pascal_template": "type PNode = ^Node;\n     Node = record\n  value: integer;\n  left, right: PNode;\nend;",
        "learning_concept_id": "advanced_structures",
    },
    "graph_edges": {
        "name_ru": "Граф",
        "description_ru": "Вершины и рёбра; обход через списки смежности.",
        "pascal_template": "for i := 1 to n do\n  for j := 1 to n do\n    if adj[i, j] = 1 then writeln(i, '->', j);",
        "learning_concept_id": "advanced_structures",
    },
    "class_type": {
        "name_ru": "Класс",
        "description_ru": "Объектный тип с полями и методами.",
        "pascal_template": (
            "type TPoint = class\n"
            "public\n"
            "  X, Y: Integer;\n"
            "end;"
        ),
        "learning_concept_id": "oop",
    },
    "object_instance": {
        "name_ru": "Экземпляр объекта",
        "description_ru": "Создание объекта через Create и освобождение через Free.",
        "pascal_template": "var p: TPoint;\nbegin\n  p := TPoint.Create;\n  try\n    p.X := 2;\n  finally\n    p.Free;\n  end;\nend;",
        "learning_concept_id": "oop",
        "parent_id": "class_type",
    },
    "field_access": {
        "name_ru": "Поля объекта",
        "description_ru": "Доступ к данным экземпляра через точку.",
        "pascal_template": "p.X := 2;\np.Y := 3;\nwriteln(p.X + p.Y);",
        "learning_concept_id": "oop",
        "parent_id": "object_instance",
    },
    "method_dispatch": {
        "name_ru": "Метод класса",
        "description_ru": "Функция или процедура, объявленная внутри класса.",
        "pascal_template": (
            "function TPoint.Sum: Integer;\nbegin\n  Result := X + Y;\nend;"
        ),
        "learning_concept_id": "oop",
        "parent_id": "class_type",
    },
    "inheritance_hierarchy": {
        "name_ru": "Наследование",
        "description_ru": "Потомок расширяет или переопределяет поведение родителя.",
        "pascal_template": "type TChild = class(TParent)\n  procedure Run; override;\nend;",
        "learning_concept_id": "oop",
    },
    "parent_class": {
        "name_ru": "Родительский класс",
        "description_ru": "Базовый тип, от которого наследуют.",
        "pascal_template": "type TParent = class\n  procedure Run; virtual;\nend;",
        "learning_concept_id": "oop",
        "parent_id": "inheritance_hierarchy",
    },
    "child_class": {
        "name_ru": "Потомок",
        "description_ru": "Класс, унаследованный от родителя.",
        "pascal_template": "type TChild = class(TParent)\n  procedure Run; override;\nend;",
        "learning_concept_id": "oop",
        "parent_id": "parent_class",
    },
}


_TC_LANG_LABELS = {
    "python": "Python",
    "cpp": "C++",
    "csharp": "C#",
    "java": "Java",
}

_TC_LANG_ADDENDUM: dict[str, dict[str, str]] = {
    "file_read": {
        "python": " В Python используют open(), read()/readline() или конструкцию with.",
        "cpp": " В C++ — ifstream и getline.",
        "csharp": " В C# — File.ReadAllLines, StreamReader или using.",
        "java": " В Java — Files.readAllLines, BufferedReader или try-with-resources.",
    },
    "file_write": {
        "python": " В Python — open(..., 'w'), write() или with.",
        "cpp": " В C++ — ofstream и оператор <<.",
        "csharp": " В C# — File.WriteAllText, StreamWriter или using.",
        "java": " В Java — Files.write, BufferedWriter или try-with-resources.",
    },
    "indexed_sequence": {
        "python": " В Python — списки list и индексация с нуля.",
        "cpp": " В C++ — std::array или C-массив с фиксированным размером.",
        "csharp": " В C# — массив T[] с индексами.",
        "java": " В Java — массив T[] с индексами.",
    },
    "simple_branch": {
        "python": " В Python — `if` / `elif` / `else` с двоеточием и отступами.",
        "cpp": " В C++ — `if (условие) { ... } else { ... }`.",
        "java": " В Java — `if (условие) { ... } else { ... }`.",
    },
    "counted_loop": {
        "python": " В Python — `for i in range(...)`.",
        "cpp": " В C++ — `for (int i = ...; i < n; i++)`.",
        "java": " В Java — `for (int i = ...; i < n; i++)`.",
    },
    "string_sequence": {
        "python": " В Python — `len(s)`, индексация с 0, `for ch in s`.",
        "cpp": " В C++ — `std::string`, `size()`, `s[i]`, range-for.",
        "java": " В Java — `String`, `length()`, `charAt(i)`.",
    },
    "search_find": {
        "python": " В Python — `x in list`, `list.index(x)` или цикл.",
        "cpp": " В C++ — `std::find` или цикл по индексам.",
        "java": " В Java — цикл, `list.contains(x)` или `indexOf`.",
    },
    "filter_select": {
        "python": " В Python — list comprehension или цикл с `if`.",
        "cpp": " В C++ — `std::copy_if` или цикл с условием.",
        "java": " В Java — `stream().filter(...)` или цикл с `if`.",
    },
    "dynamic_array": {
        "python": " В Python размер списка меняется автоматически.",
        "cpp": " В C++ — std::vector и push_back/resize.",
        "csharp": " В C# — List<T> и Add/Capacity.",
        "java": " В Java — ArrayList и add().",
    },
    "key_value_map": {
        "python": " В Python — dict.",
        "cpp": " В C++ — std::map или std::unordered_map.",
        "csharp": " В C# — Dictionary<K,V>.",
        "java": " В Java — HashMap или Map.",
    },
    "function_return": {
        "python": " В Python результат возвращают через return.",
        "cpp": " В C++ — return в теле функции.",
        "csharp": " В C# — return в методе.",
        "java": " В Java — return в методе.",
    },
    "stack_queue": {
        "python": " В Python — list/deque или collections.deque.",
        "cpp": " В C++ — std::stack и std::queue из STL.",
        "csharp": " В C# — Stack<T> и Queue<T>.",
        "java": " В Java — Stack, ArrayDeque или Queue.",
    },
}


def _strip_pascal_specific_clauses(text: str) -> str:
    cleaned = str(text or "").strip()
    cleaned = re.sub(r"\s*В Pascal[^.]*\.", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s*Для Pascal[^.]*\.", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s*в учебном Pascal[^.]*\.", "", cleaned, flags=re.I)
    cleaned = re.sub(r";\s*в других языках[^.]*\.", ".", cleaned, flags=re.I)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    return cleaned


def _description_for_language(
    *,
    concept_id: str,
    base_description: str,
    language: str,
) -> str:
    lang = str(language or "pascal").strip().lower()
    base = str(base_description or "").strip()
    if not base:
        return ""
    if lang == "pascal":
        return base
    localized = _strip_pascal_specific_clauses(base).rstrip(".")
    addendum = (_TC_LANG_ADDENDUM.get(concept_id) or {}).get(lang, "")
    if addendum:
        return f"{localized}.{addendum}".strip()
    label = _TC_LANG_LABELS.get(lang)
    if label and localized and label.lower() not in localized.lower():
        return f"{localized}. Типичный синтаксис — {label}."
    return localized or base


def _descriptions_by_language(concept_id: str, base_description: str) -> dict[str, str]:
    langs = ("pascal", "python", "cpp", "csharp", "java")
    return {
        lang: _description_for_language(
            concept_id=concept_id,
            base_description=base_description,
            language=lang,
        )
        for lang in langs
    }


def _format_tc_examples(examples_by_language: dict[str, Any]) -> dict[str, Any]:
    from application.curriculum.content.v4_code_format import format_reference_code

    formatted: dict[str, Any] = {}
    for lang, examples in examples_by_language.items():
        if not isinstance(examples, list):
            continue
        lang_key = str(lang).lower()
        formatted[lang_key] = []
        for item in examples:
            if not isinstance(item, dict):
                continue
            code = str(item.get("code") or "").strip()
            if code:
                code = format_reference_code(code, lang_key) or code
            formatted[lang_key].append({**item, "code": code})
    return formatted


def _card_for(concept_id: str) -> dict[str, Any] | None:
    raw = PEDAGOGY_CARDS.get(concept_id)
    ref = lookup_technical_concept_reference(concept_id)
    if raw is None and ref is None:
        return None

    learning_concept_id = (
        raw.get("learning_concept_id")
        if raw
        else _infer_learning_concept_id(concept_id)
    )
    examples_by_language = _format_tc_examples(dict(ref.get("examples_by_language") or {}) if ref else {})
    pascal_examples = examples_by_language.get("pascal") or []
    pascal_template = raw["pascal_template"] if raw else ""
    if not pascal_template and pascal_examples:
        pascal_template = str(pascal_examples[0].get("code") or "")

    base_description = (raw or {}).get("description_ru") or (ref or {}).get("description_ru") or ""
    descriptions_by_language = _descriptions_by_language(concept_id, base_description)

    return {
        "id": concept_id,
        "name_ru": (raw or {}).get("name_ru") or (ref or {}).get("name_ru") or concept_id,
        "description_ru": descriptions_by_language.get("pascal") or base_description,
        "descriptions_by_language": descriptions_by_language,
        "pascal_template": pascal_template,
        "examples_by_language": examples_by_language,
        "learning_concept_id": learning_concept_id,
        "learning_concept_label_ru": LEARNING_CONCEPT_LABELS_RU.get(
            learning_concept_id, learning_concept_id
        ),
        "parent_id": raw.get("parent_id") if raw else None,
        "is_auxiliary": concept_id in AUXILIARY_CONCEPT_IDS,
    }


def _infer_learning_concept_id(concept_id: str) -> str:
    for tc_id, card in PEDAGOGY_CARDS.items():
        if tc_id == concept_id:
            return card["learning_concept_id"]
    return "program_structure"


def _is_known_concept(concept_id: str) -> bool:
    key = str(concept_id or "").strip()
    if not key:
        return False
    if key.startswith("tc_"):
        return key in list_display_tc_cards()
    if key in PEDAGOGY_CARDS:
        return True
    return lookup_technical_concept_reference(key) is not None


def _dedupe_preserve_ids(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        key = str(item or "").strip()
        if not key or key in seen:
            continue
        seen.add(key)
        ordered.append(key)
    return ordered


def _teacher_expected_concept_ids_for_language(
    payload: dict[str, Any],
    language: str | None,
) -> list[str]:
    """Teacher-authored per-language TC ids from task save (patterns_by_language)."""
    lang = str(language or "").strip().lower()
    if not lang:
        return []

    collected: list[str] = []
    sources: list[Any] = [payload.get("expected_concepts")]
    code_examples = payload.get("code_examples")
    if isinstance(code_examples, dict):
        sources.append(code_examples.get("expected_concepts"))
        showcase = code_examples.get("curriculum_showcase")
        if isinstance(showcase, dict):
            sources.append(showcase.get("expected_concepts"))

    for source in sources:
        if not isinstance(source, dict):
            continue
        raw = source.get(lang)
        if not isinstance(raw, list) or not raw:
            continue
        collected.extend(str(item).strip() for item in raw if str(item).strip())

    if not collected:
        for key in ("expected_concept_ids", "patterns"):
            explicit = payload.get(key)
            if isinstance(explicit, list) and explicit:
                collected.extend(str(item).strip() for item in explicit if str(item).strip())
                break
            if isinstance(code_examples, dict):
                explicit = code_examples.get(key)
                if isinstance(explicit, list) and explicit:
                    collected.extend(str(item).strip() for item in explicit if str(item).strip())
                    break

    if not collected:
        return []

    display_ids = normalize_expected_display_tc_ids(collected)
    if display_ids:
        return _dedupe_preserve_ids(display_ids)

    validated = [str(item) for item in collected if _is_known_concept(str(item))]
    return _dedupe_preserve_ids(validated)


def resolve_expected_concept_ids(
    *,
    primary_tc: str,
    task_payload: dict[str, Any] | None = None,
    learning_language: str | None = None,
) -> list[str]:
    payload = task_payload or {}
    lang = str(
        learning_language
        or payload.get("target_language")
        or payload.get("language")
        or "",
    ).strip().lower()
    teacher_ids = _teacher_expected_concept_ids_for_language(payload, lang)
    if teacher_ids:
        return teacher_ids

    explicit = payload.get("expected_concept_ids")
    if isinstance(explicit, list) and explicit:
        normalized = normalize_expected_display_tc_ids([str(item) for item in explicit if str(item).strip()])
        if normalized:
            return normalized
        validated = [str(item) for item in explicit if _is_known_concept(str(item))]
        if validated:
            return validated

    primary = str(primary_tc or "").strip()
    bundle = list(TASK_EXPECTED_BUNDLES.get(primary, [primary]))

    pascal_features = str(payload.get("pascal_features") or "")
    if pascal_features and len(bundle) > 1:
        bundle = _filter_bundle_by_features(bundle, pascal_features)

    detected = resolve_technical_concepts(primary_tc=primary, task_payload=task_payload or {})

    ordered: list[str] = []
    seen: set[str] = set()

    def add(tc_id: str) -> None:
        if tc_id in seen:
            return
        if tc_id not in PEDAGOGY_CARDS and lookup_technical_concept_reference(tc_id) is None:
            return
        seen.add(tc_id)
        ordered.append(tc_id)

    for tc_id in bundle:
        add(tc_id)
    for tc_id in detected:
        if tc_id in bundle or tc_id == primary:
            add(tc_id)
    if primary and primary not in seen:
        ordered.insert(0, primary)
    return ordered


def _tree_prefix(index: int, total: int, depth: int) -> str:
    if depth <= 0:
        return "✓"
    is_last = index >= total - 1
    return "└─" if is_last else "├─"


def build_hierarchy_lines(concept_ids: list[str], primary_tc: str) -> list[dict[str, Any]]:
    order = HIERARCHY_ORDERS.get(primary_tc)
    if order:
        ordered = [cid for cid in order if cid in concept_ids]
        for cid in concept_ids:
            if cid not in ordered:
                ordered.append(cid)
    else:
        ordered = list(concept_ids)

    lines: list[dict[str, Any]] = []
    if primary_tc in HIERARCHY_ORDERS and primary_tc == "inheritance_hierarchy":
        root = _card_for(primary_tc)
        if root:
            lines.append(
                {
                    "depth": 0,
                    "prefix": "",
                    "concept_id": primary_tc,
                    "label": root["name_ru"],
                    "is_root": True,
                }
            )
        children = [cid for cid in ordered if cid != primary_tc]
        for index, cid in enumerate(children):
            card = _card_for(cid)
            if not card:
                continue
            depth = 1
            if cid in {"parent_class", "child_class"}:
                depth = 2
            lines.append(
                {
                    "depth": depth,
                    "prefix": _tree_prefix(index, len(children), depth),
                    "concept_id": cid,
                    "label": card["name_ru"],
                    "is_root": False,
                }
            )
        return lines

    for index, cid in enumerate(ordered):
        card = _card_for(cid)
        if not card:
            continue
        depth = 0
        prefix = "✓"
        if primary_tc in HIERARCHY_ORDERS:
            depth = 1 if cid != primary_tc else 0
            prefix = "✓" if cid == primary_tc else _tree_prefix(index, len(ordered), 1)
        lines.append(
            {
                "depth": depth,
                "prefix": prefix,
                "concept_id": cid,
                "label": card["name_ru"],
                "is_root": cid == primary_tc,
            }
        )
    return lines


def filter_concept_ids_for_language(concept_ids: list[str], language: str | None) -> list[str]:
    lang = str(language or "").strip().lower()
    if lang == "python":
        return [cid for cid in concept_ids if cid not in PASCAL_ONLY_CONCEPT_IDS]
    if lang == "pascal":
        return [cid for cid in concept_ids if cid not in PYTHON_ONLY_CONCEPT_IDS]
    return list(concept_ids)


def build_expected_concepts_payload(
    *,
    primary_tc: str,
    task_payload: dict[str, Any] | None = None,
    known_languages: list[str] | None = None,
    learning_language: str | None = None,
) -> dict[str, Any]:
    concept_ids = resolve_expected_concept_ids(
        primary_tc=primary_tc,
        task_payload=task_payload,
        learning_language=learning_language,
    )
    concept_ids = filter_concept_ids_for_language(concept_ids, learning_language)
    cards = build_display_expected_concept_cards(concept_ids)
    if not cards:
        cards = [card for cid in concept_ids if (card := _card_for(cid))]
    hierarchy_lines = build_hierarchy_lines(concept_ids, primary_tc)

    hints = build_hint_payload(
        technical_concepts=[cid for cid in concept_ids if cid in SHOWCASE_TECHNICAL_CONCEPTS],
        known_languages=known_languages,
    )
    transfer_by_language: dict[str, list[dict[str, str]]] = {}
    langs = known_languages or list(KNOWN_SOURCE_LANGUAGES)
    for lang in langs:
        lang_key = str(lang).lower()
        if lang_key not in KNOWN_SOURCE_LANGUAGES:
            continue
        items = [
            {"concept_id": cid, "label_ru": _card_for(cid)["name_ru"], "text": text}
            for cid in concept_ids
            if cid in SHOWCASE_TECHNICAL_CONCEPTS
            and (text := transfer_hint_for_tc(lang_key, cid))
        ]
        if items:
            transfer_by_language[lang_key] = items

    atcc_payload: dict[str, Any] = {}
    if task_payload and learning_language:
        source_lang = str(task_payload.get("source_language") or "").strip().lower()
        if not source_lang and isinstance(task_payload.get("known_language_variants"), dict):
            for candidate in ("python", "pascal", "cpp", "java", "csharp"):
                if candidate != str(learning_language).lower():
                    source_lang = candidate
                    break
        if source_lang:
            from application.curriculum.display.atcc_idiom_engine import build_atcc_hint_payload

            atcc_payload = build_atcc_hint_payload(
                technical_concepts=concept_ids,
                source_language=source_lang,
                target_language=str(learning_language),
            )

    return {
        "primary_technical_concept_id": primary_tc,
        "detected_technical_concepts": hints["technical_concepts"],
        "expected_concept_ids": concept_ids,
        "expected_concepts": cards,
        "concept_hierarchy": hierarchy_lines,
        "transfer_hints_by_language": transfer_by_language,
        "target_hints_ru": hints["target_hints_ru"],
        "concept_hints_ru": hints["concept_hints_ru"],
        **atcc_payload,
    }
