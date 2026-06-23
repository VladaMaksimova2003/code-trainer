"""Generate tc_display_registry.json — pedagogical TC bundles with hints for 5 languages."""

from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.validation.technical_concept_registry import normalize_display_card
OUT = BACKEND_ROOT / "resources" / "curriculum" / "tc_display_registry.json"

LANGS = ("pascal", "python", "cpp", "csharp", "java")


def tc(
    tc_id: str,
    name_ru: str,
    description_ru: str,
    technical_concept_ids: list[str],
    hints_by_language: dict[str, list[dict]],
) -> dict:
    return {
        "id": tc_id,
        "name_ru": name_ru,
        "description_ru": description_ru,
        "technical_concept_ids": technical_concept_ids,
        "hints_by_language": hints_by_language,
    }


def h(title: str, illustrates: list[str], code: str) -> dict:
    return {"title": title, "illustrates": illustrates, "code": code.strip()}


def _validate_registry(registry: dict[str, dict]) -> None:
    """Reject common typos in pedagogical code samples before writing JSON."""
    bad_patterns = (
        "array[1.100",
        "array[1.10",
        "array[1.1000",
    )
    for tc_id, card in registry.items():
        hints = card.get("hints_by_language") or {}
        for lang, rows in hints.items():
            for row in rows:
                code = str(row.get("code") or "")
                for pattern in bad_patterns:
                    if pattern in code.replace(" ", ""):
                        raise ValueError(
                            f"{tc_id}/{lang}/{row.get('title')}: invalid Pascal range {pattern!r}"
                        )


REGISTRY: dict[str, dict] = {
    "tc_program_structure": tc(
        "tc_program_structure",
        "Структура программы",
        "Каркас программы: точка входа, основной исполняемый блок и разделение объявлений от действий.",
        [
            "program_entry",
            "block_scope",
            "ast_program_root",
            "ast_main_entry",
            "pas_program_begin_end",
            "py_script_top_level",
            "py_main_guard",
            "cpp_main_return",
            "cs_top_level_statements",
            "java_public_static_main",
            "ast_compound_statement",
        ],
        {
            "pascal": [
                h("Минимальная программа", ["program_entry", "pas_program_begin_end"], "program Hello;\nbegin\n  writeln('Hello');\nend."),
                h("Секция var перед begin", ["block_scope", "typed_declaration"], "program Demo;\nvar\n  x: integer;\nbegin\n  x := 10;\nend."),
                h("Вызов процедуры из main", ["program_entry", "function_invocation"], "procedure Run;\nbegin\n  writeln('Run');\nend;\nbegin\n  Run;\nend."),
            ],
            "python": [
                h("Скрипт сверху вниз", ["py_script_top_level", "program_entry"], "print('Hello')\nx = 10"),
                h("Функция main", ["ast_main_entry"], "def main():\n    print('Hello')\n\nmain()"),
                h("Защита точки входа", ["py_main_guard"], "def main():\n    print('Hello')\n\nif __name__ == '__main__':\n    main()"),
            ],
            "cpp": [
                h("Классическая main", ["cpp_main_return", "ast_main_entry"], "#include <iostream>\n\nint main()\n{\n    std::cout << \"Hello\";\n    return 0;\n}"),
                h("main вызывает функцию", ["ast_compound_statement"], "void run() { std::cout << \"Run\"; }\n\nint main() { run(); return 0; }"),
                h("Локальный блок в main", ["block_scope"], "int main()\n{\n    int x = 10;\n    std::cout << x;\n    return 0;\n}"),
            ],
            "csharp": [
                h("Класс + Main", ["program_entry", "ast_main_entry"], "class Program\n{\n    static void Main()\n    {\n        Console.WriteLine(\"Hello\");\n    }\n}"),
                h("Top-level statements", ["cs_top_level_statements"], "using System;\nConsole.WriteLine(\"Hello\");"),
                h("Main с аргументами", ["parameter_passing"], "static void Main(string[] args)\n{\n    Console.WriteLine(args.Length);\n}"),
            ],
            "java": [
                h("Класс с main", ["java_public_static_main"], "class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Hello\");\n    }\n}"),
                h("main вызывает метод", ["ast_compound_statement"], "static void run() { System.out.println(\"Run\"); }\n\npublic static void main(String[] args) { run(); }"),
                h("Локальные переменные", ["block_scope"], "public static void main(String[] args) {\n    int x = 10;\n    System.out.println(x);\n}"),
            ],
        },
    ),
    "tc_variables_types": tc(
        "tc_variables_types",
        "Переменные и типы",
        "Именованные ячейки для данных: объявление имени и типа (явно или неявно), константы.",
        [
            "typed_declaration",
            "ast_variable_declaration",
            "ast_const_declaration",
            "pas_var_const_type",
            "pas_typed_field",
            "py_simple_binding",
            "py_type_annotation",
            "cpp_typed_decl",
            "cs_var_decl",
            "java_field_decl",
            "symbol_visibility",
        ],
        {
            "pascal": [
                h("Целое число", ["typed_declaration"], "var age: integer;"),
                h("Несколько переменных", ["pas_var_const_type"], "var a, b, sum: integer;"),
                h("Константа", ["ast_const_declaration"], "const MaxCount = 100;"),
                h("Разные типы", ["pas_typed_field"], "var\n  count: integer;\n  price: real;\n  name: string;"),
            ],
            "python": [
                h("Первая запись", ["py_simple_binding"], "age = 18\nname = 'Ann'"),
                h("Аннотация типа", ["py_type_annotation"], "age: int = 18\nprice: float = 12.5"),
                h("Несколько имён", ["py_simple_binding"], "a, b, total = 1, 2, 0"),
                h("Константа по соглашению", ["symbol_visibility"], "MAX_COUNT = 100"),
            ],
            "cpp": [
                h("Целое и вещественное", ["cpp_typed_decl"], "int age = 18;\ndouble price = 12.5;"),
                h("Строка", ["cpp_typed_decl"], "std::string name = \"Ann\";"),
                h("Константа", ["ast_const_declaration"], "const double PI = 3.14;"),
                h("Логический тип", ["typed_declaration"], "bool isReady = true;"),
            ],
            "csharp": [
                h("Явный тип", ["cs_var_decl"], "int age = 18;\ndouble price = 12.5;"),
                h("Вывод типа var", ["cs_var_decl"], "var count = 10;\nvar name = \"Ann\";"),
                h("Константа", ["ast_const_declaration"], "const double Pi = 3.14;"),
                h("Несколько переменных", ["cs_var_decl"], "int a = 1, b = 2, sum = 0;"),
            ],
            "java": [
                h("Локальная переменная", ["java_field_decl"], "int age = 18;\ndouble price = 12.5;"),
                h("Строка", ["typed_declaration"], "String name = \"Ann\";"),
                h("Константа final", ["ast_const_declaration"], "final double PI = 3.14;"),
                h("Логический тип", ["typed_declaration"], "boolean isReady = true;"),
            ],
        },
    ),
    "tc_assignment": tc(
        "tc_assignment",
        "Присваивание",
        "Запись нового значения в переменную: инициализация, обновление, накопление, обмен.",
        [
            "assignment",
            "ast_assignment",
            "ast_augmented_assignment",
            "pas_assign_colon_eq",
            "py_assign",
            "cpp_assign",
            "cs_assign",
            "java_assign",
            "field_access",
        ],
        {
            "pascal": [
                h("Простое", ["pas_assign_colon_eq"], "x := 10;"),
                h("Выражение", ["assignment"], "sum := a + b;"),
                h("Инкремент", ["ast_augmented_assignment"], "x := x + 1;"),
                h("Обмен", ["assignment"], "temp := a;\na := b;\nb := temp;"),
            ],
            "python": [
                h("Простое", ["py_assign"], "x = 10"),
                h("Составное +=", ["ast_augmented_assignment"], "x += 1\ntotal += price"),
                h("Обмен", ["assignment"], "a, b = b, a"),
                h("Атрибут объекта", ["field_access"], "self.name = name"),
            ],
            "cpp": [
                h("Простое", ["cpp_assign"], "x = 10;"),
                h("Составное", ["ast_augmented_assignment"], "x++;\ntotal += price;"),
                h("Обмен", ["assignment"], "int temp = a;\na = b;\nb = temp;"),
                h("Поле структуры", ["field_access"], "point.x = 10;"),
            ],
            "csharp": [
                h("Простое", ["cs_assign"], "x = 10;"),
                h("Составное", ["ast_augmented_assignment"], "x++;\ntotal += price;"),
                h("Обмен", ["assignment"], "int temp = a;\na = b;\nb = temp;"),
                h("Свойство", ["field_access"], "person.Name = \"Ann\";"),
            ],
            "java": [
                h("Простое", ["java_assign"], "x = 10;"),
                h("Составное", ["ast_augmented_assignment"], "x++;\ntotal += price;"),
                h("Обмен", ["assignment"], "int temp = a;\na = b;\nb = temp;"),
                h("Поле объекта", ["field_access"], "person.name = \"Ann\";"),
            ],
        },
    ),
    "tc_arithmetic": tc(
        "tc_arithmetic",
        "Арифметика и операции",
        "Числовые вычисления, сравнения, логические операции и тернарный выбор в выражении.",
        [
            "arithmetic_ops",
            "ast_binary_arithmetic",
            "ast_unary_arithmetic",
            "ast_relational_ops",
            "ast_logical_ops",
            "pas_div_mod",
            "conditional_expression",
        ],
        {
            "pascal": [
                h("Сумма и произведение", ["arithmetic_ops"], "result := a + b * c;"),
                h("div и mod", ["pas_div_mod"], "q := a div b;\nr := a mod b;"),
                h("Сравнение", ["ast_relational_ops"], "if x > 0 then writeln('ok');"),
                h("Тернарный if", ["conditional_expression"], "sign := 1;\nif x < 0 then sign := -1;"),
            ],
            "python": [
                h("Арифметика", ["ast_binary_arithmetic"], "result = a + b * c"),
                h("Целочисленное // и %", ["arithmetic_ops"], "q = a // b\nr = a % b"),
                h("Сравнение", ["ast_relational_ops"], "if x > 0:\n    print('ok')"),
                h("Тернарное выражение", ["conditional_expression"], "sign = 1 if x >= 0 else -1"),
            ],
            "cpp": [
                h("Арифметика", ["ast_binary_arithmetic"], "int result = a + b * c;"),
                h("Остаток %", ["arithmetic_ops"], "int r = a % b;"),
                h("Логика", ["ast_logical_ops"], "if (x > 0 && ready) { }"),
                h("Тернарный оператор", ["conditional_expression"], "int sign = (x >= 0) ? 1 : -1;"),
            ],
            "csharp": [
                h("Арифметика", ["ast_binary_arithmetic"], "int result = a + b * c;"),
                h("Остаток", ["arithmetic_ops"], "int r = a % b;"),
                h("Логика", ["ast_logical_ops"], "if (x > 0 && ready) { }"),
                h("Тернарный ?:", ["conditional_expression"], "int sign = x >= 0 ? 1 : -1;"),
            ],
            "java": [
                h("Арифметика", ["ast_binary_arithmetic"], "int result = a + b * c;"),
                h("Остаток", ["arithmetic_ops"], "int r = a % b;"),
                h("Логика", ["ast_logical_ops"], "if (x > 0 && ready) { }"),
                h("Тернарный ?:", ["conditional_expression"], "int sign = x >= 0 ? 1 : -1;"),
            ],
        },
    ),
    "tc_console_io": tc(
        "tc_console_io",
        "Ввод и вывод (консоль)",
        "Чтение данных с клавиатуры и вывод результата в консоль.",
        ["stdin_read", "stdout_write", "ast_io_call", "pas_readln_writeln", "py_input_print", "cpp_cin_cout", "cs_console_read_write", "java_scanner_system_out", "io"],
        {
            "pascal": [
                h("Вывод строки", ["stdout_write", "pas_readln_writeln"], "writeln('Result = ', x);"),
                h("Ввод числа", ["stdin_read"], "readln(n);"),
                h("Ввод и вывод", ["stdin_read", "stdout_write"], "readln(a, b);\nwriteln(a + b);"),
            ],
            "python": [
                h("print", ["stdout_write", "py_input_print"], "print('Result =', x)"),
                h("input", ["stdin_read"], "n = int(input())"),
                h("Ввод и вывод", ["stdin_read", "stdout_write"], "a = int(input())\nb = int(input())\nprint(a + b)"),
            ],
            "cpp": [
                h("cout", ["stdout_write", "cpp_cin_cout"], "std::cout << \"Result = \" << x;"),
                h("cin", ["stdin_read"], "int n;\nstd::cin >> n;"),
                h("Ввод и вывод", ["stdin_read", "stdout_write"], "int a, b;\nstd::cin >> a >> b;\nstd::cout << a + b;"),
            ],
            "csharp": [
                h("WriteLine", ["stdout_write"], "Console.WriteLine($\"Result = {x}\");"),
                h("ReadLine", ["stdin_read"], "int n = int.Parse(Console.ReadLine());"),
                h("Ввод и вывод", ["stdin_read", "stdout_write"], "int a = int.Parse(Console.ReadLine());\nint b = int.Parse(Console.ReadLine());\nConsole.WriteLine(a + b);"),
            ],
            "java": [
                h("System.out", ["stdout_write"], "System.out.println(\"Result = \" + x);"),
                h("Scanner", ["stdin_read"], "Scanner sc = new Scanner(System.in);\nint n = sc.nextInt();"),
                h("Ввод и вывод", ["stdin_read", "stdout_write"], "Scanner sc = new Scanner(System.in);\nint a = sc.nextInt(), b = sc.nextInt();\nSystem.out.println(a + b);"),
            ],
        },
    ),
    "tc_loops": tc(
        "tc_loops",
        "Циклы",
        "Повторение блока кода: счётный цикл, while, do-while, foreach, вложенные циклы, break/continue.",
        [
            "ast_for_c", "ast_while", "ast_do_while", "ast_foreach", "for_counted", "for_collection",
            "counted_loop", "pre_condition_loop", "post_condition_loop", "collection_iteration",
            "pas_for_to_downto", "pas_repeat_until", "py_for_in", "py_while", "cpp_range_for",
            "cs_foreach", "java_enhanced_for", "ast_nested_loops", "nested_iteration", "nested_loops",
            "ast_break_continue", "loop_control",
        ],
        {
            "pascal": [
                h("for to", ["counted_loop", "pas_for_to_downto"], "for i := 1 to n do\n  writeln(i);"),
                h("while", ["pre_condition_loop"], "while x > 0 do\nbegin\n  x := x div 2;\nend;"),
                h("repeat until", ["post_condition_loop", "pas_repeat_until"], "repeat\n  readln(x);\nuntil x = 0;"),
                h("break / exit", ["loop_control", "ast_break_continue"], "for i := 1 to 10 do\n  if i = 5 then break;"),
            ],
            "python": [
                h("for range", ["counted_loop", "py_for_in"], "for i in range(n):\n    print(i)"),
                h("for in", ["collection_iteration"], "for item in items:\n    print(item)"),
                h("while", ["pre_condition_loop", "py_while"], "while x > 0:\n    x //= 2"),
                h("break / continue", ["loop_control"], "for i in range(10):\n    if i == 5:\n        break"),
            ],
            "cpp": [
                h("for C-style", ["counted_loop", "ast_for_c"], "for (int i = 0; i < n; ++i)\n    std::cout << i;"),
                h("while", ["pre_condition_loop"], "while (x > 0) x /= 2;"),
                h("do-while", ["post_condition_loop", "ast_do_while"], "do { std::cin >> x; } while (x != 0);"),
                h("range-for", ["cpp_range_for", "collection_iteration"], "for (int v : arr)\n    sum += v;"),
            ],
            "csharp": [
                h("for", ["counted_loop"], "for (int i = 0; i < n; i++)\n    Console.WriteLine(i);"),
                h("while", ["pre_condition_loop"], "while (x > 0) x /= 2;"),
                h("foreach", ["cs_foreach", "collection_iteration"], "foreach (var item in items)\n    Console.WriteLine(item);"),
                h("break", ["loop_control"], "for (int i = 0; i < 10; i++)\n    if (i == 5) break;"),
            ],
            "java": [
                h("for", ["counted_loop"], "for (int i = 0; i < n; i++)\n    System.out.println(i);"),
                h("while", ["pre_condition_loop"], "while (x > 0) x /= 2;"),
                h("enhanced for", ["java_enhanced_for"], "for (int v : arr)\n    sum += v;"),
                h("break", ["loop_control"], "for (int i = 0; i < 10; i++)\n    if (i == 5) break;"),
            ],
        },
    ),
    "tc_conditionals": tc(
        "tc_conditionals",
        "Условия и ветвление",
        "Выбор действия по условию: if, else if, else.",
        ["simple_branch", "multi_branch", "ast_if_statement", "ast_if_else_chain", "pas_if_then_else", "py_if_elif", "condition"],
        {
            "pascal": [
                h("if then", ["simple_branch"], "if x > 0 then\n  writeln('positive');"),
                h("if else", ["simple_branch"], "if x > 0 then writeln('+') else writeln('-');"),
                h("else if", ["multi_branch"], "if x > 0 then writeln('+')\nelse if x = 0 then writeln('0')\nelse writeln('-');"),
            ],
            "python": [
                h("if", ["simple_branch", "py_if_elif"], "if x > 0:\n    print('positive')"),
                h("if else", ["simple_branch"], "if x > 0:\n    print('+')\nelse:\n    print('-')"),
                h("elif", ["multi_branch"], "if x > 0:\n    print('+')\nelif x == 0:\n    print('0')\nelse:\n    print('-')"),
            ],
            "cpp": [
                h("if", ["simple_branch"], "if (x > 0) std::cout << \"+\";"),
                h("if else", ["simple_branch"], "if (x > 0) std::cout << \"+\";\nelse std::cout << \"-\";"),
                h("else if", ["multi_branch"], "if (x > 0) {}\nelse if (x == 0) {}\nelse {}"),
            ],
            "csharp": [
                h("if", ["simple_branch"], "if (x > 0) Console.WriteLine(\"+\");"),
                h("if else", ["simple_branch"], "if (x > 0) Console.WriteLine(\"+\");\nelse Console.WriteLine(\"-\");"),
                h("else if", ["multi_branch"], "if (x > 0) { }\nelse if (x == 0) { }\nelse { }"),
            ],
            "java": [
                h("if", ["simple_branch"], "if (x > 0) System.out.println(\"+\");"),
                h("if else", ["simple_branch"], "if (x > 0) System.out.println(\"+\");\nelse System.out.println(\"-\");"),
                h("else if", ["multi_branch"], "if (x > 0) { }\nelse if (x == 0) { }\nelse { }"),
            ],
        },
    ),
    "tc_switch_selection": tc(
        "tc_switch_selection",
        "Выбор по значению",
        "Множественный выбор одного варианта: case, switch, match.",
        ["switch_selection", "ast_switch", "ast_case_label", "pas_case_of", "py_match_case", "cpp_switch_case", "cs_switch_pattern", "java_switch_case", "ast_default_branch"],
        {
            "pascal": [
                h("case of", ["pas_case_of"], "case day of\n  1: writeln('Mon');\n  2: writeln('Tue');\nelse writeln('?');\nend;"),
                h("case с диапазоном", ["switch_selection"], "case score of\n  90..100: writeln('A');\nelse writeln('B');\nend;"),
            ],
            "python": [
                h("match case", ["py_match_case"], "match day:\n    case 1: print('Mon')\n    case 2: print('Tue')\n    case _: print('?')"),
                h("match по строке", ["switch_selection"], "match cmd:\n    case 'start': run()\n    case 'stop': stop()"),
            ],
            "cpp": [
                h("switch", ["cpp_switch_case"], "switch (day) {\ncase 1: std::cout << \"Mon\"; break;\ncase 2: std::cout << \"Tue\"; break;\ndefault: break;\n}"),
                h("if/else chain", ["switch_selection"], "if (day == 1) std::cout << \"Mon\";\nelse if (day == 2) std::cout << \"Tue\";"),
            ],
            "csharp": [
                h("switch", ["cs_switch_pattern"], "switch (day) {\n    case 1: Console.WriteLine(\"Mon\"); break;\n    case 2: Console.WriteLine(\"Tue\"); break;\n    default: break;\n}"),
                h("switch expression", ["switch_selection"], "string label = day switch { 1 => \"Mon\", 2 => \"Tue\", _ => \"?\" };"),
            ],
            "java": [
                h("switch", ["java_switch_case"], "switch (day) {\n    case 1: System.out.println(\"Mon\"); break;\n    case 2: System.out.println(\"Tue\"); break;\n    default: break;\n}"),
                h("switch arrow", ["switch_selection"], "switch (day) {\n    case 1 -> System.out.println(\"Mon\");\n    case 2 -> System.out.println(\"Tue\");\n    default -> System.out.println(\"?\");\n}"),
            ],
        },
    ),
    "tc_functions": tc(
        "tc_functions",
        "Функции и процедуры",
        "Именованный блок кода для повторного использования: объявление и вызов.",
        ["function_definition", "function_invocation", "ast_function_definition", "ast_call_expression", "pas_function_procedure", "py_def", "function"],
        {
            "pascal": [
                h("procedure", ["pas_function_procedure"], "procedure Greet;\nbegin\n  writeln('Hi');\nend;"),
                h("function", ["function_definition"], "function Sqr(x: integer): integer;\nbegin\n  Sqr := x * x;\nend;"),
                h("Вызов", ["function_invocation"], "Greet;\ny := Sqr(5);"),
            ],
            "python": [
                h("def", ["py_def"], "def greet():\n    print('Hi')"),
                h("def с return", ["function_definition"], "def sqr(x):\n    return x * x"),
                h("Вызов", ["function_invocation"], "greet()\ny = sqr(5)"),
            ],
            "cpp": [
                h("void функция", ["function_definition"], "void greet() { std::cout << \"Hi\"; }"),
                h("Функция с типом", ["function_definition"], "int sqr(int x) { return x * x; }"),
                h("Вызов", ["function_invocation"], "greet();\nint y = sqr(5);"),
            ],
            "csharp": [
                h("static void", ["function_definition"], "static void Greet() { Console.WriteLine(\"Hi\"); }"),
                h("static int", ["function_definition"], "static int Sqr(int x) => x * x;"),
                h("Вызов", ["function_invocation"], "Greet();\nint y = Sqr(5);"),
            ],
            "java": [
                h("void метод", ["function_definition"], "static void greet() { System.out.println(\"Hi\"); }"),
                h("Метод с return", ["function_definition"], "static int sqr(int x) { return x * x; }"),
                h("Вызов", ["function_invocation"], "greet();\nint y = sqr(5);"),
            ],
        },
    ),
    "tc_parameters_return": tc(
        "tc_parameters_return",
        "Параметры и возврат",
        "Передача данных в функцию и возврат результата.",
        ["parameter_passing", "return_flow", "ast_parameter_list", "ast_return_statement", "pas_value_var_ref", "py_default_args"],
        {
            "pascal": [
                h("Параметры procedure", ["parameter_passing"], "procedure Add(a, b: integer; var sum: integer);\nbegin\n  sum := a + b;\nend;"),
                h("Result", ["return_flow"], "function Max(a, b: integer): integer;\nbegin\n  if a > b then Max := a else Max := b;\nend;"),
            ],
            "python": [
                h("Параметры", ["parameter_passing"], "def add(a, b):\n    return a + b"),
                h("Значение по умолчанию", ["py_default_args"], "def greet(name='Guest'):\n    print(name)"),
                h("return", ["return_flow"], "def max2(a, b):\n    return a if a > b else b"),
            ],
            "cpp": [
                h("Параметры по значению", ["parameter_passing"], "int add(int a, int b) { return a + b; }"),
                h("return", ["return_flow"], "int max2(int a, int b) { return a > b ? a : b; }"),
                h("Ссылка", ["pas_value_var_ref"], "void inc(int& x) { ++x; }"),
            ],
            "csharp": [
                h("Параметры", ["parameter_passing"], "static int Add(int a, int b) => a + b;"),
                h("out", ["parameter_passing"], "static bool TryParse(string s, out int n) => int.TryParse(s, out n);"),
                h("return", ["return_flow"], "static int Max2(int a, int b) => a > b ? a : b;"),
            ],
            "java": [
                h("Параметры", ["parameter_passing"], "static int add(int a, int b) { return a + b; }"),
                h("return", ["return_flow"], "static int max2(int a, int b) { return a > b ? a : b; }"),
                h("varargs", ["parameter_passing"], "static int sum(int... nums) { int s = 0; for (int n : nums) s += n; return s; }"),
            ],
        },
    ),
    "tc_recursion": tc(
        "tc_recursion",
        "Рекурсия",
        "Функция вызывает саму себя; обязательны базовый случай и шаг к нему.",
        ["recursion", "ast_self_call", "ast_base_case_branch", "pas_result_recursion", "py_recursive_def"],
        {
            "pascal": [
                h("Факториал", ["recursion", "pas_result_recursion"], "function Fact(n: integer): integer;\nbegin\n  if n <= 1 then Fact := 1\n  else Fact := n * Fact(n - 1);\nend;"),
                h("Fibonacci", ["ast_self_call"], "function Fib(n: integer): integer;\nbegin\n  if n <= 1 then Fib := n\n  else Fib := Fib(n-1) + Fib(n-2);\nend;"),
            ],
            "python": [
                h("Факториал", ["py_recursive_def"], "def fact(n):\n    if n <= 1:\n        return 1\n    return n * fact(n - 1)"),
                h("Обход дерева", ["ast_self_call"], "def walk(node):\n    if node is None:\n        return\n    walk(node.left)"),
            ],
            "cpp": [
                h("Факториал", ["recursion"], "int fact(int n) {\n    if (n <= 1) return 1;\n    return n * fact(n - 1);\n}"),
                h("Fibonacci", ["ast_self_call"], "int fib(int n) {\n    if (n <= 1) return n;\n    return fib(n - 1) + fib(n - 2);\n}"),
            ],
            "csharp": [
                h("Факториал", ["recursion"], "static int Fact(int n) => n <= 1 ? 1 : n * Fact(n - 1);"),
                h("Fibonacci", ["ast_self_call"], "static int Fib(int n) => n <= 1 ? n : Fib(n - 1) + Fib(n - 2);"),
            ],
            "java": [
                h("Факториал", ["recursion"], "static int fact(int n) {\n    if (n <= 1) return 1;\n    return n * fact(n - 1);\n}"),
                h("Fibonacci", ["ast_self_call"], "static int fib(int n) {\n    if (n <= 1) return n;\n    return fib(n - 1) + fib(n - 2);\n}"),
            ],
        },
    ),
    "tc_arrays": tc(
        "tc_arrays",
        "Массивы и последовательности",
        "Индексированное хранение элементов одного типа.",
        ["indexed_sequence", "dynamic_array", "ast_array_subscript", "ast_array_literal", "pas_static_array", "cpp_vector", "cs_array_list", "java_array"],
        {
            "pascal": [
                h("Статический массив", ["pas_static_array"], "var a: array[1..10] of integer;"),
                h("Доступ по индексу", ["ast_array_subscript"], "a[i] := a[i] + 1;"),
                h("Динамический", ["dynamic_array"], "var dyn: array of integer;\nSetLength(dyn, n);"),
            ],
            "python": [
                h("Список", ["dynamic_array"], "a = [0] * 10"),
                h("Индекс", ["ast_array_subscript"], "a[i] = a[i] + 1"),
                h("Литерал", ["ast_array_literal"], "nums = [1, 2, 3, 5, 8]"),
            ],
            "cpp": [
                h("C-массив", ["indexed_sequence"], "int a[10] = {};"),
                h("vector", ["cpp_vector"], "std::vector<int> a(n);"),
                h("Индекс", ["ast_array_subscript"], "a[i]++;"),
            ],
            "csharp": [
                h("Массив", ["indexed_sequence"], "int[] a = new int[10];"),
                h("List", ["cs_array_list"], "var list = new List<int>();"),
                h("Индекс", ["ast_array_subscript"], "a[i]++;"),
            ],
            "java": [
                h("Массив", ["java_array"], "int[] a = new int[10];"),
                h("ArrayList", ["dynamic_array"], "ArrayList<Integer> list = new ArrayList<>();"),
                h("Индекс", ["ast_array_subscript"], "a[i]++;"),
            ],
        },
    ),
    "tc_strings": tc(
        "tc_strings",
        "Строки",
        "Текстовые данные: литералы, конкатенация, базовые операции.",
        ["string_sequence", "ast_string_literal", "ast_string_concat", "pas_string_ops", "py_str_methods"],
        {
            "pascal": [
                h("Литерал", ["ast_string_literal"], "name := 'Ann';"),
                h("Конкатенация", ["ast_string_concat"], "msg := 'Hi, ' + name;"),
                h("Length / Copy", ["pas_string_ops"], "n := Length(s);\ns2 := Copy(s, 1, 3);"),
            ],
            "python": [
                h("Литерал", ["ast_string_literal"], "name = 'Ann'"),
                h("f-string", ["ast_string_concat"], "msg = f'Hi, {name}'"),
                h("Методы", ["py_str_methods"], "s = s.strip().lower()"),
            ],
            "cpp": [
                h("std::string", ["string_sequence"], "std::string name = \"Ann\";"),
                h("Конкатенация", ["ast_string_concat"], "std::string msg = \"Hi, \" + name;"),
            ],
            "csharp": [
                h("string", ["string_sequence"], "string name = \"Ann\";"),
                h("Интерполяция", ["ast_string_concat"], "string msg = $\"Hi, {name}\";"),
            ],
            "java": [
                h("String", ["string_sequence"], "String name = \"Ann\";"),
                h("Конкатенация", ["ast_string_concat"], "String msg = \"Hi, \" + name;"),
            ],
        },
    ),
    "tc_collection_traversal": tc(
        "tc_collection_traversal",
        "Обход коллекций",
        "Последовательный просмотр всех элементов коллекции.",
        ["collection_iteration", "for_collection", "ast_enumeration_loop", "py_enumerate_zip", "cpp_iterator_loop", "cs_ienumerable", "java_iterator"],
        {
            "pascal": [
                h("for по массиву", ["collection_iteration"], "for i := 1 to Length(a) do\n  sum := sum + a[i];"),
                h("for in (Delphi-style)", ["for_collection"], "for item in items do\n  Process(item);"),
            ],
            "python": [
                h("for in", ["collection_iteration"], "for item in items:\n    print(item)"),
                h("enumerate", ["py_enumerate_zip"], "for i, v in enumerate(items):\n    print(i, v)"),
                h("zip", ["py_enumerate_zip"], "for a, b in zip(xs, ys):\n    print(a, b)"),
            ],
            "cpp": [
                h("range-for", ["cpp_iterator_loop"], "for (int v : vec)\n    sum += v;"),
                h("iterator", ["ast_enumeration_loop"], "for (auto it = v.begin(); it != v.end(); ++it)\n    sum += *it;"),
            ],
            "csharp": [
                h("foreach", ["cs_ienumerable"], "foreach (var item in items)\n    Console.WriteLine(item);"),
                h("for index", ["collection_iteration"], "for (int i = 0; i < items.Count; i++)\n    Console.WriteLine(items[i]);"),
            ],
            "java": [
                h("enhanced for", ["java_iterator"], "for (int v : arr)\n    sum += v;"),
                h("Iterator", ["java_iterator"], "for (Iterator<String> it = list.iterator(); it.hasNext();)\n    System.out.println(it.next());"),
            ],
        },
    ),
    "tc_maps_records": tc(
        "tc_maps_records",
        "Словари и записи",
        "Структуры «ключ → значение» и составные записи с полями.",
        ["key_value_map", "ast_record_struct", "ast_map_lookup", "pas_record_field", "py_dict", "cpp_unordered_map", "cs_dictionary", "java_hashmap", "field_access"],
        {
            "pascal": [
                h("record", ["pas_record_field"], "type Point = record\n  x, y: integer;\nend;"),
                h("Доступ к полю", ["field_access"], "p.x := 10;"),
            ],
            "python": [
                h("dict", ["py_dict"], "counts = {}\ncounts['a'] = counts.get('a', 0) + 1"),
                h("dict literal", ["key_value_map"], "user = {'name': 'Ann', 'age': 18}"),
            ],
            "cpp": [
                h("struct", ["ast_record_struct"], "struct Point { int x, y; };"),
                h("unordered_map", ["cpp_unordered_map"], "std::unordered_map<std::string,int> m;\nm[\"a\"] = 1;"),
            ],
            "csharp": [
                h("record / class", ["ast_record_struct"], "record Point(int X, int Y);"),
                h("Dictionary", ["cs_dictionary"], "var m = new Dictionary<string,int>();\nm[\"a\"] = 1;"),
            ],
            "java": [
                h("class поля", ["ast_record_struct"], "class Point { int x, y; }"),
                h("HashMap", ["java_hashmap"], "Map<String,Integer> m = new HashMap<>();\nm.put(\"a\", 1);"),
            ],
        },
    ),
    "tc_search": tc(
        "tc_search",
        "Поиск в данных",
        "Линейный поиск, проверка вхождения, поиск по условию.",
        ["search_find", "ast_linear_scan", "ast_binary_search", "ast_membership_test", "py_in_operator"],
        {
            "pascal": [
                h("Линейный поиск", ["ast_linear_scan"], "found := false;\nfor i := 1 to n do\n  if a[i] = key then found := true;"),
                h("Pos", ["search_find"], "p := Pos(key, text);"),
            ],
            "python": [
                h("in", ["py_in_operator"], "if key in items:\n    print('found')"),
                h("Линейный цикл", ["ast_linear_scan"], "for x in items:\n    if x == key:\n        break"),
            ],
            "cpp": [
                h("std::find", ["search_find"], "auto it = std::find(v.begin(), v.end(), key);"),
                h("Линейный цикл", ["ast_linear_scan"], "for (int x : v)\n    if (x == key) { /* found */ break; }"),
            ],
            "csharp": [
                h("Contains / IndexOf", ["search_find"], "if (items.Contains(key)) { }"),
                h("First", ["search_find"], "var x = items.FirstOrDefault(v => v == key);"),
            ],
            "java": [
                h("indexOf", ["search_find"], "int idx = list.indexOf(key);"),
                h("Линейный цикл", ["ast_linear_scan"], "for (int x : arr)\n    if (x == key) break;"),
            ],
        },
    ),
    "tc_filter": tc(
        "tc_filter",
        "Фильтрация",
        "Отбор элементов, удовлетворяющих условию.",
        ["filter_select", "filter", "ast_predicate_loop", "py_list_comp_if", "py_filter_builtin"],
        {
            "pascal": [
                h("Цикл с if", ["ast_predicate_loop"], "for i := 1 to n do\n  if a[i] mod 2 = 0 then\n    writeln(a[i]);"),
                h("Временный массив", ["filter_select"], "k := 0;\nfor i := 1 to n do\n  if a[i] > 0 then\n  begin\n    Inc(k);\n    b[k] := a[i];\n  end;"),
            ],
            "python": [
                h("list comp", ["py_list_comp_if"], "evens = [x for x in nums if x % 2 == 0]"),
                h("filter()", ["py_filter_builtin"], "evens = list(filter(lambda x: x % 2 == 0, nums))"),
            ],
            "cpp": [
                h("copy_if", ["filter_select"], "std::copy_if(v.begin(), v.end(), std::back_inserter(out),\n    [](int x){ return x % 2 == 0; });"),
                h("Цикл с if", ["ast_predicate_loop"], "for (int x : v)\n    if (x % 2 == 0)\n        out.push_back(x);"),
            ],
            "csharp": [
                h("Where", ["filter_select"], "var evens = nums.Where(x => x % 2 == 0);"),
                h("Цикл с if", ["ast_predicate_loop"], "foreach (var x in nums)\n    if (x % 2 == 0)\n        evens.Add(x);"),
            ],
            "java": [
                h("stream filter", ["filter"], "List<Integer> evens = nums.stream()\n    .filter(x -> x % 2 == 0)\n    .toList();"),
                h("Цикл с if", ["ast_predicate_loop"], "for (int x : nums)\n    if (x % 2 == 0)\n        evens.add(x);"),
            ],
        },
    ),
    "tc_aggregate": tc(
        "tc_aggregate",
        "Накопление и свёртка",
        "Суммирование, подсчёт, накопление результата в переменной или reduce.",
        ["fold_aggregate", "reduce", "ast_accumulator_pattern", "py_reduce", "cpp_accumulate", "cs_aggregate", "java_stream_reduce"],
        {
            "pascal": [
                h("Сумма в цикле", ["fold_aggregate"], "sum := 0;\nfor i := 1 to n do\n  sum := sum + a[i];"),
                h("Счётчик", ["ast_accumulator_pattern"], "cnt := 0;\nfor i := 1 to n do\n  if a[i] > 0 then Inc(cnt);"),
            ],
            "python": [
                h("+= в цикле", ["fold_aggregate"], "total = 0\nfor x in nums:\n    total += x"),
                h("sum()", ["fold_aggregate"], "total = sum(nums)"),
                h("reduce", ["py_reduce"], "from functools import reduce\ntotal = reduce(lambda a, x: a + x, nums, 0)"),
            ],
            "cpp": [
                h("+= в цикле", ["fold_aggregate"], "int sum = 0;\nfor (int x : v) sum += x;"),
                h("accumulate", ["cpp_accumulate"], "int sum = std::accumulate(v.begin(), v.end(), 0);"),
            ],
            "csharp": [
                h("+= в цикле", ["fold_aggregate"], "int sum = 0;\nforeach (var x in nums) sum += x;"),
                h("Aggregate", ["cs_aggregate"], "int sum = nums.Aggregate(0, (a, x) => a + x);"),
            ],
            "java": [
                h("+= в цикле", ["fold_aggregate"], "int sum = 0;\nfor (int x : arr) sum += x;"),
                h("stream reduce", ["java_stream_reduce"], "int sum = Arrays.stream(arr).reduce(0, Integer::sum);"),
            ],
        },
    ),
    "tc_sort": tc(
        "tc_sort",
        "Сортировка",
        "Упорядочивание элементов по возрастанию или убыванию.",
        ["sort_order", "sort", "ast_sort_call", "py_sorted_sort", "cpp_std_sort", "cs_orderby", "java_collections_sort"],
        {
            "pascal": [
                h("Sort массива", ["sort_order"], "Sort(a, 0, n - 1);"),
                h(
                    "Пузырёк (учебный)",
                    ["sort"],
                    "for i := 1 to n - 1 do\n  for j := 1 to n - i do\n    if a[j] > a[j + 1] then\n    begin\n      temp := a[j];\n      a[j] := a[j + 1];\n      a[j + 1] := temp;\n    end;",
                ),
            ],
            "python": [
                h("sorted", ["py_sorted_sort"], "ordered = sorted(nums)"),
                h("sort in-place", ["sort_order"], "nums.sort()"),
                h("key=", ["ast_sort_call"], "pairs.sort(key=lambda p: p[1])"),
            ],
            "cpp": [
                h("std::sort", ["cpp_std_sort"], "std::sort(v.begin(), v.end());"),
                h("greater", ["sort_order"], "std::sort(v.begin(), v.end(), std::greater<int>());"),
            ],
            "csharp": [
                h("Sort", ["sort_order"], "nums.Sort();"),
                h("OrderBy", ["cs_orderby"], "var ordered = nums.OrderBy(x => x);"),
            ],
            "java": [
                h("Arrays.sort", ["java_collections_sort"], "Arrays.sort(arr);"),
                h("Collections.sort", ["sort_order"], "Collections.sort(list);"),
            ],
        },
    ),
    "tc_modules": tc(
        "tc_modules",
        "Модули и импорт",
        "Подключение внешнего кода: библиотеки, модули, namespace.",
        ["import_dependency", "module_namespace", "ast_import", "pas_unit_uses", "py_import_from", "cpp_include", "cs_using", "java_import_package", "import"],
        {
            "pascal": [
                h("unit + uses", ["pas_unit_uses"], "unit MyUtils;\ninterface\nuses SysUtils;\nimplementation\nend."),
                h("uses в program", ["import_dependency"], "program Demo;\nuses SysUtils;\nbegin\nend."),
            ],
            "python": [
                h("import", ["py_import_from"], "import math"),
                h("from import", ["import_dependency"], "from datetime import datetime"),
            ],
            "cpp": [
                h("#include", ["cpp_include"], "#include <iostream>\n#include <vector>"),
                h("namespace", ["module_namespace"], "namespace utils {\n    int add(int a, int b) { return a + b; }\n}"),
            ],
            "csharp": [
                h("using", ["cs_using"], "using System;\nusing System.Collections.Generic;"),
                h("namespace", ["module_namespace"], "namespace Utils {\n    public static class Math {\n        public static int Add(int a, int b) => a + b;\n    }\n}"),
            ],
            "java": [
                h("import", ["java_import_package"], "import java.util.List;\nimport java.util.ArrayList;"),
                h("package", ["module_namespace"], "package demo.utils;\n\npublic class Helper { }"),
            ],
        },
    ),
    "tc_file_io": tc(
        "tc_file_io",
        "Файловый ввод-вывод",
        "Чтение и запись текстовых файлов.",
        ["file_read", "file_write", "file_io", "pas_textfile", "py_open_with", "cpp_fstream", "cs_file_read_write", "java_nio_files"],
        {
            "pascal": [
                h("Чтение", ["file_read", "pas_textfile"], "var f: text;\nassign(f, 'in.txt');\nreset(f);\nreadln(f, line);"),
                h("Запись", ["file_write"], "rewrite(f);\nwriteln(f, line);"),
            ],
            "python": [
                h("with open read", ["py_open_with"], "with open('in.txt') as f:\n    text = f.read()"),
                h("with open write", ["file_write"], "with open('out.txt', 'w') as f:\n    f.write(text)"),
            ],
            "cpp": [
                h("ifstream", ["cpp_fstream"], "std::ifstream in(\"in.txt\");\nstd::string line;\nstd::getline(in, line);"),
                h("ofstream", ["file_write"], "std::ofstream out(\"out.txt\");\nout << line;"),
            ],
            "csharp": [
                h("ReadAllText", ["cs_file_read_write"], "string text = File.ReadAllText(\"in.txt\");"),
                h("WriteAllText", ["file_write"], "File.WriteAllText(\"out.txt\", text);"),
            ],
            "java": [
                h("Files.readString", ["java_nio_files"], "String text = Files.readString(Path.of(\"in.txt\"));"),
                h("Files.writeString", ["file_write"], "Files.writeString(Path.of(\"out.txt\"), text);"),
            ],
        },
    ),
    "tc_oop_classes": tc(
        "tc_oop_classes",
        "Классы и объекты",
        "Объединение данных и поведения в тип; создание экземпляра класса.",
        ["class_type", "object_instance", "ast_class_declaration", "class"],
        {
            "pascal": [
                h("Объявление class", ["class_type"], "type\n  TAnimal = class\n  public\n    Name: string;\n  end;"),
                h("Создание объекта", ["object_instance"], "var pet: TAnimal;\npet := TAnimal.Create;\npet.Name := 'Barsik';"),
            ],
            "python": [
                h("class", ["class_type"], "class Animal:\n    species = 'unknown'"),
                h("Экземпляр", ["object_instance"], "pet = Animal()\npet.name = 'Barsik'"),
            ],
            "cpp": [
                h("class", ["class_type"], "class Animal {\npublic:\n    std::string name;\n};"),
                h("Объект на стеке", ["object_instance"], "Animal pet;\npet.name = \"Barsik\";"),
            ],
            "csharp": [
                h("class", ["class_type"], "class Animal {\n    public string Name { get; set; }\n}"),
                h("new", ["object_instance"], "var pet = new Animal { Name = \"Barsik\" };"),
            ],
            "java": [
                h("class", ["class_type"], "class Animal {\n    String name;\n}"),
                h("new", ["object_instance"], "Animal pet = new Animal();\npet.name = \"Barsik\";"),
            ],
        },
    ),
    "tc_oop_methods": tc(
        "tc_oop_methods",
        "Методы",
        "Функции и процедуры внутри класса; вызов через объект.",
        ["method_dispatch", "ast_method_call", "function_invocation"],
        {
            "pascal": [
                h("Метод класса", ["method_dispatch"], "type TCounter = class\n  value: integer;\n  procedure Inc;\nend;\n\nprocedure TCounter.Inc;\nbegin\n  value := value + 1;\nend;"),
                h("Вызов метода", ["ast_method_call"], "counter.Inc;"),
            ],
            "python": [
                h("Метод экземпляра", ["method_dispatch"], "class Counter:\n    def __init__(self):\n        self.value = 0\n\n    def inc(self):\n        self.value += 1"),
                h("Вызов", ["ast_method_call"], "counter.inc()"),
            ],
            "cpp": [
                h("Метод", ["method_dispatch"], "class Counter {\npublic:\n    int value = 0;\n    void inc() { ++value; }\n};"),
                h("Вызов", ["ast_method_call"], "counter.inc();"),
            ],
            "csharp": [
                h("Метод", ["method_dispatch"], "class Counter {\n    public int Value { get; private set; }\n    public void Inc() => Value++;\n}"),
                h("Вызов", ["ast_method_call"], "counter.Inc();"),
            ],
            "java": [
                h("Метод", ["method_dispatch"], "class Counter {\n    int value = 0;\n    void inc() { value++; }\n}"),
                h("Вызов", ["ast_method_call"], "counter.inc();"),
            ],
        },
    ),
    "tc_oop_constructors": tc(
        "tc_oop_constructors",
        "Конструкторы",
        "Инициализация объекта при создании: конструктор, Create, __init__.",
        ["ast_constructor", "object_instance"],
        {
            "pascal": [
                h("Constructor Create", ["ast_constructor"], "constructor Create(const AName: string);\nbegin\n  Name := AName;\nend;"),
                h("Вызов Create", ["object_instance"], "pet := TAnimal.Create('Barsik');"),
            ],
            "python": [
                h("__init__", ["ast_constructor"], "class Animal:\n    def __init__(self, name):\n        self.name = name"),
                h("Создание", ["object_instance"], "pet = Animal('Barsik')"),
            ],
            "cpp": [
                h("Конструктор", ["ast_constructor"], "class Animal {\npublic:\n    Animal(std::string name) : name(std::move(name)) {}\n    std::string name;\n};"),
                h("new", ["object_instance"], "auto pet = new Animal(\"Barsik\");"),
            ],
            "csharp": [
                h("Конструктор", ["ast_constructor"], "class Animal {\n    public Animal(string name) { Name = name; }\n    public string Name { get; }\n}"),
                h("new", ["object_instance"], "var pet = new Animal(\"Barsik\");"),
            ],
            "java": [
                h("Конструктор", ["ast_constructor"], "class Animal {\n    String name;\n    Animal(String name) { this.name = name; }\n}"),
                h("new", ["object_instance"], "Animal pet = new Animal(\"Barsik\");"),
            ],
        },
    ),
    "tc_oop_inheritance": tc(
        "tc_oop_inheritance",
        "Наследование",
        "Производный класс расширяет или переопределяет базовый тип.",
        ["inheritance_hierarchy", "ast_inheritance"],
        {
            "pascal": [
                h("Наследник", ["inheritance_hierarchy"], "type TDog = class(TAnimal)\npublic\n  procedure Speak; override;\nend;"),
                h("virtual", ["ast_inheritance"], "type TAnimal = class\n  procedure Speak; virtual; abstract;\nend;"),
            ],
            "python": [
                h("class Dog(Animal)", ["inheritance_hierarchy"], "class Dog(Animal):\n    def speak(self):\n        print('woof')"),
                h("super()", ["ast_inheritance"], "class Dog(Animal):\n    def speak(self):\n        super().speak()"),
            ],
            "cpp": [
                h("public inheritance", ["ast_inheritance"], "class Dog : public Animal {\npublic:\n    void speak() override;\n};"),
                h("virtual base", ["inheritance_hierarchy"], "class Animal {\npublic:\n    virtual void speak() = 0;\n};"),
            ],
            "csharp": [
                h(": Animal", ["inheritance_hierarchy"], "class Dog : Animal {\n    public override void Speak() => Console.WriteLine(\"woof\");\n}"),
                h("abstract", ["ast_inheritance"], "abstract class Animal {\n    public abstract void Speak();\n}"),
            ],
            "java": [
                h("extends", ["inheritance_hierarchy"], "class Dog extends Animal {\n    void speak() { System.out.println(\"woof\"); }\n}"),
                h("abstract", ["ast_inheritance"], "abstract class Animal {\n    abstract void speak();\n}"),
            ],
        },
    ),
    "tc_oop_polymorphism": tc(
        "tc_oop_polymorphism",
        "Полиморфизм",
        "Один интерфейс — разное поведение: virtual/override и вызов через базовый тип.",
        ["ast_virtual_dispatch", "ast_override", "method_dispatch"],
        {
            "pascal": [
                h("virtual + override", ["ast_override"], "type TAnimal = class\n  procedure Speak; virtual;\nend;\n\ntype TDog = class(TAnimal)\n  procedure Speak; override;\nend;"),
                h("Вызов через базовый тип", ["ast_virtual_dispatch"], "var a: TAnimal;\na := TDog.Create;\na.Speak;"),
            ],
            "python": [
                h("Переопределение", ["ast_override"], "class Animal:\n    def speak(self):\n        print('...')\n\nclass Dog(Animal):\n    def speak(self):\n        print('woof')"),
                h("Полиморный вызов", ["ast_virtual_dispatch"], "def make_sound(animal: Animal):\n    animal.speak()"),
            ],
            "cpp": [
                h("virtual / override", ["ast_override"], "class Animal {\npublic:\n    virtual void speak() {}\n};\n\nclass Dog : public Animal {\npublic:\n    void speak() override { std::cout << \"woof\"; }\n};"),
                h("Указатель на базовый класс", ["ast_virtual_dispatch"], "Animal* a = new Dog();\na->speak();"),
            ],
            "csharp": [
                h("virtual / override", ["ast_override"], "class Animal { public virtual void Speak() { } }\nclass Dog : Animal { public override void Speak() => Console.WriteLine(\"woof\"); }"),
                h("Базовая ссылка", ["ast_virtual_dispatch"], "Animal pet = new Dog();\npet.Speak();"),
            ],
            "java": [
                h("@Override", ["ast_override"], "class Animal { void speak() { } }\nclass Dog extends Animal { @Override void speak() { System.out.println(\"woof\"); } }"),
                h("Базовая ссылка", ["ast_virtual_dispatch"], "Animal pet = new Dog();\npet.speak();"),
            ],
        },
    ),
    "tc_linear_structures": tc(
        "tc_linear_structures",
        "Стек, очередь, связный список",
        "Линейные структуры данных с операциями добавления и извлечения.",
        ["stack_queue", "linked_node", "ast_push_pop", "py_deque", "cpp_stack_queue", "java_linkedlist"],
        {
            "pascal": [
                h(
                    "Стек (массив)",
                    ["stack_queue"],
                    "var st: array[1 .. 100] of integer;\n  top: integer;\nbegin\n  top := 0;\n  Inc(top);\n  st[top] := x;\nend;",
                ),
                h("Указательный узел", ["linked_node"], "type PNode = ^TNode;\n  TNode = record\n    val: integer;\n    next: PNode;\n  end;"),
            ],
            "python": [
                h("list как стек", ["stack_queue"], "stack = []\nstack.append(x)\nx = stack.pop()"),
                h("deque", ["py_deque"], "from collections import deque\nq = deque()\nq.append(x)"),
            ],
            "cpp": [
                h("stack", ["cpp_stack_queue"], "std::stack<int> st;\nst.push(x);\nx = st.top(); st.pop();"),
                h("queue", ["stack_queue"], "std::queue<int> q;\nq.push(x);"),
            ],
            "csharp": [
                h("Stack", ["stack_queue"], "var st = new Stack<int>();\nst.Push(x);"),
                h("Queue", ["stack_queue"], "var q = new Queue<int>();\nq.Enqueue(x);"),
            ],
            "java": [
                h(
                    "Deque",
                    ["stack_queue"],
                    "import java.util.ArrayDeque;\nimport java.util.Deque;\n\nDeque<Integer> st = new ArrayDeque<>();\nst.push(x);",
                ),
                h("LinkedList", ["java_linkedlist"], "LinkedList<Integer> list = new LinkedList<>();"),
            ],
        },
    ),
    "tc_trees": tc(
        "tc_trees",
        "Деревья",
        "Иерархическая структура: узлы, потомки, обход.",
        ["tree_hierarchy", "ast_binary_tree_node", "ast_tree_traversal_pre_in_post", "ast_recursive_tree_walk"],
        {
            "pascal": [
                h("Узел дерева", ["ast_binary_tree_node"], "type PNode = ^TNode;\n  TNode = record\n    val: integer;\n    left, right: PNode;\n  end;"),
                h("Рекурсивный обход", ["ast_recursive_tree_walk"], "procedure Walk(p: PNode);\nbegin\n  if p = nil then exit;\n  Walk(p.left);\n  Process(p.val);\n  Walk(p.right);\nend;"),
            ],
            "python": [
                h("Класс узла", ["ast_binary_tree_node"], "class Node:\n    def __init__(self, val, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right"),
                h("In-order", ["ast_tree_traversal_pre_in_post"], "def walk(node):\n    if not node: return\n    walk(node.left)\n    print(node.val)\n    walk(node.right)"),
            ],
            "cpp": [
                h("struct Node", ["ast_binary_tree_node"], "struct Node {\n    int val;\n    Node* left = nullptr;\n    Node* right = nullptr;\n};"),
                h("In-order walk", ["ast_recursive_tree_walk"], "void walk(Node* p) {\n    if (!p) return;\n    walk(p->left);\n    process(p->val);\n    walk(p->right);\n}"),
            ],
            "csharp": [
                h("class Node", ["ast_binary_tree_node"], "class Node {\n    public int Val;\n    public Node? Left, Right;\n}"),
                h("Recursive walk", ["ast_recursive_tree_walk"], "void Walk(Node? node) {\n    if (node is null) return;\n    Walk(node.Left);\n    Console.WriteLine(node.Val);\n    Walk(node.Right);\n}"),
            ],
            "java": [
                h("class Node", ["ast_binary_tree_node"], "class Node {\n    int val;\n    Node left, right;\n    Node(int v) { val = v; }\n}"),
                h("In-order walk", ["ast_recursive_tree_walk"], "void walk(Node node) {\n    if (node == null) return;\n    walk(node.left);\n    System.out.println(node.val);\n    walk(node.right);\n}"),
            ],
        },
    ),
    "tc_graphs": tc(
        "tc_graphs",
        "Графы",
        "Вершины и рёбра; представление списком смежности или матрицей.",
        ["graph_edges", "ast_adjacency_list", "ast_adjacency_matrix", "ast_bfs_dfs", "ast_visited_set"],
        {
            "pascal": [
                h("Матрица смежности", ["ast_adjacency_matrix"], "var g: array[1..N,1..N] of boolean;"),
                h("BFS (очередь)", ["ast_bfs_dfs"], "while not QueueEmpty do begin\n  v := Dequeue;\n  { relax edges from v }\nend;"),
            ],
            "python": [
                h("Список смежности", ["ast_adjacency_list"], "graph = {1: [2,3], 2: [4], 3: [], 4: []}"),
                h("BFS", ["ast_bfs_dfs"], "from collections import deque\nq = deque([start])\nseen = {start}"),
            ],
            "cpp": [
                h("vector<vector>", ["ast_adjacency_list"], "std::vector<std::vector<int>> g(n);"),
                h("visited", ["ast_visited_set"], "std::vector<bool> seen(n, false);"),
            ],
            "csharp": [
                h("Dictionary adjacency", ["ast_adjacency_list"], "var g = new Dictionary<int, List<int>>();"),
                h("HashSet visited", ["ast_visited_set"], "var seen = new HashSet<int>();"),
            ],
            "java": [
                h("List<List>", ["ast_adjacency_list"], "List<List<Integer>> g = new ArrayList<>();"),
                h("HashSet visited", ["ast_visited_set"], "Set<Integer> seen = new HashSet<>();"),
            ],
        },
    ),
}


def main() -> None:
    normalized = {tc_id: normalize_display_card(card) for tc_id, card in REGISTRY.items()}
    _validate_registry(normalized)
    payload = {
        "schema_version": "2.0",
        "description": "Pedagogical TC display bundles (UI only). Detection uses ast_node_to_technical.yml.",
        "languages": list(LANGS),
        "tc_cards": normalized,
        "changelog": {
            "2.0": [
                "Renamed hint field covers -> illustrates (documentation only, not detection).",
                "technical_concept_ids and illustrates use canonical ids (assignment, program_root, …).",
            ],
            "1.1": [
                "Split tc_oop into five OOP cards.",
                "Fixed Pascal stack array bounds and bubble-sort example.",
            ],
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} ({len(REGISTRY)} TC cards)")


if __name__ == "__main__":
    main()
