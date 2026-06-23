"""One-off: compare docx raw expected concepts vs pruned catalog."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path[:0] = [str(BACKEND), str(SCRIPTS)]

from build_algorithm_syntax_course_from_docx import (  # noqa: E402
    SRC_DEFAULT,
    LANG_KEYS,
    parse_course,
    paras,
    _reference_for_lang,
)
from application.curriculum.content.v4_code_format import format_reference_code  # noqa: E402
from application.curriculum.validation.expected_concept_checker import (  # noqa: E402
    prune_expected_concepts_for_code,
)

from application.curriculum.validation import expected_concept_checker as ecc  # noqa: E402

_orig_prune = ecc.prune_expected_concepts_for_code


def _no_prune(concepts, code, language):  # noqa: ANN001
    return list(concepts)


ecc.prune_expected_concepts_for_code = _no_prune

lines = paras(SRC_DEFAULT)
tasks, _, _ = parse_course(lines)

ecc.prune_expected_concepts_for_code = _orig_prune

removed_by_concept: dict[str, int] = defaultdict(int)
removed_by_lang: dict[str, int] = defaultdict(int)
examples: list[str] = []

for task in tasks:
    n = task["task_num"]
    pattern = task["pattern_id"]
    title = task["title"][:45]
    refs = task.get("reference_codes") or {}
    impls = task.get("implementations") or {}
    for lang in LANG_KEYS:
        raw_concepts = list((task.get("expected_concepts") or {}).get(lang) or [])
        if not raw_concepts:
            continue
        code = format_reference_code(
            refs.get(lang) or _reference_for_lang(impls.get(lang) or {}, lang),
            lang,
        )
        pruned = prune_expected_concepts_for_code(raw_concepts, code, lang)
        removed = [c for c in raw_concepts if c not in pruned]
        if removed:
            for cid in removed:
                removed_by_concept[cid] += 1
                removed_by_lang[lang] += 1
            if len(examples) < 25:
                examples.append(f"{pattern} [{lang}] -{removed} | {title}")

print("REMOVED CONCEPT STATS (docx raw -> pruned reference)")
print(f"tasks: {len(tasks)}")
print("\nBy language:")
for lang in LANG_KEYS:
    print(f"  {lang}: {removed_by_lang[lang]} removals")
print("\nTop removed concept ids:")
for cid, count in sorted(removed_by_concept.items(), key=lambda x: (-x[1], x[0]))[:15]:
    print(f"  {cid}: {count}")
print("\nExamples:")
for line in examples:
    print(f"  {line}")

# save trimmed report
report = {
    "removed_by_lang": dict(removed_by_lang),
    "removed_by_concept": dict(removed_by_concept),
    "examples": examples,
}
(BACKEND / "_expected_concepts_prune_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
