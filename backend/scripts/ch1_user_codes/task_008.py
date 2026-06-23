PASCAL = """var n, i, grade, best, total, passed: integer;
begin
  readln(n);

  total := 0;
  passed := 0;

  readln(best);
  total := total + best;

  if best >= 3 then
    passed := passed + 1;

  for i := 2 to n do
  begin
    readln(grade);

    total := total + grade;

    if grade > best then
      best := grade;

    if grade >= 3 then
      passed := passed + 1;
  end;

  writeln(best, ' ', total div n, ' ', passed);
end."""

PYTHON = """n = int(input())
grades = [int(input()) for _ in range(n)]

best = grades[0]
total = 0
passed = 0

for grade in grades:
    total += grade

    if grade > best:
        best = grade

    if grade >= 3:
        passed += 1

print(best, total // n, passed)"""

CPP = """#include <iostream>
#include <vector>

int main() {
    int n;
    std::cin >> n;

    std::vector<int> grades(n);

    for (int i = 0; i < n; i++) {
        std::cin >> grades[i];
    }

    int best = grades[0];
    int total = 0;
    int passed = 0;

    for (int grade : grades) {
        total += grade;

        if (grade > best) {
            best = grade;
        }

        if (grade >= 3) {
            passed++;
        }
    }

    std::cout << best << ' ' << total / n << ' ' << passed;
    return 0;
}"""

CSHARP = """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());

        int[] grades = new int[n];

        for (int i = 0; i < n; i++) {
            grades[i] = int.Parse(Console.ReadLine());
        }

        int best = grades[0];
        int total = 0;
        int passed = 0;

        foreach (int grade in grades) {
            total += grade;

            if (grade > best) {
                best = grade;
            }

            if (grade >= 3) {
                passed++;
            }
        }

        Console.WriteLine($"{best} {total / n} {passed}");
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int[] grades = new int[n];

        for (int i = 0; i < n; i++) {
            grades[i] = sc.nextInt();
        }

        int best = grades[0];
        int total = 0;
        int passed = 0;

        for (int grade : grades) {
            total += grade;

            if (grade > best) {
                best = grade;
            }

            if (grade >= 3) {
                passed++;
            }
        }

        System.out.println(best + " " + (total / n) + " " + passed);
    }
}"""
