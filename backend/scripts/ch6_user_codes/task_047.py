FIXED_PASCAL = """function ArraySum(a: array of integer): integer;
var i, total: integer;
begin
  total := 0;

  for i := 0 to length(a) - 1 do
    total := total + a[i];

  ArraySum := total;
end;

var n, i: integer;
    a: array of integer;
begin
  readln(n);
  setlength(a, n);

  for i := 0 to n - 1 do
    readln(a[i]);

  writeln(ArraySum(a));
end."""

BUGGY_PASCAL = """function ArraySum(a: list[int]): integer;
var value, total: integer;
begin
  total = 0;

  foreach value in a do
    total += value;

  return total;
end;

var n: integer;
    a: array of integer;
begin
  n := int(input());
  a = [int(input()) for _ in range(n)];

  print(ArraySum(a));
end."""

FIXED_PYTHON = """def array_sum(arr):
    total = 0

    for value in arr:
        total += value

    return total

n = int(input())
arr = [int(input()) for _ in range(n)]

print(array_sum(arr))"""

BUGGY_PYTHON = """static int ArraySum(int[] arr) {
    int total = 0

    foreach (int value in arr) {
        total += value
    }

    return total
}

n = int(input())
arr = new int[n]

for i := 1 to n do:
    arr[i] = int(input())

print(ArraySum(arr))"""

FIXED_CPP = """#include <iostream>
#include <vector>

int arraySum(const std::vector<int>& arr) {
    int total = 0;

    for (int value : arr) {
        total += value;
    }

    return total;
}

int main() {
    int n;
    std::cin >> n;

    std::vector<int> arr(n);

    for (int i = 0; i < n; i++) {
        std::cin >> arr[i];
    }

    std::cout << arraySum(arr);
    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <vector>

def array_sum(arr):
    total := 0

    foreach value in arr:
        total += value

    return total

int main() {
    int n = int(input());
    vector<int> arr = new int[n];

    for i in range(n):
        cin >> arr[i];

    Console.WriteLine(array_sum(arr));
    return 0;
}"""

FIXED_CSHARP = """using System;

class Program {
    static int ArraySum(int[] arr) {
        int total = 0;

        foreach (int value in arr) {
            total += value;
        }

        return total;
    }

    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int[] arr = new int[n];

        for (int i = 0; i < n; i++) {
            arr[i] = int.Parse(Console.ReadLine());
        }

        Console.WriteLine(ArraySum(arr));
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    def array_sum(arr):
        total := 0

        for value in arr:
            total += value

        return total

    static void Main() {
        int n = int(input());
        int[] arr = [];

        for i in range(n):
            arr[i] = Console.ReadLine();

        print(array_sum(arr));
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    static int arraySum(int[] arr) {
        int total = 0;

        for (int value : arr) {
            total += value;
        }

        return total;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int[] arr = new int[n];

        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }

        System.out.println(arraySum(arr));
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    def array_sum(arr):
        total := 0

        for value in arr:
            total += value

        return total

    public static void main(String[] args) {
        int n = int(input());
        int[] arr = [];

        for i in range(n):
            arr[i] = Scanner.nextInt();

        Console.WriteLine(array_sum(arr));
    }
}"""
