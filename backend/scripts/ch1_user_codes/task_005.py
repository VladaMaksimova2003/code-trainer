# Reference code — task_005 Сумма выручки за период
PASCAL = """var n, i, sale, total: integer;
begin
  readln(n);
  total := 0;

  for i := 1 to n do
  begin
    readln(sale);
    total := total + sale;
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
    int n;
    std::cin >> n;

    int total = 0;

    for (int i = 0; i < n; i++) {
        int sale;
        std::cin >> sale;
        total += sale;
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
            int sale = int.Parse(Console.ReadLine());
            total += sale;
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
