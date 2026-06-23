PASCAL = """function IsPalindrome(s: string): boolean;
var i: integer;
begin
  IsPalindrome := true;

  for i := 1 to length(s) div 2 do
    if s[i] <> s[length(s) - i + 1] then
    begin
      IsPalindrome := false;
      exit;
    end;
end;

var s: string;
begin
  readln(s);

  if IsPalindrome(s) then
    writeln('yes')
  else
    writeln('no');
end."""

PYTHON = """def is_palindrome(text):
    return text == text[::-1]

s = input()

print('yes' if is_palindrome(s) else 'no')"""

CPP = """#include <iostream>
#include <string>

bool isPalindrome(const std::string& text) {
    int left = 0;
    int right = text.size() - 1;

    while (left < right) {
        if (text[left] != text[right]) {
            return false;
        }

        left++;
        right--;
    }

    return true;
}

int main() {
    std::string s;
    std::getline(std::cin, s);

    std::cout << (isPalindrome(s) ? "yes" : "no");
    return 0;
}"""

CSHARP = """using System;

class Program {
    static bool IsPalindrome(string text) {
        int left = 0;
        int right = text.Length - 1;

        while (left < right) {
            if (text[left] != text[right]) {
                return false;
            }

            left++;
            right--;
        }

        return true;
    }

    static void Main() {
        string s = Console.ReadLine();

        Console.WriteLine(IsPalindrome(s) ? "yes" : "no");
    }
}"""

JAVA = """import java.util.*;

class Main {
    static boolean isPalindrome(String text) {
        int left = 0;
        int right = text.length() - 1;

        while (left < right) {
            if (text.charAt(left) != text.charAt(right)) {
                return false;
            }

            left++;
            right--;
        }

        return true;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        String s = sc.nextLine();

        System.out.println(isPalindrome(s) ? "yes" : "no");
    }
}"""
