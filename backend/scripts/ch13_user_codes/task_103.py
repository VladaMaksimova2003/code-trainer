FIXED_PASCAL = """type
  PNode = ^TNode;
  TNode = record
    value: integer;
    next: PNode;
  end;

procedure Append(var head, tail: PNode; value: integer);
var node: PNode;
begin
  new(node);
  node^.value := value;
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

var n, m, i, x: integer;
    a, b, atail, btail, result, rtail, cur: PNode;
begin
  a := nil;
  b := nil;
  atail := nil;
  btail := nil;
  result := nil;
  rtail := nil;

  readln(n);
  for i := 1 to n do
  begin
    readln(x);
    Append(a, atail, x);
  end;

  readln(m);
  for i := 1 to m do
  begin
    readln(x);
    Append(b, btail, x);
  end;

  while (a <> nil) and (b <> nil) do
  begin
    if a^.value <= b^.value then
    begin
      Append(result, rtail, a^.value);
      a := a^.next;
    end
    else
    begin
      Append(result, rtail, b^.value);
      b := b^.next;
    end;
  end;

  while a <> nil do
  begin
    Append(result, rtail, a^.value);
    a := a^.next;
  end;

  while b <> nil do
  begin
    Append(result, rtail, b^.value);
    b := b^.next;
  end;

  cur := result;
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

function Merge(a, b: PNode): PNode;
var result: PNode;
begin
  result := nil;

  while (a <> nil) or (b <> nil) do
  begin
    if a^.value <= b^.value then
    begin
      result^.next := a;
      a := a^.next;
    end
    else
    begin
      result^.next := b;
      b := b^.next;
    end;
  end;

  Merge := result;
end;

begin
  print(Merge(a, b));
end."""

FIXED_PYTHON = """class Node:
    def __init__(self, value):
        self.value = value
        self.next = None


def append(head, tail, value):
    node = Node(value)

    if head is None:
        return node, node

    tail.next = node
    return head, node


def merge(a, b):
    dummy = Node(0)
    tail = dummy

    while a is not None and b is not None:
        if a.value <= b.value:
            tail.next = a
            a = a.next
        else:
            tail.next = b
            b = b.next

        tail = tail.next

    tail.next = a if a is not None else b
    return dummy.next


n = int(input())
a_head = None
a_tail = None

for _ in range(n):
    a_head, a_tail = append(a_head, a_tail, int(input()))

m = int(input())
b_head = None
b_tail = None

for _ in range(m):
    b_head, b_tail = append(b_head, b_tail, int(input()))

result = merge(a_head, b_head)

cur = result
while cur is not None:
    print(cur.value, end=' ')
    cur = cur.next"""

BUGGY_PYTHON = """class Node
    def __init__(self, value):
        self.value = value
        self.next = None


def merge(Node a, Node b):
    result = None

    while a and b:
        if a.value < b.value:
            result.next = a
            a = a.next
        else:
            result.next = b
            b = b.next

    return result


n = int.Parse(Console.ReadLine())
a = []

for i := 1 to n do:
    a.append(int(input()))

m = int(input())
b = []

for i := 1 to m do:
    b.append(int(input()))

print(merge(a, b))"""

FIXED_CPP = """#include <iostream>

struct Node {
    int value;
    Node* next;
};

void append(Node*& head, Node*& tail, int value) {
    Node* node = new Node{value, nullptr};

    if (head == nullptr) {
        head = node;
        tail = node;
    } else {
        tail->next = node;
        tail = node;
    }
}

Node* merge(Node* a, Node* b) {
    Node dummy{0, nullptr};
    Node* tail = &dummy;

    while (a != nullptr && b != nullptr) {
        if (a->value <= b->value) {
            tail->next = a;
            a = a->next;
        } else {
            tail->next = b;
            b = b->next;
        }

        tail = tail->next;
    }

    tail->next = a != nullptr ? a : b;

    return dummy.next;
}

int main() {
    int n, m, x;

    Node* a = nullptr;
    Node* aTail = nullptr;
    Node* b = nullptr;
    Node* bTail = nullptr;

    std::cin >> n;
    for (int i = 0; i < n; i++) {
        std::cin >> x;
        append(a, aTail, x);
    }

    std::cin >> m;
    for (int i = 0; i < m; i++) {
        std::cin >> x;
        append(b, bTail, x);
    }

    Node* result = merge(a, b);

    for (Node* cur = result; cur != nullptr; cur = cur->next) {
        std::cout << cur->value << ' ';
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream>

struct Node {
    int value;
    Node next;
};

Node* merge(Node* a, Node* b) {
    Node* result = nullptr;

    while (a != nullptr || b != nullptr) {
        if (a->value <= b->value) {
            result->next = a;
            a = a->next;
        } else {
            result->next = b;
            b = b->next;
        }
    }

    return result;
}

int main() {
    int n = int(input());
    Node* a = new Node[n];

    for i in range(n):
        cin >> a[i];

    int m = int(input());
    Node* b = new Node[m];

    for i in range(m):
        cin >> b[i];

    Console.WriteLine(merge(a, b));
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

static class ListHelper {
    public static void Append(ref Node head, ref Node tail, int value) {
        Node node = new Node(value);

        if (head == null) {
            head = node;
            tail = node;
        } else {
            tail.Next = node;
            tail = node;
        }
    }

    public static Node Merge(Node a, Node b) {
        Node dummy = new Node(0);
        Node tail = dummy;

        while (a != null && b != null) {
            if (a.Value <= b.Value) {
                tail.Next = a;
                a = a.Next;
            } else {
                tail.Next = b;
                b = b.Next;
            }

            tail = tail.Next;
        }

        tail.Next = a ?? b;

        return dummy.Next;
    }
}

Node a = null;
Node aTail = null;
Node b = null;
Node bTail = null;

int n = int.Parse(Console.ReadLine());

for (int i = 0; i < n; i++) {
    ListHelper.Append(ref a, ref aTail, int.Parse(Console.ReadLine()));
}

int m = int.Parse(Console.ReadLine());

for (int i = 0; i < m; i++) {
    ListHelper.Append(ref b, ref bTail, int.Parse(Console.ReadLine()));
}

Node result = ListHelper.Merge(a, b);

for (Node cur = result; cur != null; cur = cur.Next) {
    Console.Write(cur.Value + " ");
}"""

BUGGY_CSHARP = """using System;

class Node {
    public int Value;
    public Node Next;
}

class Program {
    static Node Merge(Node a, Node b) {
        Node result = null;

        while (a != null || b != null) {
            if (a.Value <= b.Value) {
                result.Next = a;
                a = a.Next;
            } else {
                result.Next = b;
                b = b.Next;
            }
        }

        return result;
    }

    static void Main() {
        int n = int(input());
        Node[] a = new Node[n];

        for i in range(n):
            a[i] = new Node(Console.ReadLine());

        int m = int(input());
        Node[] b = new Node[m];

        for i in range(m):
            b[i] = new Node(Console.ReadLine());

        print(Merge(a, b));
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
    static Node append(Node head, int value) {
        Node node = new Node(value);

        if (head == null) {
            return node;
        }

        Node cur = head;

        while (cur.next != null) {
            cur = cur.next;
        }

        cur.next = node;
        return head;
    }

    static Node merge(Node a, Node b) {
        Node dummy = new Node(0);
        Node tail = dummy;

        while (a != null && b != null) {
            if (a.value <= b.value) {
                tail.next = a;
                a = a.next;
            } else {
                tail.next = b;
                b = b.next;
            }

            tail = tail.next;
        }

        tail.next = a != null ? a : b;

        return dummy.next;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        Node a = null;
        int n = sc.nextInt();

        for (int i = 0; i < n; i++) {
            a = append(a, sc.nextInt());
        }

        Node b = null;
        int m = sc.nextInt();

        for (int i = 0; i < m; i++) {
            b = append(b, sc.nextInt());
        }

        Node result = merge(a, b);

        for (Node cur = result; cur != null; cur = cur.next) {
            System.out.print(cur.value + " ");
        }
    }
}"""

BUGGY_JAVA = """import java.util.*;

class Node {
    int value;
    Node next;
}

class Main {
    static Node merge(Node a, Node b) {
        Node result = null;

        while (a != null || b != null) {
            if (a.value <= b.Value) {
                result.next = a;
                a = a.next;
            } else {
                result.next = b;
                b = b.next;
            }
        }

        return result;
    }

    public static void main(String[] args) {
        int n = int(input());
        Node[] a = new Node[n];

        for i in range(n):
            a[i] = new Node(Scanner.nextInt());

        int m = int(input());
        Node[] b = new Node[m];

        for i in range(m):
            b[i] = new Node(Scanner.nextInt());

        Console.WriteLine(merge(a, b));
    }
}"""
