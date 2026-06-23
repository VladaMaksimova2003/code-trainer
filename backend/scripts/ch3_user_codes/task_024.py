PASCAL = """var n, i, x, total, mn, mx, avg: integer;
begin
  readln(n);

  if n <= 0 then
  begin
    writeln('invalid');
    exit;
  end;

  readln(x);
  total := x;
  mn := x;
  mx := x;

  for i := 2 to n do
  begin
    readln(x);
    total := total + x;

    if x < mn then
      mn := x;

    if x > mx then
      mx := x;
  end;

  avg := total div n;
  writeln(mn, ' ', mx, ' ', total, ' ', avg);
end."""

PYTHON = """n = int(input())

if n <= 0:
    print('invalid')
else:
    values = [int(input()) for _ in range(n)]
    mn = min(values)
    mx = max(values)
    total = sum(values)
    avg = total // n
    print(mn, mx, total, avg)"""

CPP = """#include <iostream>
#include <climits>

int main() {
    int n;
    std::cin >> n;

    if (n <= 0) {
        std::cout << "invalid";
        return 0;
    }

    int x;
    std::cin >> x;

    int total = x;
    int mn = x;
    int mx = x;

    for (int i = 2; i <= n; i++) {
        std::cin >> x;
        total += x;
        if (x < mn) mn = x;
        if (x > mx) mx = x;
    }

    int avg = total / n;
    std::cout << mn << ' ' << mx << ' ' << total << ' ' << avg;
    return 0;
}"""

CSHARP = """using System;
using System.Linq;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());

        if (n <= 0) {
            Console.WriteLine("invalid");
            return;
        }

        int[] values = new int[n];
        for (int i = 0; i < n; i++) {
            values[i] = int.Parse(Console.ReadLine());
        }

        int mn = values.Min();
        int mx = values.Max();
        int total = values.Sum();
        int avg = total / n;

        Console.WriteLine($"{mn} {mx} {total} {avg}");
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();

        if (n <= 0) {
            System.out.println("invalid");
            return;
        }

        int x = sc.nextInt();
        int total = x;
        int mn = x;
        int mx = x;

        for (int i = 2; i <= n; i++) {
            x = sc.nextInt();
            total += x;
            if (x < mn) mn = x;
            if (x > mx) mx = x;
        }

        int avg = total / n;
        System.out.println(mn + " " + mx + " " + total + " " + avg);
    }
}"""
