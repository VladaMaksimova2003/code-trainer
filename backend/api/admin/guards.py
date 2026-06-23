"""Admin user mutation guards."""

from fastapi import HTTPException, status

from shared.interfaces.repositories.admin.admin_user import AdminUserDetail
from shared.super_user import is_super_user_email
from shared.enums import UserType


def ensure_mutable_user(user: AdminUserDetail) -> None:
    if is_super_user_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The superuser account cannot be modified.",
        )


def ensure_can_assign_role(actor_email: str, role: UserType) -> None:
    if role == UserType.ADMIN and not is_super_user_email(actor_email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the superuser can assign the admin role.",
        )
