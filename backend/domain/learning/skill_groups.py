"""
Группы навыков профиля — укрупнение концепций из resources/concepts.yml.

Ключ словаря SKILL_GROUPS — стабильный id; label — русское название для UI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

# Все концепции из concepts.yml (ровно 17).
CONCEPT_IDS: Final[frozenset[str]] = frozenset(
    {
        "function",
        "loop",
        "condition",
        "class",
        "variable",
        "recursion",
        "map",
        "filter",
        "sort",
        "reduce",
        "file_io",
        "exception",
        "import",
        "lambda",
        "comprehension",
        "io",
        "nested_loops",
    }
)


@dataclass(frozen=True)
class SkillGroupSpec:
    id: str
    label: str
    concepts: tuple[str, ...]
    hint: str = ""


# Порядок отображения в профиле.
SKILL_GROUPS: tuple[SkillGroupSpec, ...] = (
    SkillGroupSpec(
        id="conditions_logic",
        label="Условия и логика",
        concepts=("condition", "exception"),
        hint="Ветвление, проверки и обработка ошибок",
    ),
    SkillGroupSpec(
        id="loops_recursion",
        label="Циклы и рекурсия",
        concepts=("loop", "recursion", "nested_loops"),
        hint="Повторение, обход и рекурсивные алгоритмы",
    ),
    SkillGroupSpec(
        id="functions",
        label="Функции",
        concepts=("function", "lambda"),
        hint="Определение функций и лямбда-выражения",
    ),
    SkillGroupSpec(
        id="collections",
        label="Работа с коллекциями",
        concepts=("map", "filter", "reduce", "comprehension"),
        hint="Преобразование и обход коллекций",
    ),
    SkillGroupSpec(
        id="sorting_data",
        label="Сортировка и обработка данных",
        concepts=("sort",),
        hint="Упорядочивание и подготовка данных",
    ),
    SkillGroupSpec(
        id="variables_basics",
        label="Переменные и базовые операции",
        concepts=("variable", "io"),
        hint="Присваивание, выражения, ввод и вывод",
    ),
    SkillGroupSpec(
        id="file_io",
        label="Работа с файлами",
        concepts=("file_io",),
        hint="Чтение и запись файлов",
    ),
    SkillGroupSpec(
        id="program_structure",
        label="Структура программы",
        concepts=("class", "import"),
        hint="Классы, модули и организация кода",
    ),
)

SKILL_GROUPS_BY_ID: dict[str, SkillGroupSpec] = {g.id: g for g in SKILL_GROUPS}

_concept_to_group_lists: dict[str, list[str]] = {}
for _group in SKILL_GROUPS:
    for _concept in _group.concepts:
        _concept_to_group_lists.setdefault(_concept, []).append(_group.id)
_CONCEPT_TO_GROUP_IDS: dict[str, tuple[str, ...]] = {
    concept: tuple(group_ids) for concept, group_ids in _concept_to_group_lists.items()
}

# Теги constructions задач → id концепций из concepts.yml.
CONSTRUCTION_TO_CONCEPTS: dict[str, tuple[str, ...]] = {
    "for_loop": ("loop",),
    "while_loop": ("loop",),
    "nested_loops": ("nested_loops",),
    "loop": ("loop",),
    "foreach": ("loop",),
    "recursion": ("recursion",),
    "if_statement": ("condition",),
    "cond": ("condition",),
    "condition": ("condition",),
    "exception": ("exception",),
    "function_definition": ("function",),
    "function_def": ("function",),
    "function": ("function",),
    "return_statement": ("function",),
    "return": ("function",),
    "method": ("function",),
    "method_call": ("function",),
    "direct_call": ("function",),
    "chained_call": ("function",),
    "call": ("function",),
    "io": ("io",),
    "lambda": ("lambda",),
    "binary_expression": ("variable",),
    "identifier": ("variable",),
    "arith": ("variable",),
    "assign": ("variable",),
    "assignment": ("variable",),
    "variable": ("variable",),
    "map": ("map",),
    "filter": ("filter",),
    "reduce": ("reduce",),
    "comprehension": ("comprehension",),
    "sort": ("sort",),
    "file_io": ("file_io",),
    "class": ("class",),
    "import": ("import",),
}


def constructions_to_concepts(constructions: list[str]) -> set[str]:
    """Нормализует теги задачи к id концепций из concepts.yml."""
    concepts: set[str] = set()
    for raw in constructions:
        tag = str(raw or "").strip().lower()
        if not tag:
            continue
        if tag in CONCEPT_IDS:
            concepts.add(tag)
            continue
        concepts.update(CONSTRUCTION_TO_CONCEPTS.get(tag, ()))
    return concepts


def skill_group_ids_for_concepts(concepts: set[str]) -> set[str]:
    group_ids: set[str] = set()
    for concept in concepts:
        for gid in _CONCEPT_TO_GROUP_IDS.get(concept, ()):
            group_ids.add(gid)
    return group_ids


def skill_group_ids_for_constructions(constructions: list[str]) -> set[str]:
    return skill_group_ids_for_concepts(constructions_to_concepts(constructions))
