FIXED_PASCAL = """var n, i: integer;
    prime: boolean;
begin
  readln(n);

  prime := n > 1;
  i := 2;

  while (i * i <= n) and prime do
  begin
    if n mod i = 0 then
      prime := false;

    i := i + 1;
  end;

  if prime then
    writeln('yes')
  else
    writeln('no');
end."""

BUGGY_PASCAL = """var n, i: integer;
    prime: boolean;
begin
  readln(n);

  prime := n >= 1;
  i := 2;

  while i * i <= n do
  begin
    if n mod i = 0 then
      prime := false;

    i := i + 1;
  end;

  if prime then
    writeln('yes')
  else
    writeln('no');
end."""

FIXED_PYTHON = """n = int(input())

prime = n > 1
i = 2

while i * i <= n and prime:
    if n % i == 0:
        prime = False
    i += 1

print('yes' if prime else 'no')"""

BUGGY_PYTHON = """n = int(input())

prime = n >= 1
i = 2

while i * i <= n:
    if n % i == 0:
        prime = False
    i += 1

print('yes' if prime else 'no')"""

FIXED_CPP = """#include <iostream>

int main() {
    int n;
    std::cin >> n;

    bool prime = n > 1;

    for (int i = 2; i * i <= n && prime; i++) {
        if (n % i == 0) {
            prime = false;
        }
    }

    std::cout << (prime ? "yes" : "no");
    return 0;
}"""

BUGGY_CPP = """#include <iostream>

int main() {
    int n;
    std::cin >> n;

    bool prime = n >= 1;

    for (int i = 2; i * i <= n; i++) {
        if (n % i == 0) {
            prime = false;
        }
    }

    std::cout << (prime ? "yes" : "no");
    return 0;
}"""

FIXED_CSHARP = """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());

        bool prime = n > 1;

        for (int i = 2; i * i <= n && prime; i++) {
            if (n % i == 0) {
                prime = false;
            }
        }

        Console.WriteLine(prime ? "yes" : "no");
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static void Main() {
        int n = int.Parse(Console.ReadLine());

        bool prime = n >= 1;

        for (int i = 2; i * i <= n; i++) {
            if (n % i == 0) {
                prime = false;
            }
        }

        Console.WriteLine(prime ? "yes" : "no");
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        boolean prime = n > 1;

        for (int i = 2; i * i <= n && prime; i++) {
            if (n % i == 0) {
                prime = false;
            }
        }

        System.out.println(prime ? "yes" : "no");
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        boolean prime = n >= 1;

        for (int i = 2; i * i <= n; i++) {
            if (n % i == 0) {
                prime = false;
            }
        }

        System.out.println(prime ? "yes" : "no");
    }
}"""

# Translation / reference codes (implement slot)
PASCAL = FIXED_PASCAL
PYTHON = FIXED_PYTHON
CPP = FIXED_CPP
CSHARP = FIXED_CSHARP
JAVA = FIXED_JAVA
