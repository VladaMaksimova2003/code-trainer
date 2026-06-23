"""Reference / starter C++ code for C++ Course v1 MVP-1."""

from __future__ import annotations

from typing import Any

from application.curriculum.cpp.catalog.cpp_known_language import (
    build_known_language_variants,
    code_examples_from_variants,
)
from application.curriculum.cpp.catalog.cpp_v311_capstone_catalog import (
    capstone_reference_cpp,
    capstone_starter_cpp,
)

_CPP_MAIN = (
    "#include <iostream>\n"
    "int main() {\n"
    "    std::cout << \"Hello\" << std::endl;\n"
    "    return 0;\n"
    "}\n"
)

_SLOT_REFERENCE: dict[str, str] = {
    "cpk_01": _CPP_MAIN,
    "cpk_02": "#include <iostream>\nint main() {\n    std::cout << \"Hi\" << std::endl\n    return 0;\n}\n",
    "cpk_03": _CPP_MAIN,
    "cpk_04": "int main() {\n    return 0;\n}\n",
    "cpk_08": "// line comment\n/* block */\n",
    "cpk_10": "int main() {\n    { }\n    return 0;\n}\n",
    "cpk_11": "const int MAX = 100;\nint x = 0;\n",
    "cpk_12": "#include <iostream>\nusing namespace std;\n",
    "cpk_14": "#include <iostream>\nint x = 0;\nint main() { return 0; }\n",
    "cpt_01": "int x = 0;\ndouble y = 1.5;\n",
    "cpt_02": "int x = 0;\nif (x == 1) { }\n",
    "cpt_03": "float a = 1.0f;\ndouble b = 2.0;\n",
    "cpt_04": "bool ok = true;\nif (ok) { }\n",
    "cpt_06": "const int MAX = 100;\n",
    "cpt_09": "double x = 7.9;\nint n = static_cast<int>(x);\n",
    "cpt_10": "int count = 42;\n",
    "cpt_14": "int x;\nstd::cout << x;\n",
    "cpt_15": "auto n = 5;\n",
    "cpi_01": "int x;\nstd::cin >> x;\n",
    "cpi_02": "std::cout << \"a\" << \" \" << 1 << std::endl;\n",
    "cpi_04": "#include <iomanip>\nstd::cout << std::fixed << std::setprecision(2) << 3.14159;\n",
    "cpi_05": "int n = std::stoi(\"42\");\n",
    "cpi_06": "int x;\nstd::cin >> x;\nstd::cout << x << std::endl;\n",
    "cpi_07": _CPP_MAIN,
    "cpi_09": "std::cout << \"prompt\";\nint x;\nstd::cin >> x;\n",
    "cpi_10": "int n;\nstd::cin >> n;\nstd::string line;\nstd::getline(std::cin, line);\n",
    "cpe_02": "int q = 7 / 2;\nint r = 7 % 2;\n",
    "cpe_03": "int m = (1 << 2) | 3;\n",
    "cpe_06": "double x = 5.5;\nint r = static_cast<int>(x) % 2;\n",
    "cpe_08": "int a = 10 / 3;\nint b = 10 % 3;\n",
    "cpe_10": "double r = 5 / 2;\n",
    "cpe_11": "std::cout << 1 + 2 << 3;\n",
    "cpc_01": "if (x > 0) { std::cout << \"pos\"; } else { std::cout << \"neg\"; }\n",
    "cpc_02": "if (ok) { }\nelse { }\n",
    "cpc_03": "if (a > b) { m = a; } else if (a < b) { m = b; } else { m = a; }\n",
    "cpc_05": "switch (n) {\ncase 1: std::cout << 1; break;\ndefault: break;\n}\n",
    "cpc_08": "switch (c) {\ncase 'a': break;\n}\n",
    "cpc_10": "switch (x) {\ncase 0: break;\n}\n",
    "cpc_15": "switch (n) {\ncase 1: std::cout << 1;\ncase 2: std::cout << 2; break;\n}\n",
    "cpc_16": "bool flag = true;\nif (flag) { }\n",
    "cpc_17": "if (x = 1) { }\n",
    "cpl_01": "for (int i = 0; i < n; ++i) { sum += i; }\n",
    "cpl_02": "for (int i = 0; i < 10; ++i) {\n    std::cout << i;\n}\n",
    "cpl_04": "while (n > 0) { n /= 2; }\n",
    "cpl_06": "do { std::cin >> x; } while (x != 0);\n",
    "cpl_07": "int x;\ndo { std::cin >> x; } while (x > 0);\n",
    "cpl_08": "int x;\ndo { std::cin >> x; } while (x < 0);\n",
    "cpl_09": "for (int i = 0; i < n; ++i) { if (i == 5) break; }\n",
    "cpl_12": "for (int i = 0; i < n; ++i) {\n    for (int j = 0; j < m; ++j) { }\n}\n",
    "cpl_15": "#include <vector>\nfor (int v : nums) { std::cout << v; }\n",
    "cpl_16": "for (int i = 0; i < n; i++) { }\n",
    "cpfn_01": "int sq(int x) { return x * x; }\n",
    "cpfn_02": "int absVal(int x) { return x >= 0 ? x : -x; }\n",
    "cpfn_03": "int add(int a, b) { return a + b; }\n",
    "cpfn_04": "int sign(int x) { if (x > 0) return 1; if (x < 0) return -1; return 0; }\n",
    "cpfn_05": "int mul(int a, int b);\nint mul(int a, int b) { return a * b; }\n",
    "cpfn_06": "int f() {\n    return 0;\n}\n",
    "cpfn_12": "int sum(int a, int b) { return a + b; }\nint main() { std::cout << sum(1,2); return 0; }\n",
    "cpfn_15": "int twice(int x);\nint twice(int x) { return x * 2; }\n",
    "cpfn_16": "greet() { std::cout << \"hi\"; }\n",
    "cpfn_17": "int pick(int x) { if (x > 0) return 1; }\n",
    "cpp_01": "void logMsg(const std::string& s) { std::cout << s; }\n",
    "cpp_02": "void swapVal(int a, int b) { int t = a; a = b; b = t; }\n",
    "cpp_03": "void printConst(const int x) { std::cout << x; }\n",
    "cpp_06": "void inc(int& x) { ++x; }\n",
    "cpp_07": "void reset(int& v) { v = 0; }\n",
    "cpp_10": "void hello() {\n    std::cout << \"hi\";\n}\n",
    "cpp_12": "void bump(int x) { ++x; }\n",
    "cpp_15": "void swapVal(int a, int b) { int t = a; a = b; b = t; }\n",
    "cpp_16": "void show(const std::string& s) { std::cout << s; }\n",
    "cpp_17": "int& badRef() { int x = 1; return x; }\n",
    "cpa_01": "int a[10];\nfor (int i = 0; i < 10; ++i) { a[i] = 0; }\n",
    "cpa_03": "int a[5];\nfor (int i = 0; i < 5; ++i) { std::cout << a[i]; }\n",
    "cpa_04": "int a[5];\nfor (int i = 0; i < 5; ++i) { std::cout << a[i]; }\n",
    "cpa_05": "int m[2][3] = {{1,2,3},{4,5,6}};\n",
    "cpa_06": "const int N = 5;\nint a[N];\n",
    "cpa_09": "int a[3];\nstd::cout << a[2];\n",
    "cpa_15": "#include <array>\nstd::array<int, 3> a = {1,2,3};\n",
    "cpa_16": "void f(int* p) { std::cout << p[0]; }\nint a[3];\nf(a);\n",
    "cpa_17": "int a[4];\nint* p = a;\n",
    "cpd_01": "std::vector<int> v;\nv.resize(5);\n",
    "cpd_02": "std::vector<int> v;\nv.resize(3);\nstd::cout << v.size();\n",
    "cpd_04": "std::vector<int> v;\nv.push_back(1);\n",
    "cpd_05": "std::vector<int> v;\nv.resize(2);\nv[1] = 5;\n",
    "cpd_06": "std::vector<int> v;\nv.resize(0);\n",
    "cpd_10": "std::vector<int> v;\nv.push_back(1);\nv[0] = 2;\n",
    "cpd_15": "std::vector<int> v;\nv.push_back(1);\n",
    "cpd_16": "std::vector<int> v = {1,2};\nauto it = v.begin();\nv.push_back(3);\nstd::cout << *it;\n",
    "cps_01": "std::string s = \"abc\";\nstd::cout << s.size();\n",
    "cps_03": "std::string s = \"hi\";\nchar c = s[s.size() - 1];\n",
    "cps_04": "std::string s = \"hello\";\nstd::string t = s.substr(1, 3);\n",
    "cps_05": "std::string a = \"a\";\nstd::string b = a + \"b\";\n",
    "cps_09": "std::string s = \"abc\";\nfor (size_t i = 0; i < s.size(); ++i) { std::cout << s[i]; }\n",
    "cps_15": "std::string s = \"hi\";\n",
    "cps_16": "std::string a = \"x\";\nstd::string b = \"x\";\nif (a == b) { }\n",
    "cps_17": "#include <iostream>\nstd::string s;\n",
    "cppt_01": "int x = 5;\nint* p = &x;\n",
    "cppt_02": "int x = 10;\nint* p = &x;\nstd::cout << *p;\n",
    "cppt_03": "int* p = nullptr;\n",
    "cppt_04": "#include <memory>\nauto p = std::make_unique<int>(5);\n",
    "cppt_05": "#include <memory>\nint* p = new int(1);\n",
    "cppt_06": "int* p = new int(1);\ndelete p;\ndelete p;\n",
    "cppt_07": "int x = 1;\nint* p = &x;\n",
    "cppt_08": "int x = 1;\nint& r = x;\n",
    "cppt_09": "const int x = 1;\nconst int* p = &x;\n",
    "cppt_10": "#include <memory>\nauto p = std::make_unique<int>(5);\n",
    "cppt_11": "std::unique_ptr<int> p = std::make_unique<int>(1);\n",
    "cppt_12": "int* a = new int[3]{1,2,3};\ndelete[] a;\n",
    "cppt_13": "#include <memory>\nauto p = std::make_unique<int>(42);\n",
    "cppt_14": "#include <memory>\nvoid take(std::unique_ptr<int> p) {}\nauto p = std::make_unique<int>(1);\ntake(p);\n",
    "cppt_15": "#include <memory>\nstd::unique_ptr<int> makeOne() { return std::make_unique<int>(1); }\n",
    "cppr_01": "#define MAX 100\nint n = MAX;\n",
    "cppr_03": "#ifndef GUARD_H\n#define GUARD_H\n#endif\n",
    "cptpl_01": "template<typename T>\nvoid swapVal(T& a, T& b) { T t = a; a = b; b = t; }\n",
    "cptpl_04": "template<typename T>\nclass Box { public: T value; Box(T v): value(v) {} };\n",
    "cptpl_10": "#include <utility>\nstd::pair p(1, std::string(\"x\"));\n",
    "cpen_01": "enum class Color { Red, Green, Blue };\nColor c = Color::Red;\n",
    "cpas_01": "#include <map>\nstd::map<std::string,int> m;\nm[\"a\"] = 1;\nauto it = m.find(\"a\");\n",
    "cpalg_01": "#include <algorithm>\n#include <vector>\nstd::vector<int> v{3,1,2};\nstd::sort(v.begin(), v.end());\n",
    "cpmv_01": "#include <utility>\n#include <vector>\n#include <string>\nstd::vector<std::string> v;\nstd::string s = \"hi\";\nv.push_back(std::move(s));\n",
    "cpex_01": "try { int x = 1 / 0; } catch (const std::exception& e) { std::cout << \"err\"; }\n",
    "cpex_02": "try { throw std::runtime_error(\"fail\"); } catch (const std::runtime_error& e) { std::cout << \"caught\"; }\n",
    "cpex_03": "struct Guard { ~Guard() { std::cout << \"done\"; } };\ntry { std::cout << \"work\"; Guard g; } catch (...) {}\n",
    "cpex_06": "struct EMy : public std::exception {};\nthrow EMy();\n",
    "cpex_07": "#include <fstream>\ntry { std::ifstream f(\"missing.txt\"); if (!f) throw std::runtime_error(\"no file\"); } catch (...) { std::cout << \"no file\"; }\n",
    "cpfl_01": "#include <fstream>\nstd::ifstream in(\"data.txt\");\nstd::string line;\nstd::getline(in, line);\n",
    "cpfl_02": "#include <fstream>\nstd::ofstream out(\"out.txt\");\nout << \"hi\";\nout.close();\n",
    "cpfl_03": "#include <fstream>\nstd::ofstream out(\"out.txt\");\nout << 1;\n",
    "cpfl_04": "#include <fstream>\nstd::ifstream in(\"data.txt\");\nstd::string line;\nwhile (std::getline(in, line)) { std::cout << line; }\n",
    "cpfl_07": "#include <fstream>\nstd::ifstream in;\nstd::string line;\nstd::getline(in, line);\n",
    "cpfl_08": "#include <fstream>\nstd::ifstream in(\"data.txt\");\nstd::string line;\nstd::getline(in, line);\nin.close();\n",
    "cpfl_15": "std::ifstream in(\"x.txt\");\nstd::string line;\nstd::getline(in, line);\n",
    "cpm_01": "#include \"utils.h\"\n",
    "cpm_02": "// utils.h\n#pragma once\nint add(int a, int b);\n",
    "cpm_03": "int add(int a, int b) { return a + b; }\n",
    "cpm_04": "int add(int a, int b);\n",
    "cpm_08": "#pragma once\nint add(int a, int b);\n",
    "cpm_13": "#pragma once\nint add(int,int);\n// utils.cpp\nint add(int a,int b){return a+b;}\n",
    "cpm_15": "#ifndef UTILS_H\n#define UTILS_H\nint add(int,int);\n#endif\n",
    "cpm_16": "#pragma once\nint add(int,int);\n",
    "cprc_01": "int fact(int n){ if(n<=1)return 1; return n*fact(n-1);}\n",
    "cprc_02": "int fact(int n){ return n*fact(n-1);}\n",
    "cprc_03": "int fib(int n);\nint fib(int n){ if(n<2)return n; return fib(n-1)+fib(n-2);}\n",
    "cprc_04": "int f(int n){ return f(n-1);}\n",
    "cprc_07": "int sum(int n){ if(n==0)return 0; return n+sum(n-1);}\n",
    "cpo_01": "class Point { public: int x, y; };\n",
    "cpo_02": "class Box { public: Box(int w): w_(w) {} private: int w_; };\n",
    "cpo_03": "class File { public: ~File() { close(); } void close(); };\n",
    "cpo_05": "class Base { void f(); };\nclass Der: public Base { void f() override; };\n",
    "cpo_06": "class Base { virtual void f(); };\nclass Der: public Base { void f() override; };\n",
    "cpo_09": "class A { void f() { } };\n",
    "cpo_13": "class Widget { public: int id; };\n",
    "cpo_17": "class Counter { public: Counter(): n_(0) {} private: int n_; };\n",
    "cpo_15": "class Base { virtual void f(); };\nclass Der: public Base { void f() override; };\n",
    "cpo_18": "struct Base { virtual ~Base()=default; };\nstruct Der: Base {};\nBase b = Der{};\n",
    "cpo_19": "class String { public: String(const char*); };\nString s = \"hi\";\n",
    "cpo_20": "class A { public: A()=default; A(const A&)=delete; };\n",
    "cppit_01": "if (x > 0) { ; } else { }\n",
    "cppit_04": "for (int i = 0; i < n; ++i) { i = 0; }\n",
    "cppit_16": "void swapVal(int a, int b){ int t=a; a=b; b=t; }\n",
    "cppit_18": "std::vector<int> v(3);\nstd::cout << v[3];\n",
    "cppit_20": "int* p = new int(1);\ndelete p;\ndelete p;\n",
    "cppit_21": "int& bad(){ int x=1; return x; }\n",
    "cpdg_01": "std::cout << y;\n",
    "cpdg_02": "int x = 3.14;\n",
    "cpdg_04": "int main(){ return 0 }\n",
    "cpdg_06": "int main(){ if(1){ return 0;\n",
}

_SLOT_REFERENCE.update(capstone_reference_cpp())

_SLOT_DEBUG_STARTER: dict[str, str] = {
    "cpk_02": "#include <iostream>\nint main() {\n    std::cout << \"Hi\" << std::endl\n    return 0;\n}\n",
    "cpt_02": "int x = 0;\nif (x = 1) { }\n",
    "cpt_14": "int x;\nstd::cout << x << std::endl;\n",
    "cpi_01": "int x;\ncin >> x;\n",
    "cpi_09": "int x;\nstd::cin >> x;\nstd::cout << \"Enter:\";\n",
    "cpi_10": "int n;\nstd::cin >> n;\nstd::string line;\nstd::getline(std::cin, line);\n",
    "cpe_06": "double x = 5.5;\nint r = x % 2;\n",
    "cpe_10": "double r = 5 / 2;\nstd::cout << r;\n",
    "cpe_11": "std::cout << 1 + 2 << 3 << std::endl;\n",
    "cpk_12": "#include \"iostream\"\nint main() { return 0; }\n",
    "cpc_17": "if (x = 1) { std::cout << x; }\n",
    "cpl_08": "int x;\ndo { std::cin >> x; } while (x < 0);\n",
    "cpfn_03": "int add(int a, b) { return a + b; }\n",
    "cpfn_16": "greet() { std::cout << \"hi\"; }\n",
    "cpfn_17": "int pick(int x) { if (x > 0) return 1; }\n",
    "cpp_02": "void swapVal(int a, int b) { int t = a; a = b; b = t; }\n",
    "cpp_12": "void bump(int x) { ++x; }\n",
    "cpp_15": "void swapVal(int a, int b) { int t = a; a = b; b = t; }\n",
    "cpp_17": "int& badRef() { int x = 1; return x; }\n",
    "cpa_03": "int a[5];\nstd::cout << a[5];\n",
    "cpa_09": "int a[3];\nstd::cout << a[3];\n",
    "cpd_10": "std::vector<int> v;\nv.push_back(1);\nv[v.size()] = 2;\n",
    "cpd_15": "std::vector<int> v;\nv[v.size()] = 1;\n",
    "cpd_16": "std::vector<int> v = {1,2};\nauto it = v.begin();\nv.push_back(3);\nstd::cout << *it;\n",
    "cps_03": "std::string s = \"hi\";\nchar c = s[s.size()];\n",
    "cps_16": "const char* a = \"x\";\nconst char* b = \"x\";\nif (a == b) { }\n",
    "cps_17": "std::string s;\n",
    "cppt_03": "int* p;\nif (p == nullptr) { }\n",
    "cppt_05": "int* p = new int(1);\n",
    "cppt_06": "int* p = new int(1);\ndelete p;\ndelete p;\n",
    "cppt_07": "int* p;\n{ int x = 1; p = &x; }\nstd::cout << *p;\n",
    "cppt_14": "#include <memory>\nvoid take(std::unique_ptr<int> p) {}\nauto p = std::make_unique<int>(1);\ntake(p);\n",
    "cppr_02": "#ifdef DEBUG\nstd::cout << \"dbg\";\n#endif\n",
    "cppr_04": "#define SQR(x) x*x\nint n = SQR(1+2);\n",
    "cptpl_02": "template<typename T> void swapVal(T& a, T& b);\nswapVal(1, 2.0);\n",
    "cpen_02": "enum class Color { Red };\nColor c = Color::Red;\nif (c == 1) { }\n",
    "cpas_02": "#include <map>\nstd::map<std::string,int> m{{\"a\",1}};\nint x = m[\"b\"];\n",
    "cpalg_05": "std::vector<int> v{1,2};\nstd::sort(v.begin(), v.end());\n",
    "cpalg_06": "std::vector<int> v;\nv.push_back(3);\nv.push_back(1);\nstd::sort(v.begin(), v.end() - 1);\n",
    "cpmv_05": "std::string s = \"hi\";\nstd::string t = std::move(s);\nstd::cout << s.size();\n",
    "cpex_02": "try { throw std::runtime_error(\"fail\"); } catch (const std::exception& e) { std::cout << \"caught\"; }\n",
    "cpex_04": "try { throw; } catch (...) { throw; }\n",
    "cpex_05": "try { int x = 1/0; } catch (...) { }\n",
    "cpex_07": "std::ifstream f(\"missing.txt\");\nstd::cout << \"no file\";\n",
    "cpfl_03": "#include <fstream>\nstd::ofstream out(\"out.txt\");\nout << 1;\n",
    "cpfl_07": "#include <fstream>\nstd::ifstream in;\nstd::getline(in, line);\n",
    "cpfl_15": "std::ifstream in(\"x.txt\");\nstd::getline(in, line);\n",
    "cpm_03": "int add(int a, int b) { return a + b; }\n",
    "cpm_17": "int add(int a,int b){return a+b;}\nint add(int a,int b){return a+b;}\n",
    "cprc_02": "int fact(int n){ return n*fact(n-1);}\n",
    "cprc_04": "int f(int n){ return f(n-1);}\n",
    "cpo_05": "class Base { void f(); };\nclass Der: public Base { void f() override; };\n",
    "cpo_15": "class Base { virtual void f(); };\nclass Der: public Base { void f() override; };\n",
    "cppit_01": "if (x > 0) { ; } else { }\n",
    "cppit_18": "std::vector<int> v(3);\nstd::cout << v[3];\n",
    "cppit_20": "int* p = new int(1);\ndelete p;\ndelete p;\n",
    "cppit_21": "int& bad(){ int x=1; return x; }\n",
    "cpdg_01": "std::cout << y;\n",
    "cpdg_02": "int x = 3.14;\n",
    "cpdg_04": "int main(){ return 0 }\n",
    "cpdg_06": "int main(){ if(1){ return 0;\n",
}

_SLOT_DEBUG_STARTER.update(capstone_starter_cpp())


def reference_solution_for_slot(slot_id: str, *, slot_pattern_id: str | None = None) -> str:
    if slot_id in _SLOT_REFERENCE:
        return _SLOT_REFERENCE[slot_id]
    try:
        from application.curriculum.content.algo_syntax_task_extra import (
            algo_reference_code,
            is_algo_syntax_slot,
            resolve_slot_pattern_key,
        )
        from application.curriculum.content.v4_reference_code import get_reference_code

        if is_algo_syntax_slot(slot_id):
            ref = algo_reference_code(slot_id, "cpp", slot_pattern_id=slot_pattern_id)
            if ref:
                return ref
        pattern = resolve_slot_pattern_key(slot_id, slot_pattern_id=slot_pattern_id)
        code = get_reference_code(slot_id, "cpp", pattern_key=pattern)
        if code:
            return code
    except ImportError:
        pass
    return "int main() {\n    return 0;\n}\n"


def debug_starter_for_slot(slot_id: str) -> str:
    from application.curriculum.content.algo_syntax_task_extra import (
        algo_debug_starter,
        is_algo_syntax_slot,
    )

    if is_algo_syntax_slot(slot_id):
        starter = algo_debug_starter(slot_id, "cpp")
        if starter:
            return starter
    return _SLOT_DEBUG_STARTER.get(slot_id, reference_solution_for_slot(slot_id))


def build_task_extra(row: tuple) -> dict[str, Any]:
    slot_id, _chapter, _title, fmt, _action, pattern, goal, features, _diff, _legacy = row
    extra: dict[str, Any] = {
        "slot_pattern_id": pattern,
        "task_format": fmt,
        "cpp_features": features,
        "educational_goal": goal,
        "expected_concept_ids": [],
    }
    ref = reference_solution_for_slot(slot_id, slot_pattern_id=pattern)
    from application.curriculum.content.algo_syntax_showcase_meta import (
        attach_expected_concepts_to_extra,
    )
    from application.curriculum.content.algo_syntax_task_extra import is_algo_syntax_slot
    if is_algo_syntax_slot(slot_id):
        extra = attach_expected_concepts_to_extra(
            extra,
            slot_id=slot_id,
            slot_pattern_id=pattern,
        )
    from application.curriculum.content.algo_syntax_task_extra import resolve_slot_pattern_key
    _py = "print('demo')"
    _pas = "writeln('demo');"
    _java = "System.out.println(\"demo\");"
    _cs = "Console.WriteLine(\"demo\");"
    try:
        from application.curriculum.content.v4_reference_code import get_reference_code

        pattern_key = resolve_slot_pattern_key(slot_id, slot_pattern_id=pattern)
        _py = get_reference_code(slot_id, "python", pattern_key=pattern_key) or _py
        _pas = get_reference_code(slot_id, "pascal", pattern_key=pattern_key) or _pas
        _java = get_reference_code(slot_id, "java", pattern_key=pattern_key) or _java
        _cs = get_reference_code(slot_id, "csharp", pattern_key=pattern_key) or _cs
    except ImportError:
        pass
    variants = build_known_language_variants(
        python=_py,
        pascal=_pas,
        java=_java,
        csharp=_cs,
    )
    extra["known_language_variants"] = variants
    if fmt in {"исправление", "поиск_ошибки"}:
        extra["starter_cpp"] = debug_starter_for_slot(slot_id)
        extra["reference_cpp"] = ref
    elif fmt.startswith("перевод"):
        from application.curriculum.content.algo_syntax_task_extra import (
            algo_translation_starter,
            is_algo_syntax_slot,
        )

        extra["source_language"] = "python"
        extra["source_code"] = variants["python"]["source_code"]
        extra["reference_cpp"] = ref
        extra["starter_cpp"] = (
            algo_translation_starter(slot_id, "cpp")
            if is_algo_syntax_slot(slot_id)
            else ref
        )
    elif fmt.startswith("сборка"):
        from application.curriculum.content.v4_assembly_extra import apply_v4_assembly_extra

        apply_v4_assembly_extra(
            extra,
            slot_id=slot_id,
            language="cpp",
            task_format=fmt,
            reference_code=ref,
        )
    extra["concept_patterns"] = ["assign"]
    return extra


def attach_cpp_code_examples(examples: dict[str, Any], slot_id: str, extra: dict[str, Any]) -> dict[str, Any]:
    merged = dict(examples or {})
    variants = extra.get("known_language_variants")
    if isinstance(variants, dict):
        merged.update(code_examples_from_variants(variants))
    starter = str(extra.get("starter_cpp") or "").strip()
    ref = str(extra.get("reference_cpp") or reference_solution_for_slot(slot_id)).strip()
    if starter:
        merged["cpp"] = starter
    elif ref:
        merged["cpp"] = ref
    return merged
