"""Known-language variants for Python transfer tasks (one task, four «Я знаю» sources)."""

from __future__ import annotations

from typing import Any

KNOWN_LANGUAGES: tuple[str, ...] = ("pascal", "cpp", "java", "csharp")

DEFAULT_EXPLANATIONS: dict[str, str] = {
    "pascal": "Фрагмент на Pascal — сравните синтаксис с Python.",
    "cpp": "Фрагмент на C++ — обратите внимание на типы и точку с запятой.",
    "java": "Фрагмент на Java — похож на C++ и C#.",
    "csharp": "Фрагмент на C# — похож на Java и C++.",
}


def build_known_language_variants(
    *,
    pascal: str,
    cpp: str,
    java: str,
    csharp: str,
    explanations: dict[str, str] | None = None,
) -> dict[str, dict[str, str]]:
    from application.curriculum.content.v4_code_format import normalize_authoring_code

    merged = dict(DEFAULT_EXPLANATIONS)
    if explanations:
        merged.update(explanations)
    return {
        "pascal": {"source_code": normalize_authoring_code(pascal), "explanation": merged["pascal"]},
        "cpp": {"source_code": normalize_authoring_code(cpp), "explanation": merged["cpp"]},
        "java": {"source_code": normalize_authoring_code(java), "explanation": merged["java"]},
        "csharp": {"source_code": normalize_authoring_code(csharp), "explanation": merged["csharp"]},
    }


def code_examples_from_variants(variants: dict[str, dict[str, str]]) -> dict[str, str]:
    from application.curriculum.content.v4_code_format import normalize_authoring_code

    examples: dict[str, str] = {}
    for lang in KNOWN_LANGUAGES:
        entry = variants.get(lang) or {}
        code = normalize_authoring_code(str(entry.get("source_code") or ""))
        if code.strip():
            examples[lang] = code
    return examples


def default_source_language(variants: dict[str, dict[str, str]]) -> str:
    for lang in KNOWN_LANGUAGES:
        if lang in variants and str(variants[lang].get("source_code") or "").strip():
            return lang
    return "pascal"


def default_source_code(variants: dict[str, dict[str, str]], *, lang: str | None = None) -> str:
    key = lang or default_source_language(variants)
    return str((variants.get(key) or {}).get("source_code") or "")


def validate_variants(variants: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not variants:
        return ["known_language_variants is empty"]
    for lang in KNOWN_LANGUAGES:
        entry = variants.get(lang)
        if not isinstance(entry, dict):
            errors.append(f"missing variant for {lang}")
            continue
        if not str(entry.get("source_code") or "").strip():
            errors.append(f"empty source_code for {lang}")
    return errors
