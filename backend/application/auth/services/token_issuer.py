from shared.interfaces.repositories.users.auth_session import IAuthSessionRepository
from shared.interfaces.services.auth import ITokenProvider
from domain.entities.users.auth import AuthSession
from domain.value_objects.auth import TokenPair
from domain.policies.rbac.rbac import primary_role
from domain.entities.users.user import User


def issue_token_pair(
    user: User,
    auth_session_repository: IAuthSessionRepository,
    token_provider: ITokenProvider,
) -> TokenPair:
    main_role = primary_role(user.roles)
    access_token = token_provider.create_access_token(user_id=user.id, role=main_role)
    refresh_token, jti, expires_at = token_provider.create_refresh_token(
        user_id=user.id, role=main_role
    )

    session = AuthSession(
        id=None,
        user_id=user.id,
        refresh_token_jti_hash=jti,
        expires_at=expires_at,
    )
    auth_session_repository.create(session)

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
    )
