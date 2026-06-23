"""Tests for curriculum language availability and track progress helpers."""

from application.curriculum.showcase.showcase_language_progress import (
    display_collection_total,
    effective_collection_total,
    language_is_available,
)


def test_display_collection_total_uses_catalog_plan():
    assert display_collection_total({"total_tasks": 0, "catalog_tasks": 8}) == 8
    assert display_collection_total({"total_tasks": 5, "catalog_tasks": 8}) == 8
    assert display_collection_total({"total_tasks": 5, "catalog_tasks": 0}) == 5


def test_effective_collection_total_uses_seeded_tasks_only():
    assert effective_collection_total({"total_tasks": 0, "catalog_tasks": 128}) == 0
    assert effective_collection_total({"total_tasks": 5, "catalog_tasks": 128}) == 5
    assert effective_collection_total({"total_tasks": 140, "catalog_tasks": 128}) == 128


def test_language_is_available_requires_seeded_tasks():
    collections = [
        {
            "progress": {"total_tasks": 0, "passed_tasks": 0, "catalog_tasks": 8},
        }
    ]
    assert language_is_available(collections) is False


def test_language_is_available_true_when_tasks_present():
    collections = [
        {
            "progress": {"total_tasks": 3, "passed_tasks": 0, "catalog_tasks": 8},
        }
    ]
    assert language_is_available(collections) is True


def test_language_is_available_false_when_empty():
    assert language_is_available([]) is False
