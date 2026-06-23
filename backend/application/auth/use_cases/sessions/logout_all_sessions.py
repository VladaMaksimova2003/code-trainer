from shared.interfaces.repositories.users.auth_session import IAuthSessionRepository
from shared.interfaces.uow import IUnitOfWork


class LogoutAllSessionsUseCase:
    def __init__(
        self,
        auth_session_repository: IAuthSessionRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._auth_session_repository = auth_session_repository
        self._uow = uow

    def execute(self, user_id: int) -> None:
        with self._uow(autocommit=True):
            self._auth_session_repository.revoke_all_for_user(user_id)
