from sqlalchemy import select
from sqlalchemy.orm import Session

from shared.interfaces.repositories.users.user_role import IUserRoleRepository
from domain.policies.rbac.rbac import primary_role
from shared.enums import UserType
from infrastructure.db.models.user import User as UserModel
from infrastructure.db.models.user.user_role import UserRole as UserRoleModel


class SqlAlchemyUserRoleRepository(IUserRoleRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_roles_for_user(self, user_id: int) -> frozenset[UserType]:
        stmt = select(UserRoleModel.role).where(UserRoleModel.user_id == user_id)
        rows = self._session.execute(stmt).scalars().all()
        if rows:
            return frozenset(self._parse_role(r) for r in rows)

        user = self._session.get(UserModel, user_id)
        if user is None:
            return frozenset({UserType.STUDENT})
        return frozenset({self._parse_role(user.role)})

    def assign_role(self, user_id: int, role: UserType) -> None:
        role_value = role.value
        exists = self._session.execute(
            select(UserRoleModel.id).where(
                UserRoleModel.user_id == user_id,
                UserRoleModel.role == role_value,
            )
        ).scalar_one_or_none()
        if exists is not None:
            return
        self._session.add(UserRoleModel(user_id=user_id, role=role_value))
        self._session.flush()
        roles = self.get_roles_for_user(user_id)
        self.sync_primary_role_column(user_id, roles)

    def sync_primary_role_column(self, user_id: int, roles: frozenset[UserType]) -> None:
        user = self._session.get(UserModel, user_id)
        if user is None:
            return
        user.role = primary_role(roles).value
        self._session.flush()

    def remove_role(self, user_id: int, role: UserType) -> None:
        row = self._session.execute(
            select(UserRoleModel).where(
                UserRoleModel.user_id == user_id,
                UserRoleModel.role == role.value,
            )
        ).scalar_one_or_none()
        if row is None:
            return
        self._session.delete(row)
        self._session.flush()
        roles = self.get_roles_for_user(user_id)
        if not roles:
            self.assign_role(user_id, UserType.STUDENT)
        else:
            self.sync_primary_role_column(user_id, roles)

    @staticmethod
    def _parse_role(raw: str) -> UserType:
        try:
            return UserType(raw.lower())
        except ValueError:
            return UserType.STUDENT
