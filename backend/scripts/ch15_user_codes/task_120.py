PASCAL = """type
  TClient = class
    name: string;
    orders: array[1..100] of integer;
    count: integer;
    constructor Create(n: string);
    procedure AddOrder(amount: integer);
    function TotalSpent: integer;
    procedure PrintSummary;
  end;

constructor TClient.Create(n: string);
begin
  name := n;
  count := 0;
end;

procedure TClient.AddOrder(amount: integer);
begin
  count := count + 1;
  orders[count] := amount;
end;

function TClient.TotalSpent: integer;
var
  i, total: integer;
begin
  total := 0;

  for i := 1 to count do
    total := total + orders[i];

  TotalSpent := total;
end;

procedure TClient.PrintSummary;
begin
  writeln(name, ' ', count, ' ', TotalSpent);
end;

var
  client: TClient;
begin
  client := TClient.Create('Alex');
  client.AddOrder(300);
  client.AddOrder(150);
  client.PrintSummary;
end."""

PYTHON = """class Client:
    def __init__(self, name):
        self.name = name
        self.orders = []

    def add_order(self, amount):
        self.orders.append(amount)

    def total_spent(self):
        total = 0

        for amount in self.orders:
            total += amount

        return total

    def print_summary(self):
        print(self.name, len(self.orders), self.total_spent())

client = Client("Alex")
client.add_order(300)
client.add_order(150)
client.print_summary()"""

CPP = """#include <iostream>
#include <string>
#include <vector>

class Client {
    std::string name;
    std::vector<int> orders;

public:
    Client(std::string n) {
        name = n;
    }

    void addOrder(int amount) {
        orders.push_back(amount);
    }

    int totalSpent() {
        int total = 0;

        for (int amount : orders) {
            total += amount;
        }

        return total;
    }

    void printSummary() {
        std::cout << name << ' ' << orders.size() << ' ' << totalSpent();
    }
};

int main() {
    Client client("Alex");

    client.addOrder(300);
    client.addOrder(150);
    client.printSummary();

    return 0;
}"""

CSHARP = """using System;
using System.Collections.Generic;

class Client {
    string name;
    List<int> orders = new List<int>();

    public Client(string n) {
        name = n;
    }

    public void AddOrder(int amount) {
        orders.Add(amount);
    }

    public int TotalSpent() {
        int total = 0;

        foreach (int amount in orders) {
            total += amount;
        }

        return total;
    }

    public void PrintSummary() {
        Console.WriteLine($"{name} {orders.Count} {TotalSpent()}");
    }
}

Client client = new Client("Alex");
client.AddOrder(300);
client.AddOrder(150);
client.PrintSummary();"""

JAVA = """import java.util.*;

class Client {
    String name;
    ArrayList<Integer> orders = new ArrayList<>();

    Client(String n) {
        name = n;
    }

    void addOrder(int amount) {
        orders.add(amount);
    }

    int totalSpent() {
        int total = 0;

        for (int amount : orders) {
            total += amount;
        }

        return total;
    }

    void printSummary() {
        System.out.println(name + " " + orders.size() + " " + totalSpent());
    }
}

class Main {
    public static void main(String[] args) {
        Client client = new Client("Alex");

        client.addOrder(300);
        client.addOrder(150);
        client.printSummary();
    }
}"""
