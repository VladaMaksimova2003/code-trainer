"""Fix corrupted Russian string literals in test_curriculum_next.py."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "tests/unit/test_curriculum_next.py"

FIXES = {
    'assert payload["button_label"] == "': [
        (
            "conditions baseline, zero progress",
            'assert payload["button_label"] == "Начать сборник"',
        ),
        (
            "loops after first pass",
            'assert payload["button_label"] == "Продолжить сборник"',
        ),
        (
            "global next start",
            'assert payload["button_label"] == "Начать обучение"',
        ),
    ],
}


def main() -> None:
    raw = TARGET.read_bytes()
    raw = raw.replace(b"\x97", b" - ")
    text = raw.decode("cp1251", errors="replace")
    for ch in ("\u2014", "\u2013"):
        text = text.replace(ch, " - ")

    # Replace mojibake / replacement-char button_label assertions in order.
    lines = text.splitlines()
    button_indices = [
        i
        for i, line in enumerate(lines)
        if 'assert payload["button_label"]' in line
    ]
    expected = [
        '    assert payload["button_label"] == "Начать сборник"',
        '    assert payload["button_label"] == "Продолжить сборник"',
        '    assert payload["button_label"] == "Начать обучение"',
    ]
    if len(button_indices) != len(expected):
        raise SystemExit(
            f"Expected {len(expected)} button_label lines, found {len(button_indices)}"
        )
    for idx, new_line in zip(button_indices, expected):
        lines[idx] = new_line

    TARGET.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("fixed", TARGET)


if __name__ == "__main__":
    main()
