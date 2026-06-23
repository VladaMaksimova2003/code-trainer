FIXED_PASCAL = """var s: string;
    i, count: integer;
    inWord: boolean;
begin
  readln(s);

  count := 0;
  inWord := false;

  for i := 1 to length(s) do
  begin
    if s[i] <> ' ' then
    begin
      if not inWord then
        count := count + 1;

      inWord := true;
    end
    else
      inWord := false;
  end;

  writeln(count);
end."""

BUGGY_PASCAL = """var s: string;
    words: array of string;
begin
  s := input().strip();

  words := s.split(" ");

  if s == "" then
    print(0)
  else
    writeln(words.length);
end."""

FIXED_PYTHON = """s = input().strip()

if s == '':
    print(0)
else:
    print(len(s.split()))"""

BUGGY_PYTHON = """string s = Console.ReadLine()

words = s.Split(" ")

if s = "":
    Console.WriteLine(0)
else:
    print(words.Length)"""

FIXED_CPP = """#include <iostream>
#include <string>
#include <sstream>

int main() {
    std::string s;
    std::getline(std::cin, s);

    std::stringstream ss(s);
    std::string word;

    int count = 0;

    while (ss >> word) {
        count++;
    }

    std::cout << count;
    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <string>

int main() {
    string s = input().strip();

    string[] words = s.split(" ");

    if (s == "") {
        print(0);
    } else {
        cout << words.Length;
    }

    return 0;
}"""

FIXED_CSHARP = """using System;

class Program {
    static void Main() {
        string s = Console.ReadLine();

        string[] words = s.Split(
            new char[] { ' ' },
            StringSplitOptions.RemoveEmptyEntries
        );

        Console.WriteLine(words.Length);
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static void Main() {
        string s = input().strip();

        string[] words = s.split(" ");

        if s == "" {
            print(0);
        } else {
            Console.WriteLine(len(words));
        }
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        String s = sc.nextLine().trim();

        if (s.equals("")) {
            System.out.println(0);
        } else {
            String[] words = s.split("\\s+");
            System.out.println(words.length);
        }
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        String s = input().strip();

        String[] words = s.Split(" ");

        if (s == "") {
            Console.WriteLine(0);
        } else {
            print(words.Length);
        }
    }
}"""

PASCAL = FIXED_PASCAL
PYTHON = FIXED_PYTHON
CPP = FIXED_CPP
CSHARP = FIXED_CSHARP
JAVA = FIXED_JAVA
