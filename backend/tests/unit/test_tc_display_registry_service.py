"""Tests for display TC admin registry (tc_display_registry.json)."""

from application.curriculum.display.tc_display_registry_service import (
    get_merged_tc_concept,
    list_display_tc_ids,
    list_tc_concept_summaries,
    update_tc_concept,
)


def test_list_tc_concept_summaries_uses_display_registry_not_legacy_42():
    items = list_tc_concept_summaries()
    ids = list_display_tc_ids()
    assert len(items) == len(ids)
    assert len(items) == 29
    assert "examples_by_language" not in items[0]
    assert items[0]["source"] == "tc_display_registry.json"
    assert all(item["id"].startswith("tc_") for item in items)


def test_update_tc_concept_persists_name_override(tmp_path, monkeypatch):
    overrides_file = tmp_path / "tc_display_overrides.json"
    monkeypatch.setattr(
        "application.curriculum.display.tc_display_registry_service._OVERRIDES_PATH",
        overrides_file,
    )
    monkeypatch.setattr(
        "application.curriculum.display.tc_display_registry_service._cache",
        None,
    )

    concept_id = "tc_program_structure"
    base = get_merged_tc_concept(concept_id)
    assert base is not None
    assert base["name_ru"]

    updated = update_tc_concept(
        concept_id,
        {"name_ru": "Структура программы (тест)"},
    )
    assert updated["name_ru"] == "Структура программы (тест)"

    monkeypatch.setattr(
        "application.curriculum.display.tc_display_registry_service._cache",
        None,
    )
    reloaded = get_merged_tc_concept(concept_id)
    assert reloaded is not None
    assert reloaded["name_ru"] == "Структура программы (тест)"
