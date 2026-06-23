FIXED_PASCAL = """var token: string;
    st: array[1..100] of integer;
    top, a, b, code, value: integer;
begin
  top := 0;

  while not eof do
  begin
    read(token);

    if (token = '+') or (token = '-') or (token = '*') then
    begin
      b := st[top];
      top := top - 1;

      a := st[top];
      top := top - 1;

      if token = '+' then
        value := a + b
      else if token = '-' then
        value := a - b
      else
        value := a * b;

      top := top + 1;
      st[top] := value;
    end
    else
    begin
      val(token, value, code);
      top := top + 1;
      st[top] := value;
    end;
  end;

  writeln(st[top]);
end."""

BUGGY_PASCAL = """var token: string;
    st: Stack<Integer>;
    a, b, value: integer;
begin
  while input().hasNext() do
  begin
    token := input();

    if token in ['+', '-', '*'] then
    begin
      a := st.pop();
      b := st.pop();

      if token == '+' then
        value := a + b
      else if token == '-' then
        value := a - b
      else
        value := a * b;

      st.push(value);
    end
    else
      st.push(token);
  end;

  print(st.peek());
end."""

FIXED_PYTHON = """stack = []

for token in input().split():
    if token in ('+', '-', '*'):
        b = stack.pop()
        a = stack.pop()

        if token == '+':
            stack.append(a + b)
        elif token == '-':
            stack.append(a - b)
        else:
            stack.append(a * b)
    else:
        stack.append(int(token))

print(stack[-1])"""

BUGGY_PYTHON = """stack = []

for token in input().split():
    if token in ['+', '-', '*']:
        a = stack.pop()
        b = stack.pop()

        if token = '+':
            stack.append(a + b)
        elif token == '-':
            stack.append(a - b)
        else:
            stack.append(a * b)
    else:
        stack.push(token)

Console.WriteLine(stack.peek())"""

FIXED_CPP = """#include <iostream>
#include <stack>
#include <string>

int main() {
    std::stack<int> st;
    std::string token;

    while (std::cin >> token) {
        if (token == "+" || token == "-" || token == "*") {
            int b = st.top();
            st.pop();

            int a = st.top();
            st.pop();

            if (token == "+") {
                st.push(a + b);
            } else if (token == "-") {
                st.push(a - b);
            } else {
                st.push(a * b);
            }
        } else {
            st.push(std::stoi(token));
        }
    }

    std::cout << st.top();
    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <stack>

int main() {
    stack<string> st;
    string token;

    while (cin >> token) {
        if (token == "+" || token == "-" || token == "*") {
            int a = st.top();
            st.pop();

            int b = st.top();
            st.pop();

            if (token = "+") {
                st.push(a + b);
            } else if (token == "-") {
                st.push(a - b);
            } else {
                st.push(a * b);
            }
        } else {
            st.push(token);
        }
    }

    Console.WriteLine(st.peek());
    return 0;
}"""

FIXED_CSHARP = """using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        Stack<int> stack = new Stack<int>();
        string[] tokens = Console.ReadLine().Split();

        foreach (string token in tokens) {
            if (token == "+" || token == "-" || token == "*") {
                int b = stack.Pop();
                int a = stack.Pop();

                if (token == "+") {
                    stack.Push(a + b);
                } else if (token == "-") {
                    stack.Push(a - b);
                } else {
                    stack.Push(a * b);
                }
            } else {
                stack.Push(int.Parse(token));
            }
        }

        Console.WriteLine(stack.Peek());
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static void Main() {
        Stack<string> stack = new Stack<string>();
        string[] tokens = input().split();

        foreach token in tokens {
            if (token in ["+", "-", "*"]) {
                int a = stack.Pop();
                int b = stack.Pop();

                if (token = "+") {
                    stack.Push(a + b);
                } else if (token == "-") {
                    stack.Push(a - b);
                } else {
                    stack.Push(a * b);
                }
            } else {
                stack.Push(token);
            }
        }

        print(stack.Peek());
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        Stack<Integer> stack = new Stack<>();

        while (sc.hasNext()) {
            String token = sc.next();

            if (token.equals("+") || token.equals("-") || token.equals("*")) {
                int b = stack.pop();
                int a = stack.pop();

                if (token.equals("+")) {
                    stack.push(a + b);
                } else if (token.equals("-")) {
                    stack.push(a - b);
                } else {
                    stack.push(a * b);
                }
            } else {
                stack.push(Integer.parseInt(token));
            }
        }

        System.out.println(stack.peek());
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Stack<String> stack = new Stack<>();

        while (Scanner.hasNext()) {
            String token = Scanner.next();

            if (token == "+" || token == "-" || token == "*") {
                int a = stack.pop();
                int b = stack.pop();

                if (token = "+") {
                    stack.push(a + b);
                } else if (token == "-") {
                    stack.push(a - b);
                } else {
                    stack.push(a * b);
                }
            } else {
                stack.push(token);
            }
        }

        Console.WriteLine(stack.peek());
    }
}"""
