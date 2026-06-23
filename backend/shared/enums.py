"""Unified enums for the entire project.

All previous locations now re-export from here:
  - domain.enums          → shared.enums
  - domain.assignments.enums → shared.enums
  - domain.profile.enums  → shared.enums
"""
from __future__ import annotations

from enum import Enum
from typing import Union


# ---------------------------------------------------------------------------
# Difficulty
# ---------------------------------------------------------------------------

class Difficulty(str, Enum):
    """Backward-compatible alias; prefer DifficultyLevel in new code."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class DifficultyLevel(str, Enum):
    """Teacher-selected difficulty; no automatic detection."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

    @classmethod
    def parse(cls, raw: Union[str, "DifficultyLevel"]) -> "DifficultyLevel":
        if isinstance(raw, cls):
            return raw
        value = str(raw).strip().lower()
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"Invalid difficulty level: {raw}")


# ---------------------------------------------------------------------------
# Solution / Execution
# ---------------------------------------------------------------------------

class SolutionStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ExecutionResultStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class ErrorType(str, Enum):
    SYNTAX = "syntax"
    LOGIC = "logic"
    WARNING = "warning"
    RUNTIME = "runtime"
    PATTERN = "pattern"


# ---------------------------------------------------------------------------
# Users / Roles
# ---------------------------------------------------------------------------

class UserType(str, Enum):
    ADMIN = "admin"
    STUDENT = "student"
    TEACHER = "teacher"


class TeacherRoleRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# ---------------------------------------------------------------------------
# Support / feedback
# ---------------------------------------------------------------------------

class SupportTicketCategory(str, Enum):
    TASK_CONTENT = "task_content"
    AUTOGRADER = "autograder"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    OTHER = "other"


class SupportTicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class SupportTicketTarget(str, Enum):
    TEACHER = "teacher"
    ADMIN = "admin"


class SupportTicketMessageType(str, Enum):
    USER = "user"
    SYSTEM = "system"


class NotificationKind(str, Enum):
    TICKET_CREATED = "ticket_created"
    TICKET_REPLY = "ticket_reply"
    TICKET_STATUS = "ticket_status"
    SUBMISSION_CHECKED = "submission_checked"
    COMMENT = "comment"


# ---------------------------------------------------------------------------
# Tasks / Assignments
# ---------------------------------------------------------------------------

class AssignmentWorkflowStatus(str, Enum):
    """Admin workflow for tasks (assignments)."""
    ACTIVE = "active"
    UNDER_REVIEW = "under_review"
    ARCHIVED = "archived"


class TaskType(str, Enum):
    ALGORITHM = "algorithm"
    TRANSLATION = "translation"
    DIAGRAM = "diagram"
    BLOCK_REORDER = "block_reorder"


class AssignmentType(str, Enum):
    TASK_BUILD_FROM_BLOCKS = "task_build_from_blocks"
    TASK_TRANSLATE_SNIPPET = "task_translate_snippet"
    TASK_TRANSLATE_FULL_PROGRAM = "task_translate_full_program"
    TASK_FLOWCHART_TO_CODE = "task_flowchart_to_code"
    LEGACY_ALGORITHM = "algorithm"

    @classmethod
    def parse(cls, raw: Union[str, "AssignmentType"]) -> "AssignmentType":
        if isinstance(raw, cls):
            return raw
        value = str(raw).strip().lower()
        aliases = {
            "block_reorder": cls.TASK_BUILD_FROM_BLOCKS,
            "code_assembly": cls.TASK_BUILD_FROM_BLOCKS,
            "translation": cls.TASK_TRANSLATE_FULL_PROGRAM,
            "diagram": cls.TASK_FLOWCHART_TO_CODE,
            "blocks": cls.TASK_FLOWCHART_TO_CODE,
            "algorithm": cls.LEGACY_ALGORITHM,
        }
        if value in aliases:
            return aliases[value]
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"Invalid assignment type: {raw}")

    @classmethod
    def creatable_types(cls) -> tuple["AssignmentType", ...]:
        return (
            cls.TASK_BUILD_FROM_BLOCKS,
            cls.TASK_TRANSLATE_SNIPPET,
            cls.TASK_TRANSLATE_FULL_PROGRAM,
            cls.TASK_FLOWCHART_TO_CODE,
        )

    def public_label(self) -> str:
        labels = {
            AssignmentType.TASK_BUILD_FROM_BLOCKS: "Сборка из блоков",
            AssignmentType.TASK_TRANSLATE_SNIPPET: "Перевод фрагмента",
            AssignmentType.TASK_TRANSLATE_FULL_PROGRAM: "Перевод программы",
            AssignmentType.TASK_FLOWCHART_TO_CODE: "Блок-схема в код",
            AssignmentType.LEGACY_ALGORITHM: "Алгоритм",
        }
        return labels.get(self, self.value)

    def is_translation(self) -> bool:
        return self in {
            AssignmentType.TASK_TRANSLATE_SNIPPET,
            AssignmentType.TASK_TRANSLATE_FULL_PROGRAM,
        }


class AssignmentSetVisibility(str, Enum):
    """Who can discover and access an assignment set."""
    PUBLIC = "public"
    PRIVATE = "private"

    @classmethod
    def parse(cls, raw: Union[str, "AssignmentSetVisibility"]) -> "AssignmentSetVisibility":
        if isinstance(raw, cls):
            return raw
        return cls(str(raw).strip().lower())


class TaskVisibility(str, Enum):
    """Platform-wide task visibility (independent vs teacher-scoped)."""
    PUBLIC = "public"
    PRIVATE = "private"

    @classmethod
    def parse(cls, raw: Union[str, "TaskVisibility"]) -> "TaskVisibility":
        if isinstance(raw, cls):
            return raw
        return cls(str(raw).strip().lower())


# ---------------------------------------------------------------------------
# Profile / Learning
# ---------------------------------------------------------------------------

class PreferredDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

    @classmethod
    def parse(cls, raw: Union[str, "PreferredDifficulty"]) -> "PreferredDifficulty":
        if isinstance(raw, cls):
            return raw
        value = str(raw).strip().lower()
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"Invalid preferred difficulty: {raw}")


class LearningTopic(str, Enum):
    ALGORITHMS = "algorithms"
    DATA_STRUCTURES = "data_structures"
    OOP = "oop"
    DATABASES = "databases"
    WEB = "web"
    CONCURRENCY = "concurrency"
    TESTING = "testing"
    SYSTEM_DESIGN = "system_design"

    @classmethod
    def parse_many(cls, raw_list: list[str]) -> list["LearningTopic"]:
        result: list[LearningTopic] = []
        for raw in raw_list:
            value = str(raw).strip().lower()
            matched = None
            for item in cls:
                if item.value == value:
                    matched = item
                    break
            if matched is None:
                raise ValueError(f"Invalid learning topic: {raw}")
            result.append(matched)
        return result
