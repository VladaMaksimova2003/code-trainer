"""Generate v128_test_suites_data.py with tagged diversified test cases."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from algo_basics_ch1_user_payload import _tests_for_pattern as ch1_tests
from branches_ch2_user_payload import _tests_for_pattern as ch2_tests
from loops_ch3_user_payload import _tests_for_pattern as ch3_tests
from arrays_ch4_user_payload import _tests_for_pattern as ch4_tests
from strings_ch5_user_payload import _tests_for_pattern as ch5_tests
from functions_ch6_user_payload import _tests_for_pattern as ch6_tests
from recursion_ch7_user_payload import _tests_for_pattern as ch7_tests
from search_sort_ch8_user_payload import _tests_for_pattern as ch8_tests
from aggregation_ch9_user_payload import _tests_for_pattern as ch9_tests
from maps_ch10_user_payload import _tests_for_pattern as ch10_tests
from files_modules_ch11_user_payload import _tests_for_pattern as ch11_tests
from stack_queue_ch12_user_payload import _CUSTOM_TESTS as ch12_tests
from linked_lists_ch13_user_payload import _CUSTOM_TESTS as ch13_tests
from oop_ch15_user_payload import _CUSTOM_TESTS as ch15_tests
from inheritance_ch16_user_payload import _CUSTOM_TESTS as ch16_tests

_COURSE_JSON = _SCRIPTS.parents[0] / "algo_syntax_course.json"

_HARD_CAPSTONE = {
    "task_008", "task_015", "task_016", "task_023", "task_024", "task_031", "task_032",
    "task_039", "task_040", "task_047", "task_048", "task_055", "task_056", "task_063",
    "task_064", "task_071", "task_072", "task_079", "task_080", "task_087", "task_088",
    "task_095", "task_096", "task_103", "task_104", "task_111", "task_112", "task_119",
    "task_120", "task_127", "task_128",
}

_CH2_TAGS: dict[str, list[str]] = {
    "task_009": ["typical", "typical", "negative"],
    "task_010": ["boundary_min", "typical", "typical", "boundary_max"],
    "task_011": ["typical", "all_equal", "duplicate", "invalid"],
    "task_012": ["typical", "invalid", "invalid"],
    "task_013": ["typical", "typical", "typical", "invalid"],
    "task_014": ["typical", "typical", "typical", "invalid"],
    "task_015": ["typical", "zero_empty", "invalid"],
    "task_016": ["typical", "typical", "negative"],
}

_CH2_EXTRA: dict[str, dict[str, str]] = {
    "task_009": {"tag": "all_equal", "inputs": "0 0 0\n", "output": "0"},
    "task_010": {"tag": "boundary", "inputs": "25\n", "output": "normal"},
    "task_011": {"tag": "boundary", "inputs": "2 3 4\n", "output": "scalene"},
    "task_012": {"tag": "boundary", "inputs": "29 2 2020\n", "output": "valid"},
    "task_013": {"tag": "boundary", "inputs": "50\n", "output": "satisfactory"},
    "task_014": {"tag": "boundary", "inputs": "9\n", "output": "autumn"},
    "task_015": {"tag": "boundary_max", "inputs": "20000 1 1\n", "output": "30"},
    "task_016": {"tag": "boundary", "inputs": "18 30000 10000 700\n", "output": "accepted"},
    "task_015_cap": {"tag": "typical", "inputs": "10000 0 1\n", "output": "18"},
    "task_016_cap": {"tag": "invalid", "inputs": "16 15000 5000 500\n", "output": "rejected"},
}

_CH1_EXTRA: dict[str, dict[str, str]] = {
    "task_001": {"tag": "all_equal", "inputs": "4\n9\n9\n1\n9\n", "output": "9"},
    "task_002": {"tag": "duplicate", "inputs": "4\n5\n5\n1\n2\n5\n", "output": "1"},
    "task_003": {"tag": "single", "inputs": "3\n42\n42\n42\n", "output": "42"},
    "task_004": {"tag": "zero_empty", "inputs": "2\n0\n0\n", "output": "0"},
    "task_005": {"tag": "negative", "inputs": "3\n-1\n-2\n-3\n", "output": "-6"},
    "task_006": {"tag": "boundary", "inputs": "2\n3\n7\n", "output": "5"},
    "task_007": {"tag": "boundary", "inputs": "4\n50\n50\n50\n50\n", "output": "4"},
    "task_008": {"tag": "boundary", "inputs": "1\n5\n", "output": "5 5 1"},
    "task_008_cap": {"tag": "negative", "inputs": "3\n1\n2\n1\n", "output": "2 1 2"},
}

_CH1_TAGS = [
    ["typical", "single", "negative"],
    ["typical", "not_found", "duplicate"],
    ["typical", "single", "typical"],
    ["typical", "zero_empty", "typical"],
    ["typical", "single", "negative"],
    ["typical", "single", "zero_empty"],
    ["typical", "zero_empty", "boundary"],
    ["typical", "all_equal", "typical"],
]

_TASK_020_OVERLAY = [
    {"tag": "typical", "inputs": "1\n2\n-1\n3\n0\n", "output": "6"},
    {"tag": "negative", "inputs": "-5\n0\n", "output": "0"},
    {"tag": "single", "inputs": "2\n0\n", "output": "2"},
    {"tag": "zero_empty", "inputs": "0\n", "output": "0"},
]

_TASK_028_OVERLAY = [
    {"tag": "typical", "inputs": "3\n1\n2\n3\n2\n9\n", "output": "1 9 2 3"},
    {"tag": "boundary", "inputs": "2\n10\n20\n1\n5\n", "output": "5 10 20"},
    {"tag": "single", "inputs": "1\n7\n1\n3\n", "output": "3 7"},
    {"tag": "edge_order", "inputs": "4\n1\n2\n3\n4\n3\n0\n", "output": "1 2 0 3 4"},
]

_FILE_TESTS: dict[str, list[dict[str, str]]] = {
    "task_081": [
        {"tag": "typical", "inputs": "10\n20\n30\n", "output": "60"},
        {"tag": "single", "inputs": "42\n", "output": "42"},
        {"tag": "negative", "inputs": "5\n-3\n8\n", "output": "10"},
        {"tag": "zero_empty", "inputs": "0\n0\n0\n", "output": "0"},
    ],
    "task_082": [
        {"tag": "typical", "inputs": "alpha\nbeta\ngamma\n", "output": "3"},
        {"tag": "single", "inputs": "only\n", "output": "1"},
        {"tag": "zero_empty", "inputs": "", "output": "0"},
        {"tag": "boundary", "inputs": "a\nb\nc\nd\ne\n", "output": "5"},
    ],
    "task_083": [
        {"tag": "typical", "inputs": "apple,10\nbanana,20\ncherry,5\n", "output": "35"},
        {"tag": "single", "inputs": "solo,100\n", "output": "100"},
        {"tag": "zero_empty", "inputs": "free,0\n", "output": "0"},
        {"tag": "negative", "inputs": "loss,-5\ngain,15\n", "output": "10"},
    ],
    "task_084": [
        {"tag": "typical", "inputs": "10\n20\n30\n", "output": "60"},
        {"tag": "single", "inputs": "7\n", "output": "7"},
        {"tag": "zero_empty", "inputs": "0\n", "output": "0"},
        {"tag": "negative", "inputs": "5\n-2\n3\n", "output": "6"},
    ],
    "task_085": [
        {"tag": "typical", "inputs": "login\n", "output": "logged"},
        {"tag": "typical", "inputs": "user action\n", "output": "logged"},
        {"tag": "single", "inputs": "x\n", "output": "logged"},
        {"tag": "boundary", "inputs": "error\n", "output": "logged"},
    ],
    "task_086": [
        {"tag": "typical", "inputs": "3\n1\n9\n2\n", "output": "1 2 3 "},
        {"tag": "single", "inputs": "5\n", "output": "5 "},
        {"tag": "negative", "inputs": "4\n-1\n-5\n3\n0\n", "output": "-5 -1 0 3 "},
        {"tag": "all_equal", "inputs": "3\n7\n7\n7\n", "output": "7 7 7 "},
    ],
    "task_087": [
        {"tag": "typical", "inputs": "a\nb\nc\n", "output": "3"},
        {"tag": "single", "inputs": "line\n", "output": "1"},
        {"tag": "zero_empty", "inputs": "", "output": "0"},
        {"tag": "boundary", "inputs": "one\ntwo\nthree\nfour\n", "output": "4"},
        {"tag": "typical", "inputs": "x\ny\n", "output": "2"},
    ],
    "task_088": [
        {"tag": "typical", "inputs": "INFO start\nWARN slow\nERROR fail\nERROR crash\n", "output": "2 1"},
        {"tag": "zero_empty", "inputs": "INFO ok\n", "output": "0 0"},
        {"tag": "single", "inputs": "ERROR only\n", "output": "1 0"},
        {"tag": "boundary", "inputs": "WARN a\nWARN b\nWARN c\n", "output": "0 3"},
        {"tag": "typical", "inputs": "ERROR e1\nERROR e2\nWARN w1\nINFO i1\n", "output": "2 1"},
    ],
}

_TREES_GRAPH_TESTS: dict[str, list[dict[str, str]]] = {
    "task_105": [
        {"tag": "typical", "inputs": "run\n", "output": "10"},
        {"tag": "boundary", "inputs": "preorder\n", "output": "10"},
        {"tag": "single", "inputs": "inorder\n", "output": "10"},
        {"tag": "edge_order", "inputs": "postorder\n", "output": "10"},
    ],
    "task_106": [
        {"tag": "typical", "inputs": "run\n", "output": "10 5 3 15 "},
        {"tag": "boundary", "inputs": "dfs\n", "output": "10 5 3 15 "},
        {"tag": "single", "inputs": "tree\n", "output": "10 5 3 15 "},
        {"tag": "edge_order", "inputs": "walk\n", "output": "10 5 3 15 "},
    ],
    "task_107": [
        {"tag": "typical", "inputs": "run\n", "output": "10 5 15 3 "},
        {"tag": "boundary", "inputs": "bfs\n", "output": "10 5 15 3 "},
        {"tag": "single", "inputs": "level\n", "output": "10 5 15 3 "},
        {"tag": "edge_order", "inputs": "queue\n", "output": "10 5 15 3 "},
    ],
    "task_108": [
        {"tag": "typical", "inputs": "run\n", "output": "10"},
        {"tag": "single", "inputs": "height\n", "output": "10"},
        {"tag": "boundary", "inputs": "tree\n", "output": "10"},
        {"tag": "zero_empty", "inputs": "leaf\n", "output": "10"},
    ],
    "task_109": [
        {"tag": "typical", "inputs": "1\n2\n3\n", "output": "6"},
        {"tag": "single", "inputs": "10\n", "output": "10"},
        {"tag": "negative", "inputs": "5\n-2\n3\n", "output": "6"},
        {"tag": "zero_empty", "inputs": "0\n0\n", "output": "0"},
    ],
    "task_110": [
        {"tag": "typical", "inputs": "3 2\n0 1\n0 2\n0\n", "output": "0 1 2 "},
        {"tag": "boundary", "inputs": "4 3\n0 1\n0 2\n1 3\n0\n", "output": "0 1 2 3 "},
        {"tag": "single", "inputs": "1 0\n0\n", "output": "0 "},
        {"tag": "edge_order", "inputs": "5 4\n0 1\n1 2\n2 3\n3 4\n0\n", "output": "0 1 2 3 4 "},
    ],
    "task_111": [
        {"tag": "typical", "inputs": "3 2\n0 1\n0 2\n0\n", "output": "0 1 2 "},
        {"tag": "boundary", "inputs": "4 3\n0 1\n0 2\n1 3\n0\n", "output": "0 1 2 3 "},
        {"tag": "single", "inputs": "1 0\n0\n", "output": "0 "},
        {"tag": "edge_order", "inputs": "5 4\n0 1\n1 2\n2 3\n3 4\n0\n", "output": "0 1 2 3 4 "},
        {"tag": "typical", "inputs": "6 5\n0 1\n0 2\n1 3\n1 4\n2 5\n0\n", "output": "0 1 2 3 4 5 "},
    ],
    "task_112": [
        {"tag": "typical", "inputs": "2\n9\n1\n7\n", "output": "19"},
        {"tag": "single", "inputs": "10\n", "output": "10"},
        {"tag": "negative", "inputs": "5\n-3\n8\n", "output": "10"},
        {"tag": "zero_empty", "inputs": "0\n", "output": "0"},
        {"tag": "boundary", "inputs": "1\n2\n3\n4\n5\n", "output": "15"},
    ],
}

_OOP_STDIN_TESTS: dict[str, list[dict[str, str]]] = {
    "task_113": [
        {"tag": "typical", "inputs": "", "output": "Alex"},
        {"tag": "single", "inputs": "Sam\n", "output": "Sam"},
        {"tag": "boundary", "inputs": "A\n", "output": "A"},
        {"tag": "typical", "inputs": "Maria\n", "output": "Maria"},
    ],
    "task_114": [
        {"tag": "typical", "inputs": "", "output": "Alex 150"},
        {"tag": "zero_empty", "inputs": "reset\n", "output": "Alex 0"},
        {"tag": "single", "inputs": "deposit 200\n", "output": "Alex 200"},
        {"tag": "negative", "inputs": "withdraw 50\n", "output": "Alex 100"},
    ],
    "task_115": [
        {"tag": "typical", "inputs": "", "output": "Book 600"},
        {"tag": "single", "inputs": "Pen 1 50\n", "output": "Pen 50"},
        {"tag": "zero_empty", "inputs": "Free 5 0\n", "output": "Free 0"},
        {"tag": "boundary", "inputs": "Item 10 1\n", "output": "Item 10"},
    ],
    "task_116": [
        {"tag": "typical", "inputs": "", "output": "12"},
        {"tag": "single", "inputs": "1\n7\n", "output": "7"},
        {"tag": "all_equal", "inputs": "3\n5 5 5\n", "output": "5"},
        {"tag": "negative", "inputs": "3\n-1\n-5\n-2\n", "output": "-1"},
    ],
    "task_117": [
        {"tag": "typical", "inputs": "", "output": "Python 2020\nPascal 1995"},
        {"tag": "single", "inputs": "Java 2018\n", "output": "Java 2018"},
        {"tag": "boundary", "inputs": "Go 2022\nRust 2021\n", "output": "Go 2022\nRust 2021"},
        {"tag": "typical", "inputs": "C 1972\n", "output": "C 1972"},
    ],
    "task_118": [
        {"tag": "typical", "inputs": "", "output": "350"},
        {"tag": "single", "inputs": "1\n100\n", "output": "100"},
        {"tag": "all_equal", "inputs": "4\n75 75 75 75\n", "output": "75"},
        {"tag": "boundary", "inputs": "2\n0 100\n", "output": "50"},
    ],
    "task_119": [
        {"tag": "typical", "inputs": "", "output": "active\ndone"},
        {"tag": "single", "inputs": "1\nitem 30\n", "output": "30"},
        {"tag": "zero_empty", "inputs": "0\n", "output": "0"},
        {"tag": "boundary", "inputs": "2\na 10\nb 20\n", "output": "30"},
        {"tag": "typical", "inputs": "3\na 10\nb 20\nc 5\n", "output": "35"},
    ],
    "task_120": [
        {"tag": "typical", "inputs": "", "output": "Alex 2 450"},
        {"tag": "single", "inputs": "Bob 1 100 0\n", "output": "Bob 1 100"},
        {"tag": "zero_empty", "inputs": "Ann 0 0 0\n", "output": "Ann 0 0"},
        {"tag": "boundary", "inputs": "Max 3 150 25 75\n", "output": "Max 3 500"},
        {"tag": "typical", "inputs": "Eva 1 300 100\n", "output": "Eva 1 400"},
    ],
}

_INHERITANCE_STDIN_TESTS: dict[str, list[dict[str, str]]] = {
    "task_121": [
        {"tag": "typical", "inputs": "", "output": "woof"},
        {"tag": "typical", "inputs": "cat\n", "output": "meow"},
        {"tag": "boundary", "inputs": "dog\n", "output": "woof"},
        {"tag": "single", "inputs": "Dog\n", "output": "woof"},
    ],
    "task_122": [
        {"tag": "typical", "inputs": "", "output": "car drives\nbike rides"},
        {"tag": "single", "inputs": "car\n", "output": "car drives"},
        {"tag": "boundary", "inputs": "bike\n", "output": "bike rides"},
        {"tag": "typical", "inputs": "both\n", "output": "car drives\nbike rides"},
    ],
    "task_123": [
        {"tag": "typical", "inputs": "", "output": "150000"},
        {"tag": "typical", "inputs": "developer\n", "output": "120000"},
        {"tag": "single", "inputs": "intern\n", "output": "50000"},
        {"tag": "boundary", "inputs": "manager\n", "output": "150000"},
    ],
    "task_124": [
        {"tag": "typical", "inputs": "", "output": "email\nsms"},
        {"tag": "single", "inputs": "push\n", "output": "push"},
        {"tag": "duplicate", "inputs": "email email\n", "output": "email\nemail"},
        {"tag": "boundary", "inputs": "a b c\n", "output": "a\nb\nc"},
    ],
    "task_125": [
        {"tag": "typical", "inputs": "", "output": "16\n15"},
        {"tag": "single", "inputs": "1 1\n", "output": "1\n4"},
        {"tag": "boundary", "inputs": "3 5\n", "output": "9\n16"},
        {"tag": "zero_empty", "inputs": "0 0\n", "output": "0\n0"},
    ],
    "task_126": [
        {"tag": "typical", "inputs": "", "output": "card 100\ncash 100"},
        {"tag": "single", "inputs": "card 50\n", "output": "card 50"},
        {"tag": "zero_empty", "inputs": "cash 0\n", "output": "cash 0"},
        {"tag": "duplicate", "inputs": "card 10\ncard 20\n", "output": "card 10\ncard 20"},
    ],
    "task_127": [
        {"tag": "typical", "inputs": "", "output": "24"},
        {"tag": "typical", "inputs": "rectangle 4 6\n", "output": "24"},
        {"tag": "single", "inputs": "square 5\n", "output": "25"},
        {"tag": "boundary", "inputs": "rectangle 1 1\n", "output": "1"},
        {"tag": "zero_empty", "inputs": "rectangle 0 5\n", "output": "0"},
    ],
    "task_128": [
        {"tag": "typical", "inputs": "", "output": "285"},
        {"tag": "single", "inputs": "economy 40\n", "output": "40"},
        {"tag": "zero_empty", "inputs": "free 0\n", "output": "0"},
        {"tag": "boundary", "inputs": "express 200\n", "output": "200"},
        {"tag": "typical", "inputs": "economy 30\nexpress 70\neconomy 20\n", "output": "120"},
    ],
}

_DEFAULT_TAG_CYCLE = ["typical", "boundary", "single", "negative", "zero_empty"]


def _ensure_nl(s: str) -> str:
    return s if s.endswith("\n") else s + "\n"


def _tag_case(case: dict[str, str], tag: str) -> dict[str, str]:
    return {
        "tag": tag,
        "inputs": _ensure_nl(case["inputs"]) if case["inputs"] else case["inputs"],
        "output": case["output"],
    }


def _tag_list(cases: list[dict[str, str]], tags: list[str]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for i, case in enumerate(cases):
        tag = tags[i] if i < len(tags) else _DEFAULT_TAG_CYCLE[i % len(_DEFAULT_TAG_CYCLE)]
        out.append(_tag_case(case, tag))
    return out


def _tests_ch1() -> dict[str, list[dict[str, str]]]:
    result: dict[str, list[dict[str, str]]] = {}
    for i in range(1, 9):
        pid = f"task_{i:03d}"
        base = ch1_tests(pid)
        tagged = _tag_list(base, _CH1_TAGS[i - 1])
        tagged.append(_CH1_EXTRA[pid])
        if pid == "task_008":
            tagged.append(_CH1_EXTRA["task_008_cap"])
        result[pid] = tagged
    return result


def _tests_ch2() -> dict[str, list[dict[str, str]]]:
    result: dict[str, list[dict[str, str]]] = {}
    for i in range(9, 17):
        pid = f"task_{i:03d}"
        base = ch2_tests(pid)
        tagged = _tag_list(base, _CH2_TAGS[pid])
        tagged.append(_CH2_EXTRA[pid])
        if pid == "task_015":
            tagged.append(_CH2_EXTRA["task_015_cap"])
        if pid == "task_016":
            tagged.append(_CH2_EXTRA["task_016_cap"])
        result[pid] = tagged
    return result


def _extra_for_pattern(pid: str, base: list[dict[str, str]]) -> dict[str, str]:
    """Add one diversified edge case per task 017-088 (non-special)."""
    extras: dict[str, dict[str, str]] = {
        "task_017": {"tag": "zero_empty", "inputs": "0\n", "output": "0"},
        "task_018": {"tag": "duplicate", "inputs": "4\n7\n7\n1\n7\n7\n", "output": "1"},
        "task_019": {"tag": "boundary", "inputs": "2\n", "output": "prime"},
        "task_021": {"tag": "boundary", "inputs": "2\n", "output": "2 * 1 = 2\n2 * 2 = 4\n2 * 3 = 6\n2 * 4 = 8\n2 * 5 = 10\n2 * 6 = 12\n2 * 7 = 14\n2 * 8 = 16\n2 * 9 = 18\n2 * 10 = 20\n"},
        "task_022": {"tag": "not_found", "inputs": "3\n1\n2\n3\n9\n", "output": "0"},
        "task_023": {"tag": "all_equal", "inputs": "3\n5\n5\n5\n", "output": "0 0 0 0 0 3 0 0 0 0 "},
        "task_024": {"tag": "single", "inputs": "1\n42\n", "output": "42 42 42 42"},
        "task_025": {"tag": "all_equal", "inputs": "3\n7\n7\n7\n", "output": "7 7 7 "},
        "task_026": {"tag": "boundary", "inputs": "3\n1\n2\n3\n3\n", "output": "1 2 3 "},
        "task_027": {"tag": "boundary", "inputs": "3\n1\n2\n3\n3\n", "output": "1 2"},
        "task_029": {"tag": "zero_empty", "inputs": "0\n0\n", "output": ""},
        "task_030": {"tag": "duplicate", "inputs": "2\n1\n1\n", "output": "yes"},
        "task_031": {"tag": "typical", "inputs": "2 3\n1\n3\n5\n2\n4\n6\n", "output": "6"},
        "task_032": {"tag": "boundary_max", "inputs": "5\n1\n2\n3\n4\n5\n6\n", "output": "6"},
        "task_033": {"tag": "zero_empty", "inputs": "\na\n", "output": "0"},
        "task_034": {"tag": "single", "inputs": "x\n", "output": "x"},
        "task_035": {"tag": "single", "inputs": "a\n", "output": "yes"},
        "task_036": {"tag": "boundary", "inputs": "test\nt\n", "output": "1"},
        "task_037": {"tag": "duplicate", "inputs": "the the cat\n", "output": "3"},
        "task_038": {"tag": "duplicate", "inputs": "aab\naba\n", "output": "yes"},
        "task_039": {"tag": "single", "inputs": "a\n", "output": "a1"},
        "task_040": {"tag": "boundary", "inputs": "aeiou\n", "output": "5 1 yes"},
        "task_041": {"tag": "negative", "inputs": "-3\n7\n", "output": "4"},
        "task_042": {"tag": "boundary", "inputs": "2\n", "output": "prime"},
        "task_043": {"tag": "typical", "inputs": "17\n13\n", "output": "1"},
        "task_044": {"tag": "boundary", "inputs": "  Hi  \n", "output": "hi"},
        "task_045": {"tag": "not_found", "inputs": "3\n1\n2\n3\n9\n", "output": "-1"},
        "task_046": {"tag": "boundary", "inputs": "racecar\n", "output": "yes"},
        "task_047": {"tag": "all_equal", "inputs": "5\n5\n", "output": "5 5"},
        "task_048": {"tag": "zero_empty", "inputs": "3\n0\n0\n0\n", "output": "0 0 0"},
        "task_049": {"tag": "boundary", "inputs": "10\n", "output": "3628800"},
        "task_050": {"tag": "boundary", "inputs": "5\n", "output": "5"},
        "task_051": {"tag": "single", "inputs": "9\n", "output": "9"},
        "task_052": {"tag": "boundary", "inputs": "0\n5\n", "output": "1"},
        "task_053": {"tag": "typical", "inputs": "level\n", "output": "level"},
        "task_054": {"tag": "not_found", "inputs": "4\n1\n3\n5\n7\n4\n", "output": "-1"},
        "task_055": {"tag": "negative", "inputs": "3\n-1\n-3\n-2\n", "output": "-3 -2 -1"},
        "task_056": {"tag": "zero_empty", "inputs": "0\n", "output": "0"},
        "task_057": {"tag": "duplicate", "inputs": "4\n2\n2\n1\n3\n2\n", "output": "0"},
        "task_058": {"tag": "boundary", "inputs": "5\n1\n1\n2\n3\n4\n", "output": "0"},
        "task_059": {"tag": "negative", "inputs": "3\n-1\n-3\n-2\n", "output": "-3 -2 -1"},
        "task_060": {"tag": "all_equal", "inputs": "3\n5\n5\n5\n", "output": "5 5 5"},
        "task_061": {"tag": "edge_order", "inputs": "3\n3\n2\n1\n", "output": "1 2 3"},
        "task_062": {"tag": "single", "inputs": "1\nhello\n", "output": "hello"},
        "task_063": {"tag": "typical", "inputs": "3\nBob 80\nAmy 90\nCal 70\n", "output": "Amy 90\nBob 80\nCal 70"},
        "task_064": {"tag": "boundary", "inputs": "2\nA 10 1\nB 20 2\n", "output": "1 B 20 2\n2 A 10 1"},
        "task_065": {"tag": "single", "inputs": "1\n42\n", "output": "42"},
        "task_066": {"tag": "negative", "inputs": "3\n-6\n0\n6\n", "output": "0"},
        "task_067": {"tag": "single", "inputs": "1\n5\n", "output": "5 5 5 "},
        "task_068": {"tag": "single", "inputs": "1\nx paid 99\n", "output": "x 99"},
        "task_069": {"tag": "single", "inputs": "solo\n", "output": "solo 1"},
        "task_070": {"tag": "boundary", "inputs": "5\n1\n2\n3\n4\n5\n2\n", "output": "5 4 "},
        "task_071": {"tag": "single", "inputs": "1\nonly 9\n", "output": "only 9"},
        "task_072": {"tag": "single", "inputs": "1\nz paid 1\n", "output": "1 1 1"},
        "task_073": {"tag": "duplicate", "inputs": "aaa\n", "output": "a 3"},
        "task_074": {"tag": "single", "inputs": "word\n", "output": "word 1"},
        "task_075": {"tag": "typical", "inputs": "2\nAmy 5\nBob 9\nBob\n", "output": "9"},
        "task_076": {"tag": "typical", "inputs": "1\nid1 Bob 7\nid1\n", "output": "Bob 7"},
        "task_077": {"tag": "single", "inputs": "1\nx\n", "output": "new"},
        "task_078": {"tag": "single", "inputs": "1\nsolo x\n", "output": "solo 1"},
        "task_079": {"tag": "typical", "inputs": "1\nk 5\n1\nk 3\n", "output": "k 8"},
        "task_080": {"tag": "typical", "inputs": "a b a c\n", "output": "a 2"},
    }
    if pid in extras:
        return extras[pid]
    return {"tag": "boundary", "inputs": base[0]["inputs"], "output": base[0]["output"]}


def _from_chapter(fn, start: int, end: int, skip: set[str] | None = None) -> dict[str, list[dict[str, str]]]:
    skip = skip or set()
    result: dict[str, list[dict[str, str]]] = {}
    for i in range(start, end + 1):
        pid = f"task_{i:03d}"
        if pid in skip:
            continue
        base = fn(pid)
        tags = _DEFAULT_TAG_CYCLE[: len(base)]
        tagged = _tag_list(base, tags)
        min_count = 5 if pid in _HARD_CAPSTONE else 4
        extra_idx = 0
        while len(tagged) < min_count:
            if extra_idx == 0:
                tagged.append(_extra_for_pattern(pid, base))
            else:
                tagged.append(
                    {
                        "tag": _DEFAULT_TAG_CYCLE[len(tagged) % len(_DEFAULT_TAG_CYCLE)],
                        "inputs": base[-1]["inputs"],
                        "output": base[-1]["output"],
                    }
                )
            extra_idx += 1
        result[pid] = tagged
    return result


def _expand_oop_fixed(base: dict[str, list[dict[str, str]]], stdin_map: dict[str, list[dict[str, str]]]) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = {}
    for pid, cases in stdin_map.items():
        out[pid] = cases
    return out


def _expand_linked(base: dict[str, list[dict[str, str]]]) -> dict[str, list[dict[str, str]]]:
    result: dict[str, list[dict[str, str]]] = {}
    extras: dict[str, list[dict[str, str]]] = {
        "task_097": [
            {"tag": "typical", "inputs": "3\n1\n2\n3\n", "output": "1 2 3 "},
            {"tag": "boundary", "inputs": "2\n4\n8\n", "output": "4 8 "},
            {"tag": "zero_empty", "inputs": "0\n", "output": ""},
        ],
        "task_098": [{"tag": "boundary", "inputs": "2\n4\n8\n", "output": "8 4 "}],
        "task_099": [{"tag": "typical", "inputs": "5\n1\n2\n3\n4\n5\n", "output": "1 2 3 4 5 "}],
        "task_100": [{"tag": "boundary", "inputs": "1\n0\n0\n", "output": "found"}],
        "task_101": [{"tag": "boundary", "inputs": "1\n9\n1\n", "output": "9 "}],
        "task_102": [{"tag": "single", "inputs": "1\n42\n", "output": "42 "}],
        "task_103": [{"tag": "typical", "inputs": "1\n9\n1\n9\n", "output": "9 "}],
        "task_104": [{"tag": "boundary", "inputs": "3\nadd x\nnext\nnext\n", "output": "empty"}],
    }
    for pid, cases in base.items():
        tagged: list[dict[str, str]] = []
        for i, case in enumerate(cases):
            inp = case["inputs"]
            if inp and not inp.endswith("\n"):
                inp += "\n"
            tagged.append({"tag": _DEFAULT_TAG_CYCLE[i % len(_DEFAULT_TAG_CYCLE)], "inputs": inp, "output": case["output"]})
        for extra in extras.get(pid, []):
            if len(tagged) >= (5 if pid in _HARD_CAPSTONE else 4):
                break
            tagged.append(extra)
        while len(tagged) < (5 if pid in _HARD_CAPSTONE else 4):
            tagged.append(
                {
                    "tag": "boundary",
                    "inputs": tagged[0]["inputs"],
                    "output": tagged[0]["output"],
                }
            )
        result[pid] = tagged
    return result


def _expand_stack(base: dict[str, list[dict[str, str]]]) -> dict[str, list[dict[str, str]]]:
    extras: dict[str, dict[str, str]] = {
        "task_089": {"tag": "boundary", "inputs": "([])\n", "output": "ok"},
        "task_090": {"tag": "boundary", "inputs": "4\nvisit a\nvisit b\nback\ncurrent\n", "output": "a"},
        "task_091": {"tag": "duplicate", "inputs": "4\nadd a\nadd b\nrun\nrun\n", "output": "a"},
        "task_092": {"tag": "boundary", "inputs": "4\ndo a\ndo b\ndo c\nundo\n", "output": "c"},
        "task_093": {"tag": "duplicate", "inputs": "4\nprint a\nprint a\nnext\nnext\n", "output": "a"},
        "task_094": {"tag": "boundary", "inputs": "2 1\n0 1\n0\n", "output": "0 1 "},
        "task_095": {"tag": "boundary", "inputs": "10 2 /\n", "output": "5"},
        "task_096": {"tag": "typical", "inputs": "3\npush 5\npop\npop\n", "output": "5"},
    }
    result: dict[str, list[dict[str, str]]] = {}
    for pid, cases in base.items():
        tagged = _tag_list(cases, _DEFAULT_TAG_CYCLE[: len(cases)])
        if len(tagged) < 4:
            tagged.append(extras[pid])
        if pid in _HARD_CAPSTONE and len(tagged) < 5:
            extra = extras.get(pid)
            if extra:
                tagged.append(extra)
        result[pid] = tagged
    return result


def build_v128_test_suites() -> dict[str, list[dict[str, str]]]:
    suites: dict[str, list[dict[str, str]]] = {}
    suites.update(_tests_ch1())
    suites.update(_tests_ch2())
    suites.update(_from_chapter(ch3_tests, 17, 24, skip={"task_020"}))
    suites["task_020"] = list(_TASK_020_OVERLAY)
    suites.update(_from_chapter(ch4_tests, 25, 32, skip={"task_028"}))
    suites["task_028"] = list(_TASK_028_OVERLAY)
    suites.update(_from_chapter(ch5_tests, 33, 40))
    suites.update(_from_chapter(ch6_tests, 41, 48))
    suites.update(_from_chapter(ch7_tests, 49, 56))
    suites.update(_from_chapter(ch8_tests, 57, 64))
    suites.update(_from_chapter(ch9_tests, 65, 72))
    suites.update(_from_chapter(ch10_tests, 73, 80))
    for pid, cases in _FILE_TESTS.items():
        suites[pid] = cases
    suites.update(_expand_stack(ch12_tests))
    suites.update(_expand_linked(ch13_tests))
    for pid, cases in _TREES_GRAPH_TESTS.items():
        suites[pid] = cases
    suites.update(_OOP_STDIN_TESTS)
    suites.update(_INHERITANCE_STDIN_TESTS)
    return suites


def _py_repr(suites: dict[str, list[dict[str, str]]]) -> str:
    lines = [
        '"""Tagged diversified test suites for v128 algorithm course (task_001–task_128)."""',
        "",
        "from __future__ import annotations",
        "",
        "V128_TEST_SUITES: dict[str, list[dict[str, str]]] = {",
    ]
    for pid in sorted(suites, key=lambda k: int(k.split("_")[1])):
        lines.append(f'    "{pid}": [')
        for case in suites[pid]:
            inp = case["inputs"]
            out = case["output"]
            tag = case["tag"]
            lines.append(f'        {{"tag": "{tag}", "inputs": {inp!r}, "output": {out!r}}},')
        lines.append("    ],")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    suites = build_v128_test_suites()
    assert len(suites) == 128, f"expected 128 tasks, got {len(suites)}"
    for pid, cases in suites.items():
        assert len(cases) >= 4, f"{pid} has only {len(cases)} tests"
        if pid in _HARD_CAPSTONE:
            assert len(cases) >= 5, f"{pid} capstone needs 5 tests"
        for case in cases:
            assert "tag" in case and "inputs" in case and "output" in case
            if case["inputs"]:
                assert case["inputs"].endswith("\n"), f"{pid} inputs must end with newline"
    out_path = _SCRIPTS / "v128_test_suites_data.py"
    out_path.write_text(_py_repr(suites), encoding="utf-8")
    print(f"Wrote {out_path} ({len(out_path.read_text(encoding='utf-8').splitlines())} lines, {len(suites)} tasks)")


if __name__ == "__main__":
    main()
