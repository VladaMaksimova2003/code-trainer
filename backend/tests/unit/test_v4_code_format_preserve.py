from application.curriculum.content.v4_code_format import (
    format_reference_code,
    preserve_source_layout,
)

PRETTY_PYTHON = """n = int(input())
sales = [int(input()) for _ in range(n)]

total = 0

for sale in sales:
    total += sale

print(total)"""


def test_preserve_source_layout_keeps_blank_lines():
    assert preserve_source_layout(PRETTY_PYTHON) == PRETTY_PYTHON


def test_format_reference_code_does_not_strip_blank_lines():
    assert format_reference_code(PRETTY_PYTHON, "python") == PRETTY_PYTHON


PRETTY_CPP = """#include <iostream>
#include <vector>
int main(){
  int n; std::cin >> n;
  std::vector<int> sales(n);
  for(int i = 0; i < n; i++) std::cin >> sales[i];
  int total = 0;
  for(int sale : sales) total += sale;
  std::cout << total;
  return 0;
}"""


def test_format_reference_code_preserves_cpp_layout():
    assert format_reference_code(PRETTY_CPP, "cpp") == PRETTY_CPP


def test_format_reference_code_preserves_csharp_layout():
    code = "using System;\nclass Program{\nstatic void Main(){\n  Console.WriteLine(1);\n}}"
    assert format_reference_code(code, "csharp") == code


def test_format_reference_code_still_expands_single_line_minified():
    one_liner = "n = int(input())\ntotal = 0\nfor i in range(n): total += int(input())\nprint(total)"
    out = format_reference_code(one_liner, "python")
    assert "\n" in out
    assert "for i in range(n):" in out
