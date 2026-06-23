"""Bootstrap super-user identity (single account with full platform control)."""

SUPER_USER_EMAIL = "admin@test.com"


def is_super_user_email(email: str | None) -> bool:
    return str(email or "").strip().lower() == SUPER_USER_EMAIL


def is_super_user_id(user_id: int | None, email: str | None = None) -> bool:
    return is_super_user_email(email)
