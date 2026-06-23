"""Pascal showcase collections registry — student route order and metadata."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PascalShowcaseCollection:
    chapter_key: str
    collection_id: str
    title_ru: str
    description_ru: str
    route_path: str
    showcase_group: str
    title_prefix: str
    study_order_tc: tuple[str, ...]
    yaml_chapter_id: str
    """Primary YAML learning_concept_id for chapter metadata (sorting/progress label)."""


def _col(
    chapter_key: str,
    title_ru: str,
    description_ru: str,
    route_suffix: str,
    study_order_tc: tuple[str, ...],
    yaml_chapter_id: str,
) -> PascalShowcaseCollection:
    route = f"/learn/pascal/{route_suffix}"
    return PascalShowcaseCollection(
        chapter_key=chapter_key,
        collection_id=f"pascal_{chapter_key}_showcase",
        title_ru=title_ru,
        description_ru=description_ru,
        route_path=route,
        showcase_group=f"pascal_curriculum_{chapter_key}_v1",
        title_prefix=f"[Pascal Showcase: {title_ru}] ",
        study_order_tc=study_order_tc,
        yaml_chapter_id=yaml_chapter_id,
    )


# Order = pedagogical track for /curriculum/next
PASCAL_SHOWCASE_COLLECTIONS: tuple[PascalShowcaseCollection, ...] = (
    _col(
        "variables_and_io",
        "Переменные и ввод-вывод",
        "Объявления, присваивание, Readln и Writeln.",
        "variables-and-io",
        (
            "program_entry",
            "typed_declaration",
            "assignment",
            "arithmetic_ops",
            "stdin_read",
            "stdout_write",
        ),
        "data_and_variables",
    ),
    _col(
        "conditions",
        "Условия",
        "if, else, case, логические выражения.",
        "conditions",
        ("simple_branch", "multi_branch", "switch_selection", "conditional_expression"),
        "conditions",
    ),
    _col(
        "loops",
        "Циклы",
        "for, while, repeat-until, перебор.",
        "loops",
        (
            "counted_loop",
            "pre_condition_loop",
            "post_condition_loop",
            "collection_iteration",
            "nested_iteration",
            "loop_control",
        ),
        "loops",
    ),
    _col(
        "functions",
        "Функции",
        "Объявление, вызов, return.",
        "functions",
        ("function_definition", "function_invocation", "return_flow"),
        "functions",
    ),
    _col(
        "arrays",
        "Массивы",
        "Индексация, циклы по массиву, динамические массивы.",
        "arrays",
        ("indexed_sequence", "dynamic_array"),
        "collections",
    ),
    _col(
        "strings",
        "Строки",
        "Строковый тип, length, перебор символов.",
        "strings",
        ("string_sequence",),
        "collections",
    ),
    _col(
        "records",
        "Записи",
        "record, поля, доступ через точку.",
        "records",
        ("key_value_map",),
        "collections",
    ),
    _col(
        "files",
        "Файлы",
        "Чтение и запись текстовых файлов.",
        "files",
        ("file_read", "file_write", "stdin_read", "stdout_write"),
        "files",
    ),
    _col(
        "procedures_and_parameters",
        "Процедуры и параметры",
        "procedure, var/value parameters.",
        "procedures-and-parameters",
        ("function_definition", "parameter_passing", "function_invocation"),
        "functions",
    ),
    _col(
        "modules",
        "Модули",
        "unit, uses, interface/implementation.",
        "modules",
        ("import_dependency", "module_namespace", "symbol_visibility"),
        "modules",
    ),
    _col(
        "recursion",
        "Рекурсия",
        "Базовый и рекурсивный случай, стек вызовов.",
        "recursion",
        ("recursion", "return_flow"),
        "functions",
    ),
    _col(
        "algorithms",
        "Алгоритмы",
        "Поиск, фильтрация, агрегация, сортировка.",
        "algorithms",
        ("search_find", "filter_select", "fold_aggregate", "sort_order"),
        "data_processing",
    ),
    _col(
        "data_structures",
        "Структуры данных",
        "Стек, очередь, связный список, дерево.",
        "data-structures",
        ("stack_queue", "linked_node", "tree_hierarchy", "graph_edges"),
        "advanced_structures",
    ),
    _col(
        "oop",
        "ООП",
        "class, object, method, inheritance.",
        "oop",
        (
            "class_type",
            "object_instance",
            "method_dispatch",
            "inheritance_hierarchy",
        ),
        "oop",
    ),
)

# Legacy groups (conditions/loops seeded before unified registry)
LEGACY_SHOWCASE_GROUPS: dict[str, str] = {
    "conditions": "pascal_curriculum_conditions_v1",
    "loops": "pascal_curriculum_loops_v1",
}


def collection_by_key(chapter_key: str) -> PascalShowcaseCollection | None:
    for item in PASCAL_SHOWCASE_COLLECTIONS:
        if item.chapter_key == chapter_key:
            return item
    return None


def effective_showcase_group(chapter_key: str) -> str:
    legacy = LEGACY_SHOWCASE_GROUPS.get(chapter_key)
    if legacy:
        return legacy
    col = collection_by_key(chapter_key)
    return col.showcase_group if col else f"pascal_curriculum_{chapter_key}_v1"


def effective_title_prefix(chapter_key: str) -> str:
    col = collection_by_key(chapter_key)
    if col is None:
        return f"[Pascal Showcase: {chapter_key}] "
    if chapter_key == "conditions":
        return "[Pascal Conditions Showcase] "
    if chapter_key == "loops":
        return "[Pascal Loops Showcase] "
    return col.title_prefix


def all_showcase_title_prefixes() -> tuple[str, ...]:
    from application.curriculum.pascal.showcase.pascal_v311_registry import (
        PASCAL_V311_SHOWCASE_COLLECTIONS,
    )

    prefixes = {effective_title_prefix(c.chapter_key) for c in PASCAL_SHOWCASE_COLLECTIONS}
    prefixes.add("[Pascal Conditions Showcase] ")
    prefixes.add("[Pascal Loops Showcase] ")
    for col in PASCAL_V311_SHOWCASE_COLLECTIONS:
        prefixes.add(col.title_prefix)
    return tuple(sorted(prefixes, key=len, reverse=True))
