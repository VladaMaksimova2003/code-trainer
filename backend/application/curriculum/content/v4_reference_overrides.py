"""Curated reference programs that replace docx stub rows in v4/algo catalogs."""

from __future__ import annotations

import re

_STUB_MARKER = re.compile(r"/\*[^*]+\*/\s*for\s*\(\s*int\s+\w+\s*:\s*\w+\s*\)", re.I)


def is_stub_reference_code(code: str, language: str = "") -> bool:
    text = str(code or "").strip()
    if not text:
        return False
    if _STUB_MARKER.search(text):
        return True
    if "System.out. print" in text or "System.out. println" in text:
        return True
    lang = str(language or "").lower()
    if lang in {"cpp", "java", "csharp"} and "total=0" in text.replace(" ", ""):
        if "target" in text or "pos" in text or "found" in text:
            return False
        if any(token in text for token in ("/* Поиск", "/* Бинарный", "/* Линейный", "/* Поиск первого")):
            return True
    return False


def reference_override(task_pattern: str, language: str) -> str:
    lang = str(language or "").strip().lower()
    if lang in {"cs", "c#"}:
        lang = "csharp"
    return _TASK_OVERRIDES.get(str(task_pattern or "").strip(), {}).get(lang, "")


def resolve_reference_raw(task_pattern: str, language: str, raw: str) -> str:
    lang = str(language or "").strip().lower()
    override = reference_override(task_pattern, lang)
    if override:
        return override
    if is_stub_reference_code(raw, lang):
        fallback = reference_override(task_pattern, lang)
        if fallback:
            return fallback
    return raw


def _java(body: str) -> str:
    indented = "\n".join(f"        {line}" if line.strip() else "" for line in body.strip().splitlines())
    if indented:
        indented += "\n"
    return (
        "import java.util.*;\n\n"
        "class Main\n"
        "{\n"
        "    public static void main(String[] args)\n"
        "    {\n"
        "        Scanner sc=new Scanner(System.in);\n"
        f"{indented}"
        "    }\n"
        "}"
    )


def _cpp(body: str, *, extra: str = "") -> str:
    extra_block = extra.strip()
    if extra_block and not extra_block.endswith("\n"):
        extra_block += "\n"
    indented = "\n".join(f"    {line}" if line.strip() else "" for line in body.strip().splitlines())
    return (
        "#include <iostream>\n"
        f"{extra_block}"
        "int main()\n"
        "{\n"
        f"{indented}\n"
        "}"
    )


_TASK_OVERRIDES: dict[str, dict[str, str]] = {
    "task_018": {
        "cpp": _cpp(
            "int n, target, pos = 0;\n"
            "std::cin >> n;\n"
            "std::vector<int> a(n);\n"
            "for (int i = 0; i < n; i++) std::cin >> a[i];\n"
            "std::cin >> target;\n"
            "for (int i = 0; i < n; i++)\n"
            "    if (a[i] == target && pos == 0) pos = i + 1;\n"
            "std::cout << pos;",
            extra="#include <vector>",
        ),
        "java": _java(
            "int n=sc.nextInt();\n"
            "int[] a=new int[n];\n"
            "for(int i=0;i<n;i++) a[i]=sc.nextInt();\n"
            "int target=sc.nextInt(), pos=0;\n"
            "for(int i=0;i<n;i++)\n"
            "    if(a[i]==target && pos==0) pos=i+1;\n"
            "System.out.println(pos);"
        ),
    },
    "task_022": {
        "cpp": _cpp(
            "int n, target, pos = 0;\n"
            "std::cin >> n;\n"
            "std::vector<int> a(n);\n"
            "for (int i = 0; i < n; i++) std::cin >> a[i];\n"
            "std::cin >> target;\n"
            "for (int i = n - 1; i >= 0; i--)\n"
            "    if (a[i] == target) pos = i + 1;\n"
            "std::cout << pos;",
            extra="#include <vector>",
        ),
        "java": _java(
            "int n=sc.nextInt();\n"
            "int[] a=new int[n];\n"
            "for(int i=0;i<n;i++) a[i]=sc.nextInt();\n"
            "int target=sc.nextInt(), pos=0;\n"
            "for(int i=n-1;i>=0;i--)\n"
            "    if(a[i]==target) pos=i+1;\n"
            "System.out.println(pos);"
        ),
    },
    "task_025": {
        "java": _java(
            "int n=sc.nextInt();\n"
            "int[] a=new int[n];\n"
            "for(int i=0;i<n;i++) a[i]=sc.nextInt();\n"
            "for(int i=n-1;i>=0;i--) System.out.print(a[i]+\" \");"
        ),
    },
    "task_026": {
        "java": _java(
            "int n=sc.nextInt(), k=sc.nextInt();\n"
            "int[] a=new int[n];\n"
            "for(int i=0;i<n;i++) a[i]=sc.nextInt();\n"
            "k%=n;\n"
            "if(k>0){\n"
            "    int[] b=new int[n];\n"
            "    for(int i=0;i<n;i++) b[(i+k)%n]=a[i];\n"
            "    a=b;\n"
            "}\n"
            "for(int x:a) System.out.print(x+\" \");"
        ),
    },
    "task_030": {
        "java": _java(
            "int n=sc.nextInt();\n"
            "int[] a=new int[n];\n"
            "for(int i=0;i<n;i++) a[i]=sc.nextInt();\n"
            "boolean found=false;\n"
            "for(int i=0;i<n && !found;i++)\n"
            "    for(int j=i+1;j<n;j++)\n"
            "        if(a[i]==a[j]) found=true;\n"
            "System.out.println(found?\"yes\":\"no\");"
        ),
    },
    "task_057": {
        "cpp": _cpp(
            "int n, target, pos = 0;\n"
            "std::cin >> n;\n"
            "std::vector<int> a(n);\n"
            "for (int i = 0; i < n; i++) std::cin >> a[i];\n"
            "std::cin >> target;\n"
            "for (int i = 0; i < n; i++)\n"
            "    if (a[i] == target && pos == 0) pos = i + 1;\n"
            "std::cout << pos;",
            extra="#include <vector>",
        ),
        "java": _java(
            "int n=sc.nextInt();\n"
            "int[] a=new int[n];\n"
            "for(int i=0;i<n;i++) a[i]=sc.nextInt();\n"
            "int target=sc.nextInt(), pos=0;\n"
            "for(int i=0;i<n;i++)\n"
            "    if(a[i]==target && pos==0) pos=i+1;\n"
            "System.out.println(pos);"
        ),
    },
    "task_058": {
        "cpp": _cpp(
            "int n, target;\n"
            "std::cin >> n;\n"
            "std::vector<int> a(n);\n"
            "for (int i = 0; i < n; i++) std::cin >> a[i];\n"
            "std::cin >> target;\n"
            "int lo = 0, hi = n - 1, pos = 0;\n"
            "while (lo <= hi) {\n"
            "    int mid = (lo + hi) / 2;\n"
            "    if (a[mid] == target) { pos = mid + 1; break; }\n"
            "    if (a[mid] < target) lo = mid + 1; else hi = mid - 1;\n"
            "}\n"
            "std::cout << pos;",
            extra="#include <vector>",
        ),
        "java": _java(
            "int n=sc.nextInt();\n"
            "int[] a=new int[n];\n"
            "for(int i=0;i<n;i++) a[i]=sc.nextInt();\n"
            "int target=sc.nextInt(), lo=0, hi=n-1, pos=0;\n"
            "while(lo<=hi){\n"
            "    int mid=(lo+hi)/2;\n"
            "    if(a[mid]==target){ pos=mid+1; break; }\n"
            "    if(a[mid]<target) lo=mid+1; else hi=mid-1;\n"
            "}\n"
            "System.out.println(pos);"
        ),
    },
}
