"""Registered student-facing curriculum showcase collections."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from sqlalchemy.orm import Session

from application.curriculum.pascal.showcase.pascal_v311_registry import (
    PASCAL_V311_SHOWCASE_COLLECTIONS,
)
from application.curriculum.python.showcase.python_v311_registry import (
    PYTHON_V311_SHOWCASE_COLLECTIONS,
)
from application.curriculum.cpp.showcase.cpp_v311_registry import (
    CPP_V311_SHOWCASE_COLLECTIONS,
)
from application.curriculum.csharp.showcase.csharp_v311_registry import (
    CSHARP_V311_SHOWCASE_COLLECTIONS,
)
from application.curriculum.java.showcase.java_v311_registry import (
    JAVA_V311_SHOWCASE_COLLECTIONS,
)


@dataclass(frozen=True)
class CurriculumCollectionDefinition:
    collection_id: str
    language: str
    chapter_key: str
    learning_concept_id: str
    title_ru: str
    description_ru: str
    route_path: str
    build_next: Callable[[Session, int | None], dict]


def _make_build_next_v311_pascal(chapter_key: str) -> Callable[[Session, int | None], dict]:
    def _builder(session: Session, user_id: int | None) -> dict:
        from application.curriculum.pascal.showcase.pascal_showcase_next import (
            build_pascal_v311_showcase_collection_next,
        )

        return build_pascal_v311_showcase_collection_next(session, chapter_key, user_id)

    return _builder


def _make_build_next_v311_python(chapter_key: str) -> Callable[[Session, int | None], dict]:
    def _builder(session: Session, user_id: int | None) -> dict:
        from application.curriculum.python.showcase.python_showcase_next import (
            build_python_v311_showcase_collection_next,
        )

        return build_python_v311_showcase_collection_next(session, chapter_key, user_id)

    return _builder


def _make_build_next_v311_cpp(chapter_key: str) -> Callable[[Session, int | None], dict]:
    def _builder(session: Session, user_id: int | None) -> dict:
        from application.curriculum.cpp.showcase.cpp_showcase_next import (
            build_cpp_v311_showcase_collection_next,
        )

        return build_cpp_v311_showcase_collection_next(session, chapter_key, user_id)

    return _builder


def _make_build_next_v311_csharp(chapter_key: str) -> Callable[[Session, int | None], dict]:
    def _builder(session: Session, user_id: int | None) -> dict:
        from application.curriculum.csharp.showcase.csharp_showcase_next import (
            build_csharp_v311_showcase_collection_next,
        )

        return build_csharp_v311_showcase_collection_next(session, chapter_key, user_id)

    return _builder


def _make_build_next_v311_java(chapter_key: str) -> Callable[[Session, int | None], dict]:
    def _builder(session: Session, user_id: int | None) -> dict:
        from application.curriculum.java.showcase.java_showcase_next import (
            build_java_v311_showcase_collection_next,
        )

        return build_java_v311_showcase_collection_next(session, chapter_key, user_id)

    return _builder


def _make_build_next_v311(chapter_key: str) -> Callable[[Session, int | None], dict]:
    return _make_build_next_v311_pascal(chapter_key)


def _registry() -> tuple[CurriculumCollectionDefinition, ...]:
    items: list[CurriculumCollectionDefinition] = []
    for col in PASCAL_V311_SHOWCASE_COLLECTIONS:
        items.append(
            CurriculumCollectionDefinition(
                collection_id=col.collection_id,
                language="pascal",
                chapter_key=col.chapter_key,
                learning_concept_id=col.yaml_chapter_id,
                title_ru=col.title_ru,
                description_ru=col.description_ru,
                route_path=col.route_path,
                build_next=_make_build_next_v311_pascal(col.chapter_key),
            )
        )
    for col in PYTHON_V311_SHOWCASE_COLLECTIONS:
        items.append(
            CurriculumCollectionDefinition(
                collection_id=col.collection_id,
                language="python",
                chapter_key=col.chapter_key,
                learning_concept_id=col.yaml_chapter_id,
                title_ru=col.title_ru,
                description_ru=col.description_ru,
                route_path=col.route_path,
                build_next=_make_build_next_v311_python(col.chapter_key),
            )
        )
    for col in CPP_V311_SHOWCASE_COLLECTIONS:
        items.append(
            CurriculumCollectionDefinition(
                collection_id=col.collection_id,
                language="cpp",
                chapter_key=col.chapter_key,
                learning_concept_id=col.yaml_chapter_id,
                title_ru=col.title_ru,
                description_ru=col.description_ru,
                route_path=col.route_path,
                build_next=_make_build_next_v311_cpp(col.chapter_key),
            )
        )
    for col in CSHARP_V311_SHOWCASE_COLLECTIONS:
        items.append(
            CurriculumCollectionDefinition(
                collection_id=col.collection_id,
                language="csharp",
                chapter_key=col.chapter_key,
                learning_concept_id=col.yaml_chapter_id,
                title_ru=col.title_ru,
                description_ru=col.description_ru,
                route_path=col.route_path,
                build_next=_make_build_next_v311_csharp(col.chapter_key),
            )
        )
    for col in JAVA_V311_SHOWCASE_COLLECTIONS:
        items.append(
            CurriculumCollectionDefinition(
                collection_id=col.collection_id,
                language="java",
                chapter_key=col.chapter_key,
                learning_concept_id=col.yaml_chapter_id,
                title_ru=col.title_ru,
                description_ru=col.description_ru,
                route_path=col.route_path,
                build_next=_make_build_next_v311_java(col.chapter_key),
            )
        )
    return tuple(items)


def list_curriculum_collections(
    language: str | None = None,
) -> tuple[CurriculumCollectionDefinition, ...]:
    items = _registry()
    if not language:
        return items
    lang = language.strip().lower()
    return tuple(item for item in items if item.language == lang)


def get_collection_by_id(collection_id: str) -> CurriculumCollectionDefinition | None:
    for item in list_curriculum_collections():
        if item.collection_id == collection_id:
            return item
    return None


def get_collection_by_chapter_key(chapter_key: str) -> CurriculumCollectionDefinition | None:
    for item in list_curriculum_collections():
        if item.chapter_key == chapter_key:
            return item
    return None


def route_suffix_to_chapter_key(route_suffix: str) -> str | None:
    for col in PASCAL_V311_SHOWCASE_COLLECTIONS:
        if col.route_path.endswith(f"/{route_suffix}"):
            return col.chapter_key
    return None


def route_suffix_to_chapter_key_python(route_suffix: str) -> str | None:
    for col in PYTHON_V311_SHOWCASE_COLLECTIONS:
        if col.route_path.endswith(f"/{route_suffix}"):
            return col.chapter_key
    return None


def route_suffix_to_chapter_key_cpp(route_suffix: str) -> str | None:
    for col in CPP_V311_SHOWCASE_COLLECTIONS:
        if col.route_path.endswith(f"/{route_suffix}"):
            return col.chapter_key
    return None


def route_suffix_to_chapter_key_csharp(route_suffix: str) -> str | None:
    for col in CSHARP_V311_SHOWCASE_COLLECTIONS:
        if col.route_path.endswith(f"/{route_suffix}"):
            return col.chapter_key
    return None


def route_suffix_to_chapter_key_java(route_suffix: str) -> str | None:
    for col in JAVA_V311_SHOWCASE_COLLECTIONS:
        if col.route_path.endswith(f"/{route_suffix}"):
            return col.chapter_key
    return None


def route_suffix_to_chapter_key_v311(route_suffix: str) -> str | None:
    return route_suffix_to_chapter_key(route_suffix)


# Backward-compatible constants
PASCAL_CONDITIONS_COLLECTION_ID = "pascal_conditions_showcase"
PASCAL_LOOPS_COLLECTION_ID = "pascal_loops_showcase"

