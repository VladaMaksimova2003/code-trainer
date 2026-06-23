"""FastAPI guards — delegate to AuthorizationService (no business logic here)."""

from typing import Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.users.services.authorization_service import AuthorizationService
from application.auth.dto import CurrentUserResult
from api.dependencies.auth import get_current_user
from shared.exceptions import AccessDeniedError
from domain.policies.permissions.permissions import Permission
from domain.policies.rbac.role import Role
from infrastructure.db.session import get_db
from infrastructure.repositories.users.user_role import SqlAlchemyUserRoleRepository


def get_authorization_service(db: Session = Depends(get_db)) -> AuthorizationService:
    return AuthorizationService(SqlAlchemyUserRoleRepository(db))


def _forbidden(exc: AccessDeniedError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=str(exc) or "Not enough permissions.",
    )


def require_roles(*roles: Role) -> Callable[[CurrentUserResult], CurrentUserResult]:
    def _checker(
        current_user: CurrentUserResult = Depends(get_current_user),
        authz: AuthorizationService = Depends(get_authorization_service),
    ) -> CurrentUserResult:
        try:
            authz.ensure_any_role(current_user, *roles)
        except AccessDeniedError as exc:
            raise _forbidden(exc) from exc
        return current_user

    return _checker


def require_permission(
    permission: Permission,
) -> Callable[[CurrentUserResult], CurrentUserResult]:
    def _checker(
        current_user: CurrentUserResult = Depends(get_current_user),
        authz: AuthorizationService = Depends(get_authorization_service),
    ) -> CurrentUserResult:
        try:
            authz.ensure_permission(current_user, permission)
        except AccessDeniedError as exc:
            raise _forbidden(exc) from exc
        return current_user

    return _checker


def require_super_user() -> Callable[[CurrentUserResult], CurrentUserResult]:
    from shared.super_user import is_super_user_email

    def _checker(current_user: CurrentUserResult = Depends(get_current_user)) -> CurrentUserResult:
        if not is_super_user_email(current_user.email):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the superuser can perform this action.",
            )
        return current_user

    return _checker
