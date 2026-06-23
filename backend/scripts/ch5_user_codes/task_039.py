FIXED_PASCAL = """var s, res: string;
    i, count: integer;
begin
  readln(s);

  if s = '' then
    writeln('')
  else
  begin
    res := '';
    count := 1;

    for i := 2 to length(s) + 1 do
    begin
      if (i <= length(s)) and (s[i] = s[i - 1]) then
        count := count + 1
      else
      begin
        res := res + s[i - 1] + IntToStr(count);
        count := 1;
      end;
    end;

    writeln(res);
  end;
end."""

BUGGY_PASCAL = """var s, res: string;
    i, count: integer;
begin
  s := input();

  res = "";
  count := 0;

  for i in range(1, len(s)) do
  begin
    if s[i] == s[i - 1] then
      count += 1
    else
    begin
      res := res + s[i] + str(count);
      count := 0;
    end;
  end;

  print(res);
end."""

FIXED_PYTHON = """s = input()

if s == '':
    print('')
else:
    result = ''
    count = 1

    for i in range(1, len(s) + 1):
        if i < len(s) and s[i] == s[i - 1]:
            count += 1
        else:
            result += s[i - 1] + str(count)
            count = 1

    print(result)"""

BUGGY_PYTHON = """s = Console.ReadLine()

StringBuilder result = new StringBuilder()
count := 0

for i := 1 to len(s) do:
    if s[i] = s[i - 1]:
        count++
    else:
        result.Append(s[i])
        result.Append(count)
        count = 0

Console.WriteLine(result.ToString())"""

FIXED_CPP = """#include <iostream>
#include <string>

int main() {
    std::string s;
    std::getline(std::cin, s);

    if (s.empty()) {
        std::cout << "";
    } else {
        std::string result = "";
        int count = 1;

        for (int i = 1; i <= (int)s.size(); i++) {
            if (i < (int)s.size() && s[i] == s[i - 1]) {
                count++;
            } else {
                result += s[i - 1];
                result += std::to_string(count);
                count = 1;
            }
        }

        std::cout << result;
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <string>

int main() {
    string s = input();

    StringBuilder result;
    int count := 0;

    for i in range(1, s.length()):
        if (s[i] = s[i - 1]) {
            count++;
        } else {
            result.Append(s[i]);
            result.Append(count);
            count = 0;
        }

    Console.WriteLine(result.ToString());
    return 0;
}"""

FIXED_CSHARP = """using System;
using System.Text;

class Program {
    static void Main() {
        string s = Console.ReadLine();

        if (s == "") {
            Console.WriteLine("");
        } else {
            StringBuilder result = new StringBuilder();
            int count = 1;

            for (int i = 1; i <= s.Length; i++) {
                if (i < s.Length && s[i] == s[i - 1]) {
                    count++;
                } else {
                    result.Append(s[i - 1]);
                    result.Append(count);
                    count = 1;
                }
            }

            Console.WriteLine(result.ToString());
        }
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static void Main() {
        string s = input();

        string result := "";
        int count = 0;

        for i in range(1, s.Length):
            if (s[i] = s[i - 1]) {
                count++;
            } else {
                result += s[i] + str(count);
                count = 0;
            }

        print(result);
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        String s = sc.nextLine();

        if (s.equals("")) {
            System.out.println("");
        } else {
            StringBuilder result = new StringBuilder();
            int count = 1;

            for (int i = 1; i <= s.length(); i++) {
                if (i < s.length() && s.charAt(i) == s.charAt(i - 1)) {
                    count++;
                } else {
                    result.append(s.charAt(i - 1));
                    result.append(count);
                    count = 1;
                }
            }

            System.out.println(result.toString());
        }
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        String s = input();

        string result = "";
        int count := 0;

        for i in range(1, s.length()):
            if (s[i] = s[i - 1]) {
                count++;
            } else {
                result += s[i] + str(count);
                count = 0;
            }

        Console.WriteLine(result);
    }
}"""
