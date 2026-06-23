"""Known-language variants for Java transfer tasks."""
from __future__ import annotations

from typing import Any

KNOWN_LANGUAGES: tuple[str, ...] = ("python", "pascal", "csharp", "cpp")

DEFAULT_EXPLANATIONS: dict[str, str] = {
    "python": "Фрагмент на Python — язык, который вы уже знаете.",
    "pascal": "Фрагмент на Pascal — сравните синтаксис с Java.",
    "csharp": "Фрагмент на C# — очень похож на Java.",
    "cpp": "Фрагмент на C++ — сравните управление памятью.",
}


def build_known_language_variants(
    *,
    python: str,
    pascal: str,
    csharp: str,
    cpp: str,
    explanations: dict[str, str] | None = None,
) -> dict[str, dict[str, str]]:
    from application.curriculum.content.v4_code_format import normalize_authoring_code

    merged = dict(DEFAULT_EXPLANATIONS)
    if explanations:
        merged.update(explanations)
    return {
        "python": {"source_code": normalize_authoring_code(python), "explanation": merged["python"]},
        "pascal": {"source_code": normalize_authoring_code(pascal), "explanation": merged["pascal"]},
        "csharp": {"source_code": normalize_authoring_code(csharp), "explanation": merged["csharp"]},
        "cpp": {"source_code": normalize_authoring_code(cpp), "explanation": merged["cpp"]},
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
