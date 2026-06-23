from shared.interfaces.uow import UnitOfWork
from application.execution.dto import GetSolutionDTO, UserSolutionDTO


class GetUserSolutionUseCase:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    def execute(self, data: GetSolutionDTO) -> UserSolutionDTO | None:
        with self._uow:
            student = self._uow.students.get(data.user_id)
            solution = self._uow.user_solutions.get_by_user_task_language(
                student.id, data.task_id, data.language
            )
        return UserSolutionDTO.model_validate(solution)
