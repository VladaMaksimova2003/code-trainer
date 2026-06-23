FIXED_PASCAL = """var m: integer;
begin
  readln(m);

  case m of
    12, 1, 2: writeln('winter');
    3, 4, 5: writeln('spring');
    6, 7, 8: writeln('summer');
    9, 10, 11: writeln('autumn');
  else
    writeln('invalid');
  end;
end."""

BUGGY_PASCAL = """var m: integer;
begin
  m = int(input());

  switch(m) {
    case 12:
    case 1:
    case 2:
      writeln('winter');
      break;
    case 3:
    case 4:
    case 5:
      print('spring');
      break;
    default:
      writeln('invalid');
  }
end."""

FIXED_PYTHON = """m = int(input())

if m in (12, 1, 2):
    print('winter')
elif m in (3, 4, 5):
    print('spring')
elif m in (6, 7, 8):
    print('summer')
elif m in (9, 10, 11):
    print('autumn')
else:
    print('invalid')"""

BUGGY_PYTHON = """m = int(input())

switch (m):
    case 12:
    case 1:
    case 2:
        print('winter')
        break
    case 3:
    case 4:
    case 5:
        Console.WriteLine('spring')
        break
    default:
        print('invalid')"""

FIXED_CPP = """#include <iostream>

int main() {
    int m;
    std::cin >> m;

    switch (m) {
        case 12:
        case 1:
        case 2:
            std::cout << "winter";
            break;
        case 3:
        case 4:
        case 5:
            std::cout << "spring";
            break;
        case 6:
        case 7:
        case 8:
            std::cout << "summer";
            break;
        case 9:
        case 10:
        case 11:
            std::cout << "autumn";
            break;
        default:
            std::cout << "invalid";
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream>

int main() {
    int m;
    m = int(input());

    switch m {
        case 12, 1, 2:
            std::cout << "winter";
            break;
        case 3, 4, 5:
            print("spring");
            break;
        case 6, 7, 8:
            Console.WriteLine("summer");
            break;
        default:
            std::cout << "invalid";
    }

    return 0;
}"""

FIXED_CSHARP = """using System;

class Program {
    static void Main() {
        int m = int.Parse(Console.ReadLine());

        switch (m) {
            case 12:
            case 1:
            case 2:
                Console.WriteLine("winter");
                break;
            case 3:
            case 4:
            case 5:
                Console.WriteLine("spring");
                break;
            case 6:
            case 7:
            case 8:
                Console.WriteLine("summer");
                break;
            case 9:
            case 10:
            case 11:
                Console.WriteLine("autumn");
                break;
            default:
                Console.WriteLine("invalid");
                break;
        }
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static void Main() {
        int m;
        cin >> m;

        case m of
            12, 1, 2: Console.WriteLine("winter");
            3, 4, 5: print("spring");
            6, 7, 8: Console.WriteLine("summer");
            else Console.WriteLine("invalid");
        end;
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int m = sc.nextInt();

        switch (m) {
            case 12:
            case 1:
            case 2:
                System.out.println("winter");
                break;
            case 3:
            case 4:
            case 5:
                System.out.println("spring");
                break;
            case 6:
            case 7:
            case 8:
                System.out.println("summer");
                break;
            case 9:
            case 10:
            case 11:
                System.out.println("autumn");
                break;
            default:
                System.out.println("invalid");
        }
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        int m;
        cin >> m;

        case m of {
            12, 1, 2: System.out.println("winter");
            3, 4, 5: print("spring");
            6, 7, 8: Console.WriteLine("summer");
            else: System.out.println("invalid");
        }
    }
}"""
