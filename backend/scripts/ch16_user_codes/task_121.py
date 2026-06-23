PASCAL = """type
  TAnimal = class
    function Speak: string; virtual;
  end;

  TDog = class(TAnimal)
    function Speak: string; override;
  end;

function TAnimal.Speak: string;
begin
  Speak := 'sound';
end;

function TDog.Speak: string;
begin
  Speak := 'woof';
end;

var
  pet: TAnimal;
begin
  pet := TDog.Create;
  writeln(pet.Speak);
end."""

PYTHON = """class Animal:
    def speak(self):
        return "sound"


class Dog(Animal):
    def speak(self):
        return "woof"


pet = Dog()
print(pet.speak())"""

CPP = """#include <iostream>
#include <string>

class Animal {
public:
    virtual std::string speak() {
        return "sound";
    }
};

class Dog : public Animal {
public:
    std::string speak() override {
        return "woof";
    }
};

int main() {
    Animal* pet = new Dog();
    std::cout << pet->speak();
    return 0;
}"""

CSHARP = """using System;

class Animal {
    public virtual string Speak() {
        return "sound";
    }
}

class Dog : Animal {
    public override string Speak() {
        return "woof";
    }
}

Animal pet = new Dog();
Console.WriteLine(pet.Speak());"""

JAVA = """class Animal {
    String speak() {
        return "sound";
    }
}

class Dog extends Animal {
    @Override
    String speak() {
        return "woof";
    }
}

class Main {
    public static void main(String[] args) {
        Animal pet = new Dog();
        System.out.println(pet.speak());
    }
}"""
