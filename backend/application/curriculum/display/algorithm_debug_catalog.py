"""Algorithm-debug pitfalls — orthogonal to MPLT transfer taxonomy (Stage 1)."""

from __future__ import annotations

from typing import Any, TypedDict


class AlgorithmDebugSpec(TypedDict, total=False):
    id: str
    concept_ids: list[str]
    hint_ru: str
    feedback_ru: str
    pedagogy_note_ru: str


_ALL_LANGS = ["python", "cpp", "pascal", "csharp", "java"]

ALGORITHM_DEBUG: dict[str, AlgorithmDebugSpec] = {
    "filter_positive": {
        "id": "filter_positive",
        "concept_ids": ["filter_select", "simple_branch"],
        "hint_ru": "Считайте только положительные значения; ноль и отрицательные не подходят.",
        "feedback_ru": (
            "Ошибка отладки: счётчик нужно начинать с 0, а не с 1. "
            "Пример (Pascal): count := 0; … if amount > 0 then count := count + 1. "
            "Ошибочный вариант: count := 1 — даёт лишнюю единицу. "
            "Считаются только строго положительные: amount > 0 (не >= 0)."
        ),
        "pedagogy_note_ru": "Это логическая ошибка в алгоритме, а не перенос между языками.",
    },
    "threshold_count": {
        "id": "threshold_count",
        "concept_ids": ["filter_select", "simple_branch"],
        "hint_ru": "Сравнивайте каждое значение с порогом (>= 50), а не только последнее.",
        "feedback_ru": "Ошибка отладки: неверное условие подсчёта элементов по порогу.",
        "pedagogy_note_ru": "Это логическая ошибка в алгоритме, а не перенос между языками.",
    },
    "branch_logic": {
        "id": "branch_logic",
        "concept_ids": ["simple_branch", "multi_branch"],
        "hint_ru": "Проверьте все ветви условия и граничные случаи даты.",
        "feedback_ru": "Ошибка отладки: логика ветвления некорректна.",
        "pedagogy_note_ru": "Это логическая ошибка в алгоритме, а не перенос между языками.",
    },
    "multi_branch_discount": {
        "id": "multi_branch_discount",
        "concept_ids": ["multi_branch"],
        "hint_ru": "Используйте else if / отдельные ветви, а не вложенные if без покрытия всех случаев.",
        "feedback_ru": "Ошибка отладки: цепочка условий не эквивалентна правилам скидки.",
        "pedagogy_note_ru": "Это логическая ошибка в алгоритме, а не перенос между языками.",
    },
    "map_key_missing": {
        "id": "map_key_missing",
        "concept_ids": ["key_value_map"],
        "hint_ru": "Перед чтением значения по ключу проверьте, что ключ существует.",
        "feedback_ru": "Ошибка отладки: обращение к отсутствующему ключу без проверки.",
        "pedagogy_note_ru": "Это логическая ошибка в алгоритме, а не перенос между языками.",
    },
}


def get_algorithm_debug(debug_id: str | None) -> AlgorithmDebugSpec | None:
    if not debug_id:
        return None
    spec = ALGORITHM_DEBUG.get(str(debug_id).strip())
    return dict(spec) if spec else None


def build_algorithm_debug_payload(debug_id: str | None) -> dict[str, Any]:
    spec = get_algorithm_debug(debug_id)
    if not spec:
        return {}
    return {
        "debug_id": spec.get("id") or debug_id,
        "hint_ru": spec.get("hint_ru"),
        "feedback_ru": spec.get("feedback_ru"),
        "pedagogy_note_ru": spec.get("pedagogy_note_ru"),
        "concept_ids": list(spec.get("concept_ids") or []),
    }


def list_algorithm_debug_ids() -> list[str]:
    return sorted(ALGORITHM_DEBUG.keys())


def validate_algorithm_debug_id(debug_id: str | None) -> bool:
    if not debug_id:
        return False
    return str(debug_id).strip() in ALGORITHM_DEBUG
