from domain.policies.rbac.rbac import has_any_role, has_role, normalize_roles, primary_role
from domain.entities.base import Entity
from shared.enums import UserType


class User(Entity):
    """Single account entity; capabilities come from assigned roles."""

    def __init__(
        self,
        id: int | None,
        name: str,
        email: str,
        password: str,
        roles: frozenset[UserType] | None = None,
        is_blocked: bool = False,
        is_deleted: bool = False,
    ):
        super().__init__(id)
        self.name = name
        self.email = email
        self.password = password
        self.is_blocked = is_blocked
        self.is_deleted = is_deleted
        self.roles = (
            normalize_roles(list(roles))
            if roles is not None
            else frozenset({UserType.STUDENT})
        )

    def can_authenticate(self) -> bool:
        return not self.is_blocked and not self.is_deleted

    @property
    def primary_role(self) -> UserType:
        return primary_role(self.roles)

    @property
    def TYPE(self) -> UserType:
        """Backward-compatible alias used by token issuance."""
        return self.primary_role

    def has_role(self, role: UserType | str) -> bool:
        return has_role(self.roles, role)

    def has_any_role(self, *roles: UserType | str) -> bool:
        return has_any_role(self.roles, *roles)
