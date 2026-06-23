PASCAL = """var n, i, top, head, tail, value: integer;
    command: string;
    stack, queue: array[1..100] of integer;
begin
  readln(n);

  top := 0;
  head := 1;
  tail := 0;

  for i := 1 to n do
  begin
    read(command);

    if command = 'push' then
    begin
      readln(value);
      top := top + 1;
      stack[top] := value;
    end
    else if command = 'pop' then
    begin
      readln;

      if top = 0 then
        writeln('empty')
      else
        top := top - 1;
    end
    else if command = 'enqueue' then
    begin
      readln(value);
      tail := tail + 1;
      queue[tail] := value;
    end
    else if command = 'front' then
    begin
      readln;

      if head <= tail then
        writeln(queue[head])
      else
        writeln('empty');
    end;
  end;
end."""

PYTHON = """from collections import deque

n = int(input())
stack = []
queue = deque()

for _ in range(n):
    command = input().split()

    if command[0] == 'push':
        stack.append(int(command[1]))
    elif command[0] == 'pop':
        if stack:
            stack.pop()
        else:
            print('empty')
    elif command[0] == 'enqueue':
        queue.append(int(command[1]))
    elif command[0] == 'front':
        if queue:
            print(queue[0])
        else:
            print('empty')"""

CPP = """#include <iostream>
#include <stack>
#include <queue>
#include <string>

int main() {
    int n;
    std::cin >> n;

    std::stack<int> st;
    std::queue<int> q;

    for (int i = 0; i < n; i++) {
        std::string command;
        std::cin >> command;

        if (command == "push") {
            int x;
            std::cin >> x;
            st.push(x);
        } else if (command == "pop") {
            if (st.empty()) {
                std::cout << "empty\n";
            } else {
                st.pop();
            }
        } else if (command == "enqueue") {
            int x;
            std::cin >> x;
            q.push(x);
        } else if (command == "front") {
            if (q.empty()) {
                std::cout << "empty\n";
            } else {
                std::cout << q.front() << '\n';
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

        Stack<int> stack = new Stack<int>();
        Queue<int> queue = new Queue<int>();

        for (int i = 0; i < n; i++) {
            string[] parts = Console.ReadLine().Split();

            if (parts[0] == "push") {
                stack.Push(int.Parse(parts[1]));
            } else if (parts[0] == "pop") {
                if (stack.Count == 0) {
                    Console.WriteLine("empty");
                } else {
                    stack.Pop();
                }
            } else if (parts[0] == "enqueue") {
                queue.Enqueue(int.Parse(parts[1]));
            } else if (parts[0] == "front") {
                if (queue.Count == 0) {
                    Console.WriteLine("empty");
                } else {
                    Console.WriteLine(queue.Peek());
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

        Stack<Integer> stack = new Stack<>();
        Queue<Integer> queue = new LinkedList<>();

        for (int i = 0; i < n; i++) {
            String command = sc.next();

            if (command.equals("push")) {
                stack.push(sc.nextInt());
            } else if (command.equals("pop")) {
                if (stack.empty()) {
                    System.out.println("empty");
                } else {
                    stack.pop();
                }
            } else if (command.equals("enqueue")) {
                queue.add(sc.nextInt());
            } else if (command.equals("front")) {
                if (queue.isEmpty()) {
                    System.out.println("empty");
                } else {
                    System.out.println(queue.peek());
                }
            }
        }
    }
}"""
