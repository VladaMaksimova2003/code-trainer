PASCAL = """program Ch126;
uses SysUtils;

type
  TPayment = class
    function Pay(amount: integer): string; virtual; abstract;
  end;

  TCardPayment = class(TPayment)
    function Pay(amount: integer): string; override;
  end;

  TCashPayment = class(TPayment)
    function Pay(amount: integer): string; override;
  end;

function TCardPayment.Pay(amount: integer): string;
begin
  Pay := 'card ' + IntToStr(amount);
end;

function TCashPayment.Pay(amount: integer): string;
begin
  Pay := 'cash ' + IntToStr(amount);
end;

var
  payments: array[1..2] of TPayment;
  i: integer;
begin
  payments[1] := TCardPayment.Create;
  payments[2] := TCashPayment.Create;

  for i := 1 to 2 do
    writeln(payments[i].Pay(100));
end."""

PYTHON = """class Payment:
    def pay(self, amount):
        raise NotImplementedError


class CardPayment(Payment):
    def pay(self, amount):
        return "card " + str(amount)


class CashPayment(Payment):
    def pay(self, amount):
        return "cash " + str(amount)


payments = [CardPayment(), CashPayment()]

for payment in payments:
    print(payment.pay(100))"""

CPP = """#include <iostream>
#include <string>
#include <vector>

class Payment {
public:
    virtual std::string pay(int amount) = 0;
};

class CardPayment : public Payment {
public:
    std::string pay(int amount) override {
        return "card " + std::to_string(amount);
    }
};

class CashPayment : public Payment {
public:
    std::string pay(int amount) override {
        return "cash " + std::to_string(amount);
    }
};

int main() {
    std::vector<Payment*> payments = {
        new CardPayment(),
        new CashPayment()
    };

    for (Payment* payment : payments) {
        std::cout << payment->pay(100) << '\\n';
    }

    return 0;
}"""

CSHARP = """using System;

interface IPayment {
    string Pay(int amount);
}

class CardPayment : IPayment {
    public string Pay(int amount) {
        return "card " + amount;
    }
}

class CashPayment : IPayment {
    public string Pay(int amount) {
        return "cash " + amount;
    }
}

IPayment[] payments = {
    new CardPayment(),
    new CashPayment()
};

foreach (IPayment payment in payments) {
    Console.WriteLine(payment.Pay(100));
}"""

JAVA = """interface Payment {
    String pay(int amount);
}

class CardPayment implements Payment {
    public String pay(int amount) {
        return "card " + amount;
    }
}

class CashPayment implements Payment {
    public String pay(int amount) {
        return "cash " + amount;
    }
}

class Main {
    public static void main(String[] args) {
        Payment[] payments = {
            new CardPayment(),
            new CashPayment()
        };

        for (Payment payment : payments) {
            System.out.println(payment.pay(100));
        }
    }
}"""
