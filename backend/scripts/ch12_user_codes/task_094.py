FIXED_PASCAL = """var n, m, i, a, b, start, head, tail, v, toV: integer;
    graph: array[0..99, 0..99] of integer;
    degree, queue: array[0..99] of integer;
    visited: array[0..99] of boolean;
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

  head := 0;
  tail := 0;
  queue[tail] := start;
  tail := tail + 1;
  visited[start] := true;

  while head < tail do
  begin
    v := queue[head];
    head := head + 1;
    write(v, ' ');

    for i := 0 to degree[v] - 1 do
    begin
      toV := graph[v, i];

      if not visited[toV] then
      begin
        visited[toV] := true;
        queue[tail] := toV;
        tail := tail + 1;
      end;
    end;
  end;
end."""

BUGGY_PASCAL = """var n, m, i, a, b, start, v, toV: integer;
    graph: array[0..99, 0..99] of integer;
    degree, queue: array[0..99] of integer;
    visited: array[0..99] of boolean;
begin
  readln(n, m);

  for i in range(m) do
  begin
    readln(a, b);
    graph[a].push_back(b);
    graph[b].push_back(a);
  end;

  readln(start);

  queue.append(start);

  while queue.Count > 0 do
  begin
    v := queue.pop();
    write(v, ' ');

    for toV in graph[v] do
      if not visited[toV] then
      begin
        queue.append(toV);
        visited[v] := true;
      end;
  end;
end."""

FIXED_PYTHON = """from collections import deque

n, m = map(int, input().split())
graph = [[] for _ in range(n)]

for _ in range(m):
    a, b = map(int, input().split())
    graph[a].append(b)
    graph[b].append(a)

start = int(input())

visited = [False] * n
queue = deque([start])
visited[start] = True

while queue:
    v = queue.popleft()
    print(v, end=' ')

    for to in graph[v]:
        if not visited[to]:
            visited[to] = True
            queue.append(to)"""

BUGGY_PYTHON = """n, m = map(int, input().split())
graph = [[] for _ in range(n)]

for i := 1 to m do:
    a, b = input().split()
    graph[a].append(b)
    graph[b].append(a)

start = int(input())

visited = [False] * n
queue = []
queue.append(start)

while queue:
    v = queue.pop()
    print(v, end=' ')

    for to in graph[v]:
        if visited[to] == False:
            queue.append(to)
            visited[v] = True"""

FIXED_CPP = """#include <iostream>
#include <vector>
#include <queue>

int main() {
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
    std::queue<int> q;

    q.push(start);
    visited[start] = true;

    while (!q.empty()) {
        int v = q.front();
        q.pop();

        std::cout << v << ' ';

        for (int to : graph[v]) {
            if (!visited[to]) {
                visited[to] = true;
                q.push(to);
            }
        }
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <vector>
#include <stack>

int main() {
    int n, m;
    std::cin >> n >> m;

    vector<vector<int>> graph = new vector<int>[n];

    for i in range(m):
        int a, b;
        cin >> a >> b;
        graph[a].push_back(b);
        graph[b].push_back(a);

    int start;
    cin >> start;

    vector<bool> visited(n, false);
    stack<int> q;
    q.push(start);

    while (!q.empty()) {
        int v = q.top();
        q.pop();

        cout << v << ' ';

        for (int to : graph[v]) {
            if (!visited[to]) {
                q.push(to);
                visited[v] = true;
            }
        }
    }

    return 0;
}"""

FIXED_CSHARP = """using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        string[] first = Console.ReadLine().Split();

        int n = int.Parse(first[0]);
        int m = int.Parse(first[1]);

        List<int>[] graph = new List<int>[n];

        for (int i = 0; i < n; i++) {
            graph[i] = new List<int>();
        }

        for (int i = 0; i < m; i++) {
            string[] edge = Console.ReadLine().Split();

            int a = int.Parse(edge[0]);
            int b = int.Parse(edge[1]);

            graph[a].Add(b);
            graph[b].Add(a);
        }

        int start = int.Parse(Console.ReadLine());

        bool[] visited = new bool[n];
        Queue<int> queue = new Queue<int>();

        queue.Enqueue(start);
        visited[start] = true;

        while (queue.Count > 0) {
            int v = queue.Dequeue();

            Console.Write(v + " ");

            foreach (int to in graph[v]) {
                if (!visited[to]) {
                    visited[to] = true;
                    queue.Enqueue(to);
                }
            }
        }
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static void Main() {
        int n, m = Console.ReadLine().Split();

        List<int>[] graph = new List<int>[n];

        for i in range(m):
            int a, b;
            cin >> a >> b;
            graph[a].Add(b);
            graph[b].Add(a);

        int start = int(input());

        bool[] visited = new bool[n];
        Stack<int> queue = new Stack<int>();
        queue.Push(start);

        while (queue.Count > 0) {
            int v = queue.Pop();
            Console.Write(v + " ");

            foreach (int to in graph[v]) {
                if (!visited[to]) {
                    queue.Push(to);
                    visited[v] = true;
                }
            }
        }
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int m = sc.nextInt();

        ArrayList<Integer>[] graph = new ArrayList[n];

        for (int i = 0; i < n; i++) {
            graph[i] = new ArrayList<>();
        }

        for (int i = 0; i < m; i++) {
            int a = sc.nextInt();
            int b = sc.nextInt();

            graph[a].add(b);
            graph[b].add(a);
        }

        int start = sc.nextInt();

        boolean[] visited = new boolean[n];
        Queue<Integer> queue = new LinkedList<>();

        queue.add(start);
        visited[start] = true;

        while (!queue.isEmpty()) {
            int v = queue.poll();

            System.out.print(v + " ");

            for (int to : graph[v]) {
                if (!visited[to]) {
                    visited[to] = true;
                    queue.add(to);
                }
            }
        }
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        int n = int(input());
        int m = int(input());

        ArrayList<Integer>[] graph = new ArrayList[n];

        for i in range(m):
            int a = Scanner.nextInt();
            int b = Scanner.nextInt();
            graph[a].push_back(b);
            graph[b].push_back(a);

        int start = Scanner.nextInt();

        boolean[] visited = new boolean[n];
        Stack<Integer> queue = new Stack<>();
        queue.push(start);

        while (!queue.empty()) {
            int v = queue.pop();
            System.out.print(v + " ");

            for (int to : graph[v]) {
                if (!visited[to]) {
                    queue.push(to);
                    visited[v] = true;
                }
            }
        }
    }
}"""
