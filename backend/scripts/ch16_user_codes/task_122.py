PASCAL = """type
  TTransport = class
    function Move: string; virtual;
  end;

  TCar = class(TTransport)
    function Move: string; override;
  end;

  TBike = class(TTransport)
    function Move: string; override;
  end;

function TTransport.Move: string;
begin
  Move := 'moving';
end;

function TCar.Move: string;
begin
  Move := 'car drives';
end;

function TBike.Move: string;
begin
  Move := 'bike rides';
end;

var
  vehicles: array[1..2] of TTransport;
  i: integer;
begin
  vehicles[1] := TCar.Create;
  vehicles[2] := TBike.Create;

  for i := 1 to 2 do
    writeln(vehicles[i].Move);
end."""

PYTHON = """class Transport:
    def move(self):
        return "moving"


class Car(Transport):
    def move(self):
        return "car drives"


class Bike(Transport):
    def move(self):
        return "bike rides"


vehicles = [Car(), Bike()]

for vehicle in vehicles:
    print(vehicle.move())"""

CPP = """#include <iostream>
#include <string>
#include <vector>

class Transport {
public:
    virtual std::string move() {
        return "moving";
    }
};

class Car : public Transport {
public:
    std::string move() override {
        return "car drives";
    }
};

class Bike : public Transport {
public:
    std::string move() override {
        return "bike rides";
    }
};

int main() {
    std::vector<Transport*> vehicles = {new Car(), new Bike()};

    for (Transport* vehicle : vehicles) {
        std::cout << vehicle->move() << '\\n';
    }

    return 0;
}"""

CSHARP = """using System;

class Transport {
    public virtual string Move() {
        return "moving";
    }
}

class Car : Transport {
    public override string Move() {
        return "car drives";
    }
}

class Bike : Transport {
    public override string Move() {
        return "bike rides";
    }
}

Transport[] vehicles = { new Car(), new Bike() };

foreach (Transport vehicle in vehicles) {
    Console.WriteLine(vehicle.Move());
}"""

JAVA = """class Transport {
    String move() {
        return "moving";
    }
}

class Car extends Transport {
    @Override
    String move() {
        return "car drives";
    }
}

class Bike extends Transport {
    @Override
    String move() {
        return "bike rides";
    }
}

class Main {
    public static void main(String[] args) {
        Transport[] vehicles = { new Car(), new Bike() };

        for (Transport vehicle : vehicles) {
            System.out.println(vehicle.move());
        }
    }
}"""
