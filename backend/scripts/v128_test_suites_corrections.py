"""Targeted fixes for mis-generated suites in v128_test_suites_data.py."""

from __future__ import annotations

from v128_test_matrix import tc

# Overrides merged after base V128_TEST_SUITES load.
V128_TEST_CORRECTIONS: dict[str, list[dict[str, str]]] = {
    "task_002": [
        tc("typical", "5 12\n8\n3\n12\n5\n9\n", "3"),
        tc("not_found", "3 7\n1\n2\n3\n", "0"),
        tc("duplicate", "4 5\n5\n5\n1\n2\n", "1"),
        tc("single", "1 9\n9\n", "1"),
    ],
    "task_009": [
        tc("typical", "3 7 2", "7"),
        tc("typical", "1 5 3", "5"),
        tc("negative", "-1 -5 -2", "-1"),
        tc("all_equal", "5 5 5", "5"),
    ],
    "task_010": [
        tc("typical", "-5", "freezing"),
        tc("typical", "15", "normal"),
        tc("typical", "30", "hot"),
        tc("boundary", "40", "danger"),
    ],
    "task_011": [
        tc("typical", "3 4 5", "scalene"),
        tc("all_equal", "2 2 2", "equilateral"),
        tc("duplicate", "3 3 5", "isosceles"),
        tc("invalid", "1 2 4", "invalid"),
    ],
    "task_012": [
        tc("typical", "29 2 2024", "valid"),
        tc("invalid", "31 4 2023", "invalid"),
        tc("invalid", "15 13 2023", "invalid"),
        tc("boundary", "28 2 2023", "valid"),
    ],
    "task_013": [
        tc("typical", "95", "excellent"),
        tc("typical", "75", "good"),
        tc("typical", "55", "satisfactory"),
        tc("negative", "40", "retry"),
        tc("invalid", "150", "invalid"),
    ],
    "task_014": [
        tc("typical", "12", "winter"),
        tc("typical", "4", "spring"),
        tc("typical", "7", "summer"),
        tc("invalid", "13", "invalid"),
    ],
    "task_015": [
        tc("typical", "25000 1 1", "30"),
        tc("typical", "3000 0 0", "0"),
        tc("typical", "10000 0 1", "18"),
        tc("invalid", "-1 0 0", "invalid"),
    ],
    "task_016": [
        tc("typical", "25 35000 10000 700", "accepted"),
        tc("typical", "20 25000 8000 600", "review"),
        tc("negative", "17 10000 5000 400", "rejected"),
        tc("boundary", "18 30000 10000 650", "accepted"),
    ],
    "task_017": [
        tc("typical", "2\n9\n1\n7\n0\n", "19"),
        tc("single", "10\n0\n", "10"),
        tc("negative", "-5\n-1\n-8\n-2\n0\n", "-16"),
    ],
    "task_018": [
        tc("typical", "5 7\n2\n9\n1\n7\n7\n", "4"),
        tc("not_found", "3 5\n1\n2\n3\n", "0"),
        tc("single", "1 12\n12\n", "1"),
        tc("duplicate", "4 7\n7\n7\n1\n7\n", "1"),
    ],
    "task_019": [
        tc("typical", "7\n", "yes"),
        tc("typical", "9\n", "no"),
        tc("single", "2\n", "yes"),
        tc("boundary", "1\n", "no"),
    ],
    "task_020": [
        tc("typical", "1\n2\n-1\n3\n0\n", "6"),
        tc("zero_empty", "-5\n0\n", "0"),
        tc("single", "2\n0\n", "2"),
    ],
    "task_021": [
        tc("typical", "3\n", "3 6 9"),
        tc("single", "1\n", "1"),
        tc("boundary", "2\n", "2 4"),
        tc("typical", "4\n", "4 8 12 16"),
    ],
    "task_022": [
        tc("typical", "5 7\n2\n9\n1\n7\n7\n", "5"),
        tc("not_found", "3 5\n1\n2\n3\n", "0"),
        tc("duplicate", "4 7\n7\n7\n1\n7\n", "4"),
        tc("single", "1 3\n3\n", "1"),
    ],
    "task_023": [
        tc("typical", "5\n1\n2\n1\n9\n1\n", "0 3 1 0 0 0 0 0 0 1 "),
        tc("zero_empty", "3\n0\n0\n0\n", "3 0 0 0 0 0 0 0 0 0 "),
        tc("typical", "4\n9\n8\n7\n6\n", "0 0 0 0 0 0 1 1 1 1 "),
    ],
    "task_024": [
        tc("typical", "5\n2\n9\n1\n7\n4\n", "1 9 23 4"),
        tc("single", "1\n10\n", "10 10 10 10"),
        tc("negative", "4\n-5\n-1\n-8\n-2\n", "-8 -1 -16 -4"),
        tc("all_equal", "3\n5\n5\n5\n", "5 5 15 5"),
        tc("zero_empty", "0\n", "invalid"),
    ],
    "task_026": [
        tc("typical", "5 2\n1\n2\n3\n4\n5\n", "4 5 1 2 3"),
        tc("single", "1 3\n10\n", "10"),
        tc("boundary", "3 1\n1\n2\n3\n", "3 1 2"),
        tc("boundary", "4 4\n1\n2\n3\n4\n", "1 2 3 4"),
    ],
    "task_025": [
        tc("typical", "4\n2\n9\n1\n7\n", "7 1 9 2"),
        tc("single", "1\n10\n", "10"),
        tc("negative", "4\n-5\n-1\n-8\n-2\n", "-2 -8 -1 -5"),
    ],
    "task_027": [
        tc("typical", "4\n1\n2\n3\n4\n2\n", "1 3 4"),
        tc("single", "1\n10\n1\n", ""),
        tc("invalid", "3\n5\n6\n7\n5\n", "invalid"),
    ],
    "task_028": [
        tc("typical", "3\n1\n2\n3\n2 9\n", "1 9 2 3"),
        tc("single", "1\n10\n1 5\n", "5 10"),
        tc("invalid", "2\n1\n2\n5 9\n", "invalid"),
    ],
    "task_029": [
        tc("typical", "2\n1\n2\n2\n3\n4\n", "1 2 3 4"),
        tc("single", "1\n10\n1\n20\n", "10 20"),
        tc("zero_empty", "3\n4\n5\n6\n0\n", "4 5 6"),
    ],
    "task_030": [
        tc("typical", "4\n1\n2\n3\n4\n", "no"),
        tc("duplicate", "3\n1\n2\n2\n", "yes"),
        tc("duplicate", "5\n1\n2\n3\n4\n1\n", "yes"),
    ],
    "task_031": [
        tc("typical", "3 3\n1 3 5\n2 4 6\n", "1 2 3 4 5 6"),
        tc("typical", "2 2\n1 2\n3 4\n", "1 2 3 4"),
        tc("typical", "1 3\n5\n1 2 3\n", "1 2 3 5"),
        tc("negative", "2 2\n-5 -1\n-3 -2\n", "-5 -3 -2 -1"),
    ],
    "task_032": [
        tc("typical", "4\n1\n3\n5\n7\n4\n", "3"),
        tc("boundary", "3\n1\n2\n3\n0\n", "1"),
        tc("single", "1\n10\n5\n", "1"),
    ],
    "task_033": [
        tc("typical", "hello\n", "5"),
        tc("single", "a\n", "1"),
        tc("typical", "abc def\n", "7"),
        tc("zero_empty", "\n", "0"),
    ],
    "task_034": [
        tc("typical", "abba\n", "abba"),
        tc("typical", "abc\n", "cba"),
        tc("typical", "aaabb\n", "bbaaa"),
    ],
    "task_035": [
        tc("typical", "abba\n", "yes"),
        tc("typical", "abc\n", "no"),
        tc("typical", "aaabb\n", "no"),
    ],
    "task_036": [
        tc("typical", "hello\nll\n", "3"),
        tc("not_found", "abc\nz\n", "0"),
        tc("typical", "ababab\nab\n", "1"),
    ],
    "task_037": [
        tc("typical", "one two three\n", "3"),
        tc("zero_empty", "\n", "0"),
        tc("single", "word\n", "1"),
    ],
    "task_038": [
        tc("typical", "listen\nsilent\n", "yes"),
        tc("typical", "abc\ncba\n", "yes"),
        tc("typical", "abc\nabd\n", "no"),
    ],
    "task_039": [
        tc("typical", "aaabb\n", "a3b2"),
        tc("typical", "abba\n", "a1b2a1"),
        tc("typical", "abc\n", "a1b1c1"),
    ],
    "task_040": [
        tc("typical", "abba\n", "4 1 2"),
        tc("typical", "abc\n", "3 1 1"),
        tc("typical", "a a\n", "3 2 2"),
    ],
    "task_042": [
        tc("typical", "5\n", "yes"),
        tc("typical", "4\n", "no"),
        tc("boundary", "2\n", "yes"),
        tc("boundary", "1\n", "no"),
    ],
    "task_044": [
        tc("typical", "2 3\n", "8"),
        tc("boundary", "5 0\n", "1"),
        tc("single", "3 1\n", "3"),
        tc("typical", "2 10\n", "1024"),
    ],
    "task_045": [
        tc("typical", "12345\n", "5"),
        tc("single", "7\n", "1"),
        tc("boundary", "1000\n", "4"),
        tc("zero_empty", "0\n", "1"),
    ],
    "task_054": [
        tc("typical", "5 3\n1\n3\n5\n7\n9\n", "2"),
        tc("not_found", "5 4\n1\n3\n5\n7\n9\n", "0"),
        tc("single", "1 5\n5\n", "1"),
        tc("boundary", "5 1\n1\n3\n5\n7\n9\n", "1"),
    ],
    "task_056": [
        tc("typical", "5\n5\n2\n9\n1\n7\n", "1 2 5 7 9"),
        tc("single", "1\n10\n", "10"),
        tc("negative", "3\n-1\n-3\n-2\n", "-3 -2 -1"),
        tc("edge_order", "4\n3\n1\n4\n2\n", "1 2 3 4"),
        tc("all_equal", "3\n4\n4\n4\n", "4 4 4"),
    ],
    "task_057": [
        tc("typical", "5 7\n2\n9\n1\n7\n7\n", "4"),
        tc("not_found", "3 5\n1\n2\n3\n", "0"),
        tc("single", "1 3\n3\n", "1"),
        tc("duplicate", "4 2\n2\n2\n1\n3\n", "1"),
    ],
    "task_058": [
        tc("typical", "5 9\n1\n3\n5\n7\n9\n", "5"),
        tc("not_found", "5 4\n1\n3\n5\n7\n9\n", "0"),
        tc("single", "1 3\n3\n", "1"),
        tc("boundary", "5 1\n1\n3\n5\n7\n9\n", "1"),
    ],
    "task_063": [
        tc("typical", "5\n5\n2\n9\n1\n7\n", "9 7 5 2 1"),
        tc("single", "1\n10\n", "10"),
        tc("negative", "3\n-1\n-3\n-2\n", "-1 -2 -3"),
        tc("all_equal", "3\n4\n4\n4\n", "4 4 4"),
    ],
    "task_064": [
        tc("typical", "5 2\n5\n2\n9\n1\n7\n", "9"),
        tc("single", "1 1\n10\n", "10"),
        tc("boundary", "5 1\n5\n2\n9\n1\n7\n", "9"),
        tc("typical", "4 3\n1\n3\n5\n7\n", "5"),
        tc("not_found", "4 10\n1\n3\n5\n7\n", "0"),
    ],
    "task_065": [
        tc("typical", "4\n2\n9\n1\n7\n", "7"),
        tc("duplicate", "3\n5\n5\n1\n", "5"),
        tc("single", "1\n10\n", "10"),
        tc("negative", "4\n-5\n-1\n-8\n-2\n", "-2"),
    ],
    "task_066": [
        tc("typical", "4\n2\n9\n1\n7\n", "4"),
        tc("single", "1\n10\n", "10"),
        tc("negative", "3\n-6\n0\n6\n", "0"),
        tc("boundary", "2\n3\n7\n", "5"),
    ],
    "task_067": [
        tc("typical", "5\n2\n9\n1\n7\n", "7"),
        tc("single", "1\n10\n", "10"),
        tc("boundary", "4\n1\n3\n5\n7\n", "4"),
        tc("typical", "3\n1\n3\n5\n", "3"),
    ],
    "task_068": [
        tc("typical", "5 7\n5\n2\n9\n1\n7\n7\n", "2"),
        tc("not_found", "4 3\n1\n2\n3\n4\n", "0"),
        tc("zero_empty", "3 0\n1\n2\n3\n", "3"),
        tc("duplicate", "4 2\n2\n2\n1\n3\n", "3"),
    ],
    "task_069": [
        tc("typical", "4\n2\n9\n1\n7\n", "8"),
        tc("single", "1\n10\n", "0"),
        tc("negative", "3\n-5\n-1\n-8\n", "14"),
        tc("all_equal", "3\n5\n5\n5\n", "0"),
    ],
    "task_070": [
        tc("typical", "5 3\n5\n2\n9\n1\n7\n", "9 7 5"),
        tc("single", "1 1\n10\n", "10"),
        tc("boundary", "4 2\n1\n2\n3\n4\n", "4 3"),
        tc("duplicate", "5 2\n5\n5\n1\n2\n3\n", "5 5"),
    ],
    "task_071": [
        tc("typical", "4\n2\n9\n-1\n7\n", "18 -1"),
        tc("negative", "3\n-5\n-1\n-8\n", "0 -14"),
        tc("zero_empty", "3\n0\n0\n0\n", "0 0"),
        tc("single", "1\n5\n", "5 0"),
    ],
    "task_072": [
        tc("typical", "5\n2\n9\n1\n7\n4\n", "1 9 23 4"),
        tc("single", "1\n10\n", "10 10 10 10"),
        tc("negative", "3\n-1\n-3\n-2\n", "-3 -1 -6 -2"),
        tc("all_equal", "3\n4\n4\n4\n", "4 4 12 4"),
        tc("zero_empty", "0\n", "invalid"),
    ],
}
