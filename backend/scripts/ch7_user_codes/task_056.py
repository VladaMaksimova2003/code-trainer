FIXED_PASCAL = """const MAXN = 100;

var n, i, root: integer;
    parent, size: array[1..MAXN] of integer;

function TotalSize(v: integer): integer;
var i, total: integer;
begin
  total := size[v];

  for i := 1 to n do
    if parent[i] = v then
      total := total + TotalSize(i);

  TotalSize := total;
end;

begin
  readln(n);

  for i := 1 to n do
  begin
    readln(parent[i], size[i]);

    if parent[i] = -1 then
      root := i;
  end;

  writeln(TotalSize(root));
end."""

BUGGY_PASCAL = """const MAXN = 100;

var n, i, root: integer;
    parent, size: array[1..MAXN] of integer;

function TotalSize(v: integer): integer;
var total: integer;
begin
  total := size[v];

  for i := 1 to n do
    if parent[i] = v then
      total := total + TotalSize(i);

  TotalSize := size;
end;

begin
  readln(n);

  for i := 1 to n do
  begin
    readln(parent[i], size[i]);

    if parent[i] = -1 then
      root := i;
  end;

  writeln(TotalSize(root));
end."""

FIXED_PYTHON = """def total_size(v, children, sizes):
    total = sizes[v]

    for child in children[v]:
        total += total_size(child, children, sizes)

    return total


n = int(input())

children = [[] for _ in range(n)]
sizes = [0] * n
root = 0

for i in range(n):
    parent, size = map(int, input().split())
    sizes[i] = size

    if parent == -1:
        root = i
    else:
        children[parent].append(i)

print(total_size(root, children, sizes))"""

BUGGY_PYTHON = """def total_size(int v, children, sizes):
    total := sizes[v]

    for child in children:
        total += total_size(child, children, sizes)

    return sizes


n = int.Parse(Console.ReadLine())

children = new List<int>[n]
sizes = []

for i := 1 to n do:
    parent, size = map(int, input().split())
    sizes[i] = size

    if parent = -1:
        root = i
    else:
        children[parent].Add(i)

Console.WriteLine(total_size(root, children, sizes))"""

FIXED_CPP = """#include <iostream>
#include <vector>

int totalSize(int v, const std::vector<std::vector<int>>& children, const std::vector<int>& sizes) {
    int total = sizes[v];

    for (int child : children[v]) {
        total += totalSize(child, children, sizes);
    }

    return total;
}

int main() {
    int n;
    std::cin >> n;

    std::vector<std::vector<int>> children(n);
    std::vector<int> sizes(n);

    int root = 0;

    for (int i = 0; i < n; i++) {
        int parent, size;
        std::cin >> parent >> size;

        sizes[i] = size;

        if (parent == -1) {
            root = i;
        } else {
            children[parent].push_back(i);
        }
    }

    std::cout << totalSize(root, children, sizes);
    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <vector>

int totalSize(int v, vector<int>[] children, vector<int> sizes) {
    int total := sizes[v];

    for child in children {
        total += totalSize(child, children, sizes);
    }

    return sizes;
}

int main() {
    int n = int(input());

    vector<vector<int>> children = new vector<int>[n];
    vector<int> sizes;

    for i in range(n):
        int parent, size;
        cin >> parent >> size;

        sizes[i] = size;

        if (parent = -1) {
            root := i;
        } else {
            children[parent].Add(i);
        }

    Console.WriteLine(totalSize(root, children, sizes));
    return 0;
}"""

FIXED_CSHARP = """using System;
using System.Collections.Generic;

class Program {
    static int TotalSize(int v, List<int>[] children, int[] sizes) {
        int total = sizes[v];

        foreach (int child in children[v]) {
            total += TotalSize(child, children, sizes);
        }

        return total;
    }

    static void Main() {
        int n = int.Parse(Console.ReadLine());

        List<int>[] children = new List<int>[n];
        int[] sizes = new int[n];

        for (int i = 0; i < n; i++) {
            children[i] = new List<int>();
        }

        int root = 0;

        for (int i = 0; i < n; i++) {
            string[] p = Console.ReadLine().Split();

            int parent = int.Parse(p[0]);
            int size = int.Parse(p[1]);

            sizes[i] = size;

            if (parent == -1) {
                root = i;
            } else {
                children[parent].Add(i);
            }
        }

        Console.WriteLine(TotalSize(root, children, sizes));
    }
}"""

BUGGY_CSHARP = """using System;
using System.Collections.Generic;

class Program {
    static int TotalSize(int v, List<int>[] children, int[] sizes) {
        int total := sizes[v];

        foreach child in children {
            total += TotalSize(child, children, sizes);
        }

        return sizes;
    }

    static void Main() {
        int n = int(input());

        List<int>[] children = new List<int>[n];
        int[] sizes = [];

        for i in range(n):
            children[i] = new List<int>();

        for i in range(n):
            string[] p = Console.ReadLine().Split();

            int parent = int.Parse(p[0]);
            int size = int.Parse(p[1]);

            sizes[i] = size;

            if (parent = -1) {
                root := i;
            } else {
                children[parent].push_back(i);
            }

        print(TotalSize(root, children, sizes));
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    static int totalSize(int v, ArrayList<Integer>[] children, int[] sizes) {
        int total = sizes[v];

        for (int child : children[v]) {
            total += totalSize(child, children, sizes);
        }

        return total;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();

        ArrayList<Integer>[] children = new ArrayList[n];
        int[] sizes = new int[n];

        for (int i = 0; i < n; i++) {
            children[i] = new ArrayList<>();
        }

        int root = 0;

        for (int i = 0; i < n; i++) {
            int parent = sc.nextInt();
            int size = sc.nextInt();

            sizes[i] = size;

            if (parent == -1) {
                root = i;
            } else {
                children[parent].add(i);
            }
        }

        System.out.println(totalSize(root, children, sizes));
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    static int totalSize(int v, ArrayList<Integer>[] children, int[] sizes) {
        int total := sizes[v];

        for child in children {
            total += totalSize(child, children, sizes);
        }

        return sizes;
    }

    public static void main(String[] args) {
        int n = int(input());

        ArrayList<Integer>[] children = new ArrayList[n];
        int[] sizes = [];

        for i in range(n):
            children[i] = new ArrayList<>();

        for i in range(n):
            int parent = Scanner.nextInt();
            int size = Scanner.nextInt();

            sizes[i] = size;

            if (parent = -1) {
                root := i;
            } else {
                children[parent].push_back(i);
            }

        Console.WriteLine(totalSize(root, children, sizes));
    }
}"""
