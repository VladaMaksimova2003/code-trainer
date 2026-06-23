FIXED_PASCAL = """type
  TFigure = class
    function Area: integer; virtual;
  end;

  TCircle = class(TFigure)
    radius: integer;
    constructor Create(r: integer);
    function Area: integer; override;
  end;

  TRectangle = class(TFigure)
    width, height: integer;
    constructor Create(w, h: integer);
    function Area: integer; override;
  end;

function TFigure.Area: integer;
begin
  Area := 0;
end;

constructor TCircle.Create(r: integer);
begin
  radius := r;
end;

function TCircle.Area: integer;
begin
  Area := 3 * radius * radius;
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
  figures: array[1..2] of TFigure;
  i, total: integer;
begin
  figures[1] := TCircle.Create(2);
  figures[2] := TRectangle.Create(3, 4);

  total := 0;

  for i := 1 to 2 do
    total := total + figures[i].Area;

  writeln(total);
end."""

BUGGY_PASCAL = """type
  TFigure = class
    function Area: integer;
  end;

  TCircle = class(TFigure)
    radius: string;
    constructor Create(r: string);
    function AreaCircle: integer; override;
  end;

  TRectangle = class(TFigure)
    width, height: integer;
    constructor Create(w, h: integer);
    function Area: string; override;
  end;

function TFigure.Area: integer;
begin
  Area := 0;
end;

function TCircle.AreaCircle: integer;
begin
  AreaCircle := 3 * radius * radius;
end;

function TRectangle.Area: string;
begin
  Area := IntToStr(width + height);
end;

var
  figures: array[1..2] of TFigure;
begin
  figures[1] := new Circle('2');
  figures[2] := TRectangle.Create(3, 4);

  for figure in figures do
    total += figure.Area();
end."""

FIXED_PYTHON = """class Figure:
    def area(self):
        return 0


class Circle(Figure):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3 * self.radius * self.radius


class Rectangle(Figure):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height


figures = [Circle(2), Rectangle(3, 4)]
total = 0

for figure in figures:
    total += figure.area()

print(total)"""

BUGGY_PYTHON = """class Figure:
    def area(self):
        return 0


class Circle(Figure):
    def __init__(radius):
        self.radius = radius

    def Area(self):
        return 3 * radius * radius


class Rectangle(Figure):
    def __init__(self, width, height):
        width = width
        height = height

    def area(self):
        return self.width + self.height


figures = [Circle("2"), Rectangle(3, 4)]

total = 0
for figure in figures:
    total += figure.Area()

Console.WriteLine(total)"""

FIXED_CPP = """#include <iostream>
#include <vector>

class Figure {
public:
    virtual int area() {
        return 0;
    }
};

class Circle : public Figure {
    int radius;

public:
    Circle(int r) {
        radius = r;
    }

    int area() override {
        return 3 * radius * radius;
    }
};

class Rectangle : public Figure {
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
    std::vector<Figure*> figures = {
        new Circle(2),
        new Rectangle(3, 4)
    };

    int total = 0;

    for (Figure* figure : figures) {
        total += figure->area();
    }

    std::cout << total;
    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <vector>

class Figure {
public:
    int area() {
        return 0;
    }
};

class Circle : public Figure {
    string radius;

public:
    Circle(string r) {
        radius = r;
    }

    int Area() override {
        return 3 * radius * radius;
    }
};

class Rectangle : public Figure {
    int width;
    int height;

public:
    Rectangle(int w, int h) {
        width = w;
        height = h;
    }

    string area() override {
        return width + height;
    }
};

int main() {
    vector<Figure> figures = {
        Circle("2"),
        Rectangle(3, 4)
    };

    int total = 0;

    for (auto figure : figures) {
        total += figure.Area();
    }

    Console.WriteLine(total);
}"""

FIXED_CSHARP = """using System;

class Figure {
    public virtual int Area() {
        return 0;
    }
}

class Circle : Figure {
    int radius;

    public Circle(int r) {
        radius = r;
    }

    public override int Area() {
        return 3 * radius * radius;
    }
}

class Rectangle : Figure {
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

Figure[] figures = {
    new Circle(2),
    new Rectangle(3, 4)
};

int total = 0;

foreach (Figure figure in figures) {
    total += figure.Area();
}

Console.WriteLine(total);"""

BUGGY_CSHARP = """using System;

class Figure {
    public int Area() {
        return 0;
    }
}

class Circle : Figure {
    string radius;

    public Circle(string r) {
        radius = r;
    }

    public override int AreaCircle() {
        return 3 * radius * radius;
    }
}

class Rectangle : Figure {
    int width;
    int height;

    public Rectangle(int w, int h) {
        width = w;
        height = h;
    }

    public override string Area() {
        return (width + height).ToString();
    }
}

Figure[] figures = {
    Circle("2"),
    new Rectangle(3, 4)
};

int total = 0;

for figure in figures:
    total += figure.AreaCircle();

print(total);"""

FIXED_JAVA = """class Figure {
    int area() {
        return 0;
    }
}

class Circle extends Figure {
    int radius;

    Circle(int r) {
        radius = r;
    }

    @Override
    int area() {
        return 3 * radius * radius;
    }
}

class Rectangle extends Figure {
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
        Figure[] figures = {
            new Circle(2),
            new Rectangle(3, 4)
        };

        int total = 0;

        for (Figure figure : figures) {
            total += figure.area();
        }

        System.out.println(total);
    }
}"""

BUGGY_JAVA = """class Figure {
    int area() {
        return 0;
    }
}

class Circle extends Figure {
    String radius;

    Circle(String r) {
        radius = r;
    }

    @Override
    int Area() {
        return 3 * radius * radius;
    }
}

class Rectangle extends Figure {
    int width;
    int height;

    Rectangle(int w, int h) {
        width = w;
        height = h;
    }

    @Override
    String area() {
        return String.valueOf(width + height);
    }
}

class Main {
    public static void main(String[] args) {
        Figure[] figures = {
            Circle("2"),
            new Rectangle(3, 4)
        };

        int total = 0;

        foreach (Figure figure in figures) {
            total += figure.Area();
        }

        Console.WriteLine(total);
    }
}"""
