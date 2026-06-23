"""Permission-based RBAC — extensible beyond fixed role names."""

from __future__ import annotations

from enum import Enum

from domain.policies.rbac.rbac import has_any_role, normalize_role
from shared.enums import UserType

Role = UserType


class Permission(str, Enum):
    SOLVE_ASSIGNMENTS = "solve_assignments"
    VIEW_OWN_PROGRESS = "view_own_progress"
    BROWSE_TEACHERS = "browse_teachers"
    JOIN_GROUPS = "join_groups"
    CREATE_ASSIGNMENTS = "create_assignments"
    EDIT_ASSIGNMENTS = "edit_assignments"
    MANAGE_ASSIGNMENT_SETS = "manage_assignment_sets"
    MANAGE_GROUPS = "manage_groups"
    VIEW_STUDENT_RESULTS = "view_student_results"
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    VIEW_SYSTEM_STATISTICS = "view_system_statistics"
    REVIEW_TEACHER_REQUESTS = "review_teacher_requests"
    SUBMIT_SUPPORT_REQUEST = "submit_support_request"
    MANAGE_SUPPORT_TICKETS = "manage_support_tickets"


ROLE_PERMISSIONS: dict[UserType, frozenset[Permission]] = {
    UserType.STUDENT: frozenset(
        {
            Permission.SOLVE_ASSIGNMENTS,
            Permission.VIEW_OWN_PROGRESS,
            Permission.BROWSE_TEACHERS,
            Permission.JOIN_GROUPS,
            Permission.SUBMIT_SUPPORT_REQUEST,
        }
    ),
    UserType.TEACHER: frozenset(
        {
            Permission.SOLVE_ASSIGNMENTS,
            Permission.VIEW_OWN_PROGRESS,
            Permission.BROWSE_TEACHERS,
            Permission.JOIN_GROUPS,
            Permission.CREATE_ASSIGNMENTS,
            Permission.EDIT_ASSIGNMENTS,
            Permission.MANAGE_ASSIGNMENT_SETS,
            Permission.MANAGE_GROUPS,
            Permission.VIEW_STUDENT_RESULTS,
            Permission.SUBMIT_SUPPORT_REQUEST,
        }
    ),
    UserType.ADMIN: frozenset(Permission),
}


def permissions_for_roles(roles: frozenset[UserType]) -> frozenset[Permission]:
    result: set[Permission] = set()
    for role in roles:
        result |= ROLE_PERMISSIONS.get(normalize_role(role), frozenset())
    return frozenset(result)


def can(roles: frozenset[UserType], permission: Permission) -> bool:
    return permission in permissions_for_roles(roles)


def can_any(roles: frozenset[UserType], *permissions: Permission) -> bool:
    granted = permissions_for_roles(roles)
    return any(p in granted for p in permissions)
