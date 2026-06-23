"""Укрупнённые группы Display TC для профиля студента (вместо ~29 отдельных карточек)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TcSkillGroupSpec:
    id: str
    label: str
    hint: str
    display_tc_ids: tuple[str, ...]


# Порядок отображения в профиле (8 групп, покрывают все tc_* из tc_display_registry.json).
TC_SKILL_GROUPS: tuple[TcSkillGroupSpec, ...] = (
    TcSkillGroupSpec(
        id="basics",
        label="Основы программы",
        hint="Структура, переменные, присваивание, арифметика, консоль",
        display_tc_ids=(
            "tc_program_structure",
            "tc_variables_types",
            "tc_assignment",
            "tc_arithmetic",
            "tc_console_io",
        ),
    ),
    TcSkillGroupSpec(
        id="control_flow",
        label="Условия и циклы",
        hint="if/else, switch, for/while",
        display_tc_ids=(
            "tc_conditionals",
            "tc_switch_selection",
            "tc_loops",
        ),
    ),
    TcSkillGroupSpec(
        id="functions",
        label="Функции и рекурсия",
        hint="Объявление, вызов, параметры, return, рекурсия",
        display_tc_ids=(
            "tc_functions",
            "tc_parameters_return",
            "tc_recursion",
        ),
    ),
    TcSkillGroupSpec(
        id="collections",
        label="Массивы и коллекции",
        hint="Массивы, строки, обход, словари и записи",
        display_tc_ids=(
            "tc_arrays",
            "tc_strings",
            "tc_collection_traversal",
            "tc_maps_records",
        ),
    ),
    TcSkillGroupSpec(
        id="algorithms",
        label="Алгоритмы на данных",
        hint="Поиск, фильтрация, накопление, сортировка",
        display_tc_ids=(
            "tc_search",
            "tc_filter",
            "tc_aggregate",
            "tc_sort",
        ),
    ),
    TcSkillGroupSpec(
        id="modules_files",
        label="Модули и файлы",
        hint="Импорт модулей и файловый ввод-вывод",
        display_tc_ids=(
            "tc_modules",
            "tc_file_io",
        ),
    ),
    TcSkillGroupSpec(
        id="oop",
        label="Объектно-ориентированное программирование",
        hint="Классы, методы, конструкторы, наследование, полиморфизм",
        display_tc_ids=(
            "tc_oop_classes",
            "tc_oop_methods",
            "tc_oop_constructors",
            "tc_oop_inheritance",
            "tc_oop_polymorphism",
        ),
    ),
    TcSkillGroupSpec(
        id="structures",
        label="Структуры данных",
        hint="Стек, очередь, деревья, графы",
        display_tc_ids=(
            "tc_linear_structures",
            "tc_trees",
            "tc_graphs",
        ),
    ),
)

TC_SKILL_GROUPS_BY_ID: dict[str, TcSkillGroupSpec] = {g.id: g for g in TC_SKILL_GROUPS}

_DISPLAY_TC_TO_GROUP: dict[str, str] = {}
for _group in TC_SKILL_GROUPS:
    for _tc_id in _group.display_tc_ids:
        _DISPLAY_TC_TO_GROUP[_tc_id] = _group.id


def display_tc_group_id(display_tc_id: str) -> str | None:
    return _DISPLAY_TC_TO_GROUP.get(str(display_tc_id or "").strip())


def display_tc_ids_for_group(group_id: str) -> frozenset[str]:
    spec = TC_SKILL_GROUPS_BY_ID.get(group_id)
    if spec is None:
        return frozenset()
    return frozenset(spec.display_tc_ids)
