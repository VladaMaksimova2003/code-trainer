"""Task ↔ curriculum v2 link errors."""

from __future__ import annotations


class TaskCurriculumLinkError(Exception):
    """Base error for task curriculum links."""


class TaskCurriculumLinkValidationError(TaskCurriculumLinkError):
    """Link violates curriculum rules."""


class TaskCurriculumLinkNotFoundError(TaskCurriculumLinkError):
    """Link row not found."""
