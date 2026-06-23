"""Student-facing curriculum languages (collections grouped by target language)."""

from __future__ import annotations

from dataclasses import dataclass

LANGUAGE_LABELS: dict[str, str] = {
    "python": "Python",
    "cpp": "C++",
    "csharp": "C#",
    "java": "Java",
    "pascal": "Pascal",
}

# Display order on home page `/`.
HOME_LANGUAGE_ORDER: tuple[str, ...] = ("python", "cpp", "csharp", "java", "pascal")


@dataclass(frozen=True)
class CurriculumLanguageDefinition:
    language: str
    language_label: str


def list_home_languages() -> tuple[CurriculumLanguageDefinition, ...]:
    return tuple(
        CurriculumLanguageDefinition(language=lang, language_label=LANGUAGE_LABELS[lang])
        for lang in HOME_LANGUAGE_ORDER
    )
