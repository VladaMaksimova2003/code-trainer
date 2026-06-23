PASCAL = """var s: string;
    i, top: integer;
    st: array[1..100] of char;
    ok: boolean;
begin
  readln(s);
  top := 0;
  ok := true;

  for i := 1 to length(s) do
  begin
    if s[i] = '(' then
    begin
      top := top + 1;
      st[top] := '(';
    end
    else if s[i] = ')' then
    begin
      if top = 0 then
        ok := false
      else
        top := top - 1;
    end;
  end;

  if ok and (top = 0) then
    writeln('ok')
  else
    writeln('bad');
end."""

PYTHON = """stack = []

for ch in input():
    if ch == '(':
        stack.append(ch)
    elif ch == ')':
        if not stack:
            print('bad')
            break
        stack.pop()
else:
    print('ok' if not stack else 'bad')"""

CPP = """#include <iostream>
#include <stack>
#include <string>

int main() {
    std::string s;
    std::cin >> s;

    std::stack<char> st;
    bool ok = true;

    for (char ch : s) {
        if (ch == '(') {
            st.push(ch);
        } else if (ch == ')') {
            if (st.empty()) {
                ok = false;
            } else {
                st.pop();
            }
        }
    }

    std::cout << (ok && st.empty() ? "ok" : "bad");
    return 0;
}"""

CSHARP = """using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        string s = Console.ReadLine();

        Stack<char> stack = new Stack<char>();
        bool ok = true;

        foreach (char ch in s) {
            if (ch == '(') {
                stack.Push(ch);
            } else if (ch == ')') {
                if (stack.Count == 0) {
                    ok = false;
                } else {
                    stack.Pop();
                }
            }
        }

        Console.WriteLine(ok && stack.Count == 0 ? "ok" : "bad");
    }
}"""

JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.next();

        Stack<Character> stack = new Stack<>();
        boolean ok = true;

        for (char ch : s.toCharArray()) {
            if (ch == '(') {
                stack.push(ch);
            } else if (ch == ')') {
                if (stack.empty()) {
                    ok = false;
                } else {
                    stack.pop();
                }
            }
        }

        System.out.println(ok && stack.empty() ? "ok" : "bad");
    }
}"""
