"""
ConceptRegistry — загрузка и сохранение концептов из resources/concepts.yml.

Следует паттерну hint_loader.py: YAML как источник правды,
функции load/save для чтения и обновления через API.

Публичный API:
  load_concepts()              -> dict[str, dict]   все концепты
  get_concept(concept_id)      -> dict | None        один концепт
  update_concept(id, patch)    -> dict               обновлённый концепт (записывает YAML)
  list_concept_ids()           -> list[str]
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

_CONCEPTS_PATH = (
    Path(__file__).resolve().parents[2] / "resources" / "concepts.yml"
)

# Кэш загруженных концептов. Сбрасывается при сохранении через update_concept().
_cache: dict[str, dict] | None = None


def _load_raw() -> dict[str, dict]:
    """Загружает concepts.yml и возвращает сырой dict."""
    try:
        with _CONCEPTS_PATH.open(encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except OSError:
        return {}


def load_concepts() -> dict[str, dict]:
    """
    Возвращает все концепты как словарь concept_id -> данные.
    Результат кэшируется до следующего вызова update_concept().
    """
    global _cache
    if _cache is None:
        _cache = _load_raw()
    return _cache


def get_concept(concept_id: str) -> dict | None:
    """Возвращает один концепт по id или None если не найден."""
    return load_concepts().get(concept_id)


def list_concept_ids() -> list[str]:
    """Возвращает список всех concept_id в порядке из YAML."""
    return list(load_concepts().keys())


def update_concept(concept_id: str, patch: dict[str, Any]) -> dict:
    """
    Обновляет поля концепта и записывает изменения в concepts.yml.

    patch может содержать:
      description  str              — новое описание
      hint         str              — новая подсказка
      patterns     dict[lang, str]  — примеры кода для языков (частичное обновление)
      name         str              — отображаемое имя

    Возвращает обновлённый концепт.
    Поднимает KeyError если concept_id не найден.
    Поднимает ValueError если patch содержит недопустимые поля.
    """
    global _cache

    concepts = load_concepts()
    if concept_id not in concepts:
        raise KeyError(f"Concept '{concept_id}' not found")

    _ALLOWED_FIELDS = {"name", "description", "hint", "patterns"}
    unknown = set(patch.keys()) - _ALLOWED_FIELDS
    if unknown:
        raise ValueError(f"Unknown fields: {unknown}. Allowed: {_ALLOWED_FIELDS}")

    # Глубокая копия чтобы не мутировать кэш до успешной записи
    updated = copy.deepcopy(concepts[concept_id])

    for field, value in patch.items():
        if field == "patterns":
            # Частичное обновление: только указанные языки
            if not isinstance(value, dict):
                raise ValueError("'patterns' must be a dict mapping language -> code string")
            if "patterns" not in updated:
                updated["patterns"] = {}
            updated["patterns"].update(value)
        else:
            updated[field] = value

    # Записываем обновлённый набор концептов в YAML
    new_concepts = copy.deepcopy(concepts)
    new_concepts[concept_id] = updated

    with _CONCEPTS_PATH.open("w", encoding="utf-8") as f:
        yaml.dump(
            new_concepts,
            f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            indent=2,
        )

    # Инвалидируем кэш
    _cache = new_concepts

    return updated


def to_response_dict(concept_id: str, data: dict) -> dict:
    """Формирует dict для API-ответа из сырых данных концепта."""
    return {
        "id": concept_id,
        "name": data.get("name", concept_id),
        "description": data.get("description", ""),
        "hint": data.get("hint", ""),
        "level": data.get("level", 1),
        "equivalents": data.get("equivalents", {}),
        "ast_nodes": data.get("ast_nodes", {}),
        "patterns": data.get("patterns", {}),
    }
