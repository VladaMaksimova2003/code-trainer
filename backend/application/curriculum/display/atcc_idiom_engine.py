"""ATCC idiom catalog and carryover detection for mirror tasks.

Abstract True Conceptual Carryover (ATCC): the algorithm transfers, but the
target language idiom differs. This module maps technical concepts to idioms
and emits warnings when submitted code still uses the source language's form.
"""

from __future__ import annotations

import re
from typing import Any

from application.curriculum.display.pascal_hint_engine import (
    KNOWN_SOURCE_LANGUAGES,
    TRANSFER_HINTS_RU,
    transfer_hint_for_tc,
)

ATCC_WARNING_TYPE = "TRANSFER_PITFALL"

# Brief idiom pairs for documentation / thesis (concept → source → target phrase).
ATCC_IDIOM_BRIEF: dict[str, dict[tuple[str, str], str]] = {
    "program_entry": {
        ("python", "pascal"): "program Name; begin … end.",
        ("pascal", "python"): "скрипт или def main() без program/begin/end",
        ("python", "cpp"): "#include <iostream> и int main()",
        ("cpp", "python"): "if __name__ == '__main__':",
        ("python", "java"): "public class Main { public static void main(String[] args) { … } }",
        ("java", "python"): "if __name__ == '__main__':",
        ("python", "csharp"): "class Program { static void Main() { … } }",
        ("csharp", "python"): "if __name__ == '__main__':",
        ("pascal", "cpp"): "int main() { … return 0; }",
        ("cpp", "pascal"): "program …; begin … end.",
    },
    "typed_declaration": {
        ("python", "pascal"): "var x: integer; в секции var",
        ("pascal", "python"): "x = 0 без секции var",
        ("python", "cpp"): "int x;",
        ("python", "java"): "int x;",
    },
    "assignment": {
        ("python", "pascal"): "x := 1; (= только сравнение)",
        ("pascal", "python"): "x = 1",
        ("cpp", "pascal"): "x := 1;",
    },
    "stdin_read": {
        ("python", "pascal"): "readln(x);",
        ("pascal", "python"): "x = int(input())",
        ("pascal", "cpp"): "std::cin >> x;",
        ("cpp", "python"): "int(input()) или map(int, input().split())",
    },
    "stdout_write": {
        ("python", "pascal"): "writeln(...);",
        ("pascal", "python"): "print(...)",
        ("pascal", "cpp"): "std::cout << ... << std::endl;",
        ("cpp", "python"): "print(...)",
        ("java", "python"): "print(...)",
    },
    "simple_branch": {
        ("python", "pascal"): "if cond then … else …",
        ("pascal", "python"): "if cond: … elif … else:",
    },
    "multi_branch": {
        ("python", "pascal"): "else if",
        ("pascal", "python"): "elif",
    },
    "switch_selection": {
        ("python", "pascal"): "case x of … end;",
        ("pascal", "python"): "if/elif или match/case",
        ("java", "python"): "if/elif или match",
    },
    "counted_loop": {
        ("python", "pascal"): "for i := 1 to n do",
        ("pascal", "python"): "for i in range(n): или range(1, n+1)",
        ("pascal", "cpp"): "for (int i = 0; i < n; ++i) или 1..n по задаче",
        ("cpp", "python"): "for i in range(n):",
    },
    "pre_condition_loop": {
        ("python", "pascal"): "while cond do",
        ("pascal", "python"): "while cond:",
    },
    "post_condition_loop": {
        ("python", "pascal"): "repeat … until cond;",
        ("pascal", "python"): "while True: … break",
    },
    "collection_iteration": {
        ("python", "pascal"): "for i := 1 to n do a[i]",
        ("pascal", "python"): "for x in items: или for i in range(len(a))",
    },
    "indexed_sequence": {
        ("python", "pascal"): "a[1] при array[1..n]",
        ("pascal", "python"): "a[0] при list",
    },
    "arithmetic_ops": {
        ("python", "pascal"): "div и mod вместо // и %",
        ("pascal", "python"): "целое частное — //, не /",
        ("cpp", "python"): "целое частное — //, не / (обычный / даёт float)",
        ("python", "cpp"): "для int операндов / даёт целое частное; для float — вещественное",
        ("pascal", "cpp"): "div/mod → / и % для int",
        ("cpp", "pascal"): "div и mod вместо / и %",
        ("csharp", "python"): "целое частное — //, не /",
        ("java", "python"): "целое частное — //, не /",
    },
    "function_definition": {
        ("python", "pascal"): "function Name(...): T; begin … Name := …; end;",
        ("pascal", "python"): "def name(...): return …",
    },
    "return_flow": {
        ("python", "pascal"): "ИмяФункции := значение;",
        ("pascal", "python"): "return значение",
    },
    "parameter_passing": {
        ("python", "pascal"): "procedure P(var x: integer);",
        ("pascal", "python"): "изменяемый аргумент через return или mutable объект",
    },
    "import_dependency": {
        ("python", "pascal"): "uses UnitName;",
        ("pascal", "python"): "import module",
        ("cpp", "python"): "import …",
    },
    "file_read": {
        ("python", "pascal"): "Assign; Reset; Readln; CloseFile",
        ("pascal", "python"): "with open(...) as f:",
    },
    "file_write": {
        ("python", "pascal"): "Assign; Rewrite; Writeln; CloseFile",
        ("pascal", "python"): "with open(..., 'w') as f:",
    },
}

# Source-language tokens that should not appear in target-language submissions.
_CARRYOVER_MARKERS: dict[tuple[str, str], list[tuple[str, re.Pattern[str], str]]] = {
    ("pascal", "python"): [
        ("stdout_write", re.compile(r"\bwriteln\s*\(", re.I), "writeln(...)"),
        ("stdin_read", re.compile(r"\breadln\s*\(", re.I), "readln(...)"),
        ("program_entry", re.compile(r"\bprogram\s+\w+\s*;", re.I), "program …;"),
        ("program_entry", re.compile(r"\bbegin\b", re.I), "begin"),
        ("program_entry", re.compile(r"\bend\s*\.", re.I), "end."),
        ("assignment", re.compile(r":="), ":="),
        ("counted_loop", re.compile(r"\bfor\s+\w+\s*:=\s*", re.I), "for i := … to … do"),
        ("arithmetic_ops", re.compile(r"\bdiv\b", re.I), "div"),
        ("arithmetic_ops", re.compile(r"\bmod\b", re.I), "mod"),
        ("simple_branch", re.compile(r"\bthen\b", re.I), "then"),
        ("switch_selection", re.compile(r"\bcase\s+\w+\s+of\b", re.I), "case x of"),
    ],
    ("python", "pascal"): [
        ("stdout_write", re.compile(r"\bprint\s*\("), "print(...)"),
        ("stdin_read", re.compile(r"\binput\s*\("), "input()"),
        ("assignment", re.compile(r"\belif\b"), "elif"),
        ("counted_loop", re.compile(r"\bin\s+range\s*\("), "range(...)"),
        ("collection_iteration", re.compile(r"\bfor\s+\w+\s+in\s+", re.I), "for x in …"),
        ("function_definition", re.compile(r"\bdef\s+\w+\s*\("), "def …"),
        ("return_flow", re.compile(r"\breturn\b"), "return"),
        ("exception_handling", re.compile(r"\btry\s*:"), "try:"),
        ("exception_handling", re.compile(r"\bexcept\b"), "except"),
    ],
    ("python", "cpp"): [
        ("stdout_write", re.compile(r"\bprint\s*\("), "print(...)"),
        ("stdin_read", re.compile(r"\binput\s*\("), "input()"),
        ("counted_loop", re.compile(r"\bin\s+range\s*\("), "range(...)"),
    ],
    ("python", "java"): [
        ("stdout_write", re.compile(r"\bprint\s*\("), "print(...)"),
        ("stdin_read", re.compile(r"\binput\s*\("), "input()"),
    ],
    ("python", "csharp"): [
        ("stdout_write", re.compile(r"\bprint\s*\("), "print(...)"),
        ("stdin_read", re.compile(r"\binput\s*\("), "input()"),
    ],
    ("pascal", "cpp"): [
        ("stdout_write", re.compile(r"\bwriteln\s*\(", re.I), "writeln(...)"),
        ("stdin_read", re.compile(r"\breadln\s*\(", re.I), "readln(...)"),
        ("program_entry", re.compile(r"\bbegin\b", re.I), "begin"),
        ("program_entry", re.compile(r"\bend\s*\.", re.I), "end."),
        ("assignment", re.compile(r":="), ":="),
        ("counted_loop", re.compile(r"\bfor\s+\w+\s*:=\s*", re.I), "for i := … to … do"),
        ("arithmetic_ops", re.compile(r"\bdiv\b", re.I), "div"),
        ("arithmetic_ops", re.compile(r"\bmod\b", re.I), "mod"),
    ],
    ("pascal", "csharp"): [
        ("stdout_write", re.compile(r"\bwriteln\s*\(", re.I), "writeln(...)"),
        ("stdin_read", re.compile(r"\breadln\s*\(", re.I), "readln(...)"),
        ("assignment", re.compile(r":="), ":="),
    ],
    ("pascal", "java"): [
        ("stdout_write", re.compile(r"\bwriteln\s*\(", re.I), "writeln(...)"),
        ("stdin_read", re.compile(r"\breadln\s*\(", re.I), "readln(...)"),
        ("assignment", re.compile(r":="), ":="),
    ],
    ("cpp", "python"): [
        ("stdout_write", re.compile(r"\bstd::\w*cout\b"), "std::cout"),
        ("stdout_write", re.compile(r"\bstd::\w*endl\b"), "std::endl"),
        ("stdin_read", re.compile(r"\bstd::\w*cin\b"), "std::cin"),
        ("import_dependency", re.compile(r"#include\s*<"), "#include"),
    ],
    ("java", "python"): [
        ("stdout_write", re.compile(r"\bSystem\.out\.print"), "System.out.println"),
        ("program_entry", re.compile(r"\bpublic\s+static\s+void\s+main\b"), "public static void main"),
    ],
    ("csharp", "python"): [
        ("stdout_write", re.compile(r"\bConsole\.Write(Line)?\b"), "Console.WriteLine"),
    ],
}


def _normalize_lang(language: str) -> str:
    lang = str(language or "").strip().lower()
    if lang in {"cs", "c#"}:
        return "csharp"
    return lang


def _concept_idiom_keys(concept_id: str) -> list[str]:
    from application.curriculum.validation.canonical_technical_ids import (
        LEGACY_TO_CANONICAL,
        canonical_technical_id,
    )

    keys: list[str] = []
    raw = str(concept_id or "").strip()
    if raw:
        keys.append(raw)
    canonical = canonical_technical_id(raw)
    if canonical and canonical not in keys:
        keys.append(canonical)
    for legacy, mapped in LEGACY_TO_CANONICAL.items():
        if mapped == canonical and legacy not in keys:
            keys.append(legacy)
    return keys


def idiom_hint_for_concept(
    source_language: str,
    target_language: str,
    concept_id: str,
) -> str | None:
    """ATCC/FCC idiom text for a concept and mirror pair (source → target)."""
    source = _normalize_lang(source_language)
    target = _normalize_lang(target_language)
    if source not in KNOWN_SOURCE_LANGUAGES or target not in KNOWN_SOURCE_LANGUAGES:
        return None
    if source == target:
        return None

    for key in _concept_idiom_keys(concept_id):
        brief = ATCC_IDIOM_BRIEF.get(key, {}).get((source, target))
        if brief:
            src_ru = {"pascal": "Pascal", "python": "Python", "cpp": "C++", "csharp": "C#", "java": "Java"}.get(
                source, source
            )
            tgt_ru = {"pascal": "Pascal", "python": "Python", "cpp": "C++", "csharp": "C#", "java": "Java"}.get(
                target, target
            )
            return f"В {tgt_ru} для этой конструкции:\n{brief}"

    from application.curriculum.display.mirror_idiom_matrix import matrix_idiom_brief

    matrix_hint = matrix_idiom_brief(source, target, concept_id)
    if matrix_hint:
        return matrix_hint

    if target == "pascal":
        for key in _concept_idiom_keys(concept_id):
            legacy = transfer_hint_for_tc(source, key)
            if legacy:
                return legacy

    if source == "pascal":
        tgt_ru = {"pascal": "Pascal", "python": "Python", "cpp": "C++", "csharp": "C#", "java": "Java"}.get(
            target, target
        )
        for key in _concept_idiom_keys(concept_id):
            for src_key, hints in TRANSFER_HINTS_RU.get(key, {}).items():
                if _normalize_lang(src_key) == target and hints:
                    return f"В {tgt_ru}:\n{hints}"

    return None


def idiom_hint(source_language: str, target_language: str, concept_id: str) -> str | None:
    """Return ATCC idiom mapping text for a concept and language pair."""
    return idiom_hint_for_concept(source_language, target_language, concept_id)


def _build_atcc_warning(
    *,
    source: str,
    target: str,
    concept_id: str,
    fragment: str,
    detection: str,
) -> dict[str, str]:
    from application.curriculum.display.pitfall_messages import atcc_carryover_message

    body = atcc_carryover_message(
        concept_id,
        source_language=source,
        target_language=target,
        fragment=fragment,
    )
    via = "AST" if detection == "ast" else "lex"
    return {
        "text": f"Возможный перенос (ATCC, {via}): {body}",
        "type": ATCC_WARNING_TYPE,
        "transfer_type": "ATCC",
        "concept_id": concept_id,
        "fragment": fragment,
        "detection": detection,
        "feedback_ru": body,
    }


def _detect_atcc_carryover_lex(
    source_language: str,
    target_language: str,
    code: str,
    *,
    expected_concepts: list[str] | None = None,
) -> list[dict[str, str]]:
    """Lexical fallback when AST parse is unavailable or misses a marker."""
    source = _normalize_lang(source_language)
    target = _normalize_lang(target_language)
    text = str(code or "")
    if not text.strip() or source == target:
        return []

    markers = _CARRYOVER_MARKERS.get((source, target)) or []
    if not markers:
        return []

    scope = {str(c).strip() for c in (expected_concepts or []) if str(c).strip()}
    warnings: list[dict[str, str]] = []
    seen: set[str] = set()

    for concept_id, pattern, fragment in markers:
        if scope and concept_id not in scope:
            continue
        if not pattern.search(text):
            continue
        key = f"{concept_id}:{fragment}"
        if key in seen:
            continue
        seen.add(key)
        warnings.append(
            _build_atcc_warning(
                source=source,
                target=target,
                concept_id=concept_id,
                fragment=fragment,
                detection="lex",
            )
        )

    return warnings


def detect_atcc_carryover(
    source_language: str,
    target_language: str,
    code: str,
    *,
    expected_concepts: list[str] | None = None,
) -> list[dict[str, str]]:
    """Detect source-language idioms in code submitted for the target language."""
    from application.curriculum.display.atcc_ast_carryover import (
        AST_CARRYOVER_RULES,
        detect_atcc_carryover_ast,
        _safe_parse,
    )

    source = _normalize_lang(source_language)
    target = _normalize_lang(target_language)
    text = str(code or "")
    if not text.strip() or source == target:
        return []

    ast_rules = AST_CARRYOVER_RULES.get((source, target)) or ()
    ast_covered = {(rule.concept_id, rule.fragment) for rule in ast_rules}
    parse_ok = _safe_parse(text, target) is not None

    warnings: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for hit in detect_atcc_carryover_ast(
        source,
        target,
        text,
        expected_concepts=expected_concepts,
    ):
        key = (hit.concept_id, hit.fragment)
        if key in seen:
            continue
        seen.add(key)
        warnings.append(
            _build_atcc_warning(
                source=source,
                target=target,
                concept_id=hit.concept_id,
                fragment=hit.fragment,
                detection="ast",
            )
        )

    for item in _detect_atcc_carryover_lex(
        source,
        target,
        text,
        expected_concepts=expected_concepts,
    ):
        key = (str(item["concept_id"]), str(item["fragment"]))
        if parse_ok and key in ast_covered:
            continue
        if key in seen:
            continue
        seen.add(key)
        warnings.append(item)

    return warnings


def build_atcc_hint_payload(
    *,
    technical_concepts: list[str],
    source_language: str,
    target_language: str,
) -> dict[str, Any]:
    """Proactive ATCC hints for task UI (mirror: source → target)."""
    source = _normalize_lang(source_language)
    target = _normalize_lang(target_language)
    items: list[dict[str, str]] = []
    for concept_id in technical_concepts:
        cid = str(concept_id).strip()
        if not cid:
            continue
        text = idiom_hint(source, target, cid)
        if text:
            items.append({"concept_id": cid, "text": text, "transfer_type": "ATCC"})
    return {
        "source_language": source,
        "target_language": target,
        "atcc_idiom_hints": items,
    }
