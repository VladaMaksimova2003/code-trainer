FIXED_PASCAL = """procedure QuickSort(var a: array of integer; left, right: integer);
var i, j, pivot, temp: integer;
begin
  i := left;
  j := right;
  pivot := a[(left + right) div 2];

  while i <= j do
  begin
    while a[i] < pivot do i := i + 1;
    while a[j] > pivot do j := j - 1;

    if i <= j then
    begin
      temp := a[i];
      a[i] := a[j];
      a[j] := temp;

      i := i + 1;
      j := j - 1;
    end;
  end;

  if left < j then QuickSort(a, left, j);
  if i < right then QuickSort(a, i, right);
end;

var n, i: integer;
    a: array of integer;
begin
  readln(n);
  setlength(a, n);

  for i := 0 to n - 1 do
    readln(a[i]);

  QuickSort(a, 0, n - 1);

  for i := 0 to n - 1 do
    write(a[i], ' ');
end."""

BUGGY_PASCAL = """procedure QuickSort(var a: array of integer; left, right: integer);
var i, j, pivot, temp: integer;
begin
  pivot := a[left];

  while left <= right do
  begin
    while a[left] <= pivot do left := left + 1;
    while a[right] > pivot do right := right - 1;

    if left <= right then
    begin
      temp := a[left];
      a[left] := a[right];
      a[right] := temp;
    end;
  end;

  QuickSort(a, left, right);
end;

var n, i: integer;
    a: array of integer;
begin
  readln(n);
  setlength(a, n);

  for i := 0 to n - 1 do
    readln(a[i]);

  QuickSort(a, 0, n);

  for i := 0 to n - 1 do
    writeln(a[i]);
end."""

FIXED_PYTHON = """def quicksort(a):
    if len(a) <= 1:
        return a

    pivot = a[len(a) // 2]

    left = []
    middle = []
    right = []

    for x in a:
        if x < pivot:
            left.append(x)
        elif x > pivot:
            right.append(x)
        else:
            middle.append(x)

    return quicksort(left) + middle + quicksort(right)


n = int(input())
a = [int(input()) for _ in range(n)]

print(*quicksort(a))"""

BUGGY_PYTHON = """def quicksort(int[] a):
    if len(a) < 1:
        return []

    pivot := a[0]
    left = []
    right = []

    for x in a:
        if x <= pivot:
            left.append(x)
        else:
            right.append(x)

    return quicksort(left) + pivot + quicksort(right)


n = int.Parse(Console.ReadLine())
a = new int[n]

for i := 1 to n do:
    a[i] = int(input())

Console.WriteLine(quicksort(a))"""

FIXED_CPP = """#include <iostream>
#include <vector>
#include <algorithm>

void quickSort(std::vector<int>& a, int left, int right) {
    int i = left;
    int j = right;
    int pivot = a[(left + right) / 2];

    while (i <= j) {
        while (a[i] < pivot) i++;
        while (a[j] > pivot) j--;

        if (i <= j) {
            std::swap(a[i], a[j]);
            i++;
            j--;
        }
    }

    if (left < j) quickSort(a, left, j);
    if (i < right) quickSort(a, i, right);
}

int main() {
    int n;
    std::cin >> n;

    std::vector<int> a(n);

    for (int i = 0; i < n; i++) {
        std::cin >> a[i];
    }

    quickSort(a, 0, n - 1);

    for (int x : a) {
        std::cout << x << ' ';
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <vector>

void quickSort(vector<int> a, int left, int right) {
    int pivot := a[left];

    while left <= right {
        while (a[left] <= pivot) left++;
        while (a[right] > pivot) right--;

        if (left <= right) {
            a[left], a[right] = a[right], a[left];
        }
    }

    quickSort(a, left, right);
}

int main() {
    int n = int(input());
    vector<int> a = new int[n];

    for i in range(n):
        cin >> a[i];

    quickSort(a, 0, n);

    Console.WriteLine(a);
    return 0;
}"""

FIXED_CSHARP = """using System;

class Program {
    static void QuickSort(int[] a, int left, int right) {
        int i = left;
        int j = right;
        int pivot = a[(left + right) / 2];

        while (i <= j) {
            while (a[i] < pivot) i++;
            while (a[j] > pivot) j--;

            if (i <= j) {
                int temp = a[i];
                a[i] = a[j];
                a[j] = temp;

                i++;
                j--;
            }
        }

        if (left < j) QuickSort(a, left, j);
        if (i < right) QuickSort(a, i, right);
    }

    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int[] a = new int[n];

        for (int i = 0; i < n; i++) {
            a[i] = int.Parse(Console.ReadLine());
        }

        QuickSort(a, 0, n - 1);

        foreach (int x in a) {
            Console.Write(x + " ");
        }
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static void QuickSort(int[] a, int left, int right) {
        int pivot := a[left];

        while left <= right {
            while (a[left] <= pivot) left++;
            while (a[right] > pivot) right--;

            if (left <= right) {
                a[left], a[right] = a[right], a[left];
            }
        }

        QuickSort(a, left, right);
    }

    static void Main() {
        int n = int(input());
        int[] a = [];

        for i in range(n):
            a[i] = Console.ReadLine();

        QuickSort(a, 0, n);

        print(a);
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    static void quickSort(int[] a, int left, int right) {
        int i = left;
        int j = right;
        int pivot = a[(left + right) / 2];

        while (i <= j) {
            while (a[i] < pivot) i++;
            while (a[j] > pivot) j--;

            if (i <= j) {
                int temp = a[i];
                a[i] = a[j];
                a[j] = temp;

                i++;
                j--;
            }
        }

        if (left < j) quickSort(a, left, j);
        if (i < right) quickSort(a, i, right);
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int[] a = new int[n];

        for (int i = 0; i < n; i++) {
            a[i] = sc.nextInt();
        }

        quickSort(a, 0, n - 1);

        for (int x : a) {
            System.out.print(x + " ");
        }
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    static void quickSort(int[] a, int left, int right) {
        int pivot := a[left];

        while left <= right {
            while (a[left] <= pivot) left++;
            while (a[right] > pivot) right--;

            if (left <= right) {
                a[left], a[right] = a[right], a[left];
            }
        }

        quickSort(a, left, right);
    }

    public static void main(String[] args) {
        int n = int(input());
        int[] a = [];

        for i in range(n):
            a[i] = Scanner.nextInt();

        quickSort(a, 0, n);

        Console.WriteLine(a);
    }
}"""
