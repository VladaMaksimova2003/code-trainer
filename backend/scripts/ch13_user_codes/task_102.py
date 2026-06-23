FIXED_PASCAL = """type
  PNode = ^TNode;
  TNode = record
    value: integer;
    next: PNode;
  end;

var n, i, x: integer;
    head, tail, node, prev, cur, nxt: PNode;
begin
  readln(n);
  head := nil;
  tail := nil;

  for i := 1 to n do
  begin
    readln(x);
    new(node);
    node^.value := x;
    node^.next := nil;

    if head = nil then
    begin
      head := node;
      tail := node;
    end
    else
    begin
      tail^.next := node;
      tail := node;
    end;
  end;

  prev := nil;
  cur := head;

  while cur <> nil do
  begin
    nxt := cur^.next;
    cur^.next := prev;
    prev := cur;
    cur := nxt;
  end;

  head := prev;

  cur := head;
  while cur <> nil do
  begin
    write(cur^.value, ' ');
    cur := cur^.next;
  end;
end."""

BUGGY_PASCAL = """type
  PNode = ^TNode
  TNode = record
    value: integer;
    next: PNode;
  end;

var n, i, x: integer;
    head, node, prev, cur: PNode;
begin
  n := int(input());
  head := nil;

  for i in range(n) do
  begin
    node := new Node(x);
    head.next := node;
    head := node;
  end;

  prev := nil;
  cur := head;

  while cur <> nil do
  begin
    cur^.next := prev;
    prev := cur;
    cur := cur^.next;
  end;

  print(head);
end."""

FIXED_PYTHON = """class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

n = int(input())
head = None
tail = None

for _ in range(n):
    node = Node(int(input()))

    if head is None:
        head = node
        tail = node
    else:
        tail.next = node
        tail = node

prev = None
cur = head

while cur is not None:
    nxt = cur.next
    cur.next = prev
    prev = cur
    cur = nxt

head = prev

cur = head
while cur is not None:
    print(cur.value, end=' ')
    cur = cur.next"""

BUGGY_PYTHON = """class Node
    def __init__(self, value):
        self.value = value
        self.next = None

n = int.Parse(Console.ReadLine())
head = None

for i := 1 to n do:
    node = Node(int(input()))
    head.next = node
    head = node

prev = None
cur = head

while cur:
    cur.next = prev
    prev = cur
    cur = cur.next

while head:
    Console.Write(head.value + " ")
    head = head.next"""

FIXED_CPP = """#include <iostream>

struct Node {
    int value;
    Node* next;
};

int main() {
    int n;
    std::cin >> n;

    Node* head = nullptr;
    Node* tail = nullptr;

    for (int i = 0; i < n; i++) {
        int x;
        std::cin >> x;

        Node* node = new Node{x, nullptr};

        if (head == nullptr) {
            head = node;
            tail = node;
        } else {
            tail->next = node;
            tail = node;
        }
    }

    Node* prev = nullptr;
    Node* cur = head;

    while (cur != nullptr) {
        Node* nxt = cur->next;
        cur->next = prev;
        prev = cur;
        cur = nxt;
    }

    head = prev;

    for (Node* cur = head; cur != nullptr; cur = cur->next) {
        std::cout << cur->value << ' ';
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream>

struct Node {
    int value
    Node next;
};

int main() {
    int n = int(input());

    Node* head = null;

    for i in range(n):
        Node* node = new Node{cin, nullptr};
        head.next = node;
        head = node;

    Node* prev = nullptr;
    Node* cur = head;

    while (cur != nullptr) {
        cur->next = prev;
        prev = cur;
        cur = cur->next;
    }

    Console.WriteLine(head);
    return 0;
}"""

FIXED_CSHARP = """using System;

class Node {
    public int Value;
    public Node Next;

    public Node(int value) {
        Value = value;
    }
}

int n = int.Parse(Console.ReadLine());

Node head = null;
Node tail = null;

for (int i = 0; i < n; i++) {
    Node node = new Node(int.Parse(Console.ReadLine()));

    if (head == null) {
        head = node;
        tail = node;
    } else {
        tail.Next = node;
        tail = node;
    }
}

Node prev = null;
Node cur = head;

while (cur != null) {
    Node nxt = cur.Next;
    cur.Next = prev;
    prev = cur;
    cur = nxt;
}

head = prev;

for (cur = head; cur != null; cur = cur.Next) {
    Console.Write(cur.Value + " ");
}"""

BUGGY_CSHARP = """using System;

class Node {
    public int Value
    public Node Next;
}

class Program {
    static void Main() {
        int n = int(input());

        Node head = null;

        for i in range(n):
            Node node = new Node(Console.ReadLine());
            head.Next = node;
            head = node;

        Node prev = null;
        Node cur = head;

        while (cur != null) {
            cur.Next = prev;
            prev = cur;
            cur = cur.Next;
        }

        print(head);
    }
}"""

FIXED_JAVA = """import java.util.*;

class Node {
    int value;
    Node next;

    Node(int value) {
        this.value = value;
    }
}

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();

        Node head = null;
        Node tail = null;

        for (int i = 0; i < n; i++) {
            Node node = new Node(sc.nextInt());

            if (head == null) {
                head = node;
                tail = node;
            } else {
                tail.next = node;
                tail = node;
            }
        }

        Node prev = null;
        Node cur = head;

        while (cur != null) {
            Node nxt = cur.next;
            cur.next = prev;
            prev = cur;
            cur = nxt;
        }

        head = prev;

        for (cur = head; cur != null; cur = cur.next) {
            System.out.print(cur.value + " ");
        }
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Node {
    int value
    Node next;
}

class Main {
    public static void main(String[] args) {
        int n = int(input());

        Node head = null;

        for i in range(n):
            Node node = new Node(Scanner.nextInt());
            head.next = node;
            head = node;

        Node prev = null;
        Node cur = head;

        while (cur != null) {
            cur.next = prev;
            prev = cur;
            cur = cur.next;
        }

        Console.WriteLine(head);
    }
}"""
