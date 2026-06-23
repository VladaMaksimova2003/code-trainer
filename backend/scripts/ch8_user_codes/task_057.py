PASCAL = """var n, target, i, x, position: integer;
begin
  readln(n, target);
  position := -1;

  for i := 0 to n - 1 do
  begin
    readln(x);
    if (x = target) and (position = -1) then
      position := i;
  end;

  writeln(position);
end."""

PYTHON = """n, target = map(int, input().split())
a = [int(input()) for _ in range(n)]

position = -1

for i in range(n):
    if a[i] == target and position == -1:
        position = i

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

    int position = -1;

    for (int i = 0; i < n; i++) {
        if (a[i] == target && position == -1) {
            position = i;
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

        int position = -1;

        for (int i = 0; i < n; i++) {
            if (a[i] == target && position == -1) {
                position = i;
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

        int position = -1;

        for (int i = 0; i < n; i++) {
            if (a[i] == target && position == -1) {
                position = i;
            }
        }

        System.out.println(position);
    }
}"""
