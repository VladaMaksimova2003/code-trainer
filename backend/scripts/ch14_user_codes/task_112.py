PASCAL = """var x, total: integer;
begin
  total := 0;
  while not eof do
  begin
    readln(x);
    total := total + x;
  end;
  writeln(total);
end."""

PYTHON = """import sys

total = 0
for line in sys.stdin:
    line = line.strip()
    if line:
        total += int(line)
print(total)"""

CPP = """#include <iostream>

int main() {
    int x;
    long long total = 0;
    while (std::cin >> x) {
        total += x;
    }
    std::cout << total;
    return 0;
}"""

CSHARP = """using System;

class Program {
    static void Main() {
        long total = 0;
        string line;
        while ((line = Console.ReadLine()) != null) {
            line = line.Trim();
            if (line.Length > 0) {
                total += int.Parse(line);
            }
        }
        Console.WriteLine(total);
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long total = 0;
        while (sc.hasNext()) {
            total += sc.nextInt();
        }
        System.out.println(total);
    }
}"""
