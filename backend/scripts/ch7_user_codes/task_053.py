PASCAL = """function ReverseString(s: string): string;
begin
  if length(s) <= 1 then
    ReverseString := s
  else
    ReverseString := s[length(s)] + ReverseString(copy(s, 1, length(s) - 1));
end;

var s: string;
begin
  readln(s);
  writeln(ReverseString(s));
end."""

PYTHON = """def reverse_string(s):
    if len(s) <= 1:
        return s
    return s[-1] + reverse_string(s[:-1])

s = input()
print(reverse_string(s))"""

CPP = """#include <iostream>
#include <string>

std::string reverseString(const std::string& s) {
    if (s.size() <= 1) return s;
    return s.back() + reverseString(s.substr(0, s.size() - 1));
}

int main() {
    std::string s;
    std::getline(std::cin, s);

    std::cout << reverseString(s);
    return 0;
}"""

CSHARP = """using System;

class Program {
    static string ReverseString(string s) {
        if (s.Length <= 1) return s;
        return s[s.Length - 1] + ReverseString(s.Substring(0, s.Length - 1));
    }

    static void Main() {
        string s = Console.ReadLine();
        Console.WriteLine(ReverseString(s));
    }
}"""

JAVA = """import java.util.*;

class Main {
    static String reverseString(String s) {
        if (s.length() <= 1) return s;
        return s.charAt(s.length() - 1) + reverseString(s.substring(0, s.length() - 1));
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        String s = sc.nextLine();
        System.out.println(reverseString(s));
    }
}"""
