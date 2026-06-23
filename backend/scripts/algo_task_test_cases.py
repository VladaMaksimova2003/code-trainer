"""Authoritative test cases for the 128-task algorithm-syntax course."""
from __future__ import annotations

TEST_CASES_BY_NUM: dict[int, list[dict[str, str]]] = {
    1:     [
        {
            "inputs": "5 2 9",
            "output": "9"
        },
        {
            "inputs": "5\n2\n9\n",
            "output": "9"
        },
        {
            "inputs": "4 -5 10",
            "output": "10"
        },
        {
            "inputs": "4\n-5\n10\n",
            "output": "10"
        }
    ],
    2:     [
        {
            "inputs": "5 12 8 3 12 5 9",
            "output": "3"
        },
        {
            "inputs": "3 7 1 2 3",
            "output": "0"
        },
        {
            "inputs": "4 5 5 5 1 2",
            "output": "1"
        },
        {
            "inputs": "3 7 2",
            "output": "0"
        }
    ],
    3:     [
        {
            "inputs": "5 2 9",
            "output": "9"
        },
        {
            "inputs": "5\n2\n9\n",
            "output": "9"
        },
        {
            "inputs": "4 -5 10",
            "output": "10"
        },
        {
            "inputs": "4\n-5\n10\n",
            "output": "10"
        }
    ],
    4:     [
        {
            "inputs": "5 2",
            "output": "7"
        },
        {
            "inputs": "5\n2\n",
            "output": "7"
        },
        {
            "inputs": "1 10",
            "output": "1"
        },
        {
            "inputs": "1\n10\n",
            "output": "1"
        }
    ],
    5:     [
        {
            "inputs": "5 2",
            "output": "7"
        },
        {
            "inputs": "5\n2\n",
            "output": "7"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "1\n10\n",
            "output": "10"
        }
    ],
    6:     [
        {
            "inputs": "5 2",
            "output": "7"
        },
        {
            "inputs": "5\n2\n",
            "output": "7"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "1\n10\n",
            "output": "10"
        }
    ],
    7:     [
        {
            "inputs": "5 2",
            "output": "7"
        },
        {
            "inputs": "5\n2\n",
            "output": "7"
        },
        {
            "inputs": "1 10",
            "output": "11"
        },
        {
            "inputs": "1\n10\n",
            "output": "11"
        }
    ],
    8:     [
        {
            "inputs": "5 2 9",
            "output": "16"
        },
        {
            "inputs": "5\n2\n9\n",
            "output": "16"
        },
        {
            "inputs": "4 -5 10",
            "output": "9"
        },
        {
            "inputs": "4\n-5\n10\n",
            "output": "9"
        }
    ],
    9:     [
        {
            "inputs": "5 12 8 3 12 5 9",
            "output": "12"
        },
        {
            "inputs": "3 7 1 2 3",
            "output": "7"
        },
        {
            "inputs": "4 5 5 5 1 2",
            "output": "5"
        },
        {
            "inputs": "3 7 2",
            "output": "7"
        }
    ],
    10:     [
        {
            "inputs": "5",
            "output": "normal"
        },
        {
            "inputs": "5\n",
            "output": "normal"
        },
        {
            "inputs": "1",
            "output": "normal"
        },
        {
            "inputs": "1\n",
            "output": "normal"
        }
    ],
    11:     [
        {
            "inputs": "5 12 8 3 12 5 9",
            "output": "12"
        },
        {
            "inputs": "3 7 1 2 3",
            "output": "7"
        },
        {
            "inputs": "4 5 5 5 1 2",
            "output": "5"
        },
        {
            "inputs": "3 7 2",
            "output": "7"
        }
    ],
    12:     [
        {
            "inputs": "3 7 2",
            "output": "7"
        },
        {
            "inputs": "95",
            "output": "excellent"
        },
        {
            "inputs": "40",
            "output": "retry"
        }
    ],
    13:     [
        {
            "inputs": "5",
            "output": "fail"
        },
        {
            "inputs": "5\n",
            "output": "fail"
        },
        {
            "inputs": "1",
            "output": "fail"
        },
        {
            "inputs": "1\n",
            "output": "fail"
        }
    ],
    14:     [
        {
            "inputs": "3 7 2",
            "output": "7"
        },
        {
            "inputs": "95",
            "output": "excellent"
        },
        {
            "inputs": "40",
            "output": "retry"
        }
    ],
    15:     [
        {
            "inputs": "3 7 2",
            "output": "7"
        },
        {
            "inputs": "95",
            "output": "excellent"
        },
        {
            "inputs": "40",
            "output": "retry"
        }
    ],
    16:     [
        {
            "inputs": "3 7 2",
            "output": "7"
        },
        {
            "inputs": "95",
            "output": "excellent"
        },
        {
            "inputs": "40",
            "output": "retry"
        }
    ],
    17:     [
        {
            "inputs": "5 2",
            "output": "7"
        },
        {
            "inputs": "5\n2\n",
            "output": "7"
        },
        {
            "inputs": "1 10",
            "output": "11"
        },
        {
            "inputs": "1\n10\n",
            "output": "11"
        }
    ],
    18:     [
        {
            "inputs": "5 2",
            "output": "7"
        },
        {
            "inputs": "5\n2\n",
            "output": "7"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "1\n10\n",
            "output": "10"
        }
    ],
    19:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    20:     [
        {
            "inputs": "5 2",
            "output": "7"
        },
        {
            "inputs": "5\n2\n",
            "output": "7"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "1\n10\n",
            "output": "10"
        }
    ],
    21:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    22:     [
        {
            "inputs": "5 2",
            "output": "7"
        },
        {
            "inputs": "5\n2\n",
            "output": "7"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "1\n10\n",
            "output": "10"
        }
    ],
    23:     [
        {
            "inputs": "5 2",
            "output": "7"
        },
        {
            "inputs": "5\n2\n",
            "output": "7"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "1\n10\n",
            "output": "10"
        }
    ],
    24:     [
        {
            "inputs": "5 2",
            "output": "7"
        },
        {
            "inputs": "5\n2\n",
            "output": "7"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "1\n10\n",
            "output": "10"
        }
    ],
    25:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    26:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    27:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    28:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    29:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    30:     [
        {
            "inputs": "5 2",
            "output": "no"
        },
        {
            "inputs": "5\n2\n",
            "output": "no"
        },
        {
            "inputs": "1 10",
            "output": "no"
        },
        {
            "inputs": "1\n10\n",
            "output": "no"
        }
    ],
    31:     [
        {
            "inputs": "3 7 2",
            "output": "7"
        },
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        }
    ],
    32:     [
        {
            "inputs": "5 2",
            "output": "7"
        },
        {
            "inputs": "5\n2\n",
            "output": "7"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "1\n10\n",
            "output": "10"
        }
    ],
    33:     [
        {
            "inputs": "5 2",
            "output": "7"
        },
        {
            "inputs": "5\n2\n",
            "output": "7"
        },
        {
            "inputs": "1 10",
            "output": "11"
        },
        {
            "inputs": "1\n10\n",
            "output": "11"
        }
    ],
    34:     [
        {
            "inputs": "abba",
            "output": "yes"
        },
        {
            "inputs": "abc",
            "output": "no"
        },
        {
            "inputs": "aaabb",
            "output": "a3b2"
        }
    ],
    35:     [
        {
            "inputs": "abba",
            "output": "yes"
        },
        {
            "inputs": "abba\n",
            "output": "yes"
        },
        {
            "inputs": "abc",
            "output": "no"
        }
    ],
    36:     [
        {
            "inputs": "5 2",
            "output": "7"
        },
        {
            "inputs": "5\n2\n",
            "output": "7"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "1\n10\n",
            "output": "10"
        }
    ],
    37:     [
        {
            "inputs": "abba",
            "output": "yes"
        },
        {
            "inputs": "abc",
            "output": "no"
        },
        {
            "inputs": "aaabb",
            "output": "a3b2"
        }
    ],
    38:     [
        {
            "inputs": "abba",
            "output": "yes"
        },
        {
            "inputs": "abc",
            "output": "no"
        },
        {
            "inputs": "aaabb",
            "output": "a3b2"
        }
    ],
    39:     [
        {
            "inputs": "abba",
            "output": "yes"
        },
        {
            "inputs": "abc",
            "output": "no"
        },
        {
            "inputs": "aaabb",
            "output": "a3b2"
        }
    ],
    40:     [
        {
            "inputs": "5 2",
            "output": "7"
        },
        {
            "inputs": "5\n2\n",
            "output": "7"
        },
        {
            "inputs": "1 10",
            "output": "11"
        },
        {
            "inputs": "1\n10\n",
            "output": "11"
        }
    ],
    41:     [
        {
            "inputs": "3 7 2",
            "output": "7"
        },
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        }
    ],
    42:     [
        {
            "inputs": "3 7 2",
            "output": "7"
        },
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        }
    ],
    43:     [
        {
            "inputs": "3 7 2",
            "output": "7"
        },
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        }
    ],
    44:     [
        {
            "inputs": "3 7 2",
            "output": "7"
        },
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        }
    ],
    45:     [
        {
            "inputs": "3 7 2",
            "output": "7"
        },
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        }
    ],
    46:     [
        {
            "inputs": "3 7 2",
            "output": "7"
        },
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        }
    ],
    47:     [
        {
            "inputs": "3 7 2",
            "output": "7"
        },
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        }
    ],
    48:     [
        {
            "inputs": "3 7 2",
            "output": "7"
        },
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        }
    ],
    49:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    50:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    51:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    52:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    53:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    54:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    55:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    56:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    57:     [
        {
            "inputs": "5 2",
            "output": "7"
        },
        {
            "inputs": "5\n2\n",
            "output": "7"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "1\n10\n",
            "output": "10"
        }
    ],
    58:     [
        {
            "inputs": "5 2",
            "output": "7"
        },
        {
            "inputs": "5\n2\n",
            "output": "7"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "1\n10\n",
            "output": "10"
        }
    ],
    59:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    60:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    61:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    62:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    63:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    64:     [
        {
            "inputs": "5 2",
            "output": "7"
        },
        {
            "inputs": "5\n2\n",
            "output": "7"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "1\n10\n",
            "output": "10"
        }
    ],
    65:     [
        {
            "inputs": "5 2",
            "output": "7"
        },
        {
            "inputs": "5\n2\n",
            "output": "7"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "1\n10\n",
            "output": "10"
        }
    ],
    66:     [
        {
            "inputs": "5 2",
            "output": "7"
        },
        {
            "inputs": "5\n2\n",
            "output": "7"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "1\n10\n",
            "output": "10"
        }
    ],
    67:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    68:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    69:     [
        {
            "inputs": "red blue red",
            "output": "red 2"
        },
        {
            "inputs": "a b c",
            "output": "a 1"
        },
        {
            "inputs": "one one two",
            "output": "one 2"
        }
    ],
    70:     [
        {
            "inputs": "5 2",
            "output": "7"
        },
        {
            "inputs": "5\n2\n",
            "output": "7"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "1\n10\n",
            "output": "10"
        }
    ],
    71:     [
        {
            "inputs": "red blue red",
            "output": "red 2"
        },
        {
            "inputs": "a b c",
            "output": "a 1"
        },
        {
            "inputs": "one one two",
            "output": "one 2"
        }
    ],
    72:     [
        {
            "inputs": "5 2",
            "output": "7"
        },
        {
            "inputs": "5\n2\n",
            "output": "7"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "1\n10\n",
            "output": "10"
        }
    ],
    73:     [
        {
            "inputs": "red blue red",
            "output": "red 2"
        },
        {
            "inputs": "a b c",
            "output": "a 1"
        },
        {
            "inputs": "one one two",
            "output": "one 2"
        }
    ],
    74:     [
        {
            "inputs": "red blue red",
            "output": "red 2"
        },
        {
            "inputs": "a b c",
            "output": "a 1"
        },
        {
            "inputs": "one one two",
            "output": "one 2"
        }
    ],
    75:     [
        {
            "inputs": "red blue red",
            "output": "red 2"
        },
        {
            "inputs": "a b c",
            "output": "a 1"
        },
        {
            "inputs": "one one two",
            "output": "one 2"
        }
    ],
    76:     [
        {
            "inputs": "red blue red",
            "output": "red 2"
        },
        {
            "inputs": "a b c",
            "output": "a 1"
        },
        {
            "inputs": "one one two",
            "output": "one 2"
        }
    ],
    77:     [
        {
            "inputs": "red blue red",
            "output": "red 2"
        },
        {
            "inputs": "a b c",
            "output": "a 1"
        },
        {
            "inputs": "one one two",
            "output": "one 2"
        }
    ],
    78:     [
        {
            "inputs": "red blue red",
            "output": "red 2"
        },
        {
            "inputs": "a b c",
            "output": "a 1"
        },
        {
            "inputs": "one one two",
            "output": "one 2"
        }
    ],
    79:     [
        {
            "inputs": "red blue red",
            "output": "red 2"
        },
        {
            "inputs": "a b c",
            "output": "a 1"
        },
        {
            "inputs": "one one two",
            "output": "one 2"
        }
    ],
    80:     [
        {
            "inputs": "red blue red",
            "output": "red 2"
        },
        {
            "inputs": "a b c",
            "output": "a 1"
        },
        {
            "inputs": "one one two",
            "output": "one 2"
        }
    ],
    81:     [
        {
            "inputs": "5 12 8 3 12 5 9",
            "output": "54"
        },
        {
            "inputs": "3 7 1 2 3",
            "output": "16"
        },
        {
            "inputs": "4 5 5 5 1 2",
            "output": "22"
        },
        {
            "inputs": "3 7 2",
            "output": "12"
        }
    ],
    82:     [
        {
            "inputs": "5 12 8 3 12 5 9",
            "output": "54"
        },
        {
            "inputs": "3 7 1 2 3",
            "output": "16"
        },
        {
            "inputs": "4 5 5 5 1 2",
            "output": "22"
        },
        {
            "inputs": "3 7 2",
            "output": "12"
        }
    ],
    83:     [
        {
            "inputs": "5 12 8 3 12 5 9",
            "output": "54"
        },
        {
            "inputs": "3 7 1 2 3",
            "output": "16"
        },
        {
            "inputs": "4 5 5 5 1 2",
            "output": "22"
        },
        {
            "inputs": "3 7 2",
            "output": "12"
        }
    ],
    84:     [
        {
            "inputs": "5 12 8 3 12 5 9",
            "output": "54"
        },
        {
            "inputs": "3 7 1 2 3",
            "output": "16"
        },
        {
            "inputs": "4 5 5 5 1 2",
            "output": "22"
        },
        {
            "inputs": "3 7 2",
            "output": "12"
        }
    ],
    85:     [
        {
            "inputs": "5 12 8 3 12 5 9",
            "output": "54"
        },
        {
            "inputs": "3 7 1 2 3",
            "output": "16"
        },
        {
            "inputs": "4 5 5 5 1 2",
            "output": "22"
        },
        {
            "inputs": "3 7 2",
            "output": "12"
        }
    ],
    86:     [
        {
            "inputs": "5 12 8 3 12 5 9",
            "output": "54"
        },
        {
            "inputs": "3 7 1 2 3",
            "output": "16"
        },
        {
            "inputs": "4 5 5 5 1 2",
            "output": "22"
        },
        {
            "inputs": "3 7 2",
            "output": "12"
        }
    ],
    87:     [
        {
            "inputs": "5 12 8 3 12 5 9",
            "output": "54"
        },
        {
            "inputs": "3 7 1 2 3",
            "output": "16"
        },
        {
            "inputs": "4 5 5 5 1 2",
            "output": "22"
        },
        {
            "inputs": "3 7 2",
            "output": "12"
        }
    ],
    88:     [
        {
            "inputs": "5 12 8 3 12 5 9",
            "output": "54"
        },
        {
            "inputs": "3 7 1 2 3",
            "output": "16"
        },
        {
            "inputs": "4 5 5 5 1 2",
            "output": "22"
        },
        {
            "inputs": "3 7 2",
            "output": "12"
        }
    ],
    89:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    90:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    91:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    92:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    93:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    94:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    95:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    96:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    97:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    98:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    99:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    100:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    101:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    102:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    103:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    104:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    105:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    106:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    107:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    108:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    109:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    110:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    111:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    112:     [
        {
            "inputs": "5 2 9 1 7",
            "output": "19"
        },
        {
            "inputs": "1 10",
            "output": "10"
        },
        {
            "inputs": "4 -5 -1 -8 -2",
            "output": "-16"
        }
    ],
    113:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    114:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    115:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    116:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    117:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    118:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    119:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    120:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    121:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    122:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    123:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    124:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    125:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    126:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    127:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
    128:     [
        {
            "inputs": "demo",
            "output": "ok"
        },
        {
            "inputs": "empty",
            "output": "ok"
        },
        {
            "inputs": "edge",
            "output": "ok"
        }
    ],
}


def test_cases_for_task(task_num: int) -> list[dict[str, str]]:
    raw = TEST_CASES_BY_NUM.get(int(task_num)) or []
    return [dict(item) for item in raw if isinstance(item, dict)]
