"""Application-layer authorization (RBAC guards for use cases and API)."""

from __future__ import annotations

from shared.interfaces.repositories.users.user_role import IUserRoleRepository
from application.auth.dto import CurrentUserResult
from shared.exceptions import AccessDeniedError
from domain.policies.permissions.permissions import Permission, can, can_any
from domain.policies.rbac.rbac import has_any_role, normalize_role
from shared.enums import UserType

Role = UserType


class AuthorizationService:
    def __init__(self, user_role_repository: IUserRoleRepository) -> None:
        self._user_role_repository = user_role_repository

    def get_roles_for_user(self, user_id: int) -> frozenset[UserType]:
        return self._user_role_repository.get_roles_for_user(user_id)

    @staticmethod
    def roles_from_current_user(user: CurrentUserResult) -> frozenset[UserType]:
        if user.roles:
            return frozenset(normalize_role(r) for r in user.roles)
        return frozenset({normalize_role(user.role)})

    def ensure_any_role(self, user: CurrentUserResult, *required: Role) -> None:
        roles = self.roles_from_current_user(user)
        if not has_any_role(roles, *required):
            raise AccessDeniedError("Not enough permissions.")

    def ensure_permission(self, user: CurrentUserResult, permission: Permission) -> None:
        roles = self.roles_from_current_user(user)
        if not can(roles, permission):
            raise AccessDeniedError("Not enough permissions.")

    def ensure_any_permission(
        self, user: CurrentUserResult, *permissions: Permission
    ) -> None:
        roles = self.roles_from_current_user(user)
        if not can_any(roles, *permissions):
            raise AccessDeniedError("Not enough permissions.")
