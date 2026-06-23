PASCAL = """var i, n: integer;
    a: array[1..100] of integer;
begin
  readln(n);

  for i := 1 to n do
    readln(a[i]);

  for i := n downto 1 do
    write(a[i], ' ');
end."""

PYTHON = """n = int(input())
a = [int(input()) for _ in range(n)]

for x in reversed(a):
    print(x, end=' ')"""

CPP = """#include <iostream>
#include <vector>

int main() {
    int n;
    std::cin >> n;

    std::vector<int> a(n);
    for (int i = 0; i < n; i++) {
        std::cin >> a[i];
    }

    for (int i = n - 1; i >= 0; i--) {
        std::cout << a[i] << ' ';
    }

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

        for (int i = n - 1; i >= 0; i--) {
            Console.Write(a[i] + " ");
        }
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

        for (int i = n - 1; i >= 0; i--) {
            System.out.print(a[i] + " ");
        }
    }
}"""
