#!/usr/bin/env python3
"""Audit formatted reference code for display issues."""

from __future__ import annotations

import re
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from application.curriculum.content.v4_code_format import format_reference_code
from application.curriculum.content.v4_reference_code import _TASK_REFERENCE_CODE

LANGS = ["cpp", "java", "csharp", "python", "pascal"]
BAD_PATTERNS = {
    "cpp": [
        (re.compile(r"#include\s+[<\"][^>\"]+[>\"][A-Za-z_]"), "include glued to code"),
        (re.compile(r">>\s*\n\s*\w"), "broken stream operator"),
        (re.compile(r"if\([^)]*>\s*\n"), "broken comparison"),
        (re.compile(r"^.{220,}$", re.M), "overlong line"),
    ],
    "java": [
        (re.compile(r"import[^;\n]+;[ \t]*class\b"), "import glued to class"),
        (re.compile(r"^.{220,}$", re.M), "overlong line"),
    ],
    "csharp": [
        (re.compile(r"using[^;\n]+;[ \t]*class\b"), "using glued to class"),
        (re.compile(r'\$\s*"\s*\n\s*\{'), "broken interpolation"),
        (re.compile(r"^.{220,}$", re.M), "overlong line"),
    ],
    "python": [
        (re.compile(r"int\(\s+input"), "broken int(input())"),
        (re.compile(r"\)[ \t]+[a-z_]+\s*="), "statement glued after paren"),
        (re.compile(r"\d[a-z_]"), "digit glued to name"),
        (re.compile(r"\w+in\s"), "missing space before in"),
        (re.compile(r"\[int\(input\(\)\)\nfor\b"), "broken list comprehension"),
    ],
}


def main() -> int:
    issues: list[str] = []
    for num in range(1, 129):
        pat = f"task_{num:03d}"
        for lang in LANGS:
            raw = str(_TASK_REFERENCE_CODE.get(pat, {}).get(lang, "") or "").strip()
            if not raw:
                continue
            fmt = format_reference_code(raw, lang)
            for pattern, label in BAD_PATTERNS.get(lang, []):
                if pattern.search(fmt):
                    issues.append(f"{pat} [{lang}] {label}")
                    break

    print(f"audited 128 tasks x {len(LANGS)} languages")
    print(f"issues: {len(issues)}")
    for line in issues[:40]:
        print(f"  - {line}")
    if len(issues) > 40:
        print(f"  ... and {len(issues) - 40} more")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
