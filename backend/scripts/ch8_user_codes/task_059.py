PASCAL = """var n, i, j, minIndex, temp: integer;
    a: array[0..99] of integer;
begin
  readln(n);

  for i := 0 to n - 1 do
    readln(a[i]);

  for i := 0 to n - 1 do
  begin
    minIndex := i;

    for j := i + 1 to n - 1 do
      if a[j] < a[minIndex] then
        minIndex := j;

    temp := a[i];
    a[i] := a[minIndex];
    a[minIndex] := temp;
  end;

  for i := 0 to n - 1 do
    write(a[i], ' ');
end."""

PYTHON = """n = int(input())
a = [int(input()) for _ in range(n)]

for i in range(n):
    min_index = i

    for j in range(i + 1, n):
        if a[j] < a[min_index]:
            min_index = j

    a[i], a[min_index] = a[min_index], a[i]

print(*a)"""

CPP = """#include <iostream>
#include <vector>

int main() {
    int n;
    std::cin >> n;

    std::vector<int> a(n);

    for (int i = 0; i < n; i++) {
        std::cin >> a[i];
    }

    for (int i = 0; i < n; i++) {
        int minIndex = i;

        for (int j = i + 1; j < n; j++) {
            if (a[j] < a[minIndex]) {
                minIndex = j;
            }
        }

        std::swap(a[i], a[minIndex]);
    }

    for (int x : a) {
        std::cout << x << ' ';
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

        for (int i = 0; i < n; i++) {
            int minIndex = i;

            for (int j = i + 1; j < n; j++) {
                if (a[j] < a[minIndex]) {
                    minIndex = j;
                }
            }

            int temp = a[i];
            a[i] = a[minIndex];
            a[minIndex] = temp;
        }

        foreach (int x in a) {
            Console.Write(x + " ");
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

        for (int i = 0; i < n; i++) {
            int minIndex = i;

            for (int j = i + 1; j < n; j++) {
                if (a[j] < a[minIndex]) {
                    minIndex = j;
                }
            }

            int temp = a[i];
            a[i] = a[minIndex];
            a[minIndex] = temp;
        }

        for (int x : a) {
            System.out.print(x + " ");
        }
    }
}"""
