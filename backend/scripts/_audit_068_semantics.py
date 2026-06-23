import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from import_debug_fixes import norm, run_python

TESTS = [
    ("T1", "5 7\n5\n2\n9\n1\n7\n7\n", "2"),
    ("T2", "4 3\n1\n2\n3\n4\n", "0"),
    ("T3", "3 0\n1\n2\n3\n", "3"),
    ("T4", "4 2\n2\n2\n1\n3\n", "3"),
]
COUNT = """
n, x = map(int, input().split())
count = 0
for _ in range(n):
    v = int(input())
    if v == x:
        count += 1
print(count)
"""
SEARCH = """
n, x = map(int, input().split())
for i in range(n):
    v = int(input())
    if v == x:
        print(i + 1)
        break
else:
    print(0)
"""
print("count-equal-x vs DB/correction expected:")
for name, inp, exp in TESTS:
    got = norm(run_python(COUNT, inp))
    print(f"  {name}: exp={exp} count={got} {'OK' if got == exp else 'FAIL'}")
print("first-index search vs same expected:")
for name, inp, exp in TESTS:
    got = norm(run_python(SEARCH, inp))
    print(f"  {name}: exp={exp} search={got} {'OK' if got == exp else 'FAIL'}")
