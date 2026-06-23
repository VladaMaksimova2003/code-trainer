"""Reusable Pascal hint engine: target hints + transfer hints by technical concept."""

from __future__ import annotations

from typing import Any

KNOWN_SOURCE_LANGUAGES: frozenset[str] = frozenset({"pascal", "python", "cpp", "java", "csharp"})

# 42 technical concepts used in Pascal curriculum showcase (102 slots).
SHOWCASE_TECHNICAL_CONCEPTS: frozenset[str] = frozenset(
    {
        "program_entry",
        "typed_declaration",
        "assignment",
        "arithmetic_ops",
        "stdin_read",
        "stdout_write",
        "simple_branch",
        "multi_branch",
        "switch_selection",
        "conditional_expression",
        "counted_loop",
        "pre_condition_loop",
        "post_condition_loop",
        "loop_control",
        "nested_iteration",
        "collection_iteration",
        "function_definition",
        "function_invocation",
        "return_flow",
        "indexed_sequence",
        "dynamic_array",
        "string_sequence",
        "key_value_map",
        "file_read",
        "file_write",
        "parameter_passing",
        "import_dependency",
        "module_namespace",
        "symbol_visibility",
        "recursion",
        "search_find",
        "filter_select",
        "fold_aggregate",
        "sort_order",
        "stack_queue",
        "linked_node",
        "tree_hierarchy",
        "graph_edges",
        "class_type",
        "object_instance",
        "method_dispatch",
        "inheritance_hierarchy",
    }
)

# Layer A — Pascal target hints (one focused hint per TC).
TARGET_HINTS_RU: dict[str, str] = {
    "program_entry": (
        "Точка входа: `program Name;` … `begin` … `end.` — обязательная обёртка программы на Pascal."
    ),
    "typed_declaration": (
        "Явный тип: `var a, b: integer;` — объявление переменных с типом перед `begin`."
    ),
    "assignment": (
        "В Pascal присваивание пишется через `:=`, а `=` используется для сравнения."
    ),
    "arithmetic_ops": (
        "Арифметика: `+`, `-`, `*`, `div` (целочисленное деление), `mod` (остаток)."
    ),
    "stdin_read": "Ввод с клавиатуры: `readln(x);` — читает значение в переменную `x`.",
    "stdout_write": "Вывод: `writeln(...);` — печатает аргументы и перевод строки.",
    "simple_branch": "Условие: `if условие then` … `else` … — ветвление без фигурных скобок.",
    "multi_branch": (
        "Цепочка условий: `if … then … else if … then … else …` — последовательная проверка."
    ),
    "switch_selection": (
        "Выбор по значению: `case x of` … `1: …` … `else` … `end;` — аналог switch."
    ),
    "conditional_expression": (
        "В Pascal нет тернарного `? :`; перепишите через `if … then … else …` в выражении."
    ),
    "counted_loop": "Счётный цикл: `for i := 1 to n do` — границы включаются (`to`).",
    "pre_condition_loop": "Цикл с условием в начале: `while условие do` … — может не выполниться ни разу.",
    "post_condition_loop": (
        "Цикл `repeat` … `until условие;` — тело выполняется минимум один раз."
    ),
    "loop_control": "Управление циклом: `break` / `continue` в Pascal часто заменяют флагом или `goto`.",
    "nested_iteration": "Вложенные циклы: каждый `for`/`while`/`repeat` имеет своё тело `begin` … `end`.",
    "collection_iteration": (
        "Обход коллекции: `for i := low to high do` по индексам массива или `for item in set`."
    ),
    "function_definition": (
        "Функция: `function Name(...): Type;` … `begin` … `Name := результат;` … `end;`."
    ),
    "function_invocation": "Вызов: `Name(аргументы);` — как процедура или функция.",
    "return_flow": (
        "В функции результат присваивают имени функции: `Sq := x * x;`, а не `return`."
    ),
    "indexed_sequence": (
        "Массив: `array[1..n] of integer` — индексация часто с 1; доступ `a[i]`."
    ),
    "dynamic_array": (
        "Динамический массив: `array of Type` + `SetLength(a, n);` перед использованием."
    ),
    "string_sequence": "Строка Pascal — массив символов; длина `Length(s)`, срез через индексы.",
    "key_value_map": (
        "Ассоциативная структура в базовом Pascal — массив/запись; TDictionary — в расширениях."
    ),
    "file_read": "Чтение файла: `Assign(f, 'path'); Reset(f);` … `Readln(f, x);` … `CloseFile(f);`.",
    "file_write": "Запись файла: `Assign(f, 'path'); Rewrite(f);` … `Writeln(f, x);` … `CloseFile(f);`.",
    "parameter_passing": (
        "Параметр по ссылке: `procedure P(var x: integer);` — изменения видны вызывающему."
    ),
    "import_dependency": (
        "Подключение модуля: `uses UnitName;` в секции `interface` или перед `program`."
    ),
    "module_namespace": "Модуль группирует процедуры/типы; обращение `UnitName.Proc` при необходимости.",
    "symbol_visibility": (
        "В `interface` — публичные объявления; в `implementation` — скрытая реализация."
    ),
    "recursion": (
        "Рекурсия: функция вызывает себя; базовый случай обязателен, иначе переполнение стека."
    ),
    "search_find": "Поиск: линейный проход `for i := 1 to n do if a[i] = key then …`.",
    "filter_select": "Фильтрация: цикл + `if` — собирайте элементы, удовлетворяющие условию.",
    "fold_aggregate": "Сумма/накопление: `sum := sum + a[i];` внутри цикла по элементам.",
    "sort_order": "Сортировка: в базовом Pascal — простые алгоритмы (пузырёк) или готовые процедуры.",
    "stack_queue": "Стек/очередь: массив + индекс `top` или `head`/`tail` для push/pop.",
    "linked_node": "Связный список: запись с полем `next: ^Node` — указатель на следующий узел.",
    "tree_hierarchy": "Дерево: узел с полями `left`, `right` или массив детей; обход рекурсией.",
    "graph_edges": "Граф: матрица смежности или список рёбер; обход BFS/DFS через очередь/стек.",
    "class_type": "Класс: `type TName = class` … `end;` — тип объекта с полями и методами.",
    "object_instance": (
        "Экземпляр: `obj := TName.Create;` … `obj.Free;` — создание и освобождение памяти."
    ),
    "method_dispatch": (
        "Метод класса: `function TName.Method(...): Type;` — вызов `obj.Method(...);`."
    ),
    "inheritance_hierarchy": (
        "Наследование: `type TChild = class(TParent)` — потомок наследует поля и методы родителя."
    ),
}

# Layer B — transfer hints (known language → Pascal).
_TRANSFER = TARGET_HINTS_RU  # shorthand alias for building below

TRANSFER_HINTS_RU: dict[str, dict[str, str]] = {
    "assignment": {
        "python": "Python `x = 1` → Pascal `x := 1;` (`=` только для сравнения).",
        "cpp": "C++ `x = 1;` → Pascal `x := 1;` (`=` только для сравнения).",
        "java": "Java `x = 1;` → Pascal `x := 1;` (`=` только для сравнения).",
        "csharp": "C# `x = 1;` → Pascal `x := 1;` (`=` только для сравнения).",
    },
    "simple_branch": {
        "python": "Python `if x: … else: …` → Pascal `if x then … else …`.",
        "cpp": "C++ `if (x) { … } else { … }` → Pascal `if x then begin … end else begin … end`.",
        "java": "Java `if (x) { … } else { … }` → Pascal `if x then begin … end else begin … end`.",
        "csharp": "C# `if (x) { … } else { … }` → Pascal `if x then begin … end else begin … end`.",
    },
    "multi_branch": {
        "python": "Python `elif` → Pascal `else if`.",
        "cpp": "C++ `else if` → Pascal `else if`.",
        "java": "Java `else if` → Pascal `else if`.",
        "csharp": "C# `else if` → Pascal `else if`.",
    },
    "switch_selection": {
        "python": "Python `match`/`elif` по значению → Pascal `case x of`.",
        "cpp": "C++ `switch (x)` → Pascal `case x of` … `end;`.",
        "java": "Java `switch (x)` → Pascal `case x of` … `end;`.",
        "csharp": "C# `switch (x)` → Pascal `case x of` … `end;`.",
    },
    "conditional_expression": {
        "python": "Python `a if cond else b` → Pascal `if cond then a else b`.",
        "cpp": "C++ `cond ? a : b` → Pascal `if cond then a else b`.",
        "java": "Java `cond ? a : b` → Pascal `if cond then a else b`.",
        "csharp": "C# `cond ? a : b` → Pascal `if cond then a else b`.",
    },
    "counted_loop": {
        "python": "Python `for i in range(1, n+1):` → Pascal `for i := 1 to n do`.",
        "cpp": "C++ `for (int i = 1; i <= n; ++i)` → Pascal `for i := 1 to n do`.",
        "java": "Java `for (int i = 1; i <= n; i++)` → Pascal `for i := 1 to n do`.",
        "csharp": "C# `for (int i = 1; i <= n; i++)` → Pascal `for i := 1 to n do`.",
    },
    "pre_condition_loop": {
        "python": "Python `while cond:` → Pascal `while cond do`.",
        "cpp": "C++ `while (cond)` → Pascal `while cond do`.",
        "java": "Java `while (cond)` → Pascal `while cond do`.",
        "csharp": "C# `while (cond)` → Pascal `while cond do`.",
    },
    "post_condition_loop": {
        "python": "Python `while True` + `break` → Pascal `repeat` … `until cond;`.",
        "cpp": "C++ `do { … } while (cond);` → Pascal `repeat` … `until cond;`.",
        "java": "Java `do { … } while (cond);` → Pascal `repeat` … `until cond;`.",
        "csharp": "C# `do { … } while (cond);` → Pascal `repeat` … `until cond;`.",
    },
    "collection_iteration": {
        "python": "Python `for x in items:` → Pascal цикл по индексам `for i := 1 to n do` или `for x in set`.",
        "cpp": "C++ range-for `for (auto x : v)` → Pascal `for i := low to high do` по массиву.",
        "java": "Java `for (T x : arr)` → Pascal `for i := 0 to Length(arr)-1 do` или индексы с 1.",
        "csharp": "C# `foreach (var x in arr)` → Pascal `for i := low to high do` по индексам массива.",
    },
    "nested_iteration": {
        "python": "Python вложенные `for` → Pascal вложенные `for i := … do for j := … do`.",
        "cpp": "C++ вложенные `for` → Pascal вложенные `for`/`while`.",
        "java": "Java вложенные `for` → Pascal вложенные `for`/`while`.",
        "csharp": "C# вложенные `for`/`foreach` → Pascal вложенные `for`.",
    },
    "loop_control": {
        "python": "Python `break`/`continue` → в Pascal используйте флаг или перестройте условие цикла.",
        "cpp": "C++ `break`/`continue` → в базовом Pascal часто заменяют флагом.",
        "java": "Java `break`/`continue` → в базовом Pascal часто заменяют флагом.",
        "csharp": "C# `break`/`continue` → в базовом Pascal часто заменяют флагом.",
    },
    "stdout_write": {
        "python": "Python `print(...)` → Pascal `writeln(...);`.",
        "cpp": "C++ `cout << …` → Pascal `writeln(...);`.",
        "java": "Java `System.out.println(...)` → Pascal `writeln(...);`.",
        "csharp": "C# `Console.WriteLine(...)` → Pascal `writeln(...);`.",
    },
    "stdin_read": {
        "python": "Python `input()` → Pascal `readln(x);`.",
        "cpp": "C++ `cin >> x` → Pascal `readln(x);`.",
        "java": "Java `Scanner` / `nextInt()` → Pascal `readln(x);`.",
        "csharp": "C# `Console.ReadLine()` → Pascal `readln(x);`.",
    },
    "program_entry": {
        "python": "Python скрипт без `main` → Pascal обязательно `program …; begin … end.`.",
        "cpp": "C++ `int main()` → Pascal `program …; begin … end.`.",
        "java": "Java `public static void main` → Pascal `program …; begin … end.`.",
        "csharp": "C# `static void Main` → Pascal `program …; begin … end.`.",
    },
    "typed_declaration": {
        "python": "Python без явного типа → Pascal `var x: integer;` перед `begin`.",
        "cpp": "C++ `int x;` → Pascal `var x: integer;`.",
        "java": "Java `int x;` → Pascal `var x: integer;`.",
        "csharp": "C# `int x;` → Pascal `var x: integer;`.",
    },
    "arithmetic_ops": {
        "python": "Python `//` → Pascal `div`; `%` → `mod`.",
        "cpp": "C++ `/` для целых → Pascal `div`; `%` → `mod`.",
        "java": "Java `/` для целых → Pascal `div`; `%` → `mod`.",
        "csharp": "C# `/` для целых → Pascal `div`; `%` → `mod`.",
    },
    "function_definition": {
        "python": "Python `def f(x): return …` → Pascal `function f(x: T): T;` + присвоение имени функции.",
        "cpp": "C++ `return` в функции → Pascal присвоение имени функции вместо `return`.",
        "java": "Java `return` → Pascal присвоение имени функции вместо `return`.",
        "csharp": "C# `return` → Pascal присвоение имени функции вместо `return`.",
    },
    "function_invocation": {
        "python": "Python `f(x)` → Pascal `f(x);` — тот же синтаксис вызова.",
        "cpp": "C++ `f(x);` → Pascal `f(x);`.",
        "java": "Java `f(x);` → Pascal `f(x);`.",
        "csharp": "C# `f(x);` → Pascal `f(x);`.",
    },
    "return_flow": {
        "python": "Python `return x` → Pascal `FunctionName := x;` (без `return`).",
        "cpp": "C++ `return x;` → Pascal `FunctionName := x;`.",
        "java": "Java `return x;` → Pascal `FunctionName := x;`.",
        "csharp": "C# `return x;` → Pascal `FunctionName := x;`.",
    },
    "indexed_sequence": {
        "python": "Python `list[i]` (с 0) → Pascal `a[i+1]` или объявите `array[1..n]`.",
        "cpp": "C++ `arr[i]` (с 0) → Pascal `a[i+1]` или массив с базой 1.",
        "java": "Java `arr[i]` (с 0) → Pascal `a[i+1]` или массив с базой 1.",
        "csharp": "C# `arr[i]` (с 0) → Pascal `a[i+1]` или массив с базой 1.",
    },
    "dynamic_array": {
        "python": "Python динамический `list` → Pascal `array of T` + `SetLength`.",
        "cpp": "C++ `vector<T>` → Pascal `array of T` + `SetLength`.",
        "java": "Java `ArrayList` → Pascal `array of T` + `SetLength` или фиксированный массив.",
        "csharp": "C# `List<T>` → Pascal `array of T` + `SetLength`.",
    },
    "string_sequence": {
        "python": "Python `str` / `len(s)` → Pascal `string` / `Length(s)`.",
        "cpp": "C++ `std::string` → Pascal `string`.",
        "java": "Java `String` → Pascal `string`.",
        "csharp": "C# `string` → Pascal `string`.",
    },
    "key_value_map": {
        "python": "Python `dict` → Pascal массив/запись или `TDictionary` (расширения).",
        "cpp": "C++ `map`/`unordered_map` → Pascal массив пар или расширения.",
        "java": "Java `HashMap` → Pascal массив/запись или расширения.",
        "csharp": "C# `Dictionary` → Pascal массив/запись или расширения.",
    },
    "file_read": {
        "python": "Python `open(...).read()` → Pascal `Assign; Reset; Readln; CloseFile`.",
        "cpp": "C++ `ifstream` → Pascal `Assign; Reset; Readln; CloseFile`.",
        "java": "Java `Files.read` → Pascal `Assign; Reset; Readln; CloseFile`.",
        "csharp": "C# `File.ReadAllText` → Pascal `Assign; Reset; Readln; CloseFile`.",
    },
    "file_write": {
        "python": "Python `open(..., 'w')` → Pascal `Assign; Rewrite; Writeln; CloseFile`.",
        "cpp": "C++ `ofstream` → Pascal `Assign; Rewrite; Writeln; CloseFile`.",
        "java": "Java `Files.write` → Pascal `Assign; Rewrite; Writeln; CloseFile`.",
        "csharp": "C# `File.WriteAllText` → Pascal `Assign; Rewrite; Writeln; CloseFile`.",
    },
    "parameter_passing": {
        "python": "Python изменяет объект по ссылке → Pascal `var` в параметре процедуры.",
        "cpp": "C++ ссылка `int&` → Pascal `var x: integer`.",
        "java": "Java примитивы по значению → Pascal `var` для изменения аргумента.",
        "csharp": "C# `ref`/`out` → Pascal `var` в параметре.",
    },
    "import_dependency": {
        "python": "Python `import module` → Pascal `uses UnitName;`.",
        "cpp": "C++ `#include` → Pascal `uses UnitName;`.",
        "java": "Java `import pkg.Class` → Pascal `uses UnitName;`.",
        "csharp": "C# `using Namespace` → Pascal `uses UnitName;`.",
    },
    "module_namespace": {
        "python": "Python модуль как файл → Pascal unit с `interface`/`implementation`.",
        "cpp": "C++ namespace → Pascal unit + префикс имени.",
        "java": "Java package → Pascal unit.",
        "csharp": "C# namespace → Pascal unit.",
    },
    "symbol_visibility": {
        "python": "Python `_private` по соглашению → Pascal `interface`/`implementation`.",
        "cpp": "C++ `static`/anonymous namespace → Pascal `implementation`.",
        "java": "Java `private` → Pascal скрыто в `implementation`.",
        "csharp": "C# `private` → Pascal скрыто в `implementation`.",
    },
    "recursion": {
        "python": "Python рекурсивный `def` → Pascal `function` с вызовом себя и базовым случаем.",
        "cpp": "C++ рекурсивная функция → Pascal `function` с базовым случаем.",
        "java": "Java рекурсивный метод → Pascal `function` с базовым случаем.",
        "csharp": "C# рекурсивный метод → Pascal `function` с базовым случаем.",
    },
    "search_find": {
        "python": "Python `x in list` / цикл → Pascal линейный `for` + `if a[i] = key`.",
        "cpp": "C++ `std::find` → Pascal линейный проход по массиву.",
        "java": "Java `indexOf` / цикл по массиву → Pascal `for` + `if a[i] = target`.",
        "csharp": "C# `Array.Find` → Pascal цикл + `if`.",
    },
    "filter_select": {
        "python": "Python list comprehension → Pascal цикл + `if` + накопление.",
        "cpp": "C++ `copy_if` → Pascal цикл + `if`.",
        "java": "Java `stream.filter` → Pascal цикл + `if`.",
        "csharp": "C# `Where` → Pascal цикл + `if`.",
    },
    "fold_aggregate": {
        "python": "Python `sum(...)` → Pascal `sum := sum + a[i];` в цикле.",
        "cpp": "C++ `accumulate` → Pascal накопление в цикле.",
        "java": "Java `stream.reduce` → Pascal накопление в цикле.",
        "csharp": "C# `Aggregate` → Pascal накопление в цикле.",
    },
    "sort_order": {
        "python": "Python `sorted()` → Pascal процедура сортировки или встроенные расширения.",
        "cpp": "C++ `std::sort` → Pascal процедура сортировки.",
        "java": "Java `Arrays.sort` → Pascal процедура сортировки.",
        "csharp": "C# `Array.Sort` → Pascal процедура сортировки.",
    },
    "stack_queue": {
        "python": "Python `list.append/pop` → Pascal массив + индекс вершины стека.",
        "cpp": "C++ `stack`/`queue` → Pascal массив + индексы.",
        "java": "Java `Deque` → Pascal массив + индексы.",
        "csharp": "C# `Stack`/`Queue` → Pascal массив + индексы.",
    },
    "linked_node": {
        "python": "Python класс с `next` → Pascal запись `^Node` с полем `next`.",
        "cpp": "C++ `struct Node*` → Pascal `^Node`.",
        "java": "Java `Node next` → Pascal `next: ^Node`.",
        "csharp": "C# `Node Next` → Pascal `next: ^Node`.",
    },
    "tree_hierarchy": {
        "python": "Python дерево через классы → Pascal `class`/`record` с `left`/`right`.",
        "cpp": "C++ указатели на узлы → Pascal `^Node`.",
        "java": "Java `TreeNode` → Pascal класс/запись с дочерними ссылками.",
        "csharp": "C# `TreeNode` → Pascal класс с полями детей.",
    },
    "graph_edges": {
        "python": "Python `dict` смежности → Pascal матрица или список рёбер.",
        "cpp": "C++ `vector<vector<int>>` → Pascal `array`/`array of`.",
        "java": "Java `List<List<Integer>>` → Pascal двумерный массив.",
        "csharp": "C# `List<List<int>>` → Pascal двумерный массив.",
    },
    "class_type": {
        "python": "Python `class T:` → Pascal `type T = class` … `end;`.",
        "cpp": "C++ `class T` → Pascal `type T = class`.",
        "java": "Java `class T` → Pascal `type T = class`.",
        "csharp": "C# `class T` → Pascal `type T = class`.",
    },
    "object_instance": {
        "python": "Python `T()` → Pascal `T.Create` … `Free`.",
        "cpp": "C++ `new T()` → Pascal `T.Create` … `Free`.",
        "java": "Java `new T()` → Pascal `T.Create` … `Free`.",
        "csharp": "C# `new T()` → Pascal `T.Create` … `Free`.",
    },
    "method_dispatch": {
        "python": "Python `obj.method()` → Pascal `obj.Method();`.",
        "cpp": "C++ `obj.method()` → Pascal `obj.Method();`.",
        "java": "Java `obj.method()` → Pascal `obj.Method();`.",
        "csharp": "C# `obj.Method()` → Pascal `obj.Method();`.",
    },
    "inheritance_hierarchy": {
        "python": "Python `class Child(Parent)` → Pascal `type TChild = class(TParent)`.",
        "cpp": "C++ `: public Base` → Pascal `class(TBase)`.",
        "java": "Java `extends Base` → Pascal `class(TBase)`.",
        "csharp": "C# `: Base` → Pascal `class(TBase)`.",
    },
}

# Remove unused alias
del _TRANSFER

GENERIC_BEGIN_END_ONLY = "`begin` / `end` — блок кода."


def target_hint_for_tc(technical_concept_id: str) -> str | None:
    return TARGET_HINTS_RU.get(technical_concept_id)


def transfer_hint_for_tc(
    source_language: str,
    technical_concept_id: str,
) -> str | None:
    lang = str(source_language or "").lower()
    if lang not in KNOWN_SOURCE_LANGUAGES:
        return None
    return TRANSFER_HINTS_RU.get(technical_concept_id, {}).get(lang)


def build_hint_payload(
    *,
    technical_concepts: list[str],
    known_languages: list[str] | None = None,
) -> dict[str, Any]:
    """Build API payload with target + transfer hint layers."""
    ordered_tcs: list[str] = []
    seen: set[str] = set()
    for tc in technical_concepts:
        tc_id = str(tc).strip()
        if not tc_id or tc_id in seen:
            continue
        if tc_id not in SHOWCASE_TECHNICAL_CONCEPTS:
            continue
        seen.add(tc_id)
        ordered_tcs.append(tc_id)

    target_hints = [
        {"concept_id": tc, "text": hint}
        for tc in ordered_tcs
        if (hint := target_hint_for_tc(tc))
    ]
    transfer_by_language: dict[str, list[dict[str, str]]] = {}
    langs = known_languages or list(KNOWN_SOURCE_LANGUAGES)
    for lang in langs:
        lang_key = str(lang).lower()
        if lang_key not in KNOWN_SOURCE_LANGUAGES:
            continue
        items = [
            {"concept_id": tc, "text": hint}
            for tc in ordered_tcs
            if (hint := transfer_hint_for_tc(lang_key, tc))
        ]
        if items:
            transfer_by_language[lang_key] = items

    # Legacy flat list — target texts only (no generic begin/end fallback).
    concept_hints_ru = [item["text"] for item in target_hints]

    return {
        "technical_concepts": ordered_tcs,
        "target_hints_ru": target_hints,
        "transfer_hints_by_language": transfer_by_language,
        "concept_hints_ru": concept_hints_ru,
    }
