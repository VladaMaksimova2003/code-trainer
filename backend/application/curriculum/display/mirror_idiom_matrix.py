"""Full mirror idiom hints for all directed language pairs (5×5 minus identity).

Used by ATCC popover hints and FCC proactive warnings when a pitfall has no
pair-specific override. Keys use authoring concept ids (program_entry, …).
"""

from __future__ import annotations

from typing import Any

KNOWN_LANGS: tuple[str, ...] = ("pascal", "python", "cpp", "csharp", "java")

_LANG_RU: dict[str, str] = {
    "pascal": "Pascal",
    "python": "Python",
    "cpp": "C++",
    "csharp": "C#",
    "java": "Java",
}


def _pairs(*entries: tuple[str, str, str]) -> dict[tuple[str, str], str]:
    return {(src, tgt): text for src, tgt, text in entries}


def _cross_c_family(concept_body: dict[str, str]) -> dict[tuple[str, str], str]:
    """Replicate C-family ↔ hints for cpp, csharp, java."""
    out: dict[tuple[str, str], str] = {}
    cf = ("cpp", "csharp", "java")
    for src in cf:
        for tgt in cf:
            if src != tgt and concept_body.get(f"{src}->{tgt}"):
                out[(src, tgt)] = concept_body[f"{src}->{tgt}"]
    return out


# --- Core authoring concepts (directed pair → brief text, no prefix) ---

_MATRIX: dict[str, dict[tuple[str, str], str]] = {}

_MATRIX["program_entry"] = _pairs(
    ("python", "pascal", "program Name; begin … end."),
    ("pascal", "python", "скрипт или def main() без program/begin/end"),
    ("python", "cpp", "#include <iostream> и int main()"),
    ("cpp", "python", "if __name__ == '__main__':"),
    ("python", "java", "class Main { public static void main(String[] args) { … } }"),
    ("java", "python", "if __name__ == '__main__':"),
    ("python", "csharp", "class Program { static void Main() { … } }"),
    ("csharp", "python", "if __name__ == '__main__':"),
    ("pascal", "cpp", "int main() { … return 0; }"),
    ("cpp", "pascal", "program …; begin … end."),
    ("pascal", "java", "public class Main { public static void main(String[] args) { … } }"),
    ("java", "pascal", "program …; begin … end."),
    ("pascal", "csharp", "class Program { static void Main() { … } }"),
    ("csharp", "pascal", "program …; begin … end."),
    ("cpp", "java", "public class App { public static void main(String[] args) { … } }"),
    ("java", "cpp", "int main() { … return 0; }"),
    ("cpp", "csharp", "class Program { static void Main() { … } }"),
    ("csharp", "cpp", "int main() { … return 0; }"),
    ("java", "csharp", "class Program { static void Main() { … } }"),
    ("csharp", "java", "public class Main { public static void main(String[] args) { … } }"),
)

_MATRIX["typed_declaration"] = _pairs(
    ("python", "pascal", "var x: integer; в секции var"),
    ("pascal", "python", "x = 0 без секции var"),
    ("python", "cpp", "int x;"),
    ("cpp", "python", "x = 0 без явного типа"),
    ("python", "java", "int x;"),
    ("java", "python", "x = 0 или x: int = 0"),
    ("python", "csharp", "int x;"),
    ("csharp", "python", "x = 0 или x: int = 0"),
    ("pascal", "cpp", "int x;"),
    ("cpp", "pascal", "var x: integer;"),
    ("pascal", "java", "int x;"),
    ("java", "pascal", "var x: integer;"),
    ("pascal", "csharp", "int x;"),
    ("csharp", "pascal", "var x: integer;"),
    ("cpp", "java", "int x;"),
    ("java", "cpp", "int x;"),
    ("cpp", "csharp", "int x;"),
    ("csharp", "cpp", "int x;"),
    ("java", "csharp", "int x;"),
    ("csharp", "java", "int x;"),
)

_MATRIX["assignment"] = _pairs(
    ("python", "pascal", "x := 1; (= только сравнение)"),
    ("pascal", "python", "x = 1"),
    ("python", "cpp", "x = 1;"),
    ("cpp", "python", "x = 1"),
    ("python", "java", "x = 1;"),
    ("java", "python", "x = 1"),
    ("python", "csharp", "x = 1;"),
    ("csharp", "python", "x = 1"),
    ("pascal", "cpp", "x = 1;"),
    ("cpp", "pascal", "x := 1;"),
    ("pascal", "java", "x = 1;"),
    ("java", "pascal", "x := 1;"),
    ("pascal", "csharp", "x = 1;"),
    ("csharp", "pascal", "x := 1;"),
    ("cpp", "java", "x = 1;"),
    ("java", "cpp", "x = 1;"),
    ("cpp", "csharp", "x = 1;"),
    ("csharp", "cpp", "x = 1;"),
    ("java", "csharp", "x = 1;"),
    ("csharp", "java", "x = 1;"),
)

_MATRIX["stdin_read"] = _pairs(
    ("python", "pascal", "readln(x);"),
    ("pascal", "python", "x = int(input())"),
    ("python", "cpp", "std::cin >> x;"),
    ("cpp", "python", "int(input()) или map(int, input().split())"),
    ("python", "java", "Scanner.nextInt()"),
    ("java", "python", "int(input())"),
    ("python", "csharp", "int.Parse(Console.ReadLine())"),
    ("csharp", "python", "int(input())"),
    ("pascal", "cpp", "std::cin >> x;"),
    ("cpp", "pascal", "readln(x);"),
    ("pascal", "java", "Scanner / nextInt"),
    ("java", "pascal", "readln(x);"),
    ("pascal", "csharp", "Console.ReadLine / int.Parse"),
    ("csharp", "pascal", "readln(x);"),
    ("cpp", "java", "Scanner.nextInt()"),
    ("java", "cpp", "std::cin >> x;"),
    ("cpp", "csharp", "Console.ReadLine"),
    ("csharp", "cpp", "std::cin >> x;"),
    ("java", "csharp", "int.Parse(Console.ReadLine())"),
    ("csharp", "java", "Scanner.nextInt()"),
)

_MATRIX["stdout_write"] = _pairs(
    ("python", "pascal", "writeln(...);"),
    ("pascal", "python", "print(...)"),
    ("python", "cpp", "std::cout << … << std::endl;"),
    ("cpp", "python", "print(...)"),
    ("python", "java", "System.out.println(...)"),
    ("java", "python", "print(...)"),
    ("python", "csharp", "Console.WriteLine(...)"),
    ("csharp", "python", "print(...)"),
    ("pascal", "cpp", "std::cout << … << std::endl;"),
    ("cpp", "pascal", "writeln(...);"),
    ("pascal", "java", "System.out.println(...)"),
    ("java", "pascal", "writeln(...);"),
    ("pascal", "csharp", "Console.WriteLine(...)"),
    ("csharp", "pascal", "writeln(...);"),
    ("cpp", "java", "System.out.println(...)"),
    ("java", "cpp", "std::cout << …;"),
    ("cpp", "csharp", "Console.WriteLine(...)"),
    ("csharp", "cpp", "std::cout << …;"),
    ("java", "csharp", "Console.WriteLine(...)"),
    ("csharp", "java", "System.out.println(...)"),
)

_MATRIX["counted_loop"] = _pairs(
    ("python", "pascal", "for i := 1 to n do"),
    ("pascal", "python", "for i in range(n): или range(1, n+1)"),
    ("python", "cpp", "for (int i = 0; i < n; ++i)"),
    ("cpp", "python", "for i in range(n):"),
    ("python", "java", "for (int i = 0; i < n; i++)"),
    ("java", "python", "for i in range(n):"),
    ("python", "csharp", "for (int i = 0; i < n; i++)"),
    ("csharp", "python", "for i in range(n):"),
    ("pascal", "cpp", "for (int i = 0; i < n; ++i) или 1..n по задаче"),
    ("cpp", "pascal", "for i := 1 to n do"),
    ("pascal", "java", "for (int i = 0; i < n; i++)"),
    ("java", "pascal", "for i := 1 to n do"),
    ("pascal", "csharp", "for (int i = 0; i < n; i++)"),
    ("csharp", "pascal", "for i := 1 to n do"),
    ("cpp", "java", "for (int i = 0; i < n; i++)"),
    ("java", "cpp", "for (int i = 0; i < n; ++i)"),
    ("cpp", "csharp", "for (int i = 0; i < n; i++)"),
    ("csharp", "cpp", "for (int i = 0; i < n; ++i)"),
    ("java", "csharp", "for (int i = 0; i < n; i++)"),
    ("csharp", "java", "for (int i = 0; i < n; i++)"),
)

_MATRIX["collection_iteration"] = _pairs(
    ("python", "pascal", "for i := 1 to n do a[i]"),
    ("pascal", "python", "for x in items: или for i in range(len(a))"),
    ("python", "cpp", "for (auto x : v) или индексный for"),
    ("cpp", "python", "for x in items:"),
    ("python", "java", "for (T x : arr)"),
    ("java", "python", "for x in items:"),
    ("python", "csharp", "foreach (var x in items)"),
    ("csharp", "python", "for x in items:"),
    ("pascal", "cpp", "for (int i = 0; i < n; ++i)"),
    ("cpp", "pascal", "for i := 1 to n do"),
    ("pascal", "java", "for (T x : arr)"),
    ("java", "pascal", "for i := 1 to n do"),
    ("pascal", "csharp", "foreach (var x in arr)"),
    ("csharp", "pascal", "for i := 1 to n do"),
    ("cpp", "java", "for (T x : arr)"),
    ("java", "cpp", "range-for или индекс"),
    ("cpp", "csharp", "foreach (var x in list)"),
    ("csharp", "cpp", "range-for"),
    ("java", "csharp", "foreach (var x in list)"),
    ("csharp", "java", "for (T x : arr)"),
)

_MATRIX["indexed_sequence"] = _pairs(
    ("python", "pascal", "a[1] при array[1..n]"),
    ("pascal", "python", "a[0] при list"),
    ("python", "cpp", "a[i] с нуля; vector/array"),
    ("cpp", "python", "a[0] при list"),
    ("python", "java", "a[i] с нуля"),
    ("java", "python", "a[0] при list"),
    ("python", "csharp", "a[i] с нуля"),
    ("csharp", "python", "a[0] при list"),
    ("pascal", "cpp", "array[0..n-1] или vector[i] с нуля"),
    ("cpp", "pascal", "a[1] при static array[1..n]"),
    ("pascal", "java", "arr[i] с нуля"),
    ("java", "pascal", "a[1]"),
    ("pascal", "csharp", "arr[i] с нуля"),
    ("csharp", "pascal", "a[1]"),
    ("cpp", "java", "arr[i]"),
    ("java", "cpp", "v[i]"),
    ("cpp", "csharp", "arr[i]"),
    ("csharp", "cpp", "v[i]"),
    ("java", "csharp", "arr[i]"),
    ("csharp", "java", "arr[i]"),
)

_MATRIX["arithmetic_ops"] = _pairs(
    ("python", "pascal", "div и mod вместо // и %"),
    ("pascal", "python", "целое частное — //, не /"),
    ("cpp", "python", "целое частное — //, не / (обычный / даёт float)"),
    ("python", "cpp", "для int — / целое; для float — вещественное"),
    ("pascal", "cpp", "div/mod → / и % для int"),
    ("cpp", "pascal", "div и mod вместо / и %"),
    ("python", "java", "целое частное — //"),
    ("java", "python", "целое частное — //, не /"),
    ("python", "csharp", "целое частное — //"),
    ("csharp", "python", "целое частное — //, не /"),
    ("pascal", "java", "div/mod → / и %"),
    ("java", "pascal", "div и mod"),
    ("pascal", "csharp", "div/mod → / и %"),
    ("csharp", "pascal", "div и mod"),
    ("cpp", "java", "/ и % для int; следите за типами"),
    ("java", "cpp", "/ и % для int"),
    ("cpp", "csharp", "/ и % для int"),
    ("csharp", "cpp", "/ и % для int"),
    ("java", "csharp", "/ и % для int"),
    ("csharp", "java", "/ и % для int"),
)

_MATRIX["simple_branch"] = _pairs(
    ("python", "pascal", "if cond then … else …"),
    ("pascal", "python", "if cond: … elif … else:"),
    ("python", "cpp", "if (cond) { … } else { … }"),
    ("cpp", "python", "if cond: … else:"),
    ("python", "java", "if (cond) { … } else { … }"),
    ("java", "python", "if cond: … else:"),
    ("python", "csharp", "if (cond) { … } else { … }"),
    ("csharp", "python", "if cond: … else:"),
    ("pascal", "cpp", "if (cond) { … }"),
    ("cpp", "pascal", "if cond then begin … end"),
    ("pascal", "java", "if (cond) { … }"),
    ("java", "pascal", "if cond then …"),
    ("pascal", "csharp", "if (cond) { … }"),
    ("csharp", "pascal", "if cond then …"),
    ("cpp", "java", "if (cond) { … }"),
    ("java", "cpp", "if (cond) { … }"),
    ("cpp", "csharp", "if (cond) { … }"),
    ("csharp", "cpp", "if (cond) { … }"),
    ("java", "csharp", "if (cond) { … }"),
    ("csharp", "java", "if (cond) { … }"),
)

_MATRIX["multi_branch"] = _pairs(
    ("python", "pascal", "else if"),
    ("pascal", "python", "elif"),
    ("python", "cpp", "else if"),
    ("cpp", "python", "elif"),
    ("python", "java", "else if"),
    ("java", "python", "elif"),
    ("python", "csharp", "else if"),
    ("csharp", "python", "elif"),
    ("pascal", "cpp", "else if"),
    ("cpp", "pascal", "else if"),
    ("pascal", "java", "else if"),
    ("java", "pascal", "else if"),
    ("pascal", "csharp", "else if"),
    ("csharp", "pascal", "else if"),
    ("cpp", "java", "else if"),
    ("java", "cpp", "else if"),
    ("cpp", "csharp", "else if"),
    ("csharp", "cpp", "else if"),
    ("java", "csharp", "else if"),
    ("csharp", "java", "else if"),
)

_MATRIX["switch_selection"] = _pairs(
    ("python", "pascal", "case x of … end;"),
    ("pascal", "python", "if/elif или match/case"),
    ("python", "cpp", "switch (x) { case …: break; }"),
    ("cpp", "python", "if/elif или match"),
    ("python", "java", "switch (x) { case …: break; }"),
    ("java", "python", "if/elif или match"),
    ("python", "csharp", "switch (x) { case …: break; }"),
    ("csharp", "python", "if/elif или match"),
    ("pascal", "cpp", "switch (x)"),
    ("cpp", "pascal", "case x of"),
    ("pascal", "java", "switch (x)"),
    ("java", "pascal", "case x of"),
    ("pascal", "csharp", "switch (x)"),
    ("csharp", "pascal", "case x of"),
    ("cpp", "java", "switch (x)"),
    ("java", "cpp", "switch (x)"),
    ("cpp", "csharp", "switch (x)"),
    ("csharp", "cpp", "switch (x)"),
    ("java", "csharp", "switch (x)"),
    ("csharp", "java", "switch (x)"),
)

_MATRIX["function_definition"] = _pairs(
    ("python", "pascal", "function Name(...): T; begin … Name := …; end;"),
    ("pascal", "python", "def name(...): return …"),
    ("python", "cpp", "ReturnType name(...) { return …; }"),
    ("cpp", "python", "def name(...): return …"),
    ("python", "java", "ReturnType name(...) { return …; }"),
    ("java", "python", "def name(...): return …"),
    ("python", "csharp", "ReturnType Name(...) { return …; }"),
    ("csharp", "python", "def name(...): return …"),
    ("pascal", "cpp", "ReturnType name(...) { … }"),
    ("cpp", "pascal", "function Name: T; begin Name := …; end;"),
    ("pascal", "java", "ReturnType name(...) { … }"),
    ("java", "pascal", "function Name: T; begin Name := …; end;"),
    ("pascal", "csharp", "ReturnType Name(...) { … }"),
    ("csharp", "pascal", "function Name: T; begin Name := …; end;"),
    ("cpp", "java", "ReturnType name(...) { … }"),
    ("java", "cpp", "ReturnType name(...) { … }"),
    ("cpp", "csharp", "ReturnType Name(...) { … }"),
    ("csharp", "cpp", "ReturnType name(...) { … }"),
    ("java", "csharp", "ReturnType Name(...) { … }"),
    ("csharp", "java", "ReturnType name(...) { … }"),
)

_MATRIX["return_flow"] = _pairs(
    ("python", "pascal", "ИмяФункции := значение;"),
    ("pascal", "python", "return значение"),
    ("python", "cpp", "return value;"),
    ("cpp", "python", "return value"),
    ("python", "java", "return value;"),
    ("java", "python", "return value"),
    ("python", "csharp", "return value;"),
    ("csharp", "python", "return value"),
    ("pascal", "cpp", "return value;"),
    ("cpp", "pascal", "FunctionName := value;"),
    ("pascal", "java", "return value;"),
    ("java", "pascal", "FunctionName := value;"),
    ("pascal", "csharp", "return value;"),
    ("csharp", "pascal", "FunctionName := value;"),
    ("cpp", "java", "return value;"),
    ("java", "cpp", "return value;"),
    ("cpp", "csharp", "return value;"),
    ("csharp", "cpp", "return value;"),
    ("java", "csharp", "return value;"),
    ("csharp", "java", "return value;"),
)

_MATRIX["parameter_passing"] = _pairs(
    ("python", "pascal", "procedure P(var x: integer);"),
    ("pascal", "python", "изменяемый аргумент через return или mutable объект"),
    ("python", "cpp", "void f(int& x) или указатель"),
    ("cpp", "python", "return или изменяемый list/dict"),
    ("python", "java", "объекты по ссылке; примитивы — через обёртку/массив"),
    ("java", "python", "return или mutable объект"),
    ("python", "csharp", "ref/out для in-out"),
    ("csharp", "python", "return или mutable объект"),
    ("pascal", "cpp", "int& или указатель"),
    ("cpp", "pascal", "var x: integer в заголовке"),
    ("pascal", "java", "обёртка или поле объекта"),
    ("java", "pascal", "var в заголовке procedure"),
    ("pascal", "csharp", "ref/out"),
    ("csharp", "pascal", "var в заголовке"),
    ("cpp", "java", "объект по ссылке"),
    ("java", "cpp", "int& / указатель"),
    ("cpp", "csharp", "ref/out"),
    ("csharp", "cpp", "int&"),
    ("java", "csharp", "ref/out"),
    ("csharp", "java", "объект по ссылке"),
)

_MATRIX["import_dependency"] = _pairs(
    ("python", "pascal", "uses UnitName;"),
    ("pascal", "python", "import module"),
    ("python", "cpp", "#include <…>"),
    ("cpp", "python", "import …"),
    ("python", "java", "import package.Class;"),
    ("java", "python", "import module"),
    ("python", "csharp", "using Namespace;"),
    ("csharp", "python", "import module"),
    ("pascal", "cpp", "#include <…>"),
    ("cpp", "pascal", "uses …;"),
    ("pascal", "java", "import …;"),
    ("java", "pascal", "uses …;"),
    ("pascal", "csharp", "using …;"),
    ("csharp", "pascal", "uses …;"),
    ("cpp", "java", "import …;"),
    ("java", "cpp", "#include …"),
    ("cpp", "csharp", "using …;"),
    ("csharp", "cpp", "#include …"),
    ("java", "csharp", "using …;"),
    ("csharp", "java", "import …;"),
)

_MATRIX["file_read"] = _pairs(
    ("python", "pascal", "Assign; Reset; Readln; CloseFile"),
    ("pascal", "python", "with open(...) as f:"),
    ("python", "cpp", "std::ifstream"),
    ("cpp", "python", "with open(...) as f:"),
    ("python", "java", "Files.readString / Scanner"),
    ("java", "python", "with open(...) as f:"),
    ("python", "csharp", "File.ReadAllText"),
    ("csharp", "python", "with open(...) as f:"),
    ("pascal", "cpp", "ifstream"),
    ("cpp", "pascal", "Assign/Reset/Readln"),
    ("pascal", "java", "Files.readString"),
    ("java", "pascal", "Assign/Reset"),
    ("pascal", "csharp", "File.ReadAllText"),
    ("csharp", "pascal", "Assign/Reset"),
    ("cpp", "java", "Files.readString"),
    ("java", "cpp", "ifstream"),
    ("cpp", "csharp", "File.ReadAllText"),
    ("csharp", "cpp", "ifstream"),
    ("java", "csharp", "File.ReadAllText"),
    ("csharp", "java", "Files.readString"),
)

_MATRIX["file_write"] = _pairs(
    ("python", "pascal", "Assign; Rewrite; Writeln; CloseFile"),
    ("pascal", "python", "with open(..., 'w') as f:"),
    ("python", "cpp", "std::ofstream"),
    ("cpp", "python", "with open(..., 'w') as f:"),
    ("python", "java", "Files.writeString"),
    ("java", "python", "with open(..., 'w') as f:"),
    ("python", "csharp", "File.WriteAllText"),
    ("csharp", "python", "with open(..., 'w') as f:"),
    ("pascal", "cpp", "ofstream"),
    ("cpp", "pascal", "Rewrite/Writeln"),
    ("pascal", "java", "Files.writeString"),
    ("java", "pascal", "Rewrite/Writeln"),
    ("pascal", "csharp", "File.WriteAllText"),
    ("csharp", "pascal", "Rewrite/Writeln"),
    ("cpp", "java", "Files.writeString"),
    ("java", "cpp", "ofstream"),
    ("cpp", "csharp", "File.WriteAllText"),
    ("csharp", "cpp", "ofstream"),
    ("java", "csharp", "File.WriteAllText"),
    ("csharp", "java", "Files.writeString"),
)

_MATRIX["fold_aggregate"] = _pairs(
    ("python", "pascal", "sum := 0; for i := 1 to n do sum := sum + a[i]"),
    ("pascal", "python", "total = 0; for x in nums: total += x"),
    ("python", "cpp", "int sum = 0; for (auto x : v) sum += x;"),
    ("cpp", "python", "total = 0; for x in v: total += x"),
    ("python", "java", "int sum = 0; for (int x : arr) sum += x;"),
    ("java", "python", "total = sum(arr) или цикл += "),
    ("python", "csharp", "int sum = 0; foreach (var x in nums) sum += x;"),
    ("csharp", "python", "total = sum(nums)"),
    ("pascal", "cpp", "accumulate или цикл +="),
    ("cpp", "pascal", "sum := 0; цикл"),
    ("pascal", "java", "stream reduce / цикл"),
    ("java", "pascal", "sum := 0; цикл"),
    ("pascal", "csharp", "Aggregate / цикл"),
    ("csharp", "pascal", "sum := 0; цикл"),
    ("cpp", "java", "stream reduce"),
    ("java", "cpp", "accumulate"),
    ("cpp", "csharp", "Aggregate"),
    ("csharp", "cpp", "accumulate"),
    ("java", "csharp", "Aggregate"),
    ("csharp", "java", "stream reduce"),
)

_MATRIX["filter_select"] = _pairs(
    ("python", "pascal", "for i := 1 to n do if a[i] > 0 then Inc(cnt)"),
    ("pascal", "python", "[x for x in nums if cond]"),
    ("python", "cpp", "copy_if или цикл с if"),
    ("cpp", "python", "list comp / filter()"),
    ("python", "java", "stream().filter()"),
    ("java", "python", "list comp"),
    ("python", "csharp", "Where(...)"),
    ("csharp", "python", "list comp"),
    ("pascal", "cpp", "copy_if"),
    ("cpp", "pascal", "цикл с if"),
    ("pascal", "java", "stream filter"),
    ("java", "pascal", "цикл с if"),
    ("pascal", "csharp", "Where"),
    ("csharp", "pascal", "цикл с if"),
    ("cpp", "java", "stream filter"),
    ("java", "cpp", "copy_if"),
    ("cpp", "csharp", "Where"),
    ("csharp", "cpp", "copy_if"),
    ("java", "csharp", "Where"),
    ("csharp", "java", "stream filter"),
)

_MATRIX["search_find"] = _pairs(
    ("python", "pascal", "for i := 1 to n do if a[i] = key then …"),
    ("pascal", "python", "key in items / for x in items"),
    ("python", "cpp", "std::find"),
    ("cpp", "python", "x in items / any()"),
    ("python", "java", "list.indexOf / contains"),
    ("java", "python", "key in list"),
    ("python", "csharp", "Contains / FirstOrDefault"),
    ("csharp", "python", "key in list"),
    ("pascal", "cpp", "std::find"),
    ("cpp", "pascal", "линейный for"),
    ("pascal", "java", "indexOf"),
    ("java", "pascal", "линейный for"),
    ("pascal", "csharp", "Contains"),
    ("csharp", "pascal", "линейный for"),
    ("cpp", "java", "indexOf"),
    ("java", "cpp", "std::find"),
    ("cpp", "csharp", "Contains"),
    ("csharp", "cpp", "std::find"),
    ("java", "csharp", "Contains"),
    ("csharp", "java", "indexOf"),
)

_MATRIX["exception_handling"] = _pairs(
    ("python", "pascal", "Val()/IOResult или коды ошибок, не try/except"),
    ("pascal", "python", "try/except"),
    ("python", "cpp", "try/catch"),
    ("cpp", "python", "try/except"),
    ("python", "java", "try/catch"),
    ("java", "python", "try/except"),
    ("python", "csharp", "try/catch"),
    ("csharp", "python", "try/except"),
    ("pascal", "cpp", "try/catch"),
    ("cpp", "pascal", "коды ошибок / IOResult"),
    ("pascal", "java", "try/catch"),
    ("java", "pascal", "IOResult / коды"),
    ("pascal", "csharp", "try/catch"),
    ("csharp", "pascal", "коды ошибок"),
    ("cpp", "java", "try/catch"),
    ("java", "cpp", "try/catch"),
    ("cpp", "csharp", "try/catch"),
    ("csharp", "cpp", "try/catch"),
    ("java", "csharp", "try/catch"),
    ("csharp", "java", "try/catch"),
)

# Aliases for canonical / legacy ids used in detection and pitfalls
_ALIASES: dict[str, str] = {
    "program_root": "program_entry",
    "main_entry": "program_entry",
    "block_scope": "program_entry",
    "variable_declaration": "typed_declaration",
    "console_input": "stdin_read",
    "console_output": "stdout_write",
    "loop": "counted_loop",
    "conditional": "simple_branch",
    "arithmetic": "arithmetic_ops",
    "import_module": "import_dependency",
    "reduce": "fold_aggregate",
    "filter": "filter_select",
}


def resolve_matrix_concept(concept_id: str) -> str | None:
    key = str(concept_id or "").strip()
    if not key:
        return None
    if key in _MATRIX:
        return key
    alias = _ALIASES.get(key)
    if alias and alias in _MATRIX:
        return alias
    from application.curriculum.validation.canonical_technical_ids import (
        LEGACY_TO_CANONICAL,
        canonical_technical_id,
    )

    canonical = canonical_technical_id(key)
    if canonical in _MATRIX:
        return canonical
    if canonical in _ALIASES and _ALIASES[canonical] in _MATRIX:
        return _ALIASES[canonical]
    for legacy, mapped in LEGACY_TO_CANONICAL.items():
        if mapped == canonical and legacy in _MATRIX:
            return legacy
    return None


def matrix_idiom_brief(source_language: str, target_language: str, concept_id: str) -> str | None:
    source = str(source_language or "").strip().lower()
    target = str(target_language or "").strip().lower()
    if source in {"cs", "c#"}:
        source = "csharp"
    if target in {"cs", "c#"}:
        target = "csharp"
    if source == target or source not in KNOWN_LANGS or target not in KNOWN_LANGS:
        return None
    resolved = resolve_matrix_concept(concept_id)
    if not resolved:
        return None
    text = (_MATRIX.get(resolved) or {}).get((source, target))
    if not text:
        return None
    src_ru = _LANG_RU.get(source, source)
    tgt_ru = _LANG_RU.get(target, target)
    return f"Перенос {src_ru} → {tgt_ru}: {text}"


def list_matrix_pairs(concept_id: str | None = None) -> list[dict[str, Any]]:
    """Introspection helper for docs and validation."""
    rows: list[dict[str, Any]] = []
    concepts = [concept_id] if concept_id else sorted(_MATRIX.keys())
    for concept in concepts:
        if concept not in _MATRIX:
            continue
        for (src, tgt), text in sorted(_MATRIX[concept].items()):
            rows.append({"concept": concept, "source": src, "target": tgt, "text": text})
    return rows


def count_matrix_pairs() -> int:
    return sum(len(pairs) for pairs in _MATRIX.values())
