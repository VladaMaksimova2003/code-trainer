"""Per-task «Я знаю» snippets for Python Course v1 (pascal, cpp, java, csharp)."""

from __future__ import annotations

from application.curriculum.python.catalog.python_v311_capstone_catalog import capstone_known_code
from application.curriculum.python.catalog.python_v12_delta_content import V12_KNOWN_CODE

# slot_id -> (pascal, cpp, java, csharp)
_C: dict[str, tuple[str, str, str, str]] = {
    "pyk_01": (
        "program Demo;\nbegin\n  writeln('Hello');\nend.",
        '#include <iostream>\nint main() { std::cout << "Hello"; return 0; }',
        'public class Main { public static void main(String[] a) { System.out.println("Hello"); } }',
        'using System;\nclass Program { static void Main() { Console.WriteLine("Hello"); } }',
    ),
    "pyk_04": (
        "program Demo;\nbegin\nend.",
        "int main() { return 0; }",
        "public static void main(String[] args) { }",
        "static void Main() { }",
    ),
    "pyt_02": (
        "x := 1;",
        "int x = 1;",
        "int x = 1;",
        "int x = 1;",
    ),
    "pyt_03": (
        "var x, y: real;\nbegin\n  x := 3.14;\n  y := 2.71;\nend.",
        "float x = 3.14f;\ndouble y = 2.71;",
        "float x = 3.14f;\ndouble y = 2.71;",
        "float x = 3.14f;\ndouble y = 2.71;",
    ),
    "pyt_07": (
        "x: subrange = 1..10;\nbegin\n  x := 5;\nend.",
        "int x = 5;\nassert(x >= 1 && x <= 10);",
        "int x = 5;\nassert x >= 1 && x <= 10;",
        "int x = 5;\nif (x < 1 || x > 10) throw new Exception();",
    ),
    "pyt_10": (
        "n := trunc(7.9);\nm := round(7.9);",
        "double x = 7.9;\nint n = (int)x;\nint m = (int)round(x);",
        "double x = 7.9;\nint n = (int)x;\nint m = (int)Math.round(x);",
        "double x = 7.9;\nint n = (int)x;\nint m = (int)Math.Round(x);",
    ),
    "pyt_11": (
        "x: integer = 42",
        "int x = 42;",
        "int x = 42;",
        "int x = 42;",
    ),
    "pye_01": (
        "q := a div b;\nr := a mod b;",
        "int q = a / b; int r = a % b;",
        "int q = a / b; int r = a % b;",
        "int q = a / b; int r = a % b;",
    ),
    "pyc_01": (
        "if x > 0 then writeln('yes') else writeln('no');",
        "if (x > 0) cout << \"yes\"; else cout << \"no\";",
        "if (x > 0) System.out.println(\"yes\"); else System.out.println(\"no\");",
        "if (x > 0) Console.WriteLine(\"yes\"); else Console.WriteLine(\"no\");",
    ),
    "pyl_01": (
        "for i := 1 to n do writeln(i);",
        "for (int i = 1; i <= n; ++i) cout << i << endl;",
        "for (int i = 1; i <= n; i++) System.out.println(i);",
        "for (int i = 1; i <= n; i++) Console.WriteLine(i);",
    ),
    "pyf_01": (
        "function Add(a, b: integer): integer;\nbegin Result := a + b; end;",
        "int add(int a, int b) { return a + b; }",
        "static int add(int a, int b) { return a + b; }",
        "static int Add(int a, int b) => a + b;",
    ),
    "pya_01": (
        "var a: array[0..2] of integer;\na[0] := 1;",
        "int a[3] = {1, 0, 0};",
        "int[] a = {1, 0, 0};",
        "int[] a = {1, 0, 0};",
    ),
    "pycmp_03": (
        "for i := Low(dict) to High(dict) do ...",
        "std::map<std::string,int> m;",
        "Map<String, Integer> m = new HashMap<>();",
        "Dictionary<string, int> m = new();",
    ),
}

_C.update(V12_KNOWN_CODE)
_C.update(capstone_known_code())

_FALLBACK = (
    "writeln('demo');",
    'std::cout << "demo";',
    'System.out.println("demo");',
    'Console.WriteLine("demo");',
)

_DEMO_PASCAL = _FALLBACK[0]


def get_known_code(slot_id: str) -> tuple[str, str, str, str] | None:
    return _C.get(slot_id)


def fallback_known_code() -> tuple[str, str, str, str]:
    return _FALLBACK


def is_demo_known_code(code: str | None) -> bool:
    text = str(code or "").strip()
    if not text:
        return True
    return text in _FALLBACK or text == _DEMO_PASCAL


def _codes_from_v4_reference(slot_id: str) -> tuple[str, str, str, str] | None:
    try:
        from application.curriculum.content.v4_reference_code import get_reference_code
    except ImportError:
        return None

    pascal = str(get_reference_code(slot_id, "pascal") or "").strip()
    cpp = str(get_reference_code(slot_id, "cpp") or "").strip()
    java = str(get_reference_code(slot_id, "java") or "").strip()
    csharp = str(get_reference_code(slot_id, "csharp") or "").strip()
    if not any((pascal, cpp, java, csharp)):
        return None
    return (
        pascal or _FALLBACK[0],
        cpp or _FALLBACK[1],
        java or _FALLBACK[2],
        csharp or _FALLBACK[3],
    )


def resolve_known_codes(slot_id: str) -> tuple[str, str, str, str]:
    """Return (pascal, cpp, java, csharp) snippets for a Python-course slot."""
    from application.curriculum.content.v4_placeholder_reference import (
        get_placeholder_reference,
        is_placeholder_slot,
    )

    if is_placeholder_slot(slot_id):
        return (
            get_placeholder_reference(slot_id, "pascal"),
            get_placeholder_reference(slot_id, "cpp"),
            get_placeholder_reference(slot_id, "java"),
            get_placeholder_reference(slot_id, "csharp"),
        )

    direct = get_known_code(slot_id)
    if direct is not None:
        return direct

    v4_codes = _codes_from_v4_reference(slot_id)
    if v4_codes is not None and not is_demo_known_code(v4_codes[0]):
        return v4_codes

    from application.curriculum.mirror.curriculum_slot_mirror import mirror_slot_id

    pas_id = mirror_slot_id(slot_id, target="pascal")
    if pas_id:
        from application.curriculum.pascal.catalog.pascal_v311_known_code import (
            get_known_code as get_pascal_known,
        )

        pas_codes = get_pascal_known(pas_id)
        if pas_codes is not None:
            _py, cpp, java, csharp = pas_codes
            pascal = _pascal_snippet_for_slot(pas_id)
            if not is_demo_known_code(pascal):
                return pascal, cpp, java, csharp

        mirrored_v4 = _codes_from_v4_reference(pas_id)
        if mirrored_v4 is not None and not is_demo_known_code(mirrored_v4[0]):
            return mirrored_v4

    if v4_codes is not None:
        return v4_codes

    return fallback_known_code()


def _pascal_snippet_for_slot(pascal_slot_id: str) -> str:
    v4_codes = _codes_from_v4_reference(pascal_slot_id)
    if v4_codes is not None:
        pascal = v4_codes[0].strip()
        if pascal:
            return pascal

    try:
        from application.curriculum.pascal.catalog import pascal_v311_content as pc

        starter = pc._debug_starter(pascal_slot_id)
        if starter and starter.strip():
            return starter.strip()
        ref = pc._reference_solution(pascal_slot_id, "").strip()
        if ref:
            return ref
    except Exception:
        pass
    return _DEMO_PASCAL
