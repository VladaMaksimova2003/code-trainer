"""Block capstone tasks for C++ Course v1.1."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CppCapstoneSpec:
    slot_id: str
    title: str
    task_format: str
    goal: str
    features: str
    difficulty: str
    pattern: str
    reference_cpp: str
    expected_concept_ids: tuple[str, ...]
    action: str
    starter_cpp: str = ""


_BLOCK_CAPSTONES: tuple[CppCapstoneSpec, ...] = (
    CppCapstoneSpec(
        slot_id="cpcap_01",
        title="Capstone: каркас и I/O",
        task_format="перевод_программы",
        goal="Соберите программу: main, cin/cout, сумма двух чисел.",
        features="entry; io",
        difficulty="medium",
        pattern="cpp_cpcap_01",
        reference_cpp=(
            "#include <iostream>\n"
            "int main() {\n"
            "    int a, b;\n"
            "    std::cin >> a >> b;\n"
            "    std::cout << a + b << std::endl;\n"
            "    return 0;\n"
            "}\n"
        ),
        expected_concept_ids=("program_entry", "stdin_read", "stdout_write"),
        action="translate",
    ),
    CppCapstoneSpec(
        slot_id="cpcap_02",
        title="Capstone: условия и циклы",
        task_format="исправление",
        goal="Исправьте программу с if/else и циклом for.",
        features="cond; loops",
        difficulty="medium",
        pattern="cpp_cpcap_02",
        reference_cpp=(
            "#include <iostream>\n"
            "int main() {\n"
            "    int n;\n"
            "    std::cin >> n;\n"
            "    int s = 0;\n"
            "    for (int i = 1; i <= n; ++i) s += i;\n"
            "    std::cout << s << std::endl;\n"
            "    return 0;\n"
            "}\n"
        ),
        starter_cpp=(
            "#include <iostream>\n"
            "int main() {\n"
            "    int n;\n"
            "    std::cin >> n;\n"
            "    int s = 0;\n"
            "    for (int i = 1; i < n; ++i) s += i;\n"
            "    std::cout << s << std::endl;\n"
            "    return 0;\n"
            "}\n"
        ),
        expected_concept_ids=("simple_branch", "counted_loop"),
        action="debug",
    ),
    CppCapstoneSpec(
        slot_id="cpcap_03",
        title="Capstone: функции и параметры",
        task_format="сборка_программы",
        goal="Соберите program с функцией и передачей по const&.",
        features="functions; params",
        difficulty="medium",
        pattern="cpp_cpcap_03",
        reference_cpp=(
            "#include <iostream>\n"
            "int add(int a, int b) { return a + b; }\n"
            "int main() {\n"
            "    int x, y;\n"
            "    std::cin >> x >> y;\n"
            "    std::cout << add(x, y) << std::endl;\n"
            "    return 0;\n"
            "}\n"
        ),
        expected_concept_ids=("function_definition", "parameter_passing"),
        action="assemble",
    ),
    CppCapstoneSpec(
        slot_id="cpcap_04",
        title="Capstone: vector и string",
        task_format="исправление",
        goal="Исправьте программу со std::vector и std::string.",
        features="vector; string",
        difficulty="medium",
        pattern="cpp_cpcap_04",
        reference_cpp=(
            "#include <iostream>\n"
            "#include <vector>\n"
            "#include <string>\n"
            "int main() {\n"
            "    std::vector<std::string> v = {\"a\", \"b\"};\n"
            "    std::cout << v.front() << std::endl;\n"
            "    return 0;\n"
            "}\n"
        ),
        starter_cpp=(
            "#include <iostream>\n"
            "#include <vector>\n"
            "#include <string>\n"
            "int main() {\n"
            "    std::vector<std::string> v = {\"a\", \"b\"};\n"
            "    std::cout << v[2] << std::endl;\n"
            "    return 0;\n"
            "}\n"
        ),
        expected_concept_ids=("dynamic_array", "string_sequence"),
        action="debug",
    ),
    CppCapstoneSpec(
        slot_id="cpcap_05",
        title="Capstone: файлы и заголовки",
        task_format="сборка_программы",
        goal="Соберите чтение файла через ifstream и #include.",
        features="files; headers",
        difficulty="hard",
        pattern="cpp_cpcap_05",
        reference_cpp=(
            "#include <fstream>\n"
            "#include <iostream>\n"
            "#include <string>\n"
            "int main() {\n"
            "    std::ifstream in(\"data.txt\");\n"
            "    std::string line;\n"
            "    if (in.is_open() && std::getline(in, line)) {\n"
            "        std::cout << line << std::endl;\n"
            "    }\n"
            "    return 0;\n"
            "}\n"
        ),
        expected_concept_ids=("file_read", "import_dependency"),
        action="assemble",
    ),
    CppCapstoneSpec(
        slot_id="cpcap_06",
        title="Capstone: ООП",
        task_format="исправление",
        goal="Исправьте иерархию class с virtual/override.",
        features="oop",
        difficulty="hard",
        pattern="cpp_cpcap_06",
        reference_cpp=(
            "#include <iostream>\n"
            "class Base { public: virtual ~Base() = default; virtual void f() { std::cout << \"B\"; } };\n"
            "class Der : public Base { public: void f() override { std::cout << \"D\"; } };\n"
            "int main() { Base* p = new Der(); p->f(); delete p; return 0; }\n"
        ),
        starter_cpp=(
            "#include <iostream>\n"
            "class Base { public: void f() { std::cout << \"B\"; } };\n"
            "class Der : public Base { public: void f() override { std::cout << \"D\"; } };\n"
            "int main() { Base* p = new Der(); p->f(); delete p; return 0; }\n"
        ),
        expected_concept_ids=("class_type", "inheritance_hierarchy"),
        action="debug",
    ),
    CppCapstoneSpec(
        slot_id="cpcap_07",
        title="Capstone: RAII и move",
        task_format="исправление",
        goal="Исправьте ownership: unique_ptr и std::move.",
        features="RAII; move",
        difficulty="hard",
        pattern="cpp_cpcap_07",
        reference_cpp=(
            "#include <iostream>\n"
            "#include <memory>\n"
            "#include <utility>\n"
            "#include <vector>\n"
            "#include <string>\n"
            "int main() {\n"
            "    std::vector<std::string> v;\n"
            "    auto p = std::make_unique<std::string>(\"data\");\n"
            "    v.push_back(std::move(*p));\n"
            "    std::cout << v[0] << std::endl;\n"
            "    return 0;\n"
            "}\n"
        ),
        starter_cpp=(
            "#include <iostream>\n"
            "#include <memory>\n"
            "#include <vector>\n"
            "#include <string>\n"
            "int main() {\n"
            "    std::vector<std::string> v;\n"
            "    auto p = std::make_unique<std::string>(\"data\");\n"
            "    v.push_back(*p);\n"
            "    std::cout << v[0] << std::endl;\n"
            "    return 0;\n"
            "}\n"
        ),
        expected_concept_ids=("unique_ptr", "move_semantics", "raii"),
        action="debug",
    ),
    CppCapstoneSpec(
        slot_id="cpcap_08",
        title="Capstone: STL и шаблоны",
        task_format="исправление",
        goal="Исправьте map, sort/find и function template.",
        features="map; algorithm; template",
        difficulty="hard",
        pattern="cpp_cpcap_08",
        reference_cpp=(
            "#include <algorithm>\n"
            "#include <iostream>\n"
            "#include <map>\n"
            "#include <vector>\n"
            "template<typename T>\n"
            "T maxVal(T a, T b) { return a < b ? b : a; }\n"
            "int main() {\n"
            "    std::map<std::string, int> m{{\"a\", 1}};\n"
            "    std::vector<int> v{3, 1, 2};\n"
            "    std::sort(v.begin(), v.end());\n"
            "    std::cout << maxVal(v[0], m[\"a\"]) << std::endl;\n"
            "    return 0;\n"
            "}\n"
        ),
        starter_cpp=(
            "#include <iostream>\n"
            "#include <map>\n"
            "#include <vector>\n"
            "int main() {\n"
            "    std::map<std::string, int> m;\n"
            "    std::vector<int> v{3, 1, 2};\n"
            "    std::cout << v[3] << std::endl;\n"
            "    return 0;\n"
            "}\n"
        ),
        expected_concept_ids=("stl_containers", "stl_algorithms", "templates"),
        action="debug",
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
                "cpp_capstones",
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


def capstone_reference_cpp() -> dict[str, str]:
    return {spec.slot_id: spec.reference_cpp for spec in _BLOCK_CAPSTONES}


def capstone_starter_cpp() -> dict[str, str]:
    return {
        spec.slot_id: spec.starter_cpp
        for spec in _BLOCK_CAPSTONES
        if spec.starter_cpp
    }


def capstone_expected_concepts() -> dict[str, tuple[str, ...]]:
    return {spec.slot_id: spec.expected_concept_ids for spec in _BLOCK_CAPSTONES}
