"""Chapter-scoped proactive MPLT hints (banner), complementary to pitfall_pair_hints.

Used when a task has transfer_type/pitfall context but no pair-specific pitfall text,
or to add chapter framing (algo_basics → I/O and loops, branches → conditions, …).
"""

from __future__ import annotations

from typing import Any

# chapter_key → (source, target) → brief proactive text (concrete code, no vague phrasing)
_CHAPTER_PAIR_HINTS: dict[str, dict[tuple[str, str], str]] = {
    "algo_basics": {
        ("python", "java"): (
            "Python: x = int(input())\n"
            "Java: Scanner sc = new Scanner(System.in); int x = sc.nextInt();"
        ),
        ("cpp", "java"): (
            "C++: cin >> x;\n"
            "Java: Scanner sc = new Scanner(System.in); int x = sc.nextInt();"
        ),
        ("python", "pascal"): (
            "Python: a, b = map(int, input().split())\n"
            "Pascal: readln(a, b);"
        ),
        ("cpp", "pascal"): (
            "C++: cin >> x;  // по токенам\n"
            "Pascal: readln(x);  // строка или число"
        ),
        ("pascal", "python"): (
            "Pascal: readln(x);\n"
            "Python: x = int(input())"
        ),
        ("pascal", "cpp"): (
            "Pascal: a[1] — первый элемент\n"
            "C++: arr[0] — первый элемент"
        ),
        ("python", "cpp"): (
            "Python целое: total // n\n"
            "C++ int: total / n"
        ),
        ("java", "python"): (
            "Java: sc.nextInt()\n"
            "Python: int(input()) или map(int, input().split())"
        ),
    },
    "branches": {
        ("python", "cpp"): (
            "В главе «Ветвления» баннеры без кода — синтаксис цепочек сравнений "
            "смотрите в ожидаемой конструкции «Условия и ветвление»."
        ),
        ("python", "java"): (
            "В главе «Ветвления» баннеры без кода — синтаксис цепочек сравнений "
            "смотрите в ожидаемой конструкции «Условия и ветвление»."
        ),
        ("python", "pascal"): (
            "В главе «Ветвления» баннеры без кода — присваивание, elif и case "
            "смотрите в ожидаемых конструкциях с примерами."
        ),
        ("cpp", "pascal"): (
            "В главе «Ветвления» баннеры без кода — else if и case "
            "смотрите в ожидаемых конструкциях с примерами."
        ),
    },
    "arrays_collections": {
        ("python", "pascal"): (
            "В главе «Массивы» баннеры без кода — индексацию и операции с массивом "
            "смотрите в ожидаемых конструкциях с примерами."
        ),
        ("pascal", "python"): (
            "В главе «Массивы» баннеры без кода — перенос операций с массивом "
            "смотрите в ожидаемых конструкциях с примерами."
        ),
    },
    "strings": {
        ("python", "pascal"): (
            "В главе «Строки» баннеры без кода — длину, разворот и поиск подстроки "
            "смотрите в ожидаемых конструкциях с примерами."
        ),
        ("pascal", "python"): (
            "В главе «Строки» баннеры без кода — операции со строками "
            "смотрите в ожидаемых конструкциях с примерами."
        ),
    },
}


def _normalize_lang(language: str) -> str:
    lang = str(language or "").strip().lower()
    if lang in {"cs", "c#"}:
        return "csharp"
    return lang


def chapter_key_for_pattern(pattern_key: str | None) -> str | None:
    key = str(pattern_key or "").strip()
    if not key:
        return None
    try:
        from application.curriculum.display.v128_transfer_meta import ALGO_SYNTAX_META
    except ImportError:
        return None
    raw = ALGO_SYNTAX_META.get(key) or {}
    chapter = str(raw.get("chapter_key") or "").strip()
    return chapter or None


def chapter_proactive_hint(
    pattern_key: str | None,
    *,
    source_language: str,
    target_language: str,
) -> str | None:
    chapter = chapter_key_for_pattern(pattern_key)
    if not chapter:
        return None
    source = _normalize_lang(source_language)
    target = _normalize_lang(target_language)
    if source == target:
        return None
    return (_CHAPTER_PAIR_HINTS.get(chapter) or {}).get((source, target))
