"""Chapter 1 algo_basics: per-task × per-language-pair pitfall bindings."""

from __future__ import annotations

import pytest

from application.curriculum.content.algo_syntax_showcase_meta import (
    transfer_meta_for_language_pair,
)
from application.curriculum.display.chapter1_algo_basics_pitfalls import (
    resolve_chapter1_pitfall_ids,
    resolve_chapter1_proactive_pitfall_ids,
)
from application.curriculum.display.pitfall_messages import proactive_pitfall_message

_COURSE_LANGS = ("python", "pascal", "cpp", "csharp", "java")

_EXPECTED: dict[str, dict[tuple[str, str], list[str]]] = {
    "task_001": {
        ("python", "pascal"): [
            "for_range_off_by_one",
            "input_line_model",
            "assignment_vs_compare",
        ],
        ("pascal", "python"): ["for_range_off_by_one", "input_line_model"],
        ("cpp", "java"): ["for_range_off_by_one", "input_line_model"],
    },
    "task_002": {
        ("python", "pascal"): [
            "input_line_model",
            "index_1based",
            "assignment_vs_compare",
        ],
        ("cpp", "pascal"): ["input_line_model", "index_1based", "assignment_vs_compare"],
        ("pascal", "python"): ["input_line_model"],
        ("java", "csharp"): ["input_line_model"],
    },
    "task_004": {
        ("python", "pascal"): [
            "for_range_off_by_one",
            "input_line_model",
            "assignment_vs_compare",
        ],
        ("csharp", "cpp"): ["for_range_off_by_one", "input_line_model"],
    },
    "task_005": {
        ("python", "pascal"): [
            "for_range_off_by_one",
            "input_line_model",
            "assignment_vs_compare",
        ],
        ("pascal", "cpp"): ["for_range_off_by_one", "input_line_model"],
    },
    "task_006": {
        ("python", "pascal"): [
            "integer_division",
            "for_range_off_by_one",
            "assignment_vs_compare",
        ],
        ("java", "python"): ["integer_division", "for_range_off_by_one"],
    },
    "task_007": {
        ("python", "pascal"): [
            "for_range_off_by_one",
            "output_space_separated",
            "input_line_model",
            "assignment_vs_compare",
        ],
        ("csharp", "cpp"): [
            "for_range_off_by_one",
            "output_space_separated",
            "input_line_model",
        ],
    },
    "task_008": {
        ("python", "pascal"): [],
        ("pascal", "python"): [],
        ("cpp", "java"): [],
    },
    "task_129": {
        ("python", "pascal"): [
            "integer_division",
            "for_range_off_by_one",
            "assignment_vs_compare",
        ],
        ("pascal", "python"): ["integer_division", "for_range_off_by_one"],
    },
}


@pytest.mark.parametrize("pattern_key", sorted(_EXPECTED.keys()))
def test_chapter1_same_language_returns_empty(pattern_key: str):
    for lang in _COURSE_LANGS:
        assert resolve_chapter1_pitfall_ids(
            pattern_key,
            source_language=lang,
            target_language=lang,
        ) == []


@pytest.mark.parametrize(
    "pattern_key,source,target,expected",
    [
        (pattern, source, target, expected)
        for pattern, pairs in _EXPECTED.items()
        for (source, target), expected in pairs.items()
    ],
)
def test_chapter1_resolver_ids(pattern_key: str, source: str, target: str, expected: list[str]):
    assert resolve_chapter1_pitfall_ids(
        pattern_key,
        source_language=source,
        target_language=target,
    ) == expected


@pytest.mark.parametrize(
    "pattern_key,source,target",
    [
        (pattern, source, target)
        for pattern in _EXPECTED
        for source in _COURSE_LANGS
        for target in _COURSE_LANGS
        if source != target
    ],
)
def test_chapter1_proactive_text_when_pitfalls_exist(
    pattern_key: str,
    source: str,
    target: str,
):
    ids = resolve_chapter1_pitfall_ids(
        pattern_key,
        source_language=source,
        target_language=target,
    )
    if not ids:
        meta = transfer_meta_for_language_pair(
            pattern_key,
            source_language=source,
            target_language=target,
        )
        assert not meta.get("proactive_items")
        return

    for pid in ids:
        assert proactive_pitfall_message(
            pid,
            source_language=source,
            target_language=target,
        ), f"missing proactive for {pattern_key} {source}->{target} {pid}"

    meta = transfer_meta_for_language_pair(
        pattern_key,
        source_language=source,
        target_language=target,
    )
    proactive_ids = resolve_chapter1_proactive_pitfall_ids(
        pattern_key,
        source_language=source,
        target_language=target,
    )
    assert meta["pitfall_ids"] == ids
    assert len(meta.get("proactive_items") or []) == len(proactive_ids)
    if proactive_ids:
        assert meta["proactive"]["text"]


def test_task_002_python_pascal_shows_input_banner_first():
    meta = transfer_meta_for_language_pair(
        "task_002",
        source_language="python",
        target_language="pascal",
    )
    assert len(meta["pitfall_ids"]) == 3
    assert len(meta["proactive_items"]) == 3
    banner = meta["proactive"]["text"].lower()
    assert "ввод" in banner or "строк" in banner or "readln" in banner or "чтен" in banner


def test_task_001_python_pascal_skips_repeat_proactive_banners():
    proactive = resolve_chapter1_proactive_pitfall_ids(
        "task_001",
        source_language="python",
        target_language="pascal",
    )
    assert proactive == []


def test_task_008_capstone_has_no_proactive_banners():
    for source in _COURSE_LANGS:
        for target in _COURSE_LANGS:
            if source == target:
                continue
            meta = transfer_meta_for_language_pair(
                "task_008",
                source_language=source,
                target_language=target,
            )
            assert meta["pitfall_ids"] == []
            assert not meta.get("proactive_items")
            assert not meta.get("proactive", {}).get("text")
