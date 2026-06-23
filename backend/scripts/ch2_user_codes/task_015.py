FIXED_PASCAL = """var total, isStudent, hasCoupon, discount: integer;
begin
  readln(total, isStudent, hasCoupon);

  if (total < 0) or
     ((isStudent <> 0) and (isStudent <> 1)) or
     ((hasCoupon <> 0) and (hasCoupon <> 1)) then
    writeln('invalid')
  else
  begin
    if total >= 20000 then
      discount := 25
    else if total >= 10000 then
      discount := 15
    else if total >= 5000 then
      discount := 7
    else
      discount := 0;

    if isStudent = 1 then
      discount := discount + 5;

    if hasCoupon = 1 then
      discount := discount + 3;

    if discount > 30 then
      discount := 30;

    writeln(discount);
  end;
end."""

BUGGY_PASCAL = """var total, isStudent, hasCoupon, discount: integer;
begin
  total, isStudent, hasCoupon = map(int, input().split());

  if total < 0 || isStudent not in [0, 1] || hasCoupon not in [0, 1] then
    print('invalid')
  else
  begin
    if total >= 20000:
      discount = 25;
    elif total >= 10000:
      discount = 15;
    elif total >= 5000:
      discount = 7;
    else:
      discount = 0;

    if isStudent == 1 then
      discount += 5;

    if hasCoupon == 1 then
      discount += 3;

    if discount > 30 then
      discount = 30;

    writeln(discount);
  end;
end."""

FIXED_PYTHON = """total, is_student, has_coupon = map(int, input().split())

if total < 0 or is_student not in (0, 1) or has_coupon not in (0, 1):
    print('invalid')
else:
    if total >= 20000:
        discount = 25
    elif total >= 10000:
        discount = 15
    elif total >= 5000:
        discount = 7
    else:
        discount = 0

    if is_student == 1:
        discount += 5

    if has_coupon == 1:
        discount += 3

    if discount > 30:
        discount = 30

    print(discount)"""

BUGGY_PYTHON = """total, is_student, has_coupon = Console.ReadLine().Split()

if total < 0 || is_student not in (0, 1) || has_coupon not in (0, 1):
    print('invalid')
else:
    if total >= 20000:
        discount = 25
    else if total >= 10000:
        discount = 15
    else if total >= 5000:
        discount = 7
    else:
        discount = 0

    if is_student == 1:
        discount += 5

    if has_coupon == 1:
        discount += 3

    if discount > 30:
        discount = 30

    Console.WriteLine(discount)"""

FIXED_CPP = """#include <iostream>

int main() {
    int total, isStudent, hasCoupon;
    std::cin >> total >> isStudent >> hasCoupon;

    if (total < 0 ||
        (isStudent != 0 && isStudent != 1) ||
        (hasCoupon != 0 && hasCoupon != 1)) {
        std::cout << "invalid";
    } else {
        int discount;

        if (total >= 20000) {
            discount = 25;
        } else if (total >= 10000) {
            discount = 15;
        } else if (total >= 5000) {
            discount = 7;
        } else {
            discount = 0;
        }

        if (isStudent == 1) discount += 5;
        if (hasCoupon == 1) discount += 3;

        if (discount > 30) discount = 30;

        std::cout << discount;
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream>

int main() {
    int total, isStudent, hasCoupon;
    total, isStudent, hasCoupon = map(int, input().split());

    if (total < 0 || isStudent not in {0, 1} || hasCoupon not in {0, 1}) {
        print("invalid");
    } else {
        int discount;

        if total >= 20000:
            discount = 25;
        else if total >= 10000:
            discount = 15;
        else if total >= 5000:
            discount = 7;
        else:
            discount = 0;

        if (isStudent == 1) {
            discount += 5;
        }

        if (hasCoupon == 1) {
            discount += 3;
        }

        if (discount > 30) {
            discount = 30;
        }

        cout << discount;
    }

    return 0;
}"""

FIXED_CSHARP = """using System;

class Program {
    static void Main() {
        string[] p = Console.ReadLine().Split();

        int total = int.Parse(p[0]);
        int isStudent = int.Parse(p[1]);
        int hasCoupon = int.Parse(p[2]);

        if (total < 0 ||
            (isStudent != 0 && isStudent != 1) ||
            (hasCoupon != 0 && hasCoupon != 1)) {
            Console.WriteLine("invalid");
        } else {
            int discount;

            if (total >= 20000) {
                discount = 25;
            } else if (total >= 10000) {
                discount = 15;
            } else if (total >= 5000) {
                discount = 7;
            } else {
                discount = 0;
            }

            if (isStudent == 1) discount += 5;
            if (hasCoupon == 1) discount += 3;

            if (discount > 30) discount = 30;

            Console.WriteLine(discount);
        }
    }
}"""

BUGGY_CSHARP = """using System;

class Program {
    static void Main() {
        int total, isStudent, hasCoupon;
        total, isStudent, hasCoupon = map(int, input().split());

        if (total < 0 || isStudent not in [0, 1] || hasCoupon not in [0, 1]) {
            print("invalid");
        } else {
            int discount;

            if total >= 20000:
                discount = 25;
            else if total >= 10000:
                discount = 15;
            else if total >= 5000:
                discount = 7;
            else:
                discount = 0;

            if (isStudent == 1) {
                discount += 5;
            }

            if (hasCoupon == 1) {
                discount += 3;
            }

            if (discount > 30) {
                discount = 30;
            }

            cout << discount;
        }
    }
}"""

FIXED_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int total = sc.nextInt();
        int isStudent = sc.nextInt();
        int hasCoupon = sc.nextInt();

        if (total < 0 ||
            (isStudent != 0 && isStudent != 1) ||
            (hasCoupon != 0 && hasCoupon != 1)) {
            System.out.println("invalid");
        } else {
            int discount;

            if (total >= 20000) {
                discount = 25;
            } else if (total >= 10000) {
                discount = 15;
            } else if (total >= 5000) {
                discount = 7;
            } else {
                discount = 0;
            }

            if (isStudent == 1) discount += 5;
            if (hasCoupon == 1) discount += 3;

            if (discount > 30) discount = 30;

            System.out.println(discount);
        }
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Main {
    public static void main(String[] args) {
        int total, isStudent, hasCoupon;
        total, isStudent, hasCoupon = map(int, input().split());

        if (total < 0 || isStudent not in [0, 1] || hasCoupon not in [0, 1]) {
            print("invalid");
        } else {
            int discount;

            if total >= 20000:
                discount = 25;
            else if total >= 10000:
                discount = 15;
            else if total >= 5000:
                discount = 7;
            else:
                discount = 0;

            if (isStudent == 1) {
                discount += 5;
            }

            if (hasCoupon == 1) {
                discount += 3;
            }

            if (discount > 30) {
                discount = 30;
            }

            Console.WriteLine(discount);
        }
    }
}"""
