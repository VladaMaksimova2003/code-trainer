PASCAL = """type
  TProduct = class
    name: string;
    price, count: integer;
    constructor Create(n: string; p, c: integer);
    function TotalPrice: integer;
  end;

constructor TProduct.Create(n: string; p, c: integer);
begin
  name := n;
  price := p;
  count := c;
end;

function TProduct.TotalPrice: integer;
begin
  TotalPrice := price * count;
end;

var
  p: TProduct;
begin
  p := TProduct.Create('Book', 300, 2);
  writeln(p.name, ' ', p.TotalPrice);
end."""

PYTHON = """class Product:
    def __init__(self, name, price, count):
        self.name = name
        self.price = price
        self.count = count

    def total_price(self):
        return self.price * self.count

p = Product("Book", 300, 2)
print(p.name, p.total_price())"""

CPP = """#include <iostream>
#include <string>

class Product {
    std::string name;
    int price;
    int count;

public:
    Product(std::string n, int p, int c) {
        name = n;
        price = p;
        count = c;
    }

    int totalPrice() {
        return price * count;
    }

    void print() {
        std::cout << name << ' ' << totalPrice();
    }
};

int main() {
    Product p("Book", 300, 2);
    p.print();
    return 0;
}"""

CSHARP = """using System;

class Product {
    string name;
    int price;
    int count;

    public Product(string n, int p, int c) {
        name = n;
        price = p;
        count = c;
    }

    public int TotalPrice() {
        return price * count;
    }

    public void Print() {
        Console.WriteLine($"{name} {TotalPrice()}");
    }
}

Product p = new Product("Book", 300, 2);
p.Print();"""

JAVA = """class Product {
    String name;
    int price;
    int count;

    Product(String n, int p, int c) {
        name = n;
        price = p;
        count = c;
    }

    int totalPrice() {
        return price * count;
    }

    void print() {
        System.out.println(name + " " + totalPrice());
    }
}

class Main {
    public static void main(String[] args) {
        Product p = new Product("Book", 300, 2);
        p.print();
    }
}"""
