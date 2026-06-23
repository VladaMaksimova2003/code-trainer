"""Context-aware distractor generation for placeholder block assembly."""

from __future__ import annotations

import re
from typing import Any

_WEAK_DISTRACTORS = frozenset(
    {
        "average",
        "count",
        "result",
        "value",
        "found",
        "index",
        "условие",
        "счётчик",
        "имя класса",
        "импорт",
        "placeholder",
    }
)

_KEYWORDS: dict[str, frozenset[str]] = {
    "pascal": frozenset(
        {
            "var",
            "begin",
            "end",
            "if",
            "then",
            "else",
            "for",
            "to",
            "do",
            "while",
            "repeat",
            "until",
            "procedure",
            "function",
            "program",
            "integer",
            "real",
            "string",
            "boolean",
            "writeln",
            "readln",
            "write",
            "read",
            "div",
            "mod",
            "and",
            "or",
            "not",
        }
    ),
    "python": frozenset(
        {
            "if",
            "elif",
            "else",
            "for",
            "while",
            "in",
            "def",
            "class",
            "return",
            "import",
            "from",
            "print",
            "input",
            "int",
            "float",
            "str",
            "range",
            "True",
            "False",
            "None",
        }
    ),
    "cpp": frozenset(
        {
            "if",
            "else",
            "for",
            "while",
            "return",
            "int",
            "double",
            "float",
            "char",
            "void",
            "include",
            "using",
            "namespace",
            "std",
            "cout",
            "cin",
            "vector",
            "main",
        }
    ),
    "csharp": frozenset(
        {
            "if",
            "else",
            "for",
            "while",
            "return",
            "int",
            "double",
            "float",
            "string",
            "void",
            "using",
            "class",
            "static",
            "Console",
            "WriteLine",
            "ReadLine",
            "Parse",
        }
    ),
    "java": frozenset(
        {
            "if",
            "else",
            "for",
            "while",
            "return",
            "int",
            "double",
            "float",
            "String",
            "void",
            "class",
            "public",
            "static",
            "System",
            "Scanner",
            "println",
            "nextInt",
        }
    ),
}

_TOKEN_CONFUSIONS: dict[str, dict[str, list[str]]] = {
    "pascal": {
        ":=": ["=", "+=", "-="],
        "=": [":=", "=="],
        ">=": [">", "<=", "="],
        ">": [">=", "<", "="],
        "<=": ["<", ">=", "="],
        "then": ["do", "begin"],
        "do": ["then", "begin"],
        "div": ["mod", "/"],
        "mod": ["div", "/"],
        "writeln": ["write", "readln"],
        "write": ["writeln", "readln"],
        "readln": ["read", "writeln"],
    },
    "python": {
        "==": ["=", "!=", "is"],
        "=": ["==", "+=", "-="],
        ">=": [">", "<=", "=="],
        ">": [">=", "<", "=="],
        "//": ["/", "%", "*"],
        "print": ["input", "int", "str"],
        "input": ["print", "int", "map"],
        "int": ["float", "str", "input"],
        "range": ["len", "list", "enumerate"],
    },
    "cpp": {
        ">>": ["<<", "="],
        "<<": [">>", "="],
        ">=": [">", "<=", "=="],
        "+=": ["=", "-=", "*="],
        "=": ["==", "+=", "-="],
        "std::cout": ["std::cin", "printf"],
        "std::cin": ["std::cout", "scanf"],
    },
    "csharp": {
        ">=": [">", "<=", "=="],
        "==": ["=", "!=", "Equals"],
        "Parse": ["TryParse", "ToString", "ReadLine"],
        "WriteLine": ["ReadLine", "Write", "Parse"],
        "ReadLine": ["WriteLine", "Parse", "Read"],
    },
    "java": {
        ">=": [">", "<=", "=="],
        "==": ["=", "!=", "equals"],
        "nextInt": ["nextLine", "nextDouble", "next"],
        "println": ["print", "printf", "nextInt"],
        "length": ["size", "count", "n"],
    },
}

_ACCUMULATOR_NAMES = ("sum", "s", "acc", "total", "summ")
_LOOP_INDEX_NAMES = ("i", "j", "k", "idx", "index")
_DIVISOR_EXPRESSIONS = (
    "len({collection})",
    "loads.length",
    "sales.length",
    "{collection}.length",
    "sizeof({collection})",
)

_IDENTIFIER_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
_GAP_MARKER_RE = re.compile(r"___p\d+___")
_COLLECTION_NAMES = ("loads", "sales", "scores", "values", "items", "data", "arr", "a", "nums")


def _normalize_lang(language: str) -> str:
    lang = str(language or "python").strip().lower()
    if lang in {"cs", "c#"}:
        return "csharp"
    return lang


def _extract_identifiers(text: str, language: str) -> list[str]:
    lang = _normalize_lang(language)
    keywords = _KEYWORDS.get(lang, _KEYWORDS["python"])
    seen: set[str] = set()
    ordered: list[str] = []
    for match in _IDENTIFIER_RE.finditer(str(text or "")):
        name = match.group(0)
        lower = name.lower()
        if lower in keywords or lower in seen:
            continue
        seen.add(lower)
        ordered.append(name)
    return ordered


def _label_hints(label: str) -> list[str]:
    text = str(label or "").lower()
    hints: list[str] = []
    if any(word in text for word in ("делител", "количеств", "число элемент", "размер")):
        hints.extend(["n", "i", "len", "size", "count"])
    if any(word in text for word in ("сумм", "аккумулятор", "накоп")):
        hints.extend(list(_ACCUMULATOR_NAMES))
    if any(word in text for word in ("цикл", "элемент", "текущ", "итерац")):
        hints.extend(["load", "loads", "item", "value", "x"])
    if any(word in text for word in ("позиц", "номер", "индекс", "номер")):
        hints.extend(["i", "position", "pos", "idx"])
    if any(word in text for word in ("сравн", "иском", "target", "цел")):
        hints.extend(["target", "code", "key", "value"])
    if any(word in text for word in ("присваив", "началь", "инициал")):
        hints.extend(list(_ACCUMULATOR_NAMES) + ["0"])
    if any(word in text for word in ("оператор", "услов", "ветв", "сравнен")):
        hints.extend([">=", ">", "<=", "==", "!=", "<"])
    return hints


def _collection_in_code(code: str) -> str | None:
    for name in _COLLECTION_NAMES:
        if re.search(rf"\b{re.escape(name)}\b", code):
            return name
    return None


def _expression_distractors(answer: str, code: str, language: str) -> list[str]:
    lang = _normalize_lang(language)
    extras: list[str] = []
    collection = _collection_in_code(code)

    if collection and answer in {"n", "i", "total", "load"}:
        if lang == "python":
            extras.append(f"len({collection})")
        elif lang == "java":
            extras.append(f"{collection}.length")
        elif lang in {"csharp", "cpp"}:
            extras.append(f"{collection}.length" if lang == "csharp" else f"{collection}.size()")

    if answer == "load" and collection and collection.endswith("s"):
        extras.append(collection)
    if answer == "loads" and collection == "loads":
        extras.append("load")
    if answer == collection and collection and not collection.endswith("s"):
        extras.append(f"{collection}s")

    if lang == "pascal" and answer == "n":
        extras.extend(["i", "load"])
    if lang == "python" and answer in {"i", "n"}:
        extras.extend(["n", "i"])

    return extras


def _token_confusions(token: str, language: str) -> list[str]:
    lang = _normalize_lang(language)
    table = _TOKEN_CONFUSIONS.get(lang, {})
    return list(table.get(token, table.get(token.lower(), [])))


def enrich_gap_variants(
    gap: dict[str, Any],
    *,
    all_gaps: list[dict[str, Any]],
    placeholder_code: str,
    reference_code: str = "",
    language: str = "python",
    min_variants: int = 5,
    max_variants: int = 8,
) -> list[str]:
    """Return ordered variant list: correct answer first, then plausible distractors."""
    answer = str(gap.get("answer") or gap.get("correct") or "").strip()
    label = str(gap.get("label") or "")
    raw_variants = [str(v).strip() for v in (gap.get("variants") or []) if str(v).strip()]

    code = _GAP_MARKER_RE.sub(" ", str(placeholder_code or ""))
    code_ctx = f"{code} {reference_code or ''}"
    identifiers = _extract_identifiers(code_ctx, language)

    other_answers = [
        str(g.get("answer") or g.get("correct") or "").strip()
        for g in all_gaps
        if isinstance(g, dict) and str(g.get("id") or "") != str(gap.get("id") or "")
    ]
    other_answers = [item for item in other_answers if item and item != answer]

    lang = _normalize_lang(language)
    candidates: list[str] = []
    if answer:
        candidates.append(answer)

    for source in (
        other_answers,
        identifiers,
        _label_hints(label),
        _expression_distractors(answer, code, language),
        _token_confusions(answer, language),
        raw_variants,
    ):
        for item in source:
            token = str(item).strip()
            if not token or token == answer:
                continue
            if token.lower() in _WEAK_DISTRACTORS:
                continue
            if lang == "pascal" and token in {"len", "size", "length"}:
                continue
            if token in candidates:
                continue
            candidates.append(token)

    # Drop weak legacy distractors unless they appear in the code context.
    code_lower = code_ctx.lower()
    filtered = [candidates[0]] if candidates else []
    for token in candidates[1:]:
        if token.lower() in _WEAK_DISTRACTORS and token.lower() not in code_lower:
            continue
        filtered.append(token)

    if answer and filtered and filtered[0] != answer:
        filtered = [answer, *[t for t in filtered if t != answer]]

    while len(filtered) < min_variants:
        added = False
        for token in identifiers + list(_ACCUMULATOR_NAMES) + list(_LOOP_INDEX_NAMES):
            if token == answer or token in filtered:
                continue
            if token.lower() in _WEAK_DISTRACTORS:
                continue
            if lang == "pascal" and token in {"len", "size", "length"}:
                continue
            filtered.append(token)
            added = True
            if len(filtered) >= min_variants:
                break
        if not added:
            break

    if lang == "pascal":
        filtered = [filtered[0]] + [t for t in filtered[1:] if t not in {"len", "size", "length"}]

    return filtered[:max_variants]


def contextual_decoys_for_token(token: str, reference_code: str, language: str) -> list[str]:
    """Extra decoys for inline syntax-gap assembly (v4 auto builder)."""
    lang = _normalize_lang(language)
    token = str(token or "").strip()
    if not token:
        return []

    decoys: list[str] = []
    for item in _token_confusions(token, lang):
        if item not in decoys:
            decoys.append(item)

    ref = str(reference_code or "")
    identifiers = _extract_identifiers(ref, lang)
    for name in identifiers:
        if name == token or name in decoys:
            continue
        if len(name) <= 12:
            decoys.append(name)
        if len(decoys) >= 6:
            break

    global_pool = list(_TOKEN_CONFUSIONS.get(lang, {}).keys())
    for item in global_pool:
        if item != token and item not in decoys:
            decoys.append(item)
        if len(decoys) >= 8:
            break

    return decoys
