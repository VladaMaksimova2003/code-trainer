from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class RegistrationDayBucket:
    student: int
    teacher: int
    admin: int


@dataclass(frozen=True)
class SystemStatistics:
    users_total: int
    users_by_role: dict[str, int]
    assignments_total: int
    assignments_by_status: dict[str, int]
    submissions_total: int
    submissions_successful: int
    solved_assignments_count: int
    teacher_requests_pending: int
    registrations_by_period: dict[str, list[RegistrationDayBucket]]
    users_new_last_month: int
    users_new_last_month_by_role: dict[str, int]
    tasks_new_last_30_days: int
    curriculum_catalog_tasks: int = 0

class IAdminStatisticsRepository(ABC):
    @abstractmethod
    def collect(self) -> SystemStatistics:
        pass
