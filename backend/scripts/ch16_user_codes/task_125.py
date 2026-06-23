PASCAL = """type
  TShape = class
    function Area: integer; virtual;
  end;

  TSquare = class(TShape)
    side: integer;
    constructor Create(s: integer);
    function Area: integer; override;
  end;

  TRectangle = class(TShape)
    width, height: integer;
    constructor Create(w, h: integer);
    function Area: integer; override;
  end;

function TShape.Area: integer;
begin
  Area := 0;
end;

constructor TSquare.Create(s: integer);
begin
  side := s;
end;

function TSquare.Area: integer;
begin
  Area := side * side;
end;

constructor TRectangle.Create(w, h: integer);
begin
  width := w;
  height := h;
end;

function TRectangle.Area: integer;
begin
  Area := width * height;
end;

var
  shapes: array[1..2] of TShape;
  i: integer;
begin
  shapes[1] := TSquare.Create(4);
  shapes[2] := TRectangle.Create(3, 5);

  for i := 1 to 2 do
    writeln(shapes[i].Area);
end."""

PYTHON = """class Shape:
    def area(self):
        return 0


class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side * self.side


class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height


shapes = [Square(4), Rectangle(3, 5)]

for shape in shapes:
    print(shape.area())"""

CPP = """#include <iostream>
#include <vector>

class Shape {
public:
    virtual int area() {
        return 0;
    }
};

class Square : public Shape {
    int side;

public:
    Square(int s) {
        side = s;
    }

    int area() override {
        return side * side;
    }
};

class Rectangle : public Shape {
    int width;
    int height;

public:
    Rectangle(int w, int h) {
        width = w;
        height = h;
    }

    int area() override {
        return width * height;
    }
};

int main() {
    std::vector<Shape*> shapes = {
        new Square(4),
        new Rectangle(3, 5)
    };

    for (Shape* shape : shapes) {
        std::cout << shape->area() << '\\n';
    }

    return 0;
}"""

CSHARP = """using System;

class Shape {
    public virtual int Area() {
        return 0;
    }
}

class Square : Shape {
    int side;

    public Square(int s) {
        side = s;
    }

    public override int Area() {
        return side * side;
    }
}

class Rectangle : Shape {
    int width;
    int height;

    public Rectangle(int w, int h) {
        width = w;
        height = h;
    }

    public override int Area() {
        return width * height;
    }
}

Shape[] shapes = {
    new Square(4),
    new Rectangle(3, 5)
};

foreach (Shape shape in shapes) {
    Console.WriteLine(shape.Area());
}"""

JAVA = """class Shape {
    int area() {
        return 0;
    }
}

class Square extends Shape {
    int side;

    Square(int s) {
        side = s;
    }

    @Override
    int area() {
        return side * side;
    }
}

class Rectangle extends Shape {
    int width;
    int height;

    Rectangle(int w, int h) {
        width = w;
        height = h;
    }

    @Override
    int area() {
        return width * height;
    }
}

class Main {
    public static void main(String[] args) {
        Shape[] shapes = {
            new Square(4),
            new Rectangle(3, 5)
        };

        for (Shape shape : shapes) {
            System.out.println(shape.area());
        }
    }
}"""
