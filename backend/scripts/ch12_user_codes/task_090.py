PASCAL = """var n, i, top: integer;
    command, page, current: string;
    history: array[1..100] of string;
begin
  readln(n);
  top := 0;
  current := 'home';

  for i := 1 to n do
  begin
    readln(command);

    if copy(command, 1, 5) = 'visit' then
    begin
      page := copy(command, 7, length(command));
      top := top + 1;
      history[top] := current;
      current := page;
    end
    else if command = 'back' then
    begin
      if top > 0 then
      begin
        current := history[top];
        top := top - 1;
      end;
    end
    else if command = 'current' then
      writeln(current);
  end;
end."""

PYTHON = """n = int(input())
history = []
current = 'home'

for _ in range(n):
    command = input().split()

    if command[0] == 'visit':
        history.append(current)
        current = command[1]
    elif command[0] == 'back':
        if history:
            current = history.pop()
    elif command[0] == 'current':
        print(current)"""

CPP = """#include <iostream>
#include <stack>
#include <string>

int main() {
    int n;
    std::cin >> n;

    std::stack<std::string> history;
    std::string current = "home";

    for (int i = 0; i < n; i++) {
        std::string command;
        std::cin >> command;

        if (command == "visit") {
            std::string page;
            std::cin >> page;

            history.push(current);
            current = page;
        } else if (command == "back") {
            if (!history.empty()) {
                current = history.top();
                history.pop();
            }
        } else if (command == "current") {
            std::cout << current << '\n';
        }
    }

    return 0;
}"""

CSHARP = """using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());

        Stack<string> history = new Stack<string>();
        string current = "home";

        for (int i = 0; i < n; i++) {
            string[] parts = Console.ReadLine().Split();

            if (parts[0] == "visit") {
                history.Push(current);
                current = parts[1];
            } else if (parts[0] == "back") {
                if (history.Count > 0) {
                    current = history.Pop();
                }
            } else if (parts[0] == "current") {
                Console.WriteLine(current);
            }
        }
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = Integer.parseInt(sc.nextLine());
        Stack<String> history = new Stack<>();
        String current = "home";

        for (int i = 0; i < n; i++) {
            String[] parts = sc.nextLine().split(" ");

            if (parts[0].equals("visit")) {
                history.push(current);
                current = parts[1];
            } else if (parts[0].equals("back")) {
                if (!history.empty()) {
                    current = history.pop();
                }
            } else if (parts[0].equals("current")) {
                System.out.println(current);
            }
        }
    }
}"""
