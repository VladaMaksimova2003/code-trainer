PASCAL = """type
  TBankAccount = class
    owner: string;
    balance: integer;
    constructor Create(o: string; b: integer);
    procedure Deposit(amount: integer);
    procedure PrintBalance;
  end;

constructor TBankAccount.Create(o: string; b: integer);
begin
  owner := o;
  balance := b;
end;

procedure TBankAccount.Deposit(amount: integer);
begin
  balance := balance + amount;
end;

procedure TBankAccount.PrintBalance;
begin
  writeln(owner, ' ', balance);
end;

var
  account: TBankAccount;
begin
  account := TBankAccount.Create('Alex', 100);
  account.Deposit(50);
  account.PrintBalance;
end."""

PYTHON = """class BankAccount:
    def __init__(self, owner, balance):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

    def print_balance(self):
        print(self.owner, self.balance)

account = BankAccount("Alex", 100)
account.deposit(50)
account.print_balance()"""

CPP = """#include <iostream>
#include <string>

class BankAccount {
    std::string owner;
    int balance;

public:
    BankAccount(std::string o, int b) {
        owner = o;
        balance = b;
    }

    void deposit(int amount) {
        balance += amount;
    }

    void printBalance() {
        std::cout << owner << ' ' << balance;
    }
};

int main() {
    BankAccount account("Alex", 100);
    account.deposit(50);
    account.printBalance();
    return 0;
}"""

CSHARP = """using System;

class BankAccount {
    string owner;
    int balance;

    public BankAccount(string o, int b) {
        owner = o;
        balance = b;
    }

    public void Deposit(int amount) {
        balance += amount;
    }

    public void PrintBalance() {
        Console.WriteLine($"{owner} {balance}");
    }
}

BankAccount account = new BankAccount("Alex", 100);
account.Deposit(50);
account.PrintBalance();"""

JAVA = """class BankAccount {
    String owner;
    int balance;

    BankAccount(String o, int b) {
        owner = o;
        balance = b;
    }

    void deposit(int amount) {
        balance += amount;
    }

    void printBalance() {
        System.out.println(owner + " " + balance);
    }
}

class Main {
    public static void main(String[] args) {
        BankAccount account = new BankAccount("Alex", 100);
        account.deposit(50);
        account.printBalance();
    }
}"""
