"""Block capstone tasks for Python Course v1."""

from __future__ import annotations

from dataclasses import dataclass

CAPSTONES_PER_CHAPTER = 0  # block capstones only


@dataclass(frozen=True)
class CapstoneSpec:
    slot_id: str
    title: str
    task_format: str
    goal: str
    features: str
    difficulty: str
    pattern: str
    python: str
    pascal: str
    cpp: str
    expected_concept_ids: tuple[str, ...]
    test_cases: tuple[dict[str, str], ...]
    starter_python: str = ""
    action: str = "translate"


_BLOCK_CAPSTONES: tuple[CapstoneSpec, ...] = (
    CapstoneSpec(
        slot_id="pycap_01",
        title="Capstone: основы Python",
        task_format="перевод_программы",
        goal="Перенесите программу: ввод, переменные, выражения и вывод.",
        features="basics",
        difficulty="medium",
        pattern="py_pycap_01",
        python=(
            "a = int(input())\n"
            "b = int(input())\n"
            "print(a + b)"
        ),
        pascal=(
            "program Demo;\n"
            "var a, b, s: integer;\n"
            "begin\n"
            "  readln(a);\n"
            "  readln(b);\n"
            "  s := a + b;\n"
            "  writeln(s);\n"
            "end."
        ),
        cpp=(
            "#include <iostream>\n"
            "using namespace std;\n"
            "int main() {\n"
            "    int a, b;\n"
            "    cin >> a >> b;\n"
            "    cout << a + b << endl;\n"
            "    return 0;\n"
            "}"
        ),
        expected_concept_ids=("program_entry", "stdin_read", "stdout_write", "assignment"),
        test_cases=({"inputs": "2\n3\n", "output": "5"},),
        action="translate",
    ),
    CapstoneSpec(
        slot_id="pycap_02",
        title="Capstone: управление потоком",
        task_format="исправление",
        goal="Исправьте программу с if, for и while.",
        features="control",
        difficulty="medium",
        pattern="py_pycap_02",
        python=(
            "n = int(input())\n"
            "s = 0\n"
            "for i in range(1, n + 1):\n"
            "    s += i\n"
            "print(s)"
        ),
        pascal=(
            "n := 10;\n"
            "s := 0;\n"
            "for i := 1 to n do\n"
            "  s := s + i;\n"
            "writeln(s);"
        ),
        cpp="int s = 0; for (int i = 1; i <= n; ++i) s += i;",
        expected_concept_ids=("simple_branch", "counted_loop"),
        test_cases=({"inputs": "5\n", "output": "15"},),
        starter_python=(
            "n = int(input())\n"
            "s = 0\n"
            "for i in range(1, n):\n"
            "    s += i\n"
            "print(s)"
        ),
        action="debug",
    ),
    CapstoneSpec(
        slot_id="pycap_03",
        title="Capstone: функции",
        task_format="сборка_программы",
        goal="Соберите программу с def, параметрами и return.",
        features="functions",
        difficulty="medium",
        pattern="py_pycap_03",
        python=(
            "def add(a, b):\n"
            "    return a + b\n\n"
            "x = int(input())\n"
            "y = int(input())\n"
            "print(add(x, y))"
        ),
        pascal=(
            "function Add(a, b: integer): integer;\n"
            "begin Result := a + b; end;"
        ),
        cpp="int add(int a, int b) { return a + b; }",
        expected_concept_ids=("function_definition", "return_flow"),
        test_cases=({"inputs": "4\n5\n", "output": "9"},),
        action="assemble",
    ),
    CapstoneSpec(
        slot_id="pycap_04",
        title="Capstone: коллекции",
        task_format="исправление",
        goal="Исправьте программу со списками, строками и dict.",
        features="collections",
        difficulty="medium",
        pattern="py_pycap_04",
        python="items = ['a', 'b', 'c']\nprint(items[0])",
        pascal="var items: array[0..2] of char;\nbegin items[0] := 'a'; writeln(items[0]); end.",
        cpp='std::vector<char> items = {\'a\', \'b\', \'c\'};\ncout << items[0];',
        expected_concept_ids=("indexed_sequence", "string_sequence"),
        test_cases=({"inputs": "", "output": "a"},),
        starter_python="items = ['a', 'b', 'c']\nprint(items[1])",
        action="debug",
    ),
    CapstoneSpec(
        slot_id="pycap_05",
        title="Capstone: файлы и модули",
        task_format="перевод_программы",
        goal="Перенесите модуль с чтением файла и публичным API.",
        features="modules",
        difficulty="hard",
        pattern="py_pycap_05",
        python=(
            "def read_lines(path: str) -> list[str]:\n"
            "    with open(path, encoding='utf-8') as f:\n"
            "        return f.read().splitlines()\n\n"
            "if __name__ == '__main__':\n"
            "    print(len(read_lines('data.txt')))"
        ),
        pascal=(
            "uses SysUtils;\n"
            "var f: TextFile;\n"
            "begin\n"
            "  Assign(f, 'data.txt'); Reset(f);\n"
            "  Close(f);\n"
            "end."
        ),
        cpp=(
            "#include <fstream>\n"
            "#include <vector>\n"
            "#include <string>\n"
            "std::vector<std::string> read_lines(const std::string& path);"
        ),
        expected_concept_ids=("file_read", "import_dependency"),
        test_cases=({"inputs": "", "output": "0"},),
        action="translate",
    ),
    CapstoneSpec(
        slot_id="pycap_06",
        title="Capstone: ООП",
        task_format="исправление",
        goal="Исправьте иерархию классов с наследованием и property.",
        features="oop",
        difficulty="hard",
        pattern="py_pycap_06",
        python=(
            "class Animal:\n"
            "    def speak(self):\n"
            "        return '...'\n\n"
            "class Dog(Animal):\n"
            "    def speak(self):\n"
            "        return super().speak() + ' woof'"
        ),
        pascal="type TAnimal = class\n  function Speak: string; virtual; end;",
        cpp="class Animal { public: virtual std::string speak(); };",
        expected_concept_ids=("class_type", "inheritance_hierarchy"),
        test_cases=({"inputs": "", "output": "... woof"},),
        starter_python=(
            "class Animal:\n"
            "    def speak(self):\n"
            "        return '...'\n\n"
            "class Dog(Animal):\n"
            "    def speak(self):\n"
            "        return 'woof'"
        ),
        action="debug",
    ),
    CapstoneSpec(
        slot_id="pycap_07",
        title="Capstone: исключения",
        task_format="сборка_программы",
        goal="Соберите программу с безопасным вводом и обработкой ошибок.",
        features="exceptions",
        difficulty="medium",
        pattern="py_pycap_07",
        python=(
            "while True:\n"
            "    try:\n"
            "        n = int(input())\n"
            "        break\n"
            "    except ValueError:\n"
            "        print('retry')\n"
            "print(n)"
        ),
        pascal="repeat readln(n); until n > 0;",
        cpp="while (!(cin >> n)) { cin.clear(); }",
        expected_concept_ids=("simple_branch", "stdin_read"),
        test_cases=({"inputs": "x\n5\n", "output": "retry\n5"},),
        action="assemble",
    ),
    CapstoneSpec(
        slot_id="pycap_08",
        title="Capstone: продвинутый Python",
        task_format="исправление",
        goal="Исправьте CLI-утилиту: import, def, generator/decorator, main.",
        features="pro",
        difficulty="hard",
        pattern="py_pycap_08",
        python=(
            "def gen():\n"
            "    yield 1\n"
            "    yield 2\n\n"
            "if __name__ == '__main__':\n"
            "    print(list(gen()))"
        ),
        pascal="function Next: integer; forward;",
        cpp="template<typename T> class Generator {};",
        expected_concept_ids=("function_definition", "program_entry"),
        test_cases=({"inputs": "", "output": "[1, 2]"},),
        starter_python=(
            "def gen():\n"
            "    return [1, 2]\n\n"
            "if __name__ == '__main__':\n"
            "    print(list(gen()))"
        ),
        action="debug",
    ),
    CapstoneSpec(
        slot_id="pycap_09",
        title="Capstone: Advanced Python",
        task_format="сборка_программы",
        goal="Соберите CLI с decorator, context manager и typed API.",
        features="advanced",
        difficulty="hard",
        pattern="py_pycap_09",
        python=(
            "from contextlib import contextmanager\n"
            "from functools import wraps\n\n"
            "def logged(fn):\n"
            "    @wraps(fn)\n"
            "    def wrapper(*a, **k):\n"
            "        return fn(*a, **k)\n"
            "    return wrapper\n\n"
            "@logged\n"
            "def run():\n"
            "    return 1\n\n"
            "if __name__ == '__main__':\n"
            "    print(run())"
        ),
        pascal="program Demo;\nbegin\n  writeln(1);\nend.",
        cpp="int main(){ return 1; }",
        expected_concept_ids=("function_definition", "program_entry"),
        test_cases=({"inputs": "", "output": "1"},),
        action="assemble",
    ),
)


def capstone_count() -> int:
    return len(_BLOCK_CAPSTONES)


def capstone_task_rows() -> list[tuple]:
    rows: list[tuple] = []
    for spec in _BLOCK_CAPSTONES:
        rows.append(
            (
                spec.slot_id,
                "capstones",
                spec.title,
                spec.task_format,
                spec.action,
                spec.pattern,
                spec.goal,
                spec.features,
                spec.difficulty,
                "",
            )
        )
    return rows


def capstone_reference_python() -> dict[str, str]:
    return {spec.slot_id: spec.python for spec in _BLOCK_CAPSTONES}


def capstone_starter_python() -> dict[str, str]:
    return {
        spec.slot_id: spec.starter_python
        for spec in _BLOCK_CAPSTONES
        if spec.starter_python
    }


def capstone_expected_concepts() -> dict[str, tuple[str, ...]]:
    return {spec.slot_id: spec.expected_concept_ids for spec in _BLOCK_CAPSTONES}


def capstone_known_code() -> dict[str, tuple[str, str, str, str]]:
    return {
        spec.slot_id: (spec.pascal, spec.cpp, spec.pascal, spec.cpp)
        for spec in _BLOCK_CAPSTONES
    }
