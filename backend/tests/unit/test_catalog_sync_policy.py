"""Tests for DB-only curriculum mode (no catalog file sync)."""

from __future__ import annotations

from unittest.mock import patch

from application.curriculum.catalog_sync_policy import (
    catalog_sync_disabled_message,
    is_catalog_sync_enabled,
)


def test_catalog_sync_disabled_by_default():
    with patch("application.curriculum.catalog_sync_policy.get_settings") as mock_settings:
        from shared.config import CurriculumSettings, Settings

        mock_settings.return_value = Settings(curriculum=CurriculumSettings(catalog_sync_enabled=False))
        assert is_catalog_sync_enabled() is False
        assert "DB-only" in catalog_sync_disabled_message()


def test_sync_formatted_reference_codes_skipped_when_catalog_sync_off():
    from application.curriculum.display.showcase_display import _sync_formatted_reference_codes

    payload = {
        "code_examples": {"python": "teacher_fixed = 1"},
        "curriculum": {},
    }
    showcase = {
        "slot_id": "py_005",
        "task_format": "исправление",
        "primary_action": "debug",
        "starter_python": "teacher_buggy = 2",
    }

    with patch("application.curriculum.catalog_sync_policy.is_catalog_sync_enabled", return_value=False):
        _sync_formatted_reference_codes(payload, showcase, teacher_override=False)

    assert payload["code_examples"]["python"] == "teacher_fixed = 1"
    assert showcase["starter_python"] == "teacher_buggy = 2"
