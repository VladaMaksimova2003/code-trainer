PASCAL = """var n, i, head, tail: integer;
    line, doc: string;
    q: array[1..100] of string;
begin
  readln(n);
  head := 1;
  tail := 0;

  for i := 1 to n do
  begin
    readln(line);

    if copy(line, 1, 5) = 'print' then
    begin
      doc := copy(line, 7, length(line));
      tail := tail + 1;
      q[tail] := doc;
    end
    else if line = 'next' then
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
printer = deque()

for _ in range(n):
    command = input().split()

    if command[0] == 'print':
        printer.append(command[1])
    elif command[0] == 'next':
        if printer:
            print(printer.popleft())
        else:
            print('empty')"""

CPP = """#include <iostream>
#include <queue>
#include <string>

int main() {
    int n;
    std::cin >> n;

    std::queue<std::string> printer;

    for (int i = 0; i < n; i++) {
        std::string command;
        std::cin >> command;

        if (command == "print") {
            std::string doc;
            std::cin >> doc;
            printer.push(doc);
        } else if (command == "next") {
            if (printer.empty()) {
                std::cout << "empty\n";
            } else {
                std::cout << printer.front() << '\n';
                printer.pop();
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
        Queue<string> printer = new Queue<string>();

        for (int i = 0; i < n; i++) {
            string[] parts = Console.ReadLine().Split();

            if (parts[0] == "print") {
                printer.Enqueue(parts[1]);
            } else if (parts[0] == "next") {
                if (printer.Count == 0) {
                    Console.WriteLine("empty");
                } else {
                    Console.WriteLine(printer.Dequeue());
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
        Queue<String> printer = new LinkedList<>();

        for (int i = 0; i < n; i++) {
            String command = sc.next();

            if (command.equals("print")) {
                printer.add(sc.next());
            } else if (command.equals("next")) {
                if (printer.isEmpty()) {
                    System.out.println("empty");
                } else {
                    System.out.println(printer.poll());
                }
            }
        }
    }
}"""
