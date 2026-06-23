PASCAL = """var i, n, x, pos: integer;
    a: array[1..100] of integer;
begin
  readln(n);

  for i := 1 to n do
    readln(a[i]);

  readln(x);

  pos := n + 1;

  for i := 1 to n do
    if (a[i] >= x) and (pos = n + 1) then
      pos := i;

  writeln(pos);
end."""

PYTHON = """n = int(input())
a = [int(input()) for _ in range(n)]

x = int(input())

pos = n + 1

for i in range(1, n + 1):
    if a[i - 1] >= x and pos == n + 1:
        pos = i

print(pos)"""

CPP = """#include <iostream>
#include <vector>

int main() {
    int n;
    std::cin >> n;

    std::vector<int> a(n);
    for (int i = 0; i < n; i++) {
        std::cin >> a[i];
    }

    int x;
    std::cin >> x;

    int pos = n + 1;

    for (int i = 0; i < n; i++) {
        if (a[i] >= x && pos == n + 1) {
            pos = i + 1;
        }
    }

    std::cout << pos;
    return 0;
}"""

CSHARP = """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int[] a = new int[n];

        for (int i = 0; i < n; i++) {
            a[i] = int.Parse(Console.ReadLine());
        }

        int x = int.Parse(Console.ReadLine());

        int pos = n + 1;

        for (int i = 0; i < n; i++) {
            if (a[i] >= x && pos == n + 1) {
                pos = i + 1;
            }
        }

        Console.WriteLine(pos);
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int[] a = new int[n];

        for (int i = 0; i < n; i++) {
            a[i] = sc.nextInt();
        }

        int x = sc.nextInt();

        int pos = n + 1;

        for (int i = 0; i < n; i++) {
            if (a[i] >= x && pos == n + 1) {
                pos = i + 1;
            }
        }

        System.out.println(pos);
    }
}"""
