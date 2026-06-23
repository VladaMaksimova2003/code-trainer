"""Unified exception hierarchy for the entire project.

All previous locations now re-export from here:
  - domain.auth.errors
  - domain.learning.errors
  - domain.catalogs.errors
  - domain.profile.errors
  - application.interfaces.exceptions
  - application.interfaces.repositories.exceptions
"""
from typing import Type


# ---------------------------------------------------------------------------
# Base infrastructure
# ---------------------------------------------------------------------------

class InfrastructureException(Exception):
    pass


class RepositoryException(InfrastructureException):
    pass


class EntityNotFoundError(RepositoryException):
    def __init__(self, model: Type) -> None:
        super().__init__(f"Entity({model.__name__}) not found.")


class CannotDeleteEntityError(RepositoryException):
    def __init__(self) -> None:
        super().__init__("Cannot delete entity.")


class UserNotFound(EntityNotFoundError):
    pass


class StudentNotFoundError(UserNotFound):
    def __init__(self) -> None:
        super().__init__("Student not found.")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class AuthError(Exception):
    pass


class InvalidCredentialsError(AuthError):
    pass


class InvalidTokenError(AuthError):
    pass


class TokenExpiredError(AuthError):
    pass


class SessionRevokedError(AuthError):
    pass


class AccessDeniedError(AuthError):
    pass


class UserAlreadyExistsError(AuthError):
    pass


class EmailVerificationError(AuthError):
    pass


class EmailDeliveryError(InfrastructureException):
    pass


class TeacherRoleRequestAlreadyPendingError(AuthError):
    pass


class TeacherRoleRequestNotFoundError(AuthError):
    pass


class InvalidTeacherRoleRequestStateError(AuthError):
    pass


class UserAlreadyHasTeacherRoleError(AuthError):
    pass


class UserNotFoundError(AuthError):
    pass


# ---------------------------------------------------------------------------
# Learning
# ---------------------------------------------------------------------------

class LearningDomainError(Exception):
    pass


class GroupNotFoundError(LearningDomainError):
    pass


class AssignmentSetNotFoundError(LearningDomainError):
    pass


class AccessDeniedToContentError(LearningDomainError):
    pass


class InvalidInvitationCodeError(LearningDomainError):
    pass


class AlreadyGroupMemberError(LearningDomainError):
    pass


# ---------------------------------------------------------------------------
# Catalogs / Tasks
# ---------------------------------------------------------------------------

class TaskNotFoundError(Exception):
    pass


class CatalogNotFoundError(Exception):
    pass


class TaskAlreadyAssignedError(Exception):
    pass


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

class ProfileError(Exception):
    """Base error for profile and settings operations."""


class EmailAlreadyInUseError(ProfileError):
    pass


class InvalidPasswordError(ProfileError):
    pass


class TeacherProfileAccessError(ProfileError):
    pass


# ---------------------------------------------------------------------------
# Pattern / Code analysis
# ---------------------------------------------------------------------------

class LanguageNotSupportedError(Exception):
    def __init__(self, language: str) -> None:
        super().__init__(f"Language not supported: {language}")


class NodeTypeNotFoundError(Exception):
    def __init__(self, node_type: str, language: str) -> None:
        super().__init__(f"Node type '{node_type}' not found for language '{language}'")
