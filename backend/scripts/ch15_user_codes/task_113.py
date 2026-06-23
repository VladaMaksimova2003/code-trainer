PASCAL = """type
  TUser = class
    name: string;
    constructor Create(n: string);
    procedure Print;
  end;

constructor TUser.Create(n: string);
begin
  name := n;
end;

procedure TUser.Print;
begin
  writeln(name);
end;

var
  u: TUser;
begin
  u := TUser.Create('Alex');
  u.Print;
end."""

PYTHON = """class User:
    def __init__(self, name):
        self.name = name

    def print_name(self):
        print(self.name)

u = User("Alex")
u.print_name()"""

CPP = """#include <iostream>
#include <string>

class User {
    std::string name;

public:
    User(std::string n) {
        name = n;
    }

    void print() {
        std::cout << name;
    }
};

int main() {
    User u("Alex");
    u.print();
    return 0;
}"""

CSHARP = """using System;

class User {
    string name;

    public User(string n) {
        name = n;
    }

    public void Print() {
        Console.WriteLine(name);
    }
}

User u = new User("Alex");
u.Print();"""

JAVA = """class User {
    String name;

    User(String n) {
        name = n;
    }

    void print() {
        System.out.println(name);
    }
}

class Main {
    public static void main(String[] args) {
        User u = new User("Alex");
        u.print();
    }
}"""
