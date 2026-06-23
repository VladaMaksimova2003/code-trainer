from shared.exceptions import InfrastructureException


class NormalizerError(InfrastructureException):
    pass


class LanguageNotSupportedError(NormalizerError):
    def __init__(self, language: str):
        super().__init__(f"Язык {language} не поддерживается в таблице нормализации.")


class NodeTypeNotFoundError(NormalizerError):
    def __init__(self, node_type: str, language: str):
        super().__init__(
            f"Тип узла '{node_type}' не найден в таблице нормализации для языка '{language}'."
        )
