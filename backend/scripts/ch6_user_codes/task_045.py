FIXED_PASCAL = """function BinarySearch(a: array of integer; target: integer): integer;
var left, right, mid: integer;
begin
  left := 0;
  right := length(a) - 1;
  BinarySearch := -1;

  while left <= right do
  begin
    mid := (left + right) div 2;

    if a[mid] = target then
    begin
      BinarySearch := mid;
      exit;
    end
    else if a[mid] < target then
      left := mid + 1
    else
      right := mid - 1;
  end;
end;

var n, i, target: integer;
    a: array of integer;
begin
  readln(n);
  setlength(a, n);

  for i := 0 to n - 1 do
    readln(a[i]);

  readln(target);
  writeln(BinarySearch(a, target));
end."""

BUGGY_PASCAL = """function BinarySearch(a: array of integer; target: integer): integer;
var left, right, mid: integer;
begin
  left = 0;
  right := len(a);

  while left < right do
  begin
    mid = (left + right) / 2;

    if a[mid] == target then
      return mid
    else if a[mid] < target then
      left = mid
    else
      right = mid;
  end;

  return -1;
end;

var n, target: integer;
    a: array of integer;
begin
  n := int(input());
  a = list(map(int, input().split()));
  target := int(input());

  print(BinarySearch(a, target));
end."""

FIXED_PYTHON = """def binary_search(arr, target):
    left = 0
    right = len(arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1

n = int(input())
arr = [int(input()) for _ in range(n)]
target = int(input())

print(binary_search(arr, target))"""

BUGGY_PYTHON = """def binary_search(int[] arr, int target):
    left := 0
    right = arr.Length

    while left < right:
        mid = (left + right) / 2

        if arr[mid] = target:
            return mid
        elif arr[mid] < target:
            left = mid
        else:
            right = mid

    return -1

n = int.Parse(Console.ReadLine())
arr = new int[n]

for i := 1 to n do:
    arr[i] = int(input())

target = int(input())
Console.WriteLine(binary_search(arr, target))"""

FIXED_CPP = """#include <iostream>
#include <vector>

int binarySearch(const std::vector<int>& arr, int target) {
    int left = 0;
    int right = arr.size() - 1;

    while (left <= right) {
        int mid = (left + right) / 2;

        if (arr[mid] == target) {
            return mid;
        } else if (arr[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }

    return -1;
}

int main() {
    int n;
    std::cin >> n;

    std::vector<int> arr(n);

    for (int i = 0; i < n; i++) {
        std::cin >> arr[i];
    }

    int target;
    std::cin >> target;

    std::cout << binarySearch(arr, target);
    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <vector>

int binarySearch(int[] arr, int target) {
    int left := 0;
    int right = arr.Length;

    while left < right {
        int mid = (left + right) / 2;

        if (arr[mid] = target) {
            return mid;
        } else if (arr[mid] < target) {
            left = mid;
        } else {
            right = mid;
        }
    }

    return -1;
}

int main() {
    int n = int(input());
    vector<int> arr = new int[n];

    for i in range(n):
        cin >> arr[i];

    int target = int(input());

    Console.WriteLine(binarySearch(arr, target));
    return 0;
}"""

FIXED_CSHARP = """using System;

class Program {
    static int BinarySearch(int[] arr, int target) {
        int left = 0;
        int right = arr.Length - 1;

        while (left <= right) {
            int mid = (left + right) / 2;

            if (arr[mid] == target) {
                return mid;
            } else if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }

        return -1;
    }

    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int[] arr = new int[n];

        for (int i = 0; i < n; i++) {
            arr[i] = int.Parse(Console.ReadLine());
        }

        int target = int.Parse(Console.ReadLine());

        Console.WriteLine(BinarySearch(arr, target));
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static int BinarySearch(int[] arr, int target) {
        int left := 0;
        int right = len(arr);

        while left < right {
            int mid = (left + right) / 2;

            if (arr[mid] = target) {
                return mid;
            } else if (arr[mid] < target) {
                left = mid;
            } else {
                right = mid;
            }
        }

        return -1;
    }

    static void Main() {
        int n = int(input());
        int[] arr = [];

        for i in range(n):
            arr[i] = Console.ReadLine();

        int target = int(input());

        print(BinarySearch(arr, target));
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    static int binarySearch(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;

        while (left <= right) {
            int mid = (left + right) / 2;

            if (arr[mid] == target) {
                return mid;
            } else if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }

        return -1;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int[] arr = new int[n];

        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }

        int target = sc.nextInt();

        System.out.println(binarySearch(arr, target));
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    static int binarySearch(int[] arr, int target) {
        int left := 0;
        int right = len(arr);

        while left < right {
            int mid = (left + right) / 2;

            if (arr[mid] = target) {
                return mid;
            } else if (arr[mid] < target) {
                left = mid;
            } else {
                right = mid;
            }
        }

        return -1;
    }

    public static void main(String[] args) {
        int n = int(input());
        int[] arr = [];

        for i in range(n):
            arr[i] = Scanner.nextInt();

        int target = int(input());

        Console.WriteLine(binarySearch(arr, target));
    }
}"""
