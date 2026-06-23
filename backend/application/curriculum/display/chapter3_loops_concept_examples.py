"""Chapter 3: task-specific syntax examples on expected-construction chips.

Banners stay code-free; examples here match the active task and proactive pitfall.
"""

from __future__ import annotations

from typing import Any

CH3_TASK_PITFALL_TC_EXAMPLES: dict[str, dict[str, dict[str, dict[str, list[dict[str, Any]]]]]] = {
    "task_017": {
        "while_sentinel": {
            "tc_loops": {
                "python": [
                    {
                        "title": "Сумма до нуля",
                        "illustrates": ["pre_condition_loop"],
                        "code": "x = int(input())\nwhile x != 0:\n    total += x\n    x = int(input())",
                    },
                ],
                "pascal": [
                    {
                        "title": "Сумма до нуля",
                        "illustrates": ["pre_condition_loop"],
                        "code": "readln(x);\nwhile x <> 0 do\nbegin\n  total := total + x;\n  readln(x);\nend;",
                    },
                ],
            },
        },
    },
    "task_018": {
        "search_first_guard": {
            "tc_loops": {
                "python": [
                    {
                        "title": "Первое вхождение",
                        "illustrates": ["search_find", "counted_loop"],
                        "code": "if x == target and position == 0:\n    position = i",
                    },
                ],
                "pascal": [
                    {
                        "title": "Первое вхождение",
                        "illustrates": ["search_find", "counted_loop"],
                        "code": "if (x = target) and (position = 0) then\n  position := i;",
                    },
                ],
            },
        },
    },
    "task_019": {
        "yes_no_output": {
            "tc_io": {
                "python": [
                    {
                        "title": "Ответ yes/no",
                        "illustrates": ["stdout_write"],
                        "code": "print('yes' if prime else 'no')",
                    },
                ],
                "pascal": [
                    {
                        "title": "Ответ yes/no",
                        "illustrates": ["stdout_write"],
                        "code": "if prime then writeln('yes')\nelse writeln('no');",
                    },
                ],
            },
        },
    },
    "task_020": {
        "filter_non_negative": {
            "tc_loops": {
                "python": [
                    {
                        "title": "Только неотрицательные",
                        "illustrates": ["pre_condition_loop", "simple_branch"],
                        "code": "while x != 0:\n    if x >= 0:\n        total += x\n    x = int(input())",
                    },
                ],
                "pascal": [
                    {
                        "title": "Только неотрицательные",
                        "illustrates": ["pre_condition_loop", "simple_branch"],
                        "code": "while x <> 0 do\nbegin\n  if x >= 0 then total := total + x;\n  readln(x);\nend;",
                    },
                ],
            },
        },
    },
    "task_021": {
        "loop_upper_bound_n": {
            "tc_loops": {
                "python": [
                    {
                        "title": "Таблица 1..n",
                        "illustrates": ["counted_loop"],
                        "code": "for i in range(1, n + 1):\n    ...",
                    },
                ],
                "pascal": [
                    {
                        "title": "Таблица 1..n",
                        "illustrates": ["counted_loop"],
                        "code": "for i := 1 to n do\n  ...",
                    },
                ],
            },
        },
    },
    "task_022": {
        "search_last_overwrite": {
            "tc_loops": {
                "python": [
                    {
                        "title": "Последнее вхождение",
                        "illustrates": ["search_find", "counted_loop"],
                        "code": "if x == target:\n    position = i",
                    },
                ],
                "pascal": [
                    {
                        "title": "Последнее вхождение",
                        "illustrates": ["search_find", "counted_loop"],
                        "code": "if x = target then\n  position := i;",
                    },
                ],
            },
        },
    },
    "task_023": {
        "frequency_bucket": {
            "tc_loops": {
                "python": [
                    {
                        "title": "Bucket по значению",
                        "illustrates": ["fold_aggregate", "counted_loop"],
                        "code": "if 0 <= x <= 9:\n    freq[x] += 1",
                    },
                ],
                "pascal": [
                    {
                        "title": "Bucket по значению",
                        "illustrates": ["fold_aggregate", "counted_loop"],
                        "code": "if (x >= 0) and (x <= 9) then\n  freq[x] := freq[x] + 1;",
                    },
                ],
            },
        },
    },
}


def _normalize_lang(language: str) -> str:
    lang = str(language or "").strip().lower()
    if lang in {"cs", "c#"}:
        return "csharp"
    return lang


def _merge_hint_rows(
    examples: dict[str, list[dict[str, Any]]],
    lang: str,
    rows: list[dict[str, Any]],
) -> None:
    existing = examples.setdefault(lang, [])
    seen_codes = {str(row.get("code") or "") for row in existing}
    for row in rows:
        code = str(row.get("code") or "")
        if not code or code in seen_codes:
            continue
        existing.append(dict(row))
        seen_codes.add(code)


def enrich_chapter3_concept_cards(
    cards: list[dict[str, Any]],
    *,
    pattern_key: str | None,
    pitfall_ids: list[str] | None,
    source_language: str,
    target_language: str,
) -> list[dict[str, Any]]:
    """Attach task-specific MPLT examples for chapter-3 proactive pitfalls."""
    pattern = str(pattern_key or "").strip()
    if not pattern or not pitfall_ids:
        return cards

    source = _normalize_lang(source_language)
    target = _normalize_lang(target_language)
    if not source or not target or source == target:
        return cards

    task_pitfalls = CH3_TASK_PITFALL_TC_EXAMPLES.get(pattern) or {}
    enriched: list[dict[str, Any]] = []
    for card in cards:
        item = dict(card)
        display_id = str(item.get("display_id") or item.get("id") or "").strip()
        if not display_id:
            enriched.append(item)
            continue

        examples: dict[str, list[dict[str, Any]]] = {}
        raw_examples = item.get("examples_by_language")
        if isinstance(raw_examples, dict):
            for lang, rows in raw_examples.items():
                if isinstance(rows, list):
                    examples[_normalize_lang(str(lang))] = [
                        dict(row) for row in rows if isinstance(row, dict)
                    ]

        for pid in pitfall_ids:
            tc_map = (task_pitfalls.get(str(pid or "").strip()) or {}).get(display_id) or {}
            if source in tc_map:
                _merge_hint_rows(examples, source, tc_map[source])
            if target in tc_map:
                _merge_hint_rows(examples, target, tc_map[target])

        if examples:
            item["examples_by_language"] = examples
        enriched.append(item)
    return enriched
