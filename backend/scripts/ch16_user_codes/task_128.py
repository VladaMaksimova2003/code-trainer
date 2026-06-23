PASCAL = """type
  TDelivery = class
    distance: integer;
    constructor Create(d: integer);
    function Cost: integer; virtual;
  end;

  TCourierDelivery = class(TDelivery)
    function Cost: integer; override;
  end;

  TExpressDelivery = class(TDelivery)
    function Cost: integer; override;
  end;

constructor TDelivery.Create(d: integer);
begin
  distance := d;
end;

function TDelivery.Cost: integer;
begin
  Cost := distance * 10;
end;

function TCourierDelivery.Cost: integer;
begin
  Cost := distance * 15;
end;

function TExpressDelivery.Cost: integer;
begin
  Cost := distance * 25 + 100;
end;

var
  orders: array[1..3] of TDelivery;
  i, total: integer;
begin
  orders[1] := TCourierDelivery.Create(4);
  orders[2] := TExpressDelivery.Create(3);
  orders[3] := TDelivery.Create(5);

  total := 0;

  for i := 1 to 3 do
    total := total + orders[i].Cost;

  writeln(total);
end."""

PYTHON = """class Delivery:
    def __init__(self, distance):
        self.distance = distance

    def cost(self):
        return self.distance * 10


class CourierDelivery(Delivery):
    def cost(self):
        return self.distance * 15


class ExpressDelivery(Delivery):
    def cost(self):
        return self.distance * 25 + 100


orders = [
    CourierDelivery(4),
    ExpressDelivery(3),
    Delivery(5)
]

total = 0

for order in orders:
    total += order.cost()

print(total)"""

CPP = """#include <iostream>
#include <vector>

class Delivery {
protected:
    int distance;

public:
    Delivery(int d) {
        distance = d;
    }

    virtual int cost() {
        return distance * 10;
    }
};

class CourierDelivery : public Delivery {
public:
    CourierDelivery(int d) : Delivery(d) {}

    int cost() override {
        return distance * 15;
    }
};

class ExpressDelivery : public Delivery {
public:
    ExpressDelivery(int d) : Delivery(d) {}

    int cost() override {
        return distance * 25 + 100;
    }
};

int main() {
    std::vector<Delivery*> orders = {
        new CourierDelivery(4),
        new ExpressDelivery(3),
        new Delivery(5)
    };

    int total = 0;

    for (Delivery* order : orders) {
        total += order->cost();
    }

    std::cout << total;
    return 0;
}"""

CSHARP = """using System;

class Delivery {
    protected int distance;

    public Delivery(int d) {
        distance = d;
    }

    public virtual int Cost() {
        return distance * 10;
    }
}

class CourierDelivery : Delivery {
    public CourierDelivery(int d) : base(d) {}

    public override int Cost() {
        return distance * 15;
    }
}

class ExpressDelivery : Delivery {
    public ExpressDelivery(int d) : base(d) {}

    public override int Cost() {
        return distance * 25 + 100;
    }
}

Delivery[] orders = {
    new CourierDelivery(4),
    new ExpressDelivery(3),
    new Delivery(5)
};

int total = 0;

foreach (Delivery order in orders) {
    total += order.Cost();
}

Console.WriteLine(total);"""

JAVA = """class Delivery {
    protected int distance;

    Delivery(int d) {
        distance = d;
    }

    int cost() {
        return distance * 10;
    }
}

class CourierDelivery extends Delivery {
    CourierDelivery(int d) {
        super(d);
    }

    @Override
    int cost() {
        return distance * 15;
    }
}

class ExpressDelivery extends Delivery {
    ExpressDelivery(int d) {
        super(d);
    }

    @Override
    int cost() {
        return distance * 25 + 100;
    }
}

class Main {
    public static void main(String[] args) {
        Delivery[] orders = {
            new CourierDelivery(4),
            new ExpressDelivery(3),
            new Delivery(5)
        };

        int total = 0;

        for (Delivery order : orders) {
            total += order.cost();
        }

        System.out.println(total);
    }
}"""
