FIXED_PASCAL = """function IsPrime(n: integer): boolean;
var i: integer;
begin
  if n < 2 then
  begin
    IsPrime := false;
    exit;
  end;

  i := 2;

  while i * i <= n do
  begin
    if n mod i = 0 then
    begin
      IsPrime := false;
      exit;
    end;

    i := i + 1;
  end;

  IsPrime := true;
end;

var n: integer;
begin
  readln(n);

  if IsPrime(n) then
    writeln('prime')
  else
    writeln('composite');
end."""

BUGGY_PASCAL = """function IsPrime(n: integer): boolean;
var i: integer;
begin
  if n < 2 then
    return false;

  i = 2;

  while i * i <= n && IsPrime do
  begin
    if n % i == 0 then
      IsPrime = false;

    i++;
  end;

  return true;
end;

var n: integer;
begin
  n := int(input());

  if IsPrime(n) then
    print('prime')
  else
    writeln('composite');
end."""

FIXED_PYTHON = """def is_prime(n):
    if n < 2:
        return False

    i = 2

    while i * i <= n:
        if n % i == 0:
            return False
        i += 1

    return True

n = int(input())

print('prime' if is_prime(n) else 'composite')"""

BUGGY_PYTHON = """def is_prime(n)
    if n < 2:
        return false

    i := 2

    while i * i <= n && is_prime:
        if n mod i = 0:
            return False
        i++

    return True

n = int.Parse(Console.ReadLine())
Console.WriteLine('prime' if is_prime(n) else 'composite')"""

FIXED_CPP = """#include <iostream>

bool isPrime(int n) {
    if (n < 2) {
        return false;
    }

    for (int i = 2; i * i <= n; i++) {
        if (n % i == 0) {
            return false;
        }
    }

    return true;
}

int main() {
    int n;
    std::cin >> n;

    std::cout << (isPrime(n) ? "prime" : "composite");
    return 0;
}"""

BUGGY_CPP = """#include <iostream>

bool isPrime(int n) {
    if n < 2 {
        return False;
    }

    for i in range(2, sqrt(n)) {
        if (n mod i == 0) {
            return false;
        }
    }

    return true;
}

int main() {
    int n = int(input());

    Console.WriteLine(isPrime(n) ? "prime" : "composite");
    return 0;
}"""

FIXED_CSHARP = """using System;

class Program {
    static bool IsPrime(int n) {
        if (n < 2) {
            return false;
        }

        for (int i = 2; i * i <= n; i++) {
            if (n % i == 0) {
                return false;
            }
        }

        return true;
    }

    static void Main() {
        int n = int.Parse(Console.ReadLine());

        Console.WriteLine(IsPrime(n) ? "prime" : "composite");
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static bool IsPrime(int n) {
        if n < 2 {
            return False;
        }

        for i in range(2, Math.Sqrt(n)) {
            if (n mod i == 0) {
                return false;
            }
        }

        return true;
    }

    static void Main() {
        int n = int(input());

        print(IsPrime(n) ? "prime" : "composite");
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    static boolean isPrime(int n) {
        if (n < 2) {
            return false;
        }

        for (int i = 2; i * i <= n; i++) {
            if (n % i == 0) {
                return false;
            }
        }

        return true;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();

        System.out.println(isPrime(n) ? "prime" : "composite");
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    static bool isPrime(int n) {
        if n < 2 {
            return False;
        }

        for i in range(2, sqrt(n)) {
            if (n mod i == 0) {
                return false;
            }
        }

        return true;
    }

    public static void main(String[] args) {
        int n = int(input());

        Console.WriteLine(isPrime(n) ? "prime" : "composite");
    }
}"""
