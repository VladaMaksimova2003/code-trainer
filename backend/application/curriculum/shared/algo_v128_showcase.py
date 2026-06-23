"""Shared showcase chapter definitions for the 128-task algorithm-syntax course."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

_FALLBACK_CHAPTER_KEYS: tuple[str, ...] = (
    "algo_basics",
    "branches",
    "loops",
    "arrays_collections",
    "strings",
    "functions",
    "recursion",
    "search_sort",
    "aggregation",
    "maps",
    "files_modules",
    "stack_queue",
    "linked_lists",
    "trees_graphs",
    "oop",
    "inheritance_capstone",
)

_FALLBACK_CHAPTER_TITLES: dict[str, str] = {
    "algo_basics": "Базовый синтаксис через простые алгоритмы",
    "branches": "Ветвления",
    "loops": "Циклы",
    "arrays_collections": "Массивы и коллекции",
    "strings": "Строки",
    "functions": "Функции",
    "recursion": "Рекурсия",
    "search_sort": "Поиск и сортировки",
    "aggregation": "Агрегация и фильтрация данных",
    "maps": "Словари и key-value структуры",
    "files_modules": "Файлы и модули",
    "stack_queue": "Стек и очередь",
    "linked_lists": "Связные списки",
    "trees_graphs": "Деревья и графы",
    "oop": "ООП",
    "inheritance_capstone": "Наследование и итоговый проект",
}

try:
    from algo_v128_catalog import (  # noqa: E402
        V128_CHAPTER_KEYS,
        V128_CHAPTER_ORDER,
        V128_CHAPTER_TITLES,
    )
except ImportError:
    V128_CHAPTER_KEYS = _FALLBACK_CHAPTER_KEYS
    V128_CHAPTER_ORDER = _FALLBACK_CHAPTER_KEYS
    V128_CHAPTER_TITLES = dict(_FALLBACK_CHAPTER_TITLES)

CHAPTER_STUDY_TC: dict[str, tuple[str, ...]] = {
    "algo_basics": ("program_entry", "assignment", "stdout_write"),
    "branches": ("simple_branch", "multi_branch"),
    "loops": ("counted_loop", "pre_condition_loop"),
    "arrays_collections": ("indexed_sequence", "dynamic_array"),
    "strings": ("string_sequence",),
    "functions": ("function_definition", "parameter_passing", "return_flow"),
    "recursion": ("recursion",),
    "search_sort": ("search_find", "sort_order"),
    "aggregation": ("filter_select", "fold_aggregate"),
    "maps": ("key_value_map",),
    "files_modules": ("file_read", "file_write", "import_dependency"),
    "stack_queue": ("stack_queue",),
    "linked_lists": ("linked_node",),
    "trees_graphs": ("tree_hierarchy", "graph_edges"),
    "oop": ("class_type", "object_instance", "method_dispatch"),
    "inheritance_capstone": ("inheritance_hierarchy", "method_dispatch"),
}

# Primary technical concept per algorithm-syntax chapter (shared across language catalogs).
CHAPTER_PRIMARY_TC: dict[str, str] = {
    key: values[0] for key, values in CHAPTER_STUDY_TC.items() if values
}


def primary_tc_for_chapter(chapter_key: str, overrides: dict[str, str] | None = None) -> str:
    merged = {**CHAPTER_PRIMARY_TC, **(overrides or {})}
    return merged.get(chapter_key, "program_entry")


CHAPTER_YAML_ID: dict[str, str] = {
    "algo_basics": "data_and_variables",
    "branches": "conditions",
    "loops": "loops",
    "arrays_collections": "collections",
    "strings": "collections",
    "functions": "functions",
    "recursion": "functions",
    "search_sort": "collections",
    "aggregation": "collections",
    "maps": "collections",
    "files_modules": "files",
    "stack_queue": "collections",
    "linked_lists": "collections",
    "trees_graphs": "collections",
    "oop": "oop",
    "inheritance_capstone": "oop",
}

CHAPTER_ROUTE_SUFFIX: dict[str, str] = {
    "algo_basics": "algo-basics",
    "branches": "branches",
    "loops": "loops",
    "arrays_collections": "arrays-collections",
    "strings": "strings",
    "functions": "functions",
    "recursion": "recursion",
    "search_sort": "search-sort",
    "aggregation": "aggregation",
    "maps": "maps",
    "files_modules": "files-modules",
    "stack_queue": "stack-queue",
    "linked_lists": "linked-lists",
    "trees_graphs": "trees-graphs",
    "oop": "oop",
    "inheritance_capstone": "inheritance-capstone",
}

CHAPTER_DESCRIPTION: dict[str, str] = {
    "algo_basics": "Базовые конструкции языка через классические алгоритмы.",
    "branches": "Условные операторы в задачах на сравнение и классификацию.",
    "loops": "Циклы для перебора данных и накопления результата.",
    "arrays_collections": "Массивы и коллекции в алгоритмах обработки данных.",
    "strings": "Строки: поиск, подсчёт, преобразование.",
    "functions": "Функции и процедуры для переиспользуемых алгоритмов.",
    "recursion": "Рекурсивные решения типовых задач.",
    "search_sort": "Поиск и сортировка.",
    "aggregation": "Фильтрация, свёртка и агрегация данных.",
    "maps": "Словари и key-value структуры.",
    "files_modules": "Файлы и модули.",
    "stack_queue": "Стек, очередь и их применение.",
    "linked_lists": "Связные списки.",
    "trees_graphs": "Деревья и графы.",
    "oop": "Классы и объекты.",
    "inheritance_capstone": "Наследование, полиморфизм и итоговый проект.",
}

V128_COLLECTION_TARGETS: dict[str, int] = {key: 8 for key in V128_CHAPTER_KEYS}
V128_TOTAL_TASKS: int = sum(V128_COLLECTION_TARGETS.values())

try:
    from algo_v192_plan import (  # noqa: E402
        COURSE_VARIANT,
        V192_CHAPTER_TASK_COUNT,
        V192_COLLECTION_TARGETS,
        V192_EXPANSION_INDEX,
        V192_TARGET_TASK_COUNT,
    )
except ImportError:
    COURSE_VARIANT = "128"
    V192_CHAPTER_TASK_COUNT = 8
    V192_TARGET_TASK_COUNT = V128_TOTAL_TASKS
    V192_COLLECTION_TARGETS = dict(V128_COLLECTION_TARGETS)
    V192_EXPANSION_INDEX: list = []


def curriculum_catalog_tasks_total() -> int:
    """Shipped catalog task count for the active course scope (default 128)."""
    from application.curriculum.course_scope import active_target_task_count

    return active_target_task_count()


def curriculum_target_tasks_total() -> int:
    """Planned course size after v192-B expansion."""
    return V192_TARGET_TASK_COUNT


@dataclass(frozen=True)
class AlgoV128Chapter:
    chapter_key: str
    title_ru: str
    description_ru: str
    route_suffix: str
    study_order_tc: tuple[str, ...]
    yaml_chapter_id: str


def algo_v128_chapters() -> tuple[AlgoV128Chapter, ...]:
    items: list[AlgoV128Chapter] = []
    for idx, key in enumerate(V128_CHAPTER_KEYS, start=1):
        title = V128_CHAPTER_TITLES.get(key, key)
        items.append(
            AlgoV128Chapter(
                chapter_key=key,
                title_ru=f"{idx}. {title}",
                description_ru=CHAPTER_DESCRIPTION.get(key, title),
                route_suffix=CHAPTER_ROUTE_SUFFIX.get(key, key.replace("_", "-")),
                study_order_tc=CHAPTER_STUDY_TC.get(key, ("program_entry",)),
                yaml_chapter_id=CHAPTER_YAML_ID.get(key, "collections"),
            )
        )
    return tuple(items)
