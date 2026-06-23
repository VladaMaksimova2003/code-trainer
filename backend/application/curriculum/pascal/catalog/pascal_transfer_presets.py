"""Reusable known-language source variants for Pascal transfer slots."""

from __future__ import annotations

from application.curriculum.pascal.catalog.pascal_known_language import build_known_language_variants

VAI_PROGRAM_ENTRY = build_known_language_variants(
    python="n = int(input())\nprint(n)",
    cpp="#include <iostream>\nusing namespace std;\nint main(){ int n; cin>>n; cout<<n; return 0; }",
    java="import java.util.Scanner;\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int n = sc.nextInt();\n    System.out.println(n);\n  }\n}",
    csharp="using System;\nclass Program {\n  static void Main() {\n    int n = int.Parse(Console.ReadLine());\n    Console.WriteLine(n);\n  }\n}",
)

VAI_TYPED_DECLARATION = build_known_language_variants(
    python="a = int(input())\nb = int(input())\nprint(a + b)",
    cpp="#include <iostream>\nusing namespace std;\nint main(){ int a,b; cin>>a>>b; cout<<(a+b); return 0; }",
    java="import java.util.Scanner;\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int a = sc.nextInt(), b = sc.nextInt();\n    System.out.println(a + b);\n  }\n}",
    csharp="using System;\nclass Program {\n  static void Main() {\n    int a = int.Parse(Console.ReadLine());\n    int b = int.Parse(Console.ReadLine());\n    Console.WriteLine(a + b);\n  }\n}",
)

VAI_ASSIGNMENT = build_known_language_variants(
    python="a = int(input())\nb = int(input())\nresult = a - b\nprint(result)",
    cpp="#include <iostream>\nusing namespace std;\nint main(){ int a,b,result; cin>>a>>b; result=a-b; cout<<result; return 0; }",
    java="import java.util.Scanner;\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int a = sc.nextInt(), b = sc.nextInt();\n    System.out.println(a - b);\n  }\n}",
    csharp="using System;\nclass Program {\n  static void Main() {\n    int a = int.Parse(Console.ReadLine());\n    int b = int.Parse(Console.ReadLine());\n    Console.WriteLine(a - b);\n  }\n}",
)

VAI_ARITHMETIC_OPS = build_known_language_variants(
    python="x = int(input())\ny = int(input())\nprint(x * x + y * y)",
    cpp="#include <iostream>\nusing namespace std;\nint main(){ int x,y; cin>>x>>y; cout<<(x*x+y*y); return 0; }",
    java="import java.util.Scanner;\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int x = sc.nextInt(), y = sc.nextInt();\n    System.out.println(x * x + y * y);\n  }\n}",
    csharp="using System;\nclass Program {\n  static void Main() {\n    int x = int.Parse(Console.ReadLine());\n    int y = int.Parse(Console.ReadLine());\n    Console.WriteLine(x * x + y * y);\n  }\n}",
)

VAI_STDOUT_WRITE = build_known_language_variants(
    python="a = int(input())\nb = int(input())\nprint(a + b)",
    cpp="#include <iostream>\nusing namespace std;\nint main(){ int a,b; cin>>a>>b; cout<<(a+b); return 0; }",
    java="import java.util.Scanner;\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int a = sc.nextInt(), b = sc.nextInt();\n    System.out.println(a + b);\n  }\n}",
    csharp="using System;\nclass Program {\n  static void Main() {\n    int a = int.Parse(Console.ReadLine());\n    int b = int.Parse(Console.ReadLine());\n    Console.WriteLine(a + b);\n  }\n}",
)

VAI_STDIN_READ = build_known_language_variants(
    python="a = int(input())\nb = int(input())\nprint(a + b)",
    cpp="#include <iostream>\nusing namespace std;\nint main(){ int a,b; cin>>a>>b; cout<<(a+b); return 0; }",
    java="import java.util.Scanner;\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int a = sc.nextInt(), b = sc.nextInt();\n    System.out.println(a + b);\n  }\n}",
    csharp="using System;\nclass Program {\n  static void Main() {\n    int a = int.Parse(Console.ReadLine());\n    int b = int.Parse(Console.ReadLine());\n    Console.WriteLine(a + b);\n  }\n}",
)

COND_SIMPLE_BRANCH = build_known_language_variants(
    python="n = int(input())\nif n > 0:\n    print('pos')\nelse:\n    print('nonpos')",
    cpp="#include <iostream>\nusing namespace std;\nint main(){ int n; cin>>n; if(n>0) cout<<\"pos\"; else cout<<\"nonpos\"; return 0; }",
    java="import java.util.Scanner;\npublic class Main {\n  public static void main(String[] args) {\n    int n = new Scanner(System.in).nextInt();\n    System.out.println(n > 0 ? \"pos\" : \"nonpos\");\n  }\n}",
    csharp="using System;\nclass Program {\n  static void Main() {\n    int n = int.Parse(Console.ReadLine());\n    Console.WriteLine(n > 0 ? \"pos\" : \"nonpos\");\n  }\n}",
)

COND_SWITCH = build_known_language_variants(
    python="code = int(input())\nif code == 1:\n    print('one')\nelif code == 2:\n    print('two')\nelse:\n    print('other')",
    cpp="#include <iostream>\nusing namespace std;\nint main(){ int code; cin>>code; switch(code){ case 1: cout<<\"one\"; break; case 2: cout<<\"two\"; break; default: cout<<\"other\"; } return 0; }",
    java="import java.util.Scanner;\npublic class Main {\n  public static void main(String[] args) {\n    int code = new Scanner(System.in).nextInt();\n    switch(code){ case 1: System.out.print(\"one\"); break; case 2: System.out.print(\"two\"); break; default: System.out.print(\"other\"); }\n  }\n}",
    csharp="using System;\nclass Program {\n  static void Main() {\n    int code = int.Parse(Console.ReadLine());\n    switch(code){ case 1: Console.Write(\"one\"); break; case 2: Console.Write(\"two\"); break; default: Console.Write(\"other\"); break; }\n  }\n}",
)

COND_MULTI_BRANCH = build_known_language_variants(
    python=(
        "score = int(input())\n"
        "if score >= 90:\n"
        "    print('A')\n"
        "elif score >= 70:\n"
        "    print('B')\n"
        "else:\n"
        "    print('C')"
    ),
    cpp=(
        "#include <iostream>\nusing namespace std;\n"
        "int main(){ int score; cin>>score; "
        "if(score>=90) cout<<\"A\"; else if(score>=70) cout<<\"B\"; else cout<<\"C\"; return 0; }"
    ),
    java=(
        "import java.util.Scanner;\npublic class Main {\n"
        "  public static void main(String[] args) {\n"
        "    int score = new Scanner(System.in).nextInt();\n"
        "    if(score>=90) System.out.print(\"A\");\n"
        "    else if(score>=70) System.out.print(\"B\");\n"
        "    else System.out.print(\"C\");\n"
        "  }\n}"
    ),
    csharp=(
        "using System;\nclass Program {\n"
        "  static void Main() {\n"
        "    int score = int.Parse(Console.ReadLine());\n"
        "    if(score>=90) Console.Write(\"A\");\n"
        "    else if(score>=70) Console.Write(\"B\");\n"
        "    else Console.Write(\"C\");\n"
        "  }\n}"
    ),
)

COND_IF_ASSEMBLE = build_known_language_variants(
    python="n = int(input())\nif n % 2 == 0:\n    print('even')\nelse:\n    print('odd')",
    cpp="#include <iostream>\nusing namespace std;\nint main(){ int n; cin>>n; if(n%2==0) cout<<\"even\"; else cout<<\"odd\"; return 0; }",
    java="import java.util.Scanner;\npublic class Main {\n  public static void main(String[] args) {\n    int n = new Scanner(System.in).nextInt();\n    System.out.println(n % 2 == 0 ? \"even\" : \"odd\");\n  }\n}",
    csharp="using System;\nclass Program {\n  static void Main() {\n    int n = int.Parse(Console.ReadLine());\n    Console.WriteLine(n % 2 == 0 ? \"even\" : \"odd\");\n  }\n}",
)

LOOP_COUNTED = build_known_language_variants(
    python="n = int(input())\ntotal = 0\nfor i in range(1, n + 1):\n    total += i\nprint(total)",
    cpp="#include <iostream>\nusing namespace std;\nint main(){ int n,total=0; cin>>n; for(int i=1;i<=n;++i) total+=i; cout<<total; return 0; }",
    java="import java.util.Scanner;\npublic class Main {\n  public static void main(String[] args) {\n    int n = new Scanner(System.in).nextInt(), total = 0;\n    for(int i=1;i<=n;i++) total += i;\n    System.out.println(total);\n  }\n}",
    csharp="using System;\nclass Program {\n  static void Main() {\n    int n = int.Parse(Console.ReadLine()), total = 0;\n    for(int i=1;i<=n;i++) total += i;\n    Console.WriteLine(total);\n  }\n}",
)

LOOP_FOR_ASSEMBLE = LOOP_COUNTED

LOOP_COLLECTION = build_known_language_variants(
    python="s = input().strip()\ncount = 0\nfor ch in s:\n    if ch == 'a':\n        count += 1\nprint(count)",
    cpp="#include <iostream>\n#include <string>\nusing namespace std;\nint main(){ string s; cin>>s; int c=0; for(char ch:s) if(ch=='a') ++c; cout<<c; return 0; }",
    java="import java.util.Scanner;\npublic class Main {\n  public static void main(String[] args) {\n    String s = new Scanner(System.in).next();\n    int c = 0; for(char ch : s.toCharArray()) if(ch=='a') c++;\n    System.out.println(c);\n  }\n}",
    csharp="using System;\nclass Program {\n  static void Main() {\n    string s = Console.ReadLine().Trim();\n    int c = 0; foreach(char ch in s) if(ch=='a') c++;\n    Console.WriteLine(c);\n  }\n}",
)

FN_INVOCATION = build_known_language_variants(
    python="def add(a, b):\n    return a + b\nx = int(input())\ny = int(input())\nprint(add(x, y))",
    cpp="#include <iostream>\nusing namespace std;\nint add(int a,int b){ return a+b; }\nint main(){ int x,y; cin>>x>>y; cout<<add(x,y); return 0; }",
    java="import java.util.Scanner;\npublic class Main {\n  static int add(int a,int b){ return a+b; }\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    System.out.println(add(sc.nextInt(), sc.nextInt()));\n  }\n}",
    csharp="using System;\nclass Program {\n  static int Add(int a,int b) => a + b;\n  static void Main() {\n    Console.WriteLine(Add(int.Parse(Console.ReadLine()), int.Parse(Console.ReadLine())));\n  }\n}",
)

ARR_SUM3 = build_known_language_variants(
    python="a = [int(input()), int(input()), int(input())]\nprint(a[0] + a[1] + a[2])",
    cpp="#include <iostream>\nusing namespace std;\nint main(){ int a,b,c; cin>>a>>b>>c; cout<<(a+b+c); return 0; }",
    java="import java.util.Scanner;\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    System.out.println(sc.nextInt()+sc.nextInt()+sc.nextInt());\n  }\n}",
    csharp="using System;\nclass Program {\n  static void Main() {\n    Console.WriteLine(int.Parse(Console.ReadLine())+int.Parse(Console.ReadLine())+int.Parse(Console.ReadLine()));\n  }\n}",
)

STR_LEN = build_known_language_variants(
    python="s = input().strip()\nprint(len(s))",
    cpp="#include <iostream>\n#include <string>\nusing namespace std;\nint main(){ string s; cin>>s; cout<<s.size(); return 0; }",
    java="import java.util.Scanner;\npublic class Main {\n  public static void main(String[] args) {\n    System.out.println(new Scanner(System.in).next().length());\n  }\n}",
    csharp="using System;\nclass Program {\n  static void Main() { Console.WriteLine(Console.ReadLine().Trim().Length); }\n}",
)

REC_PAIR = build_known_language_variants(
    python="a = int(input())\nb = int(input())\nitem = {'x': a, 'y': b}\nprint(item['x'] + item['y'])",
    cpp="#include <iostream>\nusing namespace std;\nint main(){ int x,y; cin>>x>>y; cout<<(x+y); return 0; }",
    java="import java.util.Scanner;\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    System.out.println(sc.nextInt()+sc.nextInt());\n  }\n}",
    csharp="using System;\nclass Program {\n  static void Main() {\n    Console.WriteLine(int.Parse(Console.ReadLine())+int.Parse(Console.ReadLine()));\n  }\n}",
)

MOD_IMPORT = build_known_language_variants(
    python="a = int(input())\nb = int(input())\nprint(a + b)",
    cpp="#include <iostream>\nusing namespace std;\nint add(int a,int b){ return a+b; }\nint main(){ int a,b; cin>>a>>b; cout<<add(a,b); return 0; }",
    java="import java.util.Scanner;\npublic class Main {\n  static int add(int a,int b){ return a+b; }\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    System.out.println(add(sc.nextInt(), sc.nextInt()));\n  }\n}",
    csharp="using System;\nclass Program {\n  static int Add(int a,int b) => a + b;\n  static void Main() {\n    Console.WriteLine(Add(int.Parse(Console.ReadLine()), int.Parse(Console.ReadLine())));\n  }\n}",
)

RECU_FACT = build_known_language_variants(
    python="def fact(n):\n    if n <= 1:\n        return 1\n    return n * fact(n - 1)\nn = int(input())\nprint(fact(n))",
    cpp="#include <iostream>\nusing namespace std;\nint fact(int n){ if(n<=1) return 1; return n*fact(n-1);}\nint main(){ int n; cin>>n; cout<<fact(n); return 0; }",
    java="import java.util.Scanner;\npublic class Main {\n  static int fact(int n){ if(n<=1) return 1; return n*fact(n-1);}\n  public static void main(String[] args) {\n    System.out.println(fact(new Scanner(System.in).nextInt()));\n  }\n}",
    csharp="using System;\nclass Program {\n  static int Fact(int n){ if(n<=1) return 1; return n*Fact(n-1);}\n  static void Main(){ Console.WriteLine(Fact(int.Parse(Console.ReadLine()))); }\n}",
)

ALG_SUM_ABS = build_known_language_variants(
    python="a = int(input())\nb = int(input())\nprint(abs(a) + abs(b))",
    cpp="#include <iostream>\n#include <cstdlib>\nusing namespace std;\nint main(){ int a,b; cin>>a>>b; cout<<(abs(a)+abs(b)); return 0; }",
    java="import java.util.Scanner;\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int a = sc.nextInt(), b = sc.nextInt();\n    System.out.println(Math.abs(a)+Math.abs(b));\n  }\n}",
    csharp="using System;\nclass Program {\n  static void Main() {\n    int a = int.Parse(Console.ReadLine()), b = int.Parse(Console.ReadLine());\n    Console.WriteLine(Math.Abs(a)+Math.Abs(b));\n  }\n}",
)

DS_NODE = build_known_language_variants(
    python="first = int(input())\nsecond = int(input())\nprint(second)",
    cpp="#include <iostream>\nusing namespace std;\nint main(){ int first,second; cin>>first>>second; cout<<second; return 0; }",
    java="import java.util.Scanner;\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    sc.nextInt();\n    System.out.println(sc.nextInt());\n  }\n}",
    csharp="using System;\nclass Program {\n  static void Main() {\n    Console.ReadLine();\n    Console.WriteLine(Console.ReadLine());\n  }\n}",
)

DS_TREE = build_known_language_variants(
    python="parent = int(input())\nchild = int(input())\nprint(parent)",
    cpp="#include <iostream>\nusing namespace std;\nint main(){ int p,c; cin>>p>>c; cout<<p; return 0; }",
    java="import java.util.Scanner;\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    System.out.println(sc.nextInt());\n    sc.nextInt();\n  }\n}",
    csharp="using System;\nclass Program {\n  static void Main() {\n    Console.WriteLine(Console.ReadLine());\n    Console.ReadLine();\n  }\n}",
)

OOP_POINT = build_known_language_variants(
    python="x = int(input())\ny = int(input())\nprint(x + y)",
    cpp="#include <iostream>\nusing namespace std;\nint main(){ int x,y; cin>>x>>y; cout<<(x+y); return 0; }",
    java="import java.util.Scanner;\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    System.out.println(sc.nextInt()+sc.nextInt());\n  }\n}",
    csharp="using System;\nclass Program {\n  static void Main() {\n    Console.WriteLine(int.Parse(Console.ReadLine())+int.Parse(Console.ReadLine()));\n  }\n}",
)

