PASCAL = """var n, i, x, total: integer;
begin
  readln(n);
  total := 0;

  for i := 1 to n do
  begin
    readln(x);
    total := total + x;
  end;

  writeln(total);
end."""

PYTHON = """n = int(input())
total = 0

for _ in range(n):
    total += int(input())

print(total)"""

CPP = """#include <iostream>

int main() {
    int n, x, total = 0;
    std::cin >> n;

    for (int i = 0; i < n; i++) {
        std::cin >> x;
        total += x;
    }

    std::cout << total;
    return 0;
}"""

CSHARP = """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int total = 0;

        for (int i = 0; i < n; i++) {
            total += int.Parse(Console.ReadLine());
        }

        Console.WriteLine(total);
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int total = 0;

        for (int i = 0; i < n; i++) {
            total += sc.nextInt();
        }

        System.out.println(total);
    }
}"""
