PASCAL = """var n, target, i, left, right, mid, position: integer;
    a: array[0..99] of integer;
begin
  readln(n, target);

  for i := 0 to n - 1 do
    readln(a[i]);

  left := 0;
  right := n - 1;
  position := -1;

  while left <= right do
  begin
    mid := (left + right) div 2;

    if a[mid] = target then
    begin
      position := mid;
      break;
    end
    else if a[mid] < target then
      left := mid + 1
    else
      right := mid - 1;
  end;

  writeln(position);
end."""

PYTHON = """n, target = map(int, input().split())
a = [int(input()) for _ in range(n)]

left = 0
right = n - 1
position = -1

while left <= right:
    mid = (left + right) // 2

    if a[mid] == target:
        position = mid
        break
    elif a[mid] < target:
        left = mid + 1
    else:
        right = mid - 1

print(position)"""

CPP = """#include <iostream>
#include <vector>

int main() {
    int n, target;
    std::cin >> n >> target;

    std::vector<int> a(n);

    for (int i = 0; i < n; i++) {
        std::cin >> a[i];
    }

    int left = 0;
    int right = n - 1;
    int position = -1;

    while (left <= right) {
        int mid = (left + right) / 2;

        if (a[mid] == target) {
            position = mid;
            break;
        } else if (a[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }

    std::cout << position;
    return 0;
}"""

CSHARP = """using System;

class Program {
    static void Main() {
        string[] first = Console.ReadLine().Split();

        int n = int.Parse(first[0]);
        int target = int.Parse(first[1]);

        int[] a = new int[n];

        for (int i = 0; i < n; i++) {
            a[i] = int.Parse(Console.ReadLine());
        }

        int left = 0;
        int right = n - 1;
        int position = -1;

        while (left <= right) {
            int mid = (left + right) / 2;

            if (a[mid] == target) {
                position = mid;
                break;
            } else if (a[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }

        Console.WriteLine(position);
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int target = sc.nextInt();

        int[] a = new int[n];

        for (int i = 0; i < n; i++) {
            a[i] = sc.nextInt();
        }

        int left = 0;
        int right = n - 1;
        int position = -1;

        while (left <= right) {
            int mid = (left + right) / 2;

            if (a[mid] == target) {
                position = mid;
                break;
            } else if (a[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }

        System.out.println(position);
    }
}"""
