from application.curriculum.content.v4_test_cases_io import (
    format_stdin_layout,
    infer_stdin_layout,
    normalize_test_case_inputs,
    stdin_tokens_to_lines,
)

REF = """n = int(input())
scores = [int(input()) for _ in range(n)]
best = scores[0]
for score in scores:
    if score > best:
        best = score
print(best)"""


def test_space_separated_inputs_become_lines():
    assert stdin_tokens_to_lines("5 2 9 1 7", REF) == "4\n2\n9\n1\n7\n"


def test_multiline_inputs_preserved():
    raw = "5\n2\n9\n"
    assert stdin_tokens_to_lines(raw, REF) == raw


def test_count_target_line_layout():
    layout = infer_stdin_layout("task_002")
    assert layout == "count_target_line"
    assert (
        format_stdin_layout(layout, ["5", "12", "8", "3", "12", "5", "9"])
        == "5 12\n8\n3\n12\n5\n9\n"
    )


def test_normalize_task_002_compact_tokens():
    assert (
        normalize_test_case_inputs("5 12 8 3 12 5 9", pattern_id="task_002")
        == "5 12\n8\n3\n12\n5\n9\n"
    )


def test_normalize_count_then_lines_idempotent():
    raw = "4\n2\n9\n1\n7\n"
    assert (
        normalize_test_case_inputs(raw, pattern_id="task_001", goal="Вводится количество")
        == raw
    )


def test_first_line_three_scalars():
    layout = infer_stdin_layout(goal="Даны три целых числа.")
    assert layout == "first_line_3"
    assert format_stdin_layout(layout, ["3", "7", "2"]) == "3 7 2\n"
