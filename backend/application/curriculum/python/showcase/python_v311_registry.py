"""Python Course showcase collections — 192 tasks, 16 chapters (algorithm-syntax, v192-B)."""

from __future__ import annotations

from dataclasses import dataclass

from application.curriculum.course_scope import active_collection_targets
from application.curriculum.shared.algo_v128_showcase import (
    V128_CHAPTER_ORDER,
    algo_v128_chapters,
)


@dataclass(frozen=True)
class PythonV311Collection:
    chapter_key: str
    collection_id: str
    title_ru: str
    description_ru: str
    route_path: str
    showcase_group: str
    title_prefix: str
    study_order_tc: tuple[str, ...]
    yaml_chapter_id: str


def _col(chapter) -> PythonV311Collection:
    return PythonV311Collection(
        chapter_key=chapter.chapter_key,
        collection_id=f"python_{chapter.chapter_key}_v311",
        title_ru=chapter.title_ru,
        description_ru=chapter.description_ru,
        route_path=f"/learn/python/{chapter.route_suffix}",
        showcase_group=f"python_curriculum_v311_{chapter.chapter_key}",
        title_prefix=f"[{chapter.title_ru}] ",
        study_order_tc=chapter.study_order_tc,
        yaml_chapter_id=chapter.yaml_chapter_id,
    )


PYTHON_V311_SHOWCASE_COLLECTIONS: tuple[PythonV311Collection, ...] = tuple(
    _col(ch) for ch in algo_v128_chapters()
)

V311_CHAPTER_ORDER: tuple[str, ...] = V128_CHAPTER_ORDER
V311_COLLECTION_TARGETS: dict[str, int] = active_collection_targets()


def v311_collection_by_key(chapter_key: str) -> PythonV311Collection | None:
    for item in PYTHON_V311_SHOWCASE_COLLECTIONS:
        if item.chapter_key == chapter_key:
            return item
    return None


def v311_title_prefix(chapter_key: str) -> str:
    col = v311_collection_by_key(chapter_key)
    return col.title_prefix if col else ""


def v311_showcase_group(chapter_key: str) -> str:
    col = v311_collection_by_key(chapter_key)
    return col.showcase_group if col else f"python_curriculum_v311_{chapter_key}"
