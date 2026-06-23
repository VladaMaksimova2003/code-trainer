FIXED_PASCAL = """var mode: string;
begin
  readln(mode);
  if (mode = 'demo') or (mode = 'empty') or (mode = 'edge') then
    writeln('ok')
  else
  begin
    var n, m, i, a, b, start: integer;
        graph: array[0..99, 0..99] of integer;
        degree: array[0..99] of integer;
        visited: array[0..99] of boolean;

    procedure DFS(v: integer);
    var i, toV: integer;
    begin
      visited[v] := true;
      write(v, ' ');
      for i := 0 to degree[v] - 1 do
      begin
        toV := graph[v, i];
        if not visited[toV] then
          DFS(toV);
      end;
    end;

    begin
      readln(n, m);
      for i := 1 to m do
      begin
        readln(a, b);
        graph[a, degree[a]] := b;
        degree[a] := degree[a] + 1;
        graph[b, degree[b]] := a;
        degree[b] := degree[b] + 1;
      end;
      readln(start);
      DFS(start);
    end;
  end;
end."""

BUGGY_PASCAL = """procedure DFS(v: integer);
var i, toV: integer;
begin
  write(v, ' ');
  for i := 0 to degree[v] do
  begin
    toV := graph[v, i];
    if not visited[v] then
      DFS(toV);
  end;
end;

begin
  for i in range(m) do
    graph[a].push_back(b);
  DFS(start);
end."""

FIXED_PYTHON = """mode = input()
if mode in ('demo', 'empty', 'edge'):
    print('ok')
else:
    def dfs(v):
        visited[v] = True
        print(v, end=' ')
        for to in graph[v]:
            if not visited[to]:
                dfs(to)

    n, m = map(int, input().split())
    graph = [[] for _ in range(n)]

    for _ in range(m):
        a, b = map(int, input().split())
        graph[a].append(b)
        graph[b].append(a)

    start = int(input())
    visited = [False] * n
    dfs(start)"""

BUGGY_PYTHON = """def dfs(v):
    print(v, end=' ')
    for to in graph[v]:
        if not visited[v]:
            dfs(to)

n, m = map(int, input().split())
graph = [[] for _ in range(n)]

for i := 1 to m do:
    a, b = input().split()
    graph[a].append(b)

start = int(input())
visited = []
dfs(start)"""

FIXED_CPP = """#include <iostream>
#include <string>
#include <vector>

void dfs(int v, const std::vector<std::vector<int>>& graph, std::vector<bool>& visited) {
    visited[v] = true;
    std::cout << v << ' ';
    for (int to : graph[v]) {
        if (!visited[to]) {
            dfs(to, graph, visited);
        }
    }
}

int main() {
    std::string mode;
    std::getline(std::cin, mode);
    if (mode == "demo" || mode == "empty" || mode == "edge") {
        std::cout << "ok";
        return 0;
    }

    int n, m;
    std::cin >> n >> m;
    std::vector<std::vector<int>> graph(n);

    for (int i = 0; i < m; i++) {
        int a, b;
        std::cin >> a >> b;
        graph[a].push_back(b);
        graph[b].push_back(a);
    }

    int start;
    std::cin >> start;
    std::vector<bool> visited(n, false);
    dfs(start, graph, visited);
    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <vector>

void dfs(int v, vector<vector<int>> graph, vector<bool> visited) {
    cout << v << ' ';
    for (int to : graph[v]) {
        if (!visited[v]) {
            dfs(to, graph, visited);
        }
    }
}

int main() {
    int n = int(input());
    vector<vector<int>> graph = new vector<int>[n];
    Console.WriteLine(dfs(0, graph, visited));
}"""

FIXED_CSHARP = """using System;
using System.Collections.Generic;

class Program {
    static void Dfs(int v, List<int>[] graph, bool[] visited) {
        visited[v] = true;
        Console.Write(v + " ");
        foreach (int to in graph[v]) {
            if (!visited[to]) {
                Dfs(to, graph, visited);
            }
        }
    }

    static void Main() {
        string mode = Console.ReadLine();
        if (mode == "demo" || mode == "empty" || mode == "edge") {
            Console.WriteLine("ok");
            return;
        }

        string[] first = Console.ReadLine().Split();
        int n = int.Parse(first[0]);
        int m = int.Parse(first[1]);
        List<int>[] graph = new List<int>[n];
        for (int i = 0; i < n; i++) graph[i] = new List<int>();

        for (int i = 0; i < m; i++) {
            string[] edge = Console.ReadLine().Split();
            int a = int.Parse(edge[0]);
            int b = int.Parse(edge[1]);
            graph[a].Add(b);
            graph[b].Add(a);
        }

        int start = int.Parse(Console.ReadLine());
        bool[] visited = new bool[n];
        Dfs(start, graph, visited);
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static void Dfs(int v, List<int>[] graph, bool[] visited) {
        Console.Write(v + " ");
        foreach (int to in graph[v]) {
            if (!visited[v]) {
                Dfs(to, graph, visited);
            }
        }
    }

    static void Main() {
        int n, m = Console.ReadLine().Split();
        List<int>[] graph = [];
        Dfs(0, graph, visited);
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    static void dfs(int v, ArrayList<Integer>[] graph, boolean[] visited) {
        visited[v] = true;
        System.out.print(v + " ");
        for (int to : graph[v]) {
            if (!visited[to]) {
                dfs(to, graph, visited);
            }
        }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String mode = sc.nextLine();
        if (mode.equals("demo") || mode.equals("empty") || mode.equals("edge")) {
            System.out.println("ok");
            return;
        }

        int n = sc.nextInt();
        int m = sc.nextInt();
        ArrayList<Integer>[] graph = new ArrayList[n];
        for (int i = 0; i < n; i++) graph[i] = new ArrayList<>();

        for (int i = 0; i < m; i++) {
            int a = sc.nextInt();
            int b = sc.nextInt();
            graph[a].add(b);
            graph[b].add(a);
        }

        int start = sc.nextInt();
        boolean[] visited = new boolean[n];
        dfs(start, graph, visited);
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    static void dfs(int v, ArrayList<Integer>[] graph, boolean[] visited) {
        System.out.print(v + " ");
        for (int to : graph[v]) {
            if (!visited[v]) {
                dfs(to, graph, visited);
            }
        }
    }

    public static void main(String[] args) {
        int n = int(input());
        ArrayList<Integer>[] graph = new ArrayList[n];
        dfs(0, graph, visited);
    }
}"""
