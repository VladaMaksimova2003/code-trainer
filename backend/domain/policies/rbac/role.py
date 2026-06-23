"""Re-export RBAC helpers (single entry point for role checks)."""

from domain.policies.rbac.rbac import (  # noqa: F401
    Role,
    has_any_role,
    has_role,
    normalize_role,
    normalized_role_key,
    normalize_roles,
    primary_role,
    roles_to_strings,
)

