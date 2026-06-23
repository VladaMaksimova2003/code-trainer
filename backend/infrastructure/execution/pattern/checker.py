from application.analysis.core.educational_validator import EducationalValidator


class PatternChecker:
    def __init__(self, _extractor: object | None = None) -> None:
        self._validator = EducationalValidator()

    def check(
        self, code: str, language: str, expected_patterns: list[str] | list[dict]
    ) -> list[str]:
        return self._validator.missing_structure_labels(
            code,
            str(language).lower(),
            expected_patterns,
        )
