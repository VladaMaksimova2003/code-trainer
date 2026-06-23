PASCAL = """function MaxValue(a: array of integer): integer;
var i, best: integer;
begin
  best := a[0];

  for i := 1 to length(a) - 1 do
    if a[i] > best then
      best := a[i];

  MaxValue := best;
end;

function AverageValue(a: array of integer): integer;
var i, total: integer;
begin
  total := 0;

  for i := 0 to length(a) - 1 do
    total := total + a[i];

  AverageValue := total div length(a);
end;

function CountPositive(a: array of integer): integer;
var i, count: integer;
begin
  count := 0;

  for i := 0 to length(a) - 1 do
    if a[i] > 0 then
      count := count + 1;

  CountPositive := count;
end;

var n, i: integer;
    a: array of integer;
begin
  readln(n);
  setlength(a, n);

  for i := 0 to n - 1 do
    readln(a[i]);

  writeln(MaxValue(a), ' ', AverageValue(a), ' ', CountPositive(a));
end."""

PYTHON = """def max_value(arr):
    best = arr[0]

    for value in arr:
        if value > best:
            best = value

    return best


def average_value(arr):
    total = 0

    for value in arr:
        total += value

    return total // len(arr)


def count_positive(arr):
    count = 0

    for value in arr:
        if value > 0:
            count += 1

    return count


n = int(input())
arr = [int(input()) for _ in range(n)]

print(max_value(arr), average_value(arr), count_positive(arr))"""

CPP = """#include <iostream>
#include <vector>

int maxValue(const std::vector<int>& arr) {
    int best = arr[0];

    for (int value : arr) {
        if (value > best) {
            best = value;
        }
    }

    return best;
}

int averageValue(const std::vector<int>& arr) {
    int total = 0;

    for (int value : arr) {
        total += value;
    }

    return total / static_cast<int>(arr.size());
}

int countPositive(const std::vector<int>& arr) {
    int count = 0;

    for (int value : arr) {
        if (value > 0) {
            count++;
        }
    }

    return count;
}

int main() {
    int n;
    std::cin >> n;

    std::vector<int> arr(n);

    for (int i = 0; i < n; i++) {
        std::cin >> arr[i];
    }

    std::cout << maxValue(arr) << ' '
              << averageValue(arr) << ' '
              << countPositive(arr);

    return 0;
}"""

CSHARP = """using System;

class Program {
    static int MaxValue(int[] arr) {
        int best = arr[0];

        foreach (int value in arr) {
            if (value > best) {
                best = value;
            }
        }

        return best;
    }

    static int AverageValue(int[] arr) {
        int total = 0;

        foreach (int value in arr) {
            total += value;
        }

        return total / arr.Length;
    }

    static int CountPositive(int[] arr) {
        int count = 0;

        foreach (int value in arr) {
            if (value > 0) {
                count++;
            }
        }

        return count;
    }

    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int[] arr = new int[n];

        for (int i = 0; i < n; i++) {
            arr[i] = int.Parse(Console.ReadLine());
        }

        Console.WriteLine(
            $"{MaxValue(arr)} {AverageValue(arr)} {CountPositive(arr)}"
        );
    }
}"""

JAVA = """import java.util.*;

class Main {
    static int maxValue(int[] arr) {
        int best = arr[0];

        for (int value : arr) {
            if (value > best) {
                best = value;
            }
        }

        return best;
    }

    static int averageValue(int[] arr) {
        int total = 0;

        for (int value : arr) {
            total += value;
        }

        return total / arr.length;
    }

    static int countPositive(int[] arr) {
        int count = 0;

        for (int value : arr) {
            if (value > 0) {
                count++;
            }
        }

        return count;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int[] arr = new int[n];

        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }

        System.out.println(
            maxValue(arr) + " " + averageValue(arr) + " " + countPositive(arr)
        );
    }
}"""
