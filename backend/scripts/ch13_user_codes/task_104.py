PASCAL = """type
  PNode = ^TNode;
  TNode = record
    song: string;
    next: PNode;
  end;

var n, i: integer;
    line, song: string;
    current, tail, node: PNode;
begin
  readln(n);
  current := nil;
  tail := nil;

  for i := 1 to n do
  begin
    readln(line);

    if copy(line, 1, 3) = 'add' then
    begin
      song := copy(line, 5, length(line));
      new(node);
      node^.song := song;

      if current = nil then
      begin
        current := node;
        tail := node;
        node^.next := node;
      end
      else
      begin
        node^.next := current;
        tail^.next := node;
        tail := node;
      end;
    end
    else if line = 'next' then
    begin
      if current <> nil then
        current := current^.next;
    end
    else if line = 'current' then
    begin
      if current = nil then
        writeln('empty')
      else
        writeln(current^.song);
    end;
  end;
end."""

PYTHON = """class Node:
    def __init__(self, song):
        self.song = song
        self.next = None

n = int(input())
current = None
tail = None

for _ in range(n):
    command = input().split()

    if command[0] == 'add':
        node = Node(command[1])

        if current is None:
            current = node
            tail = node
            node.next = node
        else:
            node.next = current
            tail.next = node
            tail = node

    elif command[0] == 'next':
        if current:
            current = current.next

    elif command[0] == 'current':
        if current:
            print(current.song)
        else:
            print('empty')"""

CPP = """#include <iostream>
#include <string>

struct Node {
    std::string song;
    Node* next;
};

int main() {
    int n;
    std::cin >> n;

    Node* current = nullptr;
    Node* tail = nullptr;

    for (int i = 0; i < n; i++) {
        std::string command;
        std::cin >> command;

        if (command == "add") {
            std::string song;
            std::cin >> song;

            Node* node = new Node{song, nullptr};

            if (!current) {
                current = node;
                tail = node;
                node->next = node;
            } else {
                node->next = current;
                tail->next = node;
                tail = node;
            }
        } else if (command == "next") {
            if (current) current = current->next;
        } else if (command == "current") {
            if (current) std::cout << current->song << '\\n';
            else std::cout << "empty\\n";
        }
    }

    return 0;
}"""

CSHARP = """using System;

class Node {
    public string Song;
    public Node Next;

    public Node(string song) {
        Song = song;
    }
}

int n = int.Parse(Console.ReadLine());

Node current = null;
Node tail = null;

for (int i = 0; i < n; i++) {
    string[] parts = Console.ReadLine().Split();

    if (parts[0] == "add") {
        Node node = new Node(parts[1]);

        if (current == null) {
            current = node;
            tail = node;
            node.Next = node;
        } else {
            node.Next = current;
            tail.Next = node;
            tail = node;
        }
    } else if (parts[0] == "next") {
        if (current != null) {
            current = current.Next;
        }
    } else if (parts[0] == "current") {
        Console.WriteLine(current == null ? "empty" : current.Song);
    }
}"""

JAVA = """import java.util.*;

class Node {
    String song;
    Node next;

    Node(String song) {
        this.song = song;
    }
}

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();

        Node current = null;
        Node tail = null;

        for (int i = 0; i < n; i++) {
            String command = sc.next();

            if (command.equals("add")) {
                Node node = new Node(sc.next());

                if (current == null) {
                    current = node;
                    tail = node;
                    node.next = node;
                } else {
                    node.next = current;
                    tail.next = node;
                    tail = node;
                }
            } else if (command.equals("next")) {
                if (current != null) {
                    current = current.next;
                }
            } else if (command.equals("current")) {
                System.out.println(current == null ? "empty" : current.song);
            }
        }
    }
}"""
