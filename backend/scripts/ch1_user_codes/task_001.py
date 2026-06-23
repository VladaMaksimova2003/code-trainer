# Reference code — task_001 Поиск максимума в массиве
PASCAL = """var n, i, score, best: integer;
begin
  readln(n);
  best := -1000000000;

  for i := 1 to n do
  begin
    readln(score);
    if score > best then
      best := score;
  end;

  writeln(best);
end."""

PYTHON = """n = int(input())
best = None

for _ in range(n):
    score = int(input())
    if best is None or score > best:
        best = score

print(best)"""

CPP = """#include <iostream>
#include <climits>

int main() {
    int n;
    std::cin >> n;

    int best = INT_MIN;

    for (int i = 0; i < n; i++) {
        int score;
        std::cin >> score;
        if (score > best) {
            best = score;
        }
    }

    std::cout << best;
    return 0;
}"""

CSHARP = """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int best = int.MinValue;

        for (int i = 0; i < n; i++) {
            int score = int.Parse(Console.ReadLine());
            if (score > best) {
                best = score;
            }
        }

        Console.WriteLine(best);
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int best = Integer.MIN_VALUE;

        for (int i = 0; i < n; i++) {
            int score = sc.nextInt();
            if (score > best) {
                best = score;
            }
        }

        System.out.println(best);
    }
}"""
