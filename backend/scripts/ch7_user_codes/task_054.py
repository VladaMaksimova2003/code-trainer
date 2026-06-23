FIXED_PASCAL = """function BinarySearch(a: array of integer; left, right, target: integer): integer;
var mid: integer;
begin
  if left > right then
    BinarySearch := -1
  else
  begin
    mid := (left + right) div 2;

    if a[mid] = target then
      BinarySearch := mid
    else if a[mid] < target then
      BinarySearch := BinarySearch(a, mid + 1, right, target)
    else
      BinarySearch := BinarySearch(a, left, mid - 1, target);
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

  writeln(BinarySearch(a, 0, n - 1, target));
end."""

BUGGY_PASCAL = """function BinarySearch(a: array of integer; left, right, target: integer): integer;
var mid: integer;
begin
  if left >= right then
    BinarySearch := -1
  else
  begin
    mid := (left + right) / 2;

    if a[mid] = target then
      BinarySearch := mid
    else if a[mid] < target then
      BinarySearch := BinarySearch(a, mid, right, target)
    else
      BinarySearch := BinarySearch(a, left, mid, target);
  end;
end;

var n, i, target: integer;
    a: array of integer;
begin
  readln(n);
  setlength(a, n);

  for i := 1 to n do
    readln(a[i]);

  readln(target);

  writeln(BinarySearch(a, 0, n, target));
end."""

FIXED_PYTHON = """def binary_search(a, left, right, target):
    if left > right:
        return -1

    mid = (left + right) // 2

    if a[mid] == target:
        return mid
    elif a[mid] < target:
        return binary_search(a, mid + 1, right, target)
    else:
        return binary_search(a, left, mid - 1, target)


n = int(input())
a = [int(input()) for _ in range(n)]
target = int(input())

print(binary_search(a, 0, n - 1, target))"""

BUGGY_PYTHON = """def binary_search(int[] a, left, right, target):
    if left >= right:
        return -1

    mid := (left + right) / 2

    if a[mid] = target:
        return mid
    elif a[mid] < target:
        return binary_search(a, mid, right, target)
    else:
        return binary_search(a, left, mid, target)


n = int.Parse(Console.ReadLine())
a = new int[n]

for i := 1 to n do:
    a[i] = int(input())

target = int(input())
Console.WriteLine(binary_search(a, 0, n, target))"""

FIXED_CPP = """#include <iostream>
#include <vector>

int binarySearch(const std::vector<int>& a, int left, int right, int target) {
    if (left > right) {
        return -1;
    }

    int mid = (left + right) / 2;

    if (a[mid] == target) {
        return mid;
    } else if (a[mid] < target) {
        return binarySearch(a, mid + 1, right, target);
    } else {
        return binarySearch(a, left, mid - 1, target);
    }
}

int main() {
    int n;
    std::cin >> n;

    std::vector<int> a(n);

    for (int i = 0; i < n; i++) {
        std::cin >> a[i];
    }

    int target;
    std::cin >> target;

    std::cout << binarySearch(a, 0, n - 1, target);
    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <vector>

int binarySearch(int[] a, int left, int right, int target) {
    if left >= right {
        return -1;
    }

    int mid := (left + right) / 2;

    if (a[mid] = target) {
        return mid;
    } else if (a[mid] < target) {
        return binarySearch(a, mid, right, target);
    } else {
        return binarySearch(a, left, mid, target);
    }
}

int main() {
    int n = int(input());
    vector<int> a = new int[n];

    for i in range(n):
        cin >> a[i];

    int target = int(input());

    Console.WriteLine(binarySearch(a, 0, n, target));
    return 0;
}"""

FIXED_CSHARP = """using System;

class Program {
    static int BinarySearch(int[] a, int left, int right, int target) {
        if (left > right) {
            return -1;
        }

        int mid = (left + right) / 2;

        if (a[mid] == target) {
            return mid;
        } else if (a[mid] < target) {
            return BinarySearch(a, mid + 1, right, target);
        } else {
            return BinarySearch(a, left, mid - 1, target);
        }
    }

    static void Main() {
        int n = int.Parse(Console.ReadLine());
        int[] a = new int[n];

        for (int i = 0; i < n; i++) {
            a[i] = int.Parse(Console.ReadLine());
        }

        int target = int.Parse(Console.ReadLine());

        Console.WriteLine(BinarySearch(a, 0, n - 1, target));
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static int BinarySearch(int[] a, int left, int right, int target) {
        if left >= right {
            return -1;
        }

        int mid := (left + right) / 2;

        if (a[mid] = target) {
            return mid;
        } else if (a[mid] < target) {
            return BinarySearch(a, mid, right, target);
        } else {
            return BinarySearch(a, left, mid, target);
        }
    }

    static void Main() {
        int n = int(input());
        int[] a = [];

        for i in range(n):
            a[i] = Console.ReadLine();

        int target = int(input());

        print(BinarySearch(a, 0, n, target));
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    static int binarySearch(int[] a, int left, int right, int target) {
        if (left > right) {
            return -1;
        }

        int mid = (left + right) / 2;

        if (a[mid] == target) {
            return mid;
        } else if (a[mid] < target) {
            return binarySearch(a, mid + 1, right, target);
        } else {
            return binarySearch(a, left, mid - 1, target);
        }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int[] a = new int[n];

        for (int i = 0; i < n; i++) {
            a[i] = sc.nextInt();
        }

        int target = sc.nextInt();

        System.out.println(binarySearch(a, 0, n - 1, target));
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    static int binarySearch(int[] a, int left, int right, int target) {
        if left >= right {
            return -1;
        }

        int mid := (left + right) / 2;

        if (a[mid] = target) {
            return mid;
        } else if (a[mid] < target) {
            return binarySearch(a, mid, right, target);
        } else {
            return binarySearch(a, left, mid, target);
        }
    }

    public static void main(String[] args) {
        int n = int(input());
        int[] a = [];

        for i in range(n):
            a[i] = Scanner.nextInt();

        int target = int(input());

        Console.WriteLine(binarySearch(a, 0, n, target));
    }
}"""
