from shared.interfaces.repositories.admin.admin_statistics import (
    IAdminStatisticsRepository,
    SystemStatistics,
)
from shared.interfaces.uow import IUnitOfWork


class GetSystemStatisticsUseCase:
    def __init__(self, repo: IAdminStatisticsRepository, uow: IUnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def execute(self) -> SystemStatistics:
        with self._uow():
            return self._repo.collect()
