"""Centralized role checks for multi-role RBAC."""

from __future__ import annotations

from shared.enums import UserType

Role = UserType

_ROLE_PRIORITY: tuple[UserType, ...] = (
    UserType.ADMIN,
    UserType.TEACHER,
    UserType.STUDENT,
)


def normalize_role(raw: UserType | str | object) -> UserType:
    if isinstance(raw, UserType):
        return raw
    s = str(raw).strip()
    if s.startswith("UserType."):
        s = s.split(".", 1)[1]
    return UserType(s.lower())


def normalized_role_key(role: UserType | str | object) -> str:
    return normalize_role(role).name


def normalize_roles(raw_roles: list[UserType | str] | None) -> frozenset[UserType]:
    if not raw_roles:
        return frozenset({UserType.STUDENT})
    return frozenset(normalize_role(r) for r in raw_roles)


def primary_role(roles: frozenset[UserType] | set[UserType] | list[UserType]) -> UserType:
    role_set = frozenset(roles) if not isinstance(roles, frozenset) else roles
    for candidate in _ROLE_PRIORITY:
        if candidate in role_set:
            return candidate
    return UserType.STUDENT


def has_role(roles: frozenset[UserType], role: UserType | str) -> bool:
    return normalize_role(role) in roles


def has_any_role(roles: frozenset[UserType], *required: UserType | str) -> bool:
    if not required:
        return True
    allowed = {normalize_role(r) for r in required}
    return bool(roles & allowed)


def roles_to_strings(roles: frozenset[UserType]) -> list[str]:
    return sorted(r.value for r in roles)
