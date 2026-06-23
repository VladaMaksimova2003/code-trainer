"""Recursion slot corruption fix — task_052 debug reverse, task_053 assemble palindrome."""

T052_TITLE = "Рекурсивный разворот строки"
T052_DESC = (
    "Дана строка s. Рекурсивно разверните строку и выведите результат."
)
T052_TESTS = [
    {"name": "Тест 1", "inputs": "hello\n", "output": "olleh"},
    {"name": "Тест 2", "inputs": "a\n", "output": "a"},
    {"name": "Тест 3", "inputs": "ab\n", "output": "ba"},
    {"name": "Тест 4", "inputs": "level\n", "output": "level"},
]

T052_REF = {
    "pascal": """function ReverseString(s: string): string;
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
end.""",
    "python": """def reverse_string(s):
    if len(s) <= 1:
        return s
    return s[-1] + reverse_string(s[:-1])


s = input()
print(reverse_string(s))""",
    "cpp": """#include <iostream>
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
}""",
    "csharp": """using System;

class Program {
    static string ReverseString(string s) {
        if (s.Length <= 1) return s;
        return s[s.Length - 1] + ReverseString(s.Substring(0, s.Length - 1));
    }

    static void Main() {
        string s = Console.ReadLine();
        Console.WriteLine(ReverseString(s));
    }
}""",
    "java": """import java.util.*;

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
}""",
}

T052_BUGGY = {
    "pascal": """function ReverseString(s: string): string;
begin
  if length(s) <= 1 then
    ReverseString := s
  else
    ReverseString := ReverseString(copy(s, 1, length(s) - 1));
end;

var s: string;
begin
  readln(s);
  writeln(ReverseString(s));
end.""",
    "python": """def reverse_string(s):
    if len(s) <= 1:
        return s
    return reverse_string(s[:-1])


s = input()
print(reverse_string(s))""",
    "cpp": """#include <iostream>
#include <string>

std::string reverseString(const std::string& s) {
    if (s.size() <= 1) return s;
    return reverseString(s.substr(0, s.size() - 1));
}

int main() {
    std::string s;
    std::getline(std::cin, s);

    std::cout << reverseString(s);
    return 0;
}""",
    "csharp": """using System;

class Program {
    static string ReverseString(string s) {
        if (s.Length <= 1) return s;
        return ReverseString(s.Substring(0, s.Length - 1));
    }

    static void Main() {
        string s = Console.ReadLine();
        Console.WriteLine(ReverseString(s));
    }
}""",
    "java": """import java.util.*;

class Main {
    static String reverseString(String s) {
        if (s.length() <= 1) return s;
        return reverseString(s.substring(0, s.length() - 1));
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        String s = sc.nextLine();
        System.out.println(reverseString(s));
    }
}""",
}

T052_HINTS = [
    "Базовый случай: строка длиной 0 или 1 уже «развёрнута».",
    "Рекурсивный шаг: первый символ результата — последний символ строки.",
    "Оставшуюся часть разворачивайте рекурсивно без последнего символа.",
]
T052_POST = (
    "Правильный reverse: last + reverse(prefix). "
    "Если рекурсия обрабатывает только s[:-1] и теряет последний символ на каждом шаге, "
    "строка не зеркалится."
)

T053_TITLE = "Рекурсивная проверка палиндрома"
T053_DESC = (
    "Дана строка s. Рекурсивно проверьте, является ли строка палиндромом, "
    "и выведите yes или no."
)
T053_TESTS = [
    {"name": "Тест 1", "inputs": "abba\n", "output": "yes"},
    {"name": "Тест 2", "inputs": "abc\n", "output": "no"},
    {"name": "Тест 3", "inputs": "a\n", "output": "yes"},
    {"name": "Тест 4", "inputs": "racecar\n", "output": "yes"},
]

T053_REF = {
    "pascal": """function IsPalindrome(s: string): boolean;
begin
  if length(s) <= 1 then
    IsPalindrome := true
  else if s[1] <> s[length(s)] then
    IsPalindrome := false
  else
    IsPalindrome := IsPalindrome(copy(s, 2, length(s) - 2));
end;

var s: string;
begin
  readln(s);
  if IsPalindrome(s) then
    writeln('yes')
  else
    writeln('no');
end.""",
    "python": """def is_palindrome(s):
    if len(s) <= 1:
        return True
    if s[0] != s[-1]:
        return False
    return is_palindrome(s[1:-1])


s = input()
print('yes' if is_palindrome(s) else 'no')""",
    "cpp": """#include <iostream>
#include <string>

bool isPalindrome(const std::string& s) {
    if (s.size() <= 1) return true;
    if (s.front() != s.back()) return false;
    return isPalindrome(s.substr(1, s.size() - 2));
}

int main() {
    std::string s;
    std::getline(std::cin, s);

    std::cout << (isPalindrome(s) ? "yes" : "no");
    return 0;
}""",
    "csharp": """using System;

class Program {
    static bool IsPalindrome(string s) {
        if (s.Length <= 1) return true;
        if (s[0] != s[s.Length - 1]) return false;
        return IsPalindrome(s.Substring(1, s.Length - 2));
    }

    static void Main() {
        string s = Console.ReadLine();
        Console.WriteLine(IsPalindrome(s) ? "yes" : "no");
    }
}""",
    "java": """import java.util.*;

class Main {
    static boolean isPalindrome(String s) {
        if (s.length() <= 1) return true;
        if (s.charAt(0) != s.charAt(s.length() - 1)) return false;
        return isPalindrome(s.substring(1, s.length() - 1));
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        String s = sc.nextLine();
        System.out.println(isPalindrome(s) ? "yes" : "no");
    }
}""",
}

T053_HINTS = [
    "Строка длиной 0 или 1 — палиндром (базовый случай).",
    "Сравните первый и последний символ; если они разные — ответ no.",
    "Иначе рекурсивно проверьте подстроку без первого и последнего символа.",
]
T053_POST = (
    "Рекурсивный палиндром: сравнить края, затем is_palindrome(s[1:-1]). "
    "Разворот строки или факториал — другие алгоритмы и не подходят под условие yes/no."
)

T052_CONCEPTS = [
    "program_entry",
    "typed_declaration",
    "assignment",
    "stdin_read",
    "stdout_write",
    "function_definition",
    "function_invocation",
    "recursion",
]

T053_CONCEPTS = list(T052_CONCEPTS)
