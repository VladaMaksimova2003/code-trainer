FIXED_PASCAL = """var n, k, i, j, temp: integer;
    a: array[1..100] of integer;
begin
  readln(n);

  for i := 1 to n do
    readln(a[i]);

  readln(k);

  for i := 1 to n do
    for j := i + 1 to n do
      if a[j] > a[i] then
      begin
        temp := a[i];
        a[i] := a[j];
        a[j] := temp;
      end;

  if k > n then
    k := n;

  for i := 1 to k do
    write(a[i], ' ');
end."""

BUGGY_PASCAL = """var n, k, i: integer;
    a: array[1..100] of integer;
begin
  n := int(input());

  for i in range(n) do
    a[i] := int(input());

  k := int(input());

  a.sort(reverse=True);

  for i := 0 to k do
    print(a[i]);
end."""

FIXED_PYTHON = """n = int(input())
a = [int(input()) for _ in range(n)]
k = int(input())

a.sort(reverse=True)

for i in range(min(k, n)):
    print(a[i], end=' ')"""

BUGGY_PYTHON = """n = int.Parse(Console.ReadLine())
a = new int[n]

for i := 1 to n do:
    a[i] = int(input())

k = int(input())

a.Sort()
a.Reverse

for i in range(1, k + 1):
    Console.Write(a[i] + " ")"""

FIXED_CPP = """#include <iostream>
#include <vector>
#include <algorithm>

int main() {
    int n;
    std::cin >> n;

    std::vector<int> a(n);

    for (int i = 0; i < n; i++) {
        std::cin >> a[i];
    }

    int k;
    std::cin >> k;

    std::sort(a.begin(), a.end(), std::greater<int>());

    for (int i = 0; i < k && i < n; i++) {
        std::cout << a[i] << ' ';
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <vector>

int main() {
    int n = int(input());
    vector<int> a = new int[n];

    for i in range(n):
        cin >> a[i];

    int k;
    Console.ReadLine(k);

    a.sort(reverse=True);

    for (int i = 1; i <= k; i++) {
        cout << a[i] << " ";
    }

    return 0;
}"""

FIXED_CSHARP = """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int[] a = new int[n];

        for (int i = 0; i < n; i++) {
            a[i] = int.Parse(Console.ReadLine());
        }

        int k = int.Parse(Console.ReadLine());

        Array.Sort(a);
        Array.Reverse(a);

        for (int i = 0; i < k && i < n; i++) {
            Console.Write(a[i] + " ");
        }
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static void Main() {
        int n = int(input());
        int[] a = [];

        for i in range(n):
            a[i] = Console.ReadLine();

        int k = int(input());

        a.sort(reverse=True);

        for (int i = 1; i <= k; i++) {
            print(a[i]);
        }
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        Integer[] a = new Integer[n];

        for (int i = 0; i < n; i++) {
            a[i] = sc.nextInt();
        }

        int k = sc.nextInt();

        Arrays.sort(a, Collections.reverseOrder());

        for (int i = 0; i < k && i < n; i++) {
            System.out.print(a[i] + " ");
        }
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        int n = int(input());
        int[] a = [];

        for i in range(n):
            a[i] = Scanner.nextInt();

        int k = input();

        a.sort(reverse=True);

        for (Int i = 1; i <= k; i++) {
            Console.WriteLine(a[i]);
        }
    }
}"""
