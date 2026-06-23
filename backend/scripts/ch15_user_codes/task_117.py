PASCAL = """type
  TBook = class
    title: string;
    year: integer;
    constructor Create(t: string; y: integer);
    procedure PrintInfo;
  end;

constructor TBook.Create(t: string; y: integer);
begin
  title := t;
  year := y;
end;

procedure TBook.PrintInfo;
begin
  writeln(title, ' ', year);
end;

var
  books: array[1..2] of TBook;
  i: integer;
begin
  books[1] := TBook.Create('Python', 2020);
  books[2] := TBook.Create('Pascal', 1995);

  for i := 1 to 2 do
    books[i].PrintInfo;
end."""

PYTHON = """class Book:
    def __init__(self, title, year):
        self.title = title
        self.year = year

    def print_info(self):
        print(self.title, self.year)

books = [
    Book("Python", 2020),
    Book("Pascal", 1995)
]

for book in books:
    book.print_info()"""

CPP = """#include <iostream>
#include <string>
#include <vector>

class Book {
    std::string title;
    int year;

public:
    Book(std::string t, int y) {
        title = t;
        year = y;
    }

    void printInfo() {
        std::cout << title << ' ' << year << '\\n';
    }
};

int main() {
    std::vector<Book> books;
    books.push_back(Book("Python", 2020));
    books.push_back(Book("Pascal", 1995));

    for (Book& book : books) {
        book.printInfo();
    }

    return 0;
}"""

CSHARP = """using System;

class Book {
    string title;
    int year;

    public Book(string t, int y) {
        title = t;
        year = y;
    }

    public void PrintInfo() {
        Console.WriteLine($"{title} {year}");
    }
}

Book[] books = {
    new Book("Python", 2020),
    new Book("Pascal", 1995)
};

foreach (Book book in books) {
    book.PrintInfo();
}"""

JAVA = """class Book {
    String title;
    int year;

    Book(String t, int y) {
        title = t;
        year = y;
    }

    void printInfo() {
        System.out.println(title + " " + year);
    }
}

class Main {
    public static void main(String[] args) {
        Book[] books = {
            new Book("Python", 2020),
            new Book("Pascal", 1995)
        };

        for (Book book : books) {
            book.printInfo();
        }
    }
}"""
