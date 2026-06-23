# Reference code — task_006 Средняя загрузка сервера (целая часть)
PASCAL = """var n, i, load, total: integer;
begin
  readln(n);
  total := 0;

  for i := 1 to n do
  begin
    readln(load);
    total := total + load;
  end;

  writeln(total div n);
end."""

PYTHON = """n = int(input())
total = 0

for _ in range(n):
    total += int(input())

print(total // n)"""

CPP = """#include <iostream>

int main() {
    int n;
    std::cin >> n;

    int total = 0;

    for (int i = 0; i < n; i++) {
        int load;
        std::cin >> load;
        total += load;
    }

    std::cout << total / n;
    return 0;
}"""

CSHARP = """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int total = 0;

        for (int i = 0; i < n; i++) {
            int load = int.Parse(Console.ReadLine());
            total += load;
        }

        Console.WriteLine(total / n);
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

        System.out.println(total / n);
    }
}"""
