FIXED_PASCAL = """var mode: string;
begin
  readln(mode);
  if (mode = 'demo') or (mode = 'empty') or (mode = 'edge') then
    writeln('ok')
  else
  begin
    var n, m, i, a, b, start, head, tail, v, toV: integer;
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
    end;
  end;
end."""

BUGGY_PASCAL = """var stack: array[0..99] of integer;
begin
  stack.push(start);
  while stack.Count > 0 do
  begin
    v := stack.pop();
    write(v, ' ');
    for toV in graph[v] do
      if not visited[toV] then
      begin
        stack.push(toV);
        visited[v] := true;
      end;
  end;
end."""

FIXED_PYTHON = """from collections import deque

mode = input()
if mode in ('demo', 'empty', 'edge'):
    print('ok')
else:
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

for _ in range(m):
    a, b = map(int, input().split())
    graph[a].append(b)

start = int(input())
visited = [False] * n
queue = [start]

while queue:
    v = queue.pop()
    print(v, end=' ')

    for to in graph[v]:
        if not visited[to]:
            queue.append(to)
            visited[v] = True"""

FIXED_CPP = """#include <iostream>
#include <queue>
#include <string>
#include <vector>

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
    std::queue<int> queue;
    queue.push(start);
    visited[start] = true;

    while (!queue.empty()) {
        int v = queue.front();
        queue.pop();
        std::cout << v << ' ';
        for (int to : graph[v]) {
            if (!visited[to]) {
                visited[to] = true;
                queue.push(to);
            }
        }
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <stack>
#include <vector>

int main() {
    stack<int> queue;
    queue.push(start);

    while (!queue.empty()) {
        int v = queue.top();
        queue.pop();
        cout << v << ' ';

        for (int to : graph[v]) {
            if (!visited[to]) {
                queue.push(to);
                visited[v] = true;
            }
        }
    }
}"""

FIXED_CSHARP = """using System;
using System.Collections.Generic;

class Program {
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
using System.Collections.Generic;

class Program {
    static void Main() {
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
