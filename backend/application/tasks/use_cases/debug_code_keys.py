"""Canonical DB keys for teacher-authored debug (исправить) task code."""

from __future__ import annotations

from typing import Any

KNOWN_DEBUG_LANGS = ("pascal", "python", "cpp", "csharp", "java")


def is_starter_field(key: str) -> bool:
    return str(key or "").startswith("starter_")


def strip_starter_fields(mapping: dict[str, Any]) -> None:
    """Remove catalog starter_* keys from a flat mapping (in place)."""
    for key in list(mapping.keys()):
        if is_starter_field(str(key)):
            del mapping[key]


def teacher_task_blocks_starters(examples: dict[str, Any] | None) -> bool:
    return bool(dict(examples or {}).get("teacher_assembly_override"))


def buggy_code_key(language: str) -> str:
    return f"buggy_{str(language or '').lower()}"


def is_buggy_code_key(key: str) -> bool:
    text = str(key or "").lower()
    if not text.startswith("buggy_"):
        return False
    return text.removeprefix("buggy_") in KNOWN_DEBUG_LANGS


def read_teacher_buggy_code(
    examples: dict[str, Any],
    showcase: dict[str, Any],
    language: str,
    *,
    allow_legacy_starter: bool = True,
) -> str:
    """Teacher «Учу» code from DB (`buggy_{lang}`). Legacy starter_* only when allowed."""
    key = buggy_code_key(language)
    text = str(examples.get(key) or "")
    if text.strip():
        return text
    if not allow_legacy_starter or teacher_task_blocks_starters(examples):
        return ""
    return str(showcase.get(f"starter_{language}") or "")


def migrate_legacy_starter_to_buggy(examples: dict[str, Any], showcase: dict[str, Any]) -> bool:
    """Move showcase.starter_{lang} → code_examples.buggy_{lang} once."""
    changed = False
    for lang in KNOWN_DEBUG_LANGS:
        legacy_key = f"starter_{lang}"
        legacy = str(showcase.get(legacy_key) or "")
        if not legacy.strip():
            continue
        key = buggy_code_key(lang)
        if str(examples.get(key) or "").strip():
            showcase.pop(legacy_key, None)
            changed = True
            continue
        examples[key] = legacy
        showcase.pop(legacy_key, None)
        changed = True
    if changed:
        examples["curriculum_showcase"] = showcase
    return changed
