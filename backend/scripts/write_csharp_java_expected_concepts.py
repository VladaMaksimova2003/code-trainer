#!/usr/bin/env python3
"""Write csharp/java expected concept override modules from parsed docx JSON."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "scripts" / "course_270_expected_concepts_from_docx.json"


def render_lang_module(lang: str, slots: dict[str, list[str]]) -> str:
    label = "C#" if lang == "csharp" else "Java"
    lines = ["SLOT_OVERRIDES: dict[str, list[str]] = {"]
    for slot in sorted(slots, key=lambda item: int(item.rsplit("_", 1)[-1])):
        quoted = ", ".join(f'"{item}"' for item in slots[slot])
        lines.append(f'    "{slot}": [{quoted}],')
    lines.append("}")
    slot_block = "\n".join(lines)
    return f'''"""Expected concept ids for {label} Course v1 tasks."""

from __future__ import annotations

from application.curriculum.cpp.catalog.cpp_v311_expected_concepts import CHAPTER_DEFAULTS

{slot_block}


def expected_concept_ids_for_row(
    slot_id: str,
    chapter_key: str,
    *,
    _features: str = "",
) -> list[str]:
    override = SLOT_OVERRIDES.get(slot_id)
    if override:
        return list(override)
    return list(CHAPTER_DEFAULTS.get(chapter_key, ["program_entry"]))


__all__ = ["expected_concept_ids_for_row", "CHAPTER_DEFAULTS", "SLOT_OVERRIDES"]
'''


def main() -> None:
    payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    by_slot = payload["by_slot"]
    for lang in ("csharp", "java"):
        path = ROOT / f"application/curriculum/{lang}/catalog/{lang}_v311_expected_concepts.py"
        path.write_text(render_lang_module(lang, by_slot[lang]), encoding="utf-8")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
