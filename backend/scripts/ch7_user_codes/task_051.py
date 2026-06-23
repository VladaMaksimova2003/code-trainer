PASCAL = """function SumArray(a: array of integer; index: integer): integer;
begin
  if index = length(a) then
    SumArray := 0
  else
    SumArray := a[index] + SumArray(a, index + 1);
end;

var n, i: integer;
    a: array of integer;
begin
  readln(n);
  setlength(a, n);

  for i := 0 to n - 1 do
    readln(a[i]);

  writeln(SumArray(a, 0));
end."""

PYTHON = """def sum_array(arr, index):
    if index == len(arr):
        return 0
    return arr[index] + sum_array(arr, index + 1)

n = int(input())
arr = [int(input()) for _ in range(n)]

print(sum_array(arr, 0))"""

CPP = """#include <iostream>
#include <vector>

int sumArray(const std::vector<int>& arr, int index) {
    if (index == (int)arr.size()) return 0;
    return arr[index] + sumArray(arr, index + 1);
}

int main() {
    int n;
    std::cin >> n;

    std::vector<int> arr(n);
    for (int i = 0; i < n; i++) {
        std::cin >> arr[i];
    }

    std::cout << sumArray(arr, 0);
    return 0;
}"""

CSHARP = """using System;

class Program {
    static int SumArray(int[] arr, int index) {
        if (index == arr.Length) return 0;
        return arr[index] + SumArray(arr, index + 1);
    }

    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int[] arr = new int[n];

        for (int i = 0; i < n; i++) {
            arr[i] = int.Parse(Console.ReadLine());
        }

        Console.WriteLine(SumArray(arr, 0));
    }
}"""

JAVA = """import java.util.*;

class Main {
    static int sumArray(int[] arr, int index) {
        if (index == arr.length) return 0;
        return arr[index] + sumArray(arr, index + 1);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int[] arr = new int[n];

        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }

        System.out.println(sumArray(arr, 0));
    }
}"""
