from pydantic import BaseModel, field_validator

from shared.language import parse_language
from domain.entities.learning.error_message import ErrorMessage


class ErrorMessageDTO(BaseModel):
    text: str
    error_type: str


class CheckSolutionDTO(BaseModel):
    code: str
    language: str
    constructions: list[str]
    task_id: int
    mode: str = "full"

    @field_validator("language")
    @classmethod
    def _validate_language(cls, value: str) -> str:
        return parse_language(value)


class CheckResultDTO(BaseModel):
    success: bool
    errors: list[ErrorMessageDTO]
    task_id: int


class GetSolutionDTO(BaseModel):
    user_id: int
    task_id: int
    language: str

    @field_validator("language")
    @classmethod
    def _validate_language(cls, value: str) -> str:
        return parse_language(value)


class SaveSolutionDTO(BaseModel):
    user_id: int
    task_id: int
    code: str
    language: str

    @field_validator("language")
    @classmethod
    def _validate_language(cls, value: str) -> str:
        return parse_language(value)


class UserSolutionDTO(BaseModel):
    id: int
    user_id: int
    task_id: int
    code: str
    language: str

    @field_validator("language")
    @classmethod
    def _validate_language(cls, value: str) -> str:
        return parse_language(value)
