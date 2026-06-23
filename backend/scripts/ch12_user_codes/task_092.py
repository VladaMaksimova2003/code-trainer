FIXED_PASCAL = """var n, i, top: integer;
    line, action: string;
    st: array[1..100] of string;
begin
  readln(n);
  top := 0;

  for i := 1 to n do
  begin
    readln(line);

    if copy(line, 1, 2) = 'do' then
    begin
      action := copy(line, 4, length(line));
      top := top + 1;
      st[top] := action;
    end
    else if line = 'undo' then
    begin
      if top > 0 then
      begin
        writeln(st[top]);
        top := top - 1;
      end
      else
        writeln('nothing');
    end;
  end;
end."""

BUGGY_PASCAL = """var n, i, top: integer;
    line, action: string;
    st: array[1..100] of string;
begin
  n := int(input());
  top = 0;

  for i in range(n) do
  begin
    line := input();

    if line.startsWith('do') then
    begin
      action := line.split(' ')[1];
      st.push(action);
    end
    else if line = 'undo' then
    begin
      if top >= 0 then
        print(st[0])
      else
        writeln('nothing');
    end;
  end;
end."""

FIXED_PYTHON = """n = int(input())
actions = []

for _ in range(n):
    command = input().split()

    if command[0] == 'do':
        actions.append(command[1])
    elif command[0] == 'undo':
        if actions:
            print(actions.pop())
        else:
            print('nothing')"""

BUGGY_PYTHON = """n = int.Parse(Console.ReadLine())
actions = new Stack<string>()

for i := 1 to n do:
    command = input().split()

    if command[0] = 'do':
        actions.Push(command[1])
    elif command[0] == 'undo':
        if actions.Count > 0:
            print(actions[0])
        else:
            Console.WriteLine('nothing')"""

FIXED_CPP = """#include <iostream>
#include <stack>
#include <string>

int main() {
    int n;
    std::cin >> n;

    std::stack<std::string> actions;

    for (int i = 0; i < n; i++) {
        std::string command;
        std::cin >> command;

        if (command == "do") {
            std::string action;
            std::cin >> action;
            actions.push(action);
        } else if (command == "undo") {
            if (actions.empty()) {
                std::cout << "nothing\n";
            } else {
                std::cout << actions.top() << '\n';
                actions.pop();
            }
        }
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <stack>

int main() {
    int n = int(input());
    Stack<string> actions;

    for i in range(n):
        string command;
        cin >> command;

        if (command = "do") {
            string action;
            cin >> action;
            actions.add(action);
        } else if (command == "undo") {
            if (actions.Count == 0) {
                Console.WriteLine("nothing");
            } else {
                cout << actions.front();
                actions.pop();
            }
        }

    return 0;
}"""

FIXED_CSHARP = """using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());
        Stack<string> actions = new Stack<string>();

        for (int i = 0; i < n; i++) {
            string[] parts = Console.ReadLine().Split();

            if (parts[0] == "do") {
                actions.Push(parts[1]);
            } else if (parts[0] == "undo") {
                if (actions.Count == 0) {
                    Console.WriteLine("nothing");
                } else {
                    Console.WriteLine(actions.Pop());
                }
            }
        }
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static void Main() {
        int n = int(input());
        Stack<string> actions = [];

        for i in range(n):
            string[] parts = Console.ReadLine().Split();

            if (parts[0] = "do") {
                actions.Add(parts[1]);
            } else if (parts[0] == "undo") {
                if (actions.Length == 0) {
                    print("nothing");
                } else {
                    Console.WriteLine(actions[0]);
                }
            }
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        Stack<String> actions = new Stack<>();

        for (int i = 0; i < n; i++) {
            String command = sc.next();

            if (command.equals("do")) {
                actions.push(sc.next());
            } else if (command.equals("undo")) {
                if (actions.empty()) {
                    System.out.println("nothing");
                } else {
                    System.out.println(actions.pop());
                }
            }
        }
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        int n = int(input());
        Stack<String> actions = new Stack<>();

        for i in range(n):
            String command = Scanner.next();

            if (command == "do") {
                actions.add(Scanner.next());
            } else if (command == "undo") {
                if (actions.Count == 0) {
                    Console.WriteLine("nothing");
                } else {
                    System.out.println(actions.get(0));
                }
            }
    }
}"""
