from shared.interfaces.uow import UnitOfWork
from application.execution.dto import SaveSolutionDTO, UserSolutionDTO


class SaveUserSolutionUseCase:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    def execute(self, data: SaveSolutionDTO) -> UserSolutionDTO:
        with self._uow(autocommit=True):
            student = self._uow.students.get(data.user_id)
            task = self._uow.tasks.get(data.task_id)

            solution = self._uow.user_solutions.get_by_user_task_language(
                student.id, task.id, data.language
            )

            if solution:
                new_solution = solution.update(data.code)
                updated_solution = self._uow.user_solutions.update(new_solution)
                return UserSolutionDTO.model_validate(updated_solution)

            new_solution = student.create_solution(
                task=task, code=data.code, language=data.language
            )

            created_solution = self._uow.user_solutions.create(new_solution)
            return UserSolutionDTO.model_validate(created_solution)
