PASCAL = """var i, n, k, idx: integer;
    a: array[1..100] of integer;
begin
  readln(n, k);

  for i := 1 to n do
    readln(a[i]);

  if n > 0 then
    k := k mod n
  else
    k := 0;

  for i := 1 to n do
  begin
    idx := i - k;

    if idx < 1 then
      idx := idx + n;

    write(a[idx], ' ');
  end;
end."""

PYTHON = """parts = input().split()
n, k = int(parts[0]), int(parts[1])
a = [int(input()) for _ in range(n)]

if n > 0:
    k %= n
    if k:
        a = a[-k:] + a[:-k]

print(*a)"""

CPP = """#include <iostream>
#include <vector>

int main() {
    int n, k;
    std::cin >> n >> k;

    std::vector<int> a(n);
    for (int i = 0; i < n; i++) {
        std::cin >> a[i];
    }

    if (n > 0) {
        k %= n;
        if (k > 0) {
            std::vector<int> b(n);
            for (int i = 0; i < n; i++) {
                b[i] = a[(i - k + n) % n];
            }
            a = b;
        }
    }

    for (int i = 0; i < n; i++) {
        if (i > 0) {
            std::cout << ' ';
        }
        std::cout << a[i];
    }

    return 0;
}"""

CSHARP = """using System;

class Program {
    static void Main() {
        string[] parts = Console.ReadLine().Split();
        int n = int.Parse(parts[0]);
        int k = int.Parse(parts[1]);
        int[] a = new int[n];

        for (int i = 0; i < n; i++) {
            a[i] = int.Parse(Console.ReadLine());
        }

        if (n > 0) {
            k %= n;
            if (k > 0) {
                int[] b = new int[n];
                for (int i = 0; i < n; i++) {
                    b[i] = a[(i - k + n) % n];
                }
                a = b;
            }
        }

        Console.WriteLine(string.Join(" ", a));
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int k = sc.nextInt();
        int[] a = new int[n];

        for (int i = 0; i < n; i++) {
            a[i] = sc.nextInt();
        }

        if (n > 0) {
            k %= n;
            if (k > 0) {
                int[] b = new int[n];
                for (int i = 0; i < n; i++) {
                    b[i] = a[(i - k + n) % n];
                }
                a = b;
            }
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) {
                sb.append(' ');
            }
            sb.append(a[i]);
        }
        System.out.print(sb);
    }
}"""
