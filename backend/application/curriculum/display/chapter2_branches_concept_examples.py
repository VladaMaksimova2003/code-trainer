"""Chapter 2: task-specific syntax examples on expected-construction chips.

Banners stay code-free; examples here match the active task and proactive pitfall.
"""

from __future__ import annotations

from typing import Any

# pattern → pitfall_id → display_tc_id → language → hint rows
CH2_TASK_PITFALL_TC_EXAMPLES: dict[str, dict[str, dict[str, dict[str, list[dict[str, Any]]]]]] = {
    "task_009": {
        "assignment_vs_compare": {
            "tc_conditionals": {
                "python": [
                    {
                        "title": "Максимум: сравнение в if",
                        "illustrates": ["conditional"],
                        "code": "m = a\nif b > m:\n    m = b",
                    },
                ],
                "pascal": [
                    {
                        "title": "Максимум: := и =",
                        "illustrates": ["conditional"],
                        "code": "m := a;\nif b > m then\n  m := b;",
                    },
                ],
            },
        },
    },
    "task_010": {
        "elif_chain": {
            "tc_conditionals": {
                "python": [
                    {
                        "title": "Температура: elif",
                        "illustrates": ["conditional", "multi_branch"],
                        "code": "if t < 0:\n    print('freezing')\nelif t <= 25:\n    print('normal')\nelif t <= 35:\n    print('hot')\nelse:\n    print('danger')",
                    },
                ],
                "pascal": [
                    {
                        "title": "Температура: else if",
                        "illustrates": ["conditional", "multi_branch"],
                        "code": "if t < 0 then writeln('freezing')\nelse if t <= 25 then writeln('normal')\nelse if t <= 35 then writeln('hot')\nelse writeln('danger');",
                    },
                ],
                "cpp": [
                    {
                        "title": "Температура: else if",
                        "illustrates": ["conditional", "multi_branch"],
                        "code": "if (t < 0) std::cout << \"freezing\";\nelse if (t <= 25) std::cout << \"normal\";\nelse if (t <= 35) std::cout << \"hot\";\nelse std::cout << \"danger\";",
                    },
                ],
                "csharp": [
                    {
                        "title": "Температура: else if",
                        "illustrates": ["conditional", "multi_branch"],
                        "code": "if (t < 0) Console.WriteLine(\"freezing\");\nelse if (t <= 25) Console.WriteLine(\"normal\");\nelse if (t <= 35) Console.WriteLine(\"hot\");\nelse Console.WriteLine(\"danger\");",
                    },
                ],
                "java": [
                    {
                        "title": "Температура: else if",
                        "illustrates": ["conditional", "multi_branch"],
                        "code": "if (t < 0) System.out.println(\"freezing\");\nelse if (t <= 25) System.out.println(\"normal\");\nelse if (t <= 35) System.out.println(\"hot\");\nelse System.out.println(\"danger\");",
                    },
                ],
            },
        },
    },
    "task_013": {
        "chain_comparison": {
            "tc_conditionals": {
                "python": [
                    {
                        "title": "Баллы: цепочка сравнений",
                        "illustrates": ["conditional"],
                        "code": "if 0 <= score <= 100:\n    ...",
                    },
                ],
                "pascal": [
                    {
                        "title": "Баллы: два сравнения",
                        "illustrates": ["conditional"],
                        "code": "if (score >= 0) and (score <= 100) then\n  ...",
                    },
                ],
            },
        },
        "elif_chain": {
            "tc_conditionals": {
                "python": [
                    {
                        "title": "Шкала: elif",
                        "illustrates": ["multi_branch"],
                        "code": "if score < 0 or score > 100:\n    print('invalid')\nelif score >= 90:\n    print('excellent')",
                    },
                ],
                "pascal": [
                    {
                        "title": "Шкала: else if",
                        "illustrates": ["multi_branch"],
                        "code": "if (score < 0) or (score > 100) then writeln('invalid')\nelse if score >= 90 then writeln('excellent')",
                    },
                ],
            },
        },
    },
    "task_011": {
        "elif_chain": {
            "tc_conditionals": {
                "python": [
                    {
                        "title": "Треугольник: elif",
                        "illustrates": ["multi_branch"],
                        "code": "if a + b <= c or ...:\n    print('invalid')\nelif a == b == c:\n    print('equilateral')",
                    },
                ],
                "pascal": [
                    {
                        "title": "Треугольник: else if",
                        "illustrates": ["multi_branch"],
                        "code": "if (a + b <= c) or ... then writeln('invalid')\nelse if (a = b) and (b = c) then writeln('equilateral')",
                    },
                ],
            },
        },
        "and_or_keywords": {
            "tc_conditionals": {
                "python": [
                    {
                        "title": "Неравенство треугольника: and",
                        "illustrates": ["conditional"],
                        "code": "if (a + b > c) and (a + c > b) and (b + c > a):",
                    },
                ],
                "cpp": [
                    {
                        "title": "Неравенство треугольника: &&",
                        "illustrates": ["conditional"],
                        "code": "if ((a + b > c) && (a + c > b) && (b + c > a))",
                    },
                ],
            },
        },
    },
    "task_012": {
        "input_line_model": {
            "tc_console_io": {
                "python": [
                    {
                        "title": "Дата: три числа из строки",
                        "illustrates": ["console_input"],
                        "code": "d, m, y = map(int, input().split())",
                    },
                ],
                "pascal": [
                    {
                        "title": "Дата: readln(d, m, y)",
                        "illustrates": ["console_input"],
                        "code": "readln(d, m, y);",
                    },
                ],
            },
        },
        "leap_year_mod": {
            "tc_arithmetic": {
                "python": [
                    {
                        "title": "Високосный год",
                        "illustrates": ["arithmetic_ops"],
                        "code": "leap = (y % 400 == 0) or (y % 4 == 0 and y % 100 != 0)",
                    },
                ],
                "pascal": [
                    {
                        "title": "Високосный год (mod)",
                        "illustrates": ["arithmetic_ops"],
                        "code": "leap := (y mod 400 = 0) or ((y mod 4 = 0) and (y mod 100 <> 0));",
                    },
                ],
            },
        },
        "mod_negative": {
            "tc_arithmetic": {
                "pascal": [
                    {
                        "title": "Остаток mod",
                        "illustrates": ["arithmetic_ops"],
                        "code": "y mod 4",
                    },
                ],
                "python": [
                    {
                        "title": "Остаток %",
                        "illustrates": ["arithmetic_ops"],
                        "code": "y % 4",
                    },
                ],
            },
        },
    },
    "task_014": {
        "pascal_case_labels": {
            "tc_switch_selection": {
                "python": [
                    {
                        "title": "Сезон: in (...)",
                        "illustrates": ["switch_selection"],
                        "code": "if m in (12, 1, 2):\n    print('winter')",
                    },
                ],
                "pascal": [
                    {
                        "title": "Сезон: case 12, 1, 2",
                        "illustrates": ["switch_selection"],
                        "code": "case m of\n  12, 1, 2: writeln('winter');\n  3, 4, 5: writeln('spring');\nelse writeln('invalid');\nend;",
                    },
                ],
                "cpp": [
                    {
                        "title": "Сезон: case подряд",
                        "illustrates": ["switch_selection"],
                        "code": "switch (m) {\ncase 12:\ncase 1:\ncase 2:\n  std::cout << \"winter\"; break;\ndefault: break;\n}",
                    },
                ],
            },
        },
        "switch_fallthrough": {
            "tc_switch_selection": {
                "cpp": [
                    {
                        "title": "break после case",
                        "illustrates": ["switch_selection"],
                        "code": "case 3:\n  std::cout << \"spring\";\n  break;",
                    },
                ],
                "csharp": [
                    {
                        "title": "break после case",
                        "illustrates": ["switch_selection"],
                        "code": "case 3:\n    Console.WriteLine(\"spring\");\n    break;",
                    },
                ],
            },
        },
    },
    "task_015": {
        "elif_chain": {
            "tc_conditionals": {
                "python": [
                    {
                        "title": "Скидка: elif по сумме",
                        "illustrates": ["multi_branch"],
                        "code": "if total < 0:\n    print('invalid')\nelif total >= 20000:\n    base = 25",
                    },
                ],
                "pascal": [
                    {
                        "title": "Скидка: else if",
                        "illustrates": ["multi_branch"],
                        "code": "if total < 0 then writeln('invalid')\nelse if total >= 20000 then base := 25",
                    },
                ],
            },
        },
        "chain_comparison": {
            "tc_conditionals": {
                "python": [
                    {
                        "title": "Флаги 0/1",
                        "illustrates": ["conditional"],
                        "code": "if isStudent not in (0, 1) or hasCoupon not in (0, 1):",
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
    bucket: dict[str, list[dict[str, Any]]],
    language: str,
    rows: list[dict[str, Any]],
) -> None:
    lang = _normalize_lang(language)
    if not lang or not rows:
        return
    existing = bucket.setdefault(lang, [])
    seen_codes = {str(row.get("code") or "") for row in existing}
    for row in rows:
        code = str(row.get("code") or "")
        if not code or code in seen_codes:
            continue
        existing.append(dict(row))
        seen_codes.add(code)


def enrich_chapter2_concept_cards(
    cards: list[dict[str, Any]],
    *,
    pattern_key: str | None,
    pitfall_ids: list[str] | None,
    source_language: str,
    target_language: str,
) -> list[dict[str, Any]]:
    """Attach task-specific MPLT examples for chapter-2 proactive pitfalls."""
    pattern = str(pattern_key or "").strip()
    if not pattern or not pitfall_ids:
        return cards

    source = _normalize_lang(source_language)
    target = _normalize_lang(target_language)
    if not source or not target or source == target:
        return cards

    task_pitfalls = CH2_TASK_PITFALL_TC_EXAMPLES.get(pattern) or {}
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
