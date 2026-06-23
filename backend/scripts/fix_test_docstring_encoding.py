"""One-off: replace cp1252 em-dash bytes in test module docstrings."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "tests/unit/test_pascal_loops_showcase_seed.py",
    ROOT / "tests/unit/test_pascal_loops_showcase_student_api.py",
    ROOT / "tests/unit/test_student_curriculum_progress.py",
    ROOT / "tests/integration/test_pascal_curriculum_showcase_e2e.py",
]


def fix_file(path: Path) -> None:
    raw = path.read_bytes()
    if b"\x97" in raw:
        raw = raw.replace(b"\x97", b" - ")
    text = raw.decode("utf-8", errors="replace")
    for ch in ("\u2014", "\u2013", "\ufffd"):
        text = text.replace(ch, " - ")
    path.write_text(text, encoding="utf-8", newline="\n")
    print(path.relative_to(ROOT), "->", text.split("\n", 1)[0])


def main() -> None:
    for path in FILES:
        if path.is_file():
            fix_file(path)
        else:
            print("skip missing", path)


if __name__ == "__main__":
    main()
