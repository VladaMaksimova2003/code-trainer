"""Pair-specific proactive FCC/AFCC/ATCC warnings (override generic hint_ru)."""

from __future__ import annotations

from application.curriculum.display.pitfall_messages import proactive_pitfall_message


def proactive_pitfall_hint(
    pitfall_id: str | None,
    *,
    source_language: str,
    target_language: str,
) -> str | None:
    return proactive_pitfall_message(
        pitfall_id,
        source_language=source_language,
        target_language=target_language,
    )
