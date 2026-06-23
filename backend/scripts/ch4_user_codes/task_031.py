FIXED_PASCAL = """var n, m, i, j, k: integer;
    a, b, res: array[1..1000] of integer;
begin
  readln(n, m);

  for i := 1 to n do
    read(a[i]);

  for j := 1 to m do
    read(b[j]);

  i := 1;
  j := 1;
  k := 0;

  while (i <= n) and (j <= m) do
  begin
    k := k + 1;

    if a[i] <= b[j] then
    begin
      res[k] := a[i];
      i := i + 1;
    end
    else
    begin
      res[k] := b[j];
      j := j + 1;
    end;
  end;

  while i <= n do
  begin
    k := k + 1;
    res[k] := a[i];
    i := i + 1;
  end;

  while j <= m do
  begin
    k := k + 1;
    res[k] := b[j];
    j := j + 1;
  end;

  for i := 1 to k do
  begin
    if i > 1 then
      write(' ');
    write(res[i]);
  end;
end."""

BUGGY_PASCAL = """var n, m, i, j, k: integer;
    a, b, res: array[1..1000] of integer;
begin
  readln(n, m);

  for i := 1 to n do
    read(a[i]);

  for j := 1 to m do
    read(b[j]);

  i := 1;
  j := 1;
  k := 0;

  while (i <= n) and (j <= m) do
  begin
    if a[i] < b[j] then
    begin
      k := k + 1;
      res[k] := a[i];
      i := i + 1;
    end
    else
    begin
      k := k + 1;
      res[k] := b[j];
      i := i + 1;
    end;
  end;

  while i <= n do
  begin
    res[k] := a[i];
    i := i + 1;
  end;

  for i := 1 to k do
    write(res[i]);
end."""

FIXED_PYTHON = """n, m = map(int, input().split())
a = list(map(int, input().split()))
b = list(map(int, input().split()))

i = j = 0
result = []

while i < n and j < m:
    if a[i] <= b[j]:
        result.append(a[i])
        i += 1
    else:
        result.append(b[j])
        j += 1

while i < n:
    result.append(a[i])
    i += 1

while j < m:
    result.append(b[j])
    j += 1

print(' '.join(map(str, result)))"""

BUGGY_PYTHON = """n, m = map(int, input().split())
a = list(map(int, input().split()))
b = list(map(int, input().split()))

i = 0
j = 0
result = []

while i < n and j < m:
    if a[i] < b[j]:
        result.append(a[i])
        i += 1
    else:
        result.append(b[j])
        i += 1

while i <= n:
    result.append(a[i])
    i += 1

print(' '.join(map(str, result)))"""

FIXED_CPP = """#include <iostream>
#include <vector>

int main() {
    int n, m;
    std::cin >> n >> m;

    std::vector<int> a(n), b(m), result;
    for (int i = 0; i < n; i++) {
        std::cin >> a[i];
    }
    for (int j = 0; j < m; j++) {
        std::cin >> b[j];
    }

    int i = 0, j = 0;
    while (i < n && j < m) {
        if (a[i] <= b[j]) {
            result.push_back(a[i++]);
        } else {
            result.push_back(b[j++]);
        }
    }
    while (i < n) {
        result.push_back(a[i++]);
    }
    while (j < m) {
        result.push_back(b[j++]);
    }

    for (size_t p = 0; p < result.size(); p++) {
        if (p > 0) {
            std::cout << ' ';
        }
        std::cout << result[p];
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <vector>

int main() {
    int n, m;
    std::cin >> n >> m;

    std::vector<int> a(n), b(m), result;
    for (int i = 0; i < n; i++) std::cin >> a[i];
    for (int j = 0; j < m; j++) std::cin >> b[j];

    int i = 0, j = 0;
    while (i < n && j < m) {
        if (a[i] < b[j]) {
            result.push_back(a[i++]);
        } else {
            result.push_back(b[j]);
            i++;
        }
    }
    while (i <= n) {
        result.push_back(a[i++]);
    }

    for (int x : result) std::cout << x << ' ';
    return 0;
}"""

FIXED_CSHARP = """using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        string[] nm = Console.ReadLine().Split();
        int n = int.Parse(nm[0]);
        int m = int.Parse(nm[1]);
        int[] a = Array.ConvertAll(Console.ReadLine().Split(), int.Parse);
        int[] b = Array.ConvertAll(Console.ReadLine().Split(), int.Parse);

        List<int> result = new List<int>();
        int i = 0, j = 0;

        while (i < n && j < m) {
            if (a[i] <= b[j]) {
                result.Add(a[i++]);
            } else {
                result.Add(b[j++]);
            }
        }
        while (i < n) {
            result.Add(a[i++]);
        }
        while (j < m) {
            result.Add(b[j++]);
        }

        Console.WriteLine(string.Join(" ", result));
    }
}"""

BUGGY_CSHARP = """using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        string[] nm = Console.ReadLine().Split();
        int n = int.Parse(nm[0]);
        int m = int.Parse(nm[1]);
        int[] a = Array.ConvertAll(Console.ReadLine().Split(), int.Parse);
        int[] b = Array.ConvertAll(Console.ReadLine().Split(), int.Parse);

        List<int> result = new List<int>();
        int i = 0, j = 0;

        while (i < n && j < m) {
            if (a[i] < b[j]) {
                result.Add(a[i++]);
            } else {
                result.Add(b[j]);
                i++;
            }
        }
        while (i <= n) {
            result.Add(a[i++]);
        }

        Console.WriteLine(string.Join(" ", result));
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int m = sc.nextInt();
        int[] a = new int[n];
        int[] b = new int[m];

        for (int i = 0; i < n; i++) {
            a[i] = sc.nextInt();
        }
        for (int j = 0; j < m; j++) {
            b[j] = sc.nextInt();
        }

        ArrayList<Integer> result = new ArrayList<>();
        int i = 0, j = 0;

        while (i < n && j < m) {
            if (a[i] <= b[j]) {
                result.add(a[i++]);
            } else {
                result.add(b[j++]);
            }
        }
        while (i < n) {
            result.add(a[i++]);
        }
        while (j < m) {
            result.add(b[j++]);
        }

        StringBuilder sb = new StringBuilder();
        for (int p = 0; p < result.size(); p++) {
            if (p > 0) {
                sb.append(' ');
            }
            sb.append(result.get(p));
        }
        System.out.print(sb);
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int m = sc.nextInt();
        int[] a = new int[n];
        int[] b = new int[m];

        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        for (int j = 0; j < m; j++) b[j] = sc.nextInt();

        ArrayList<Integer> result = new ArrayList<>();
        int i = 0, j = 0;

        while (i < n && j < m) {
            if (a[i] < b[j]) {
                result.add(a[i++]);
            } else {
                result.add(b[j]);
                i++;
            }
        }
        while (i <= n) {
            result.add(a[i++]);
        }

        System.out.println(result);
    }
}"""
