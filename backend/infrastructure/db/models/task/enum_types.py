"""Shared SQLAlchemy enum column helpers (string-backed, portable across DBs)."""

from __future__ import annotations

from enum import Enum
from typing import TypeVar

import sqlalchemy as sa

E = TypeVar("E", bound=Enum)


def str_enum_column(enum_cls: type[E], *, name: str) -> sa.Enum:
    """
    Non-native enum stored as VARCHAR using enum `.value` strings.
    Matches existing pattern (e.g. Language on translation_task).
    """
    return sa.Enum(
        enum_cls,
        name=name,
        native_enum=False,
        values_callable=lambda enum: [member.value for member in enum],
    )


def coerce_enum(enum_cls: type[E], value: E | str | None, *, default: E) -> E:
    """Normalize ORM/API/DB values to a domain enum member."""
    if value is None:
        return default
    if isinstance(value, enum_cls):
        return value
    parse = getattr(enum_cls, "parse", None)
    if callable(parse):
        return parse(value)
    return enum_cls(str(value).strip().lower())
