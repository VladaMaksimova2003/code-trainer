"""Known-language variants for C++ transfer tasks."""

from __future__ import annotations

from typing import Any

KNOWN_LANGUAGES: tuple[str, ...] = ("python", "pascal", "java", "csharp")

DEFAULT_EXPLANATIONS: dict[str, str] = {
    "python": "Фрагмент на Python — язык, который вы уже знаете.",
    "pascal": "Фрагмент на Pascal — сравните синтаксис с C++.",
    "java": "Фрагмент на Java — обратите внимание на типы и точку с запятой.",
    "csharp": "Фрагмент на C# — похож на Java и C++.",
}


def build_known_language_variants(
    *,
    python: str,
    pascal: str,
    java: str,
    csharp: str,
    explanations: dict[str, str] | None = None,
) -> dict[str, dict[str, str]]:
    from application.curriculum.content.v4_code_format import normalize_authoring_code

    merged = dict(DEFAULT_EXPLANATIONS)
    if explanations:
        merged.update(explanations)
    return {
        "python": {"source_code": normalize_authoring_code(python), "explanation": merged["python"]},
        "pascal": {"source_code": normalize_authoring_code(pascal), "explanation": merged["pascal"]},
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
    return "python"


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
