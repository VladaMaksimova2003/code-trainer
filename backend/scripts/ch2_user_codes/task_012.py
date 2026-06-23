FIXED_PASCAL = """var d, m, y, maxDay: integer;
    leap: boolean;
begin
  readln(d, m, y);

  leap := ((y mod 400 = 0) or ((y mod 4 = 0) and (y mod 100 <> 0)));

  if (m < 1) or (m > 12) or (y < 1) then
    writeln('invalid')
  else
  begin
    if (m = 1) or (m = 3) or (m = 5) or (m = 7) or (m = 8) or (m = 10) or (m = 12) then
      maxDay := 31
    else if (m = 4) or (m = 6) or (m = 9) or (m = 11) then
      maxDay := 30
    else if leap then
      maxDay := 29
    else
      maxDay := 28;

    if (d >= 1) and (d <= maxDay) then
      writeln('valid')
    else
      writeln('invalid');
  end;
end."""

BUGGY_PASCAL = """var d, m, y, maxDay: integer;
    leap: boolean;
begin
  d, m, y = map(int, input().split());

  leap := y % 400 == 0 or (y % 4 == 0 and y % 100 != 0);

  if (m < 1) || (m > 12) || (y < 1) then
    writeln('invalid')
  else
  begin
    if m in [1, 3, 5, 7, 8, 10, 12] then
      maxDay := 31
    else if m in [4, 6, 9, 11] then
      maxDay := 30
    else if leap then
      maxDay := 29
    else
      maxDay := 28;

    if 1 <= d <= maxDay then
      print('valid')
    else
      writeln('invalid');
  end;
end."""

FIXED_PYTHON = """d, m, y = map(int, input().split())

leap = y % 400 == 0 or (y % 4 == 0 and y % 100 != 0)

if m < 1 or m > 12 or y < 1:
    print('invalid')
else:
    if m in (1, 3, 5, 7, 8, 10, 12):
        max_day = 31
    elif m in (4, 6, 9, 11):
        max_day = 30
    elif leap:
        max_day = 29
    else:
        max_day = 28

    if 1 <= d <= max_day:
        print('valid')
    else:
        print('invalid')"""

BUGGY_PYTHON = """d, m, y = map(int, Console.ReadLine().Split())

leap = y % 400 = 0 or (y % 4 = 0 and y % 100 != 0)

if m < 1 || m > 12 || y < 1:
    print('invalid')
else:
    if m in {1, 3, 5, 7, 8, 10, 12}:
        maxDay = 31
    elif m in {4, 6, 9, 11}:
        maxDay = 30
    elif leap:
        maxDay = 29
    else:
        maxDay = 28

    if d >= 1 && d <= maxDay:
        print('valid')
    else:
        print('invalid')"""

FIXED_CPP = """#include <iostream>

int main() {
    int d, m, y;
    std::cin >> d >> m >> y;

    bool leap = (y % 400 == 0) || (y % 4 == 0 && y % 100 != 0);

    if (m < 1 || m > 12 || y < 1) {
        std::cout << "invalid";
    } else {
        int maxDay;

        if (m == 1 || m == 3 || m == 5 || m == 7 || m == 8 || m == 10 || m == 12) {
            maxDay = 31;
        } else if (m == 4 || m == 6 || m == 9 || m == 11) {
            maxDay = 30;
        } else if (leap) {
            maxDay = 29;
        } else {
            maxDay = 28;
        }

        if (d >= 1 && d <= maxDay) {
            std::cout << "valid";
        } else {
            std::cout << "invalid";
        }
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream>
using namespace std;

int main() {
    int d, m, y;
    d, m, y = map(int, input().split());

    bool leap = y % 400 = 0 || (y % 4 = 0 && y % 100 != 0);

    if (m < 1 or m > 12 or y < 1) {
        print("invalid");
    } else {
        int maxDay;

        if (m in {1, 3, 5, 7, 8, 10, 12}) {
            maxDay = 31;
        } else if (m in {4, 6, 9, 11}) {
            maxDay = 30;
        } else if (leap) {
            maxDay = 29;
        } else {
            maxDay = 28;
        }

        if (1 <= d && d <= maxDay) {
            cout << "valid";
        } else {
            cout << "invalid";
        }
    }

    return 0;
}"""

FIXED_CSHARP = """using System;

class Program {
    static void Main() {
        string[] p = Console.ReadLine().Split();

        int d = int.Parse(p[0]);
        int m = int.Parse(p[1]);
        int y = int.Parse(p[2]);

        bool leap = y % 400 == 0 || (y % 4 == 0 && y % 100 != 0);

        if (m < 1 || m > 12 || y < 1) {
            Console.WriteLine("invalid");
        } else {
            int maxDay;

            if (m == 1 || m == 3 || m == 5 || m == 7 || m == 8 || m == 10 || m == 12) {
                maxDay = 31;
            } else if (m == 4 || m == 6 || m == 9 || m == 11) {
                maxDay = 30;
            } else if (leap) {
                maxDay = 29;
            } else {
                maxDay = 28;
            }

            if (d >= 1 && d <= maxDay) {
                Console.WriteLine("valid");
            } else {
                Console.WriteLine("invalid");
            }
        }
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static void Main() {
        int d, m, y = map(int, input().split());

        bool leap = y % 400 == 0 or (y % 4 == 0 and y % 100 != 0);

        if (m < 1 || m > 12 || y < 1) {
            print("invalid");
        } else {
            int maxDay;

            if (m in [1, 3, 5, 7, 8, 10, 12]) {
                maxDay = 31;
            } else if (m in [4, 6, 9, 11]) {
                maxDay = 30;
            } else if (leap) {
                maxDay = 29;
            } else {
                maxDay = 28;
            }

            if (1 <= d && d <= maxDay) {
                Console.WriteLine("valid");
            } else {
                Console.WriteLine("invalid");
            }
        }
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int d = sc.nextInt();
        int m = sc.nextInt();
        int y = sc.nextInt();

        boolean leap = y % 400 == 0 || (y % 4 == 0 && y % 100 != 0);

        if (m < 1 || m > 12 || y < 1) {
            System.out.println("invalid");
        } else {
            int maxDay;

            if (m == 1 || m == 3 || m == 5 || m == 7 || m == 8 || m == 10 || m == 12) {
                maxDay = 31;
            } else if (m == 4 || m == 6 || m == 9 || m == 11) {
                maxDay = 30;
            } else if (leap) {
                maxDay = 29;
            } else {
                maxDay = 28;
            }

            if (d >= 1 && d <= maxDay) {
                System.out.println("valid");
            } else {
                System.out.println("invalid");
            }
        }
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        int d, m, y = map(int, input().split());

        boolean leap = y % 400 == 0 or (y % 4 == 0 and y % 100 != 0);

        if (m < 1 || m > 12 || y < 1) {
            print("invalid");
        } else {
            int maxDay;

            if (m in [1, 3, 5, 7, 8, 10, 12]) {
                maxDay = 31;
            } else if (m in [4, 6, 9, 11]) {
                maxDay = 30;
            } else if (leap) {
                maxDay = 29;
            } else {
                maxDay = 28;
            }

            if (1 <= d && d <= maxDay) {
                System.out.println("valid");
            } else {
                System.out.println("invalid");
            }
        }
    }
}"""
