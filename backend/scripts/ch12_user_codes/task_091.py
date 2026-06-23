PASCAL = """var n, i, head, tail: integer;
    line, task: string;
    q: array[1..100] of string;
begin
  readln(n);
  head := 1;
  tail := 0;

  for i := 1 to n do
  begin
    readln(line);

    if copy(line, 1, 3) = 'add' then
    begin
      task := copy(line, 5, length(line));
      tail := tail + 1;
      q[tail] := task;
    end
    else if line = 'run' then
    begin
      if head <= tail then
      begin
        writeln(q[head]);
        head := head + 1;
      end
      else
        writeln('empty');
    end;
  end;
end."""

PYTHON = """from collections import deque

n = int(input())
queue = deque()

for _ in range(n):
    command = input().split()

    if command[0] == 'add':
        queue.append(command[1])
    elif command[0] == 'run':
        if queue:
            print(queue.popleft())
        else:
            print('empty')"""

CPP = """#include <iostream>
#include <queue>
#include <string>

int main() {
    int n;
    std::cin >> n;

    std::queue<std::string> q;

    for (int i = 0; i < n; i++) {
        std::string command;
        std::cin >> command;

        if (command == "add") {
            std::string task;
            std::cin >> task;
            q.push(task);
        } else if (command == "run") {
            if (q.empty()) {
                std::cout << "empty\n";
            } else {
                std::cout << q.front() << '\n';
                q.pop();
            }
        }
    }

    return 0;
}"""

CSHARP = """using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        Queue<string> queue = new Queue<string>();

        for (int i = 0; i < n; i++) {
            string[] parts = Console.ReadLine().Split();

            if (parts[0] == "add") {
                queue.Enqueue(parts[1]);
            } else if (parts[0] == "run") {
                if (queue.Count == 0) {
                    Console.WriteLine("empty");
                } else {
                    Console.WriteLine(queue.Dequeue());
                }
            }
        }
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        Queue<String> queue = new LinkedList<>();

        for (int i = 0; i < n; i++) {
            String command = sc.next();

            if (command.equals("add")) {
                queue.add(sc.next());
            } else if (command.equals("run")) {
                if (queue.isEmpty()) {
                    System.out.println("empty");
                } else {
                    System.out.println(queue.poll());
                }
            }
        }
    }
}"""
