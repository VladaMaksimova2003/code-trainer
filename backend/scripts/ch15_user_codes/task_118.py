FIXED_PASCAL = """type
  TProduct = class
    name: string;
    price: integer;
    constructor Create(n: string; p: integer);
  end;

  TOrder = class
    products: array[1..100] of TProduct;
    count: integer;
    procedure AddProduct(product: TProduct);
    function Total: integer;
  end;

constructor TProduct.Create(n: string; p: integer);
begin
  name := n;
  price := p;
end;

procedure TOrder.AddProduct(product: TProduct);
begin
  count := count + 1;
  products[count] := product;
end;

function TOrder.Total: integer;
var
  i, resultSum: integer;
begin
  resultSum := 0;

  for i := 1 to count do
    resultSum := resultSum + products[i].price;

  Total := resultSum;
end;

var
  order: TOrder;
begin
  order := TOrder.Create;
  order.count := 0;

  order.AddProduct(TProduct.Create('Book', 300));
  order.AddProduct(TProduct.Create('Pen', 50));

  writeln(order.Total);
end."""

BUGGY_PASCAL = """type
  TProduct = class
    name: string;
    price: integer
    constructor Create(n: string; p: integer);
  end;

  TOrder = class
    products: list[TProduct];
    procedure AddProduct(product: TProduct);
    function Total: integer;
  end;

constructor TProduct.Create(n: string; p: integer);
begin
  name = n;
  price = p;
end;

procedure TOrder.AddProduct(product: TProduct);
begin
  products.Add(product);
end;

function TOrder.Total: integer;
var product: TProduct;
begin
  Total := 0;
  for product in products do
    Total := Total + product.Price;
end;

var order: TOrder;
begin
  order := new Order();
  order.AddProduct(TProduct.Create('Book', '300'));
  order.AddProduct(TProduct.Create('Pen', 50));
  print(order.Total());
end."""

FIXED_PYTHON = """class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price

class Order:
    def __init__(self):
        self.products = []

    def add_product(self, product):
        self.products.append(product)

    def total(self):
        result = 0
        for product in self.products:
            result += product.price
        return result

order = Order()
order.add_product(Product("Book", 300))
order.add_product(Product("Pen", 50))

print(order.total())"""

BUGGY_PYTHON = """class Product
    def __init__(self, name, price):
        self.name = name
        price = price

class Order:
    products = []

    def add_product(product):
        products.append(product)

    def total(self):
        result = 0
        for product in self.products:
            result += product.Price
        print(result)

order = new Order()
order.add_product(Product("Book", "300"))
order.add_product(Product("Pen", 50))

Console.WriteLine(order.total())"""

FIXED_CPP = """#include <iostream>
#include <string>
#include <vector>

class Product {
public:
    std::string name;
    int price;

    Product(std::string n, int p) {
        name = n;
        price = p;
    }
};

class Order {
    std::vector<Product> products;

public:
    void addProduct(Product product) {
        products.push_back(product);
    }

    int total() {
        int result = 0;

        for (Product& product : products) {
            result += product.price;
        }

        return result;
    }
};

int main() {
    Order order;
    order.addProduct(Product("Book", 300));
    order.addProduct(Product("Pen", 50));

    std::cout << order.total();
    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <string>

class Product {
public:
    string name;
    int price;

    Product(string n, int p) {
        name := n;
        price := p;
    }
};

class Order {
    List<Product> products;

public:
    void addProduct(Product product) {
        products.Add(product);
    }

    int total() {
        int result = 0;

        foreach (Product product in products) {
            result += product.Price;
        }

        return result;
    }
};

int main() {
    Order order = new Order();
    order.addProduct(Product("Book", "300"));
    order.addProduct(Product("Pen", 50));

    Console.WriteLine(order.total());
}"""

FIXED_CSHARP = """using System;
using System.Collections.Generic;

class Product {
    public string Name;
    public int Price;

    public Product(string name, int price) {
        Name = name;
        Price = price;
    }
}

class Order {
    List<Product> products = new List<Product>();

    public void AddProduct(Product product) {
        products.Add(product);
    }

    public int Total() {
        int result = 0;

        foreach (Product product in products) {
            result += product.Price;
        }

        return result;
    }
}

Order order = new Order();
order.AddProduct(new Product("Book", 300));
order.AddProduct(new Product("Pen", 50));
Console.WriteLine(order.Total());"""

BUGGY_CSHARP = """using System;

class Product {
    public string Name;
    public int Price;

    public Product(name, price) {
        Name := name;
        Price := price;
    }
}

class Order {
    List<Product> products = [];

    public void AddProduct(Product product) {
        products.push(product);
    }

    public int Total() {
        int result = 0;

        for product in products:
            result += product.price;

        return result;
    }
}

Order order = Order();
order.AddProduct(Product("Book", "300"));
order.AddProduct(new Product("Pen", 50));
print(order.Total);"""

FIXED_JAVA = """import java.util.*;

class Product {
    String name;
    int price;

    Product(String name, int price) {
        this.name = name;
        this.price = price;
    }
}

class Order {
    ArrayList<Product> products = new ArrayList<>();

    void addProduct(Product product) {
        products.add(product);
    }

    int total() {
        int result = 0;

        for (Product product : products) {
            result += product.price;
        }

        return result;
    }
}

class Main {
    public static void main(String[] args) {
        Order order = new Order();
        order.addProduct(new Product("Book", 300));
        order.addProduct(new Product("Pen", 50));

        System.out.println(order.total());
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Product {
    string name;
    int price;

    Product(name, price) {
        this.name := name;
        this.price := price;
    }
}

class Order {
    List<Product> products = [];

    void addProduct(Product product) {
        products.push(product);
    }

    int total() {
        int result = 0;

        foreach (Product product in products) {
            result += product.Price;
        }

        return result;
    }
}

class Main {
    public static void main(String[] args) {
        Order order = Order();
        order.addProduct(Product("Book", "300"));
        order.addProduct(new Product("Pen", 50));

        Console.WriteLine(order.total);
    }
}"""
