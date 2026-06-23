from sqlalchemy import select
from sqlalchemy.orm import Session

from shared.interfaces.repositories.users.user import IUserRepository
from domain.policies.rbac.rbac import primary_role
from shared.enums import UserType
from domain.entities.users.user import User
from infrastructure.db.models.user import User as UserModel
from infrastructure.repositories.users.user_role import SqlAlchemyUserRoleRepository


class SqlAlchemyUsersRepository(IUserRepository[User]):
    def __init__(self, session: Session) -> None:
        self._session = session
        self._role_repo = SqlAlchemyUserRoleRepository(session)

    def get(self, entity_id: int) -> User | None:
        stmt = select(UserModel).where(UserModel.id == entity_id)
        model = self._session.execute(stmt).scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        model = self._session.execute(stmt).scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    def create(self, entity: User) -> User:
        roles = entity.roles or frozenset({UserType.STUDENT})
        model = UserModel(
            name=entity.name,
            email=entity.email,
            password=entity.password,
            role=primary_role(roles).value,
            is_blocked=entity.is_blocked,
            is_deleted=entity.is_deleted,
        )
        self._session.add(model)
        self._session.flush()
        self._session.refresh(model)
        for role in roles:
            self._role_repo.assign_role(model.id, role)
        return self._to_domain(model)

    def _to_domain(self, model: UserModel) -> User:
        roles = self._role_repo.get_roles_for_user(model.id)
        return User(
            id=model.id,
            name=model.name,
            email=model.email,
            password=model.password,
            roles=roles,
            is_blocked=bool(model.is_blocked),
            is_deleted=bool(model.is_deleted),
        )
