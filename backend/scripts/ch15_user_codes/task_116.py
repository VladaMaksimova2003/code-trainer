FIXED_PASCAL = """type
  TCounter = class
    value: integer;
    constructor Create;
    procedure Add(amount: integer);
    procedure PrintValue;
  end;

constructor TCounter.Create;
begin
  value := 0;
end;

procedure TCounter.Add(amount: integer);
begin
  value := value + amount;
end;

procedure TCounter.PrintValue;
begin
  writeln(value);
end;

var
  counter: TCounter;
begin
  counter := TCounter.Create;
  counter.Add(5);
  counter.Add(7);
  counter.PrintValue;
end."""

BUGGY_PASCAL = """type
  TCounter = class
    value: integer
    constructor Create;
    procedure Add(amount: integer);
    procedure PrintValue;
  end;

constructor TCounter.Create;
begin
  value = 0;
end;

procedure TCounter.Add(amount: integer);
begin
  self.value := value + amount;
end;

procedure TCounter.PrintValue;
begin
  Console.WriteLine(value);
end;

var counter: TCounter;
begin
  counter := new Counter();
  counter.Add('5');
  counter.Add(7);
  counter.PrintValue();
end."""

FIXED_PYTHON = """class Counter:
    def __init__(self):
        self.value = 0

    def add(self, amount):
        self.value += amount

    def print_value(self):
        print(self.value)

counter = Counter()
counter.add(5)
counter.add(7)
counter.print_value()"""

BUGGY_PYTHON = """class Counter
    def __init__(self):
        value = 0

    def add(amount):
        self.value = self.value + amount

    def print_value(self):
        Console.WriteLine(value)

counter = Counter()
counter.add("5")
counter.add(7)
counter.print_value()"""

FIXED_CPP = """#include <iostream>

class Counter {
    int value;

public:
    Counter() {
        value = 0;
    }

    void add(int amount) {
        value += amount;
    }

    void printValue() {
        std::cout << value;
    }
};

int main() {
    Counter counter;
    counter.add(5);
    counter.add(7);
    counter.printValue();
    return 0;
}"""

BUGGY_CPP = """#include <iostream>

class Counter {
    int value

public:
    Counter() {
        value := 0;
    }

    void add(amount) {
        self.value = value + amount;
    }

    void printValue() {
        Console.WriteLine(value);
    }
};

int main() {
    Counter counter = new Counter();
    counter.add("5");
    counter.add(7);
    counter.printValue();
}"""

FIXED_CSHARP = """using System;

class Counter {
    int value;

    public Counter() {
        value = 0;
    }

    public void Add(int amount) {
        value += amount;
    }

    public void PrintValue() {
        Console.WriteLine(value);
    }
}

Counter counter = new Counter();
counter.Add(5);
counter.Add(7);
counter.PrintValue();"""

BUGGY_CSHARP = """using System;

class Counter {
    int value

    public Counter() {
        value := 0;
    }

    public void Add(amount) {
        self.value = value + amount;
    }

    public void PrintValue() {
        print(value);
    }
}

Counter counter = Counter();
counter.Add("5");
counter.Add(7);
counter.PrintValue;"""

FIXED_JAVA = """class Counter {
    int value;

    Counter() {
        value = 0;
    }

    void add(int amount) {
        value += amount;
    }

    void printValue() {
        System.out.println(value);
    }
}

class Main {
    public static void main(String[] args) {
        Counter counter = new Counter();
        counter.add(5);
        counter.add(7);
        counter.printValue();
    }
}"""

BUGGY_JAVA = """class Counter {
    int value

    Counter() {
        value := 0;
    }

    void add(amount) {
        self.value = value + amount;
    }

    void printValue() {
        Console.WriteLine(value);
    }
}

class Main {
    public static void main(String[] args) {
        Counter counter = Counter();
        counter.add("5");
        counter.add(7);
        counter.printValue;
    }
}"""
