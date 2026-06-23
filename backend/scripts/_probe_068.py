"""Probe task_068 correction test format."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from import_debug_fixes import run_python, norm

TESTS = [
    ("typical", "5 7\n5\n2\n9\n1\n7\n7\n", "2"),
    ("not_found", "4 3\n1\n2\n3\n4\n", "0"),
    ("zero_empty", "3 0\n1\n2\n3\n", "3"),
    ("duplicate", "4 2\n2\n2\n1\n3\n", "3"),
]

CANDIDATES = {
    "v1_nx_loop_n": """
n, x = map(int, input().split())
count = 0
for _ in range(n):
    v = int(input())
    if v == x:
        count += 1
print(count)
""",
    "v3_read_all_after_nx": """
n, x = map(int, input().split())
count = 0
while True:
    try:
        v = int(input())
    except EOFError:
        break
    if v == x:
        count += 1
print(count)
""",
    "v4_n6_typical": """
n, x = map(int, input().split())
count = 0
for _ in range(n):
    v = int(input())
    if v == x:
        count += 1
print(count)
""",
    "v5_count_nonzero_when_x0": """
n, x = map(int, input().split())
count = 0
for _ in range(n):
    v = int(input())
    if x == 0:
        if v != 0:
            count += 1
    elif v == x:
        count += 1
print(count)
""",
    "v6_n_then_x_separate": """
n = int(input())
vals = []
for _ in range(n):
    vals.append(int(input()))
x = int(input())
count = sum(1 for v in vals if v == x)
print(count)
""",
    "v7_fix_t1_n6": None,
}

# patch test1 with n=6
TESTS_N6 = list(TESTS)
TESTS_N6[0] = ("typical", "6 7\n5\n2\n9\n1\n7\n7\n", "2")

for name, code in CANDIDATES.items():
    if code is None:
        continue
    print("===", name)
    for tag, inp, exp in TESTS:
        got = run_python(code, inp)
        ok = norm(got) == norm(exp)
        print(f"  {tag}: {'OK' if ok else 'FAIL'} exp={exp!r} got={norm(got)!r}")
    print("  --- with n=6 fix on T1 ---")
    for tag, inp, exp in TESTS_N6:
        got = run_python(code, inp)
        ok = norm(got) == norm(exp)
        print(f"  {tag}: {'OK' if ok else 'FAIL'} exp={exp!r} got={norm(got)!r}")
