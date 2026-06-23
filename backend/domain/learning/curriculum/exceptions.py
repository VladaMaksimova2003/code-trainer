"""Curriculum validation errors."""

from __future__ import annotations


class CurriculumError(Exception):
    """Base curriculum error."""


class CurriculumNotFoundError(CurriculumError):
    """Unknown language track."""


class CurriculumValidationError(CurriculumError):
    """YAML consistency validation failed."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        message = "; ".join(errors[:5])
        if len(errors) > 5:
            message += f" (+{len(errors) - 5} more)"
        super().__init__(message)
