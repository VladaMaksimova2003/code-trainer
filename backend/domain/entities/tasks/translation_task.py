from domain.entities.tasks.base_task import BaseTask
from shared.enums import Difficulty, TaskType
from domain.entities.construction import Construction


class TranslationTask(BaseTask):

    def __init__(
        self,
        id: int,
        teacher_id: int,
        title: str,
        difficulty: Difficulty,
        task_type: TaskType,
        source_language: str,
        source_code: str,
        constructions: list[Construction] | None = None,
        description: str = "РџРµСЂРµРІРµРґРёС‚Рµ РґР°РЅРЅС‹Р№ РёСЃС…РѕРґРЅС‹Р№ РєРѕРґ РЅР° РґСЂСѓРіРѕР№ СЏР·С‹Рє РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёСЏ.",
    ):
        super().__init__(
            id,
            teacher_id,
            title,
            difficulty,
            description,
            task_type,
            constructions,
        )
        self.source_code = source_code
        self.source_language = source_language

    @staticmethod
    def create(
        teacher_id: int,
        title: str,
        description: str,
        difficulty: Difficulty,
        task_type: TaskType,
        source_language: str,
        source_code: str,
        constructions: list[Construction] | None = None,
    ) -> "TranslationTask":
        return TranslationTask(
            id=None,
            teacher_id=teacher_id,
            title=title,
            description=description,
            difficulty=difficulty,
            task_type=task_type,
            source_language=source_language,
            source_code=source_code,
            constructions=constructions,
        )

    def update(self, data: "TranslationTask") -> "TranslationTask":
        new_task = self.clone()
        self.title = data.title
        self.description = data.description
        self.difficulty = data.difficulty
        self.source_code = data.source_code
        self.source_language = data.source_language
        self.constructions = data.constructions
        return new_task
