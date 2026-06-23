"""Capstone (block synthesis) tasks for Pascal v3.1.1 — end of each chapter.

Each chapter gets CAPSTONES_PER_CHAPTER full programs with explicit expected
concepts, teacher reference code, and seed test cases (expanded to 3+ by generator).
"""

from __future__ import annotations

from dataclasses import dataclass

CAPSTONES_PER_CHAPTER = 4

_CHAPTER_SLOT_PREFIX: dict[str, str] = {
    "program_skeleton": "psk",
    "typed_variables": "typ",
    "io": "io",
    "expressions": "exp",
    "conditions": "cnd",
    "loops": "lop",
    "functions": "fn",
    "procedures": "prc",
    "static_arrays": "arr",
    "dynamic_arrays": "dyn",
    "strings": "str",
    "records": "rec",
    "files": "fil",
    "units": "unt",
    "recursion": "rcu",
    "oop": "oop",
    "error_handling": "exc",
    "pascal_pitfalls": "pit",
    "compiler_diagnostics": "cdg",
}


@dataclass(frozen=True)
class CapstoneSpec:
    title: str
    task_format: str
    goal: str
    features: str
    difficulty: str
    pattern: str
    pascal: str
    python: str
    cpp: str
    expected_concept_ids: tuple[str, ...]
    test_cases: tuple[dict[str, str], ...]
    starter_pascal: str = ""
    action: str = "translate"


def _prog(body: str) -> str:
    return f"program Demo;\nvar\n  n: integer;\nbegin\n{body}\nend.\n"


def _cap(
    title: str,
    goal: str,
    features: str,
    pascal: str,
    py: str,
    cpp: str,
    concepts: tuple[str, ...],
    tests: tuple[dict[str, str], ...],
    *,
    task_format: str = "перевод_программы",
    difficulty: str = "medium",
    pattern: str = "cap_translate",
    starter: str = "",
) -> CapstoneSpec:
    action = "debug" if task_format in {"исправление", "поиск_ошибки"} else "translate"
    if task_format == "исправление":
        pattern = "cap_fix"
    return CapstoneSpec(
        title=title,
        task_format=task_format,
        goal=goal,
        features=features,
        difficulty=difficulty,
        pattern=pattern,
        pascal=pascal,
        python=py,
        cpp=cpp,
        expected_concept_ids=concepts,
        test_cases=tests,
        starter_pascal=starter,
        action=action,
    )


# fmt: off
_CAPSTONE_BY_CHAPTER: dict[str, tuple[CapstoneSpec, ...]] = {
    "program_skeleton": (
        _cap(
            "Итог: приветствие по имени",
            "Собрать program с Readln и Writeln для приветствия",
            "program; readln; writeln; var; string",
            _prog("  Writeln('Enter name:');\n  Readln(n);\n  Writeln('Hello, user #', n);"),
            "print('Enter name:')\nn = int(input())\nprint('Hello, user #' + str(n))",
            "#include <iostream>\nusing namespace std;\nint main() {\n  int n;\n  cout << \"Enter number: \";\n  cin >> n;\n  cout << \"Hello, user #\" << n << endl;\n  return 0;\n}",
            ("program_entry", "block_scope", "stdin_read", "stdout_write", "typed_declaration"),
            ({"inputs": "7\n", "output": "Enter name:\nHello, user #7"},),
            starter="program Demo;\nvar\n  n: integer;\nbegin\n\nend.\n",
        ),
        _cap(
            "Итог: линейный алгоритм",
            "Перенести последовательность операторов в каркас program",
            "program; writeln; assignment",
            _prog("  n := 2;\n  Writeln(n + 3);"),
            "x = 2\nprint(x + 3)",
            "int main() {\n  int n = 2;\n  cout << n + 3 << endl;\n  return 0;\n}",
            ("program_entry", "block_scope", "assignment", "stdout_write"),
            ({"inputs": "", "output": "5"},),
            starter="program Demo;\nvar\n  n: integer;\nbegin\n\nend.\n",
        ),
        _cap(
            "Итог: исправить end.",
            "Исправить завершение program — нужна точка после end",
            "program; begin; end.",
            _prog("  Writeln('done');"),
            "print('done')",
            "int main() { cout << \"done\" << endl; return 0; }",
            ("program_entry", "block_scope", "stdout_write"),
            ({"inputs": "", "output": "done"},),
            task_format="исправление",
            starter="program Demo;\nbegin\n  Writeln('done');\nend\n",
        ),
        _cap(
            "Итог: комментарии в программе",
            "Добавить комментарии Pascal в рабочую программу",
            "program; comment; writeln",
            "program Demo;\nbegin\n  { start marker }\n  Writeln('ok');\n  (* finish *)\nend.\n",
            "# start\nprint('ok')  # finish",
            "int main() {\n  // start\n  cout << \"ok\" << endl;\n  return 0;\n}",
            ("program_entry", "block_scope", "pascal_comment", "stdout_write"),
            ({"inputs": "", "output": "ok"},),
        ),
    ),
    "typed_variables": (
        _cap(
            "Итог: сумма двух integer",
            "Объявить переменные и вывести сумму",
            "var; integer; readln; writeln",
            _prog("  Readln(n);\n  Writeln(n + 10);"),
            "a = int(input())\nprint(a + 10)",
            "int main() {\n  int n;\n  cin >> n;\n  cout << n + 10 << endl;\n  return 0;\n}",
            ("typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops"),
            ({"inputs": "5\n", "output": "15"},),
        ),
        _cap(
            "Итог: вещественное среднее",
            "Использовать real и вывести среднее двух чисел",
            "var; real; readln; writeln",
            "program Demo;\nvar\n  a, b: real;\n  avg: real;\nbegin\n  Readln(a);\n  Readln(b);\n  avg := (a + b) / 2;\n  Writeln(avg:0:2);\nend.\n",
            "a = float(input())\nb = float(input())\nprint(f'{(a+b)/2:.2f}')",
            "int main() {\n  double a, b;\n  cin >> a >> b;\n  cout << fixed << (a+b)/2 << endl;\n  return 0;\n}",
            ("typed_declaration", "stdin_read", "stdout_write", "assignment", "arithmetic_ops"),
            ({"inputs": "2\n4\n", "output": "3.00"},),
        ),
        _cap(
            "Итог: флаг boolean",
            "Сравнить число с порогом через boolean",
            "var; boolean; if; writeln",
            "program Demo;\nvar\n  n: integer;\n  ok: boolean;\nbegin\n  Readln(n);\n  ok := n >= 18;\n  if ok then Writeln('yes') else Writeln('no');\nend.\n",
            "n = int(input())\nprint('yes' if n >= 18 else 'no')",
            "int main() {\n  int n; cin >> n;\n  cout << (n>=18?\"yes\":\"no\") << endl;\n  return 0;\n}",
            ("typed_declaration", "simple_branch", "stdin_read", "stdout_write"),
            ({"inputs": "20\n", "output": "yes"}, {"inputs": "10\n", "output": "no"}),
        ),
        _cap(
            "Итог: исправить :=",
            "Заменить = на := в теле program",
            "assignment; var; writeln",
            _prog("  n := 42;\n  Writeln(n);"),
            "n = 42\nprint(n)",
            "int main() { int n = 42; cout << n << endl; return 0; }",
            ("assignment", "typed_declaration", "stdout_write"),
            ({"inputs": "", "output": "42"},),
            task_format="исправление",
            starter="program Demo;\nvar n: integer;\nbegin\n  n = 42;\n  Writeln(n);\nend.\n",
        ),
    ),
    "io": (
        _cap(
            "Итог: ввод двух чисел — сумма",
            "Readln два раза, Writeln сумму",
            "readln; writeln; integer",
            "program Demo;\nvar\n  a, b: integer;\nbegin\n  Readln(a);\n  Readln(b);\n  Writeln(a + b);\nend.\n",
            "a = int(input())\nb = int(input())\nprint(a+b)",
            "int main() {\n  int a,b; cin>>a>>b; cout<<a+b<<endl; return 0;\n}",
            ("stdin_read", "stdout_write", "typed_declaration", "arithmetic_ops"),
            ({"inputs": "3\n4\n", "output": "7"},),
        ),
        _cap(
            "Итог: echo строки",
            "Прочитать строку и вывести её же",
            "readln; writeln; string",
            "program Demo;\nvar\n  s: string;\nbegin\n  Readln(s);\n  Writeln(s);\nend.\n",
            "s = input()\nprint(s)",
            "int main() {\n  string s; getline(cin,s); cout<<s<<endl; return 0;\n}",
            ("stdin_read", "stdout_write", "string_sequence"),
            ({"inputs": "hi\n", "output": "hi"},),
        ),
        _cap(
            "Итог: несколько аргументов Writeln",
            "Writeln с несколькими значениями",
            "writeln; integer",
            _prog("  n := 7;\n  Writeln('n=', n);"),
            "n=7\nprint('n=', n)",
            "int main() { int n=7; cout<<\"n=\"<<n<<endl; return 0; }",
            ("stdout_write", "assignment"),
            ({"inputs": "", "output": "n=7"},),
        ),
        _cap(
            "Итог: порядок Readln/Writeln",
            "Исправить порядок: сначала ввод, потом вывод",
            "readln; writeln",
            _prog("  Readln(n);\n  Writeln(n);"),
            "n=int(input())\nprint(n)",
            "int main(){int n;cin>>n;cout<<n<<endl;return 0;}",
            ("stdin_read", "stdout_write"),
            ({"inputs": "9\n", "output": "9"},),
            task_format="исправление",
            starter="program Demo;\nvar n: integer;\nbegin\n  Writeln(n);\n  Readln(n);\nend.\n",
        ),
    ),
    "expressions": (
        _cap(
            "Итог: div и mod",
            "Вывести частное и остаток через div/mod",
            "div; mod; writeln",
            _prog("  n := 17;\n  Writeln(n div 5, ' ', n mod 5);"),
            "n=17\nprint(n//5, n%5)",
            "int main(){int n=17; cout<<n/5<<' '<<n%5<<endl; return 0;}",
            ("arithmetic_ops", "assignment", "stdout_write"),
            ({"inputs": "", "output": "3 2"},),
        ),
        _cap(
            "Итог: арифметика в выражении",
            "Вычислить выражение с +, *, скобками",
            "arithmetic_ops; assignment",
            _prog("  n := (2 + 3) * 4;\n  Writeln(n);"),
            "n=(2+3)*4\nprint(n)",
            "int main(){int n=(2+3)*4; cout<<n<<endl; return 0;}",
            ("arithmetic_ops", "assignment", "stdout_write"),
            ({"inputs": "", "output": "20"},),
        ),
        _cap(
            "Итог: логика and/or",
            "Составное условие с and",
            "and; or; if",
            "program Demo;\nvar\n  x, y: integer;\nbegin\n  Readln(x);\n  Readln(y);\n  if (x > 0) and (y > 0) then Writeln('ok') else Writeln('no');\nend.\n",
            "x=int(input()); y=int(input())\nprint('ok' if x>0 and y>0 else 'no')",
            "int main(){int x,y;cin>>x>>y; if(x>0&&y>0) cout<<\"ok\"; else cout<<\"no\"; return 0;}",
            ("simple_branch", "stdin_read", "stdout_write", "arithmetic_ops"),
            ({"inputs": "1\n2\n", "output": "ok"}, {"inputs": "-1\n2\n", "output": "no"}),
        ),
        _cap(
            "Итог: mod только для integer",
            "Исправить mod для целых",
            "mod; div",
            _prog("  n := 10 mod 3;\n  Writeln(n);"),
            "print(10 % 3)",
            "int main(){cout<<10%3<<endl;return 0;}",
            ("arithmetic_ops", "stdout_write"),
            ({"inputs": "", "output": "1"},),
            task_format="исправление",
            starter="program Demo;\nvar n: real;\nbegin\n  n := 10 mod 3;\n  Writeln(n:0:0);\nend.\n",
        ),
    ),
    "conditions": (
        _cap(
            "Итог: знак числа",
            "if then else для определения знака",
            "if then else; readln",
            _prog("  Readln(n);\n  if n > 0 then Writeln('pos') else if n < 0 then Writeln('neg') else Writeln('zero');"),
            "n=int(input())\nprint('pos' if n>0 else 'neg' if n<0 else 'zero')",
            "int main(){int n;cin>>n; if(n>0)cout<<\"pos\"; else if(n<0)cout<<\"neg\"; else cout<<\"zero\"; return 0;}",
            ("simple_branch", "multi_branch", "stdin_read", "stdout_write"),
            ({"inputs": "5\n", "output": "pos"}, {"inputs": "-1\n", "output": "neg"}, {"inputs": "0\n", "output": "zero"}),
        ),
        _cap(
            "Итог: case of день недели",
            "case of по номеру 1..3",
            "case of; readln",
            "program Demo;\nvar\n  d: integer;\nbegin\n  Readln(d);\n  case d of\n    1: Writeln('mon');\n    2: Writeln('tue');\n    3: Writeln('wed');\n  else Writeln('?');\n  end;\nend.\n",
            "d=int(input())\nm={1:'mon',2:'tue',3:'wed'}.get(d,'?')\nprint(m)",
            "int main(){int d;cin>>d; switch(d){case 1:cout<<\"mon\";break;case 2:cout<<\"tue\";break;case 3:cout<<\"wed\";break;default:cout<<\"?\";} return 0;}",
            ("switch_selection", "stdin_read", "stdout_write"),
            ({"inputs": "2\n", "output": "tue"}, {"inputs": "9\n", "output": "?"}),
        ),
        _cap(
            "Итог: max из двух",
            "if then else для максимума",
            "if then else",
            "program Demo;\nvar\n  a, b, m: integer;\nbegin\n  Readln(a);\n  Readln(b);\n  if a > b then m := a else m := b;\n  Writeln(m);\nend.\n",
            "a,b=map(int,input().split())\nprint(max(a,b))",
            "int main(){int a,b;cin>>a>>b; cout<<max(a,b)<<endl; return 0;}",
            ("simple_branch", "assignment", "stdin_read", "stdout_write"),
            ({"inputs": "3\n7\n", "output": "7"},),
        ),
        _cap(
            "Итог: ; перед else",
            "Убрать лишнюю ; перед else",
            "if then else",
            _prog("  n := 1;\n  if n > 0 then Writeln('yes') else Writeln('no');"),
            "n=1\nprint('yes' if n>0 else 'no')",
            "int main(){int n=1; if(n>0) cout<<\"yes\"; else cout<<\"no\"; return 0;}",
            ("simple_branch", "stdout_write"),
            ({"inputs": "", "output": "yes"},),
            task_format="исправление",
            starter="program Demo;\nvar n: integer;\nbegin\n  n := 1;\n  if n > 0 then;\n    Writeln('yes')\n  else\n    Writeln('no');\nend.\n",
        ),
    ),
    "loops": (
        _cap(
            "Итог: сумма 1..n",
            "for to do — сумма чисел",
            "for to do",
            "program Demo;\nvar\n  n, i, s: integer;\nbegin\n  Readln(n);\n  s := 0;\n  for i := 1 to n do s := s + i;\n  Writeln(s);\nend.\n",
            "n=int(input())\nprint(sum(range(1,n+1)))",
            "int main(){int n,s=0; cin>>n; for(int i=1;i<=n;i++) s+=i; cout<<s<<endl; return 0;}",
            ("counted_loop", "stdin_read", "stdout_write", "assignment"),
            ({"inputs": "5\n", "output": "15"},),
        ),
        _cap(
            "Итог: while — степень двойки",
            "while do пока n < 100",
            "while do",
            "program Demo;\nvar\n  n: integer;\nbegin\n  n := 1;\n  while n < 100 do n := n * 2;\n  Writeln(n);\nend.\n",
            "n=1\nwhile n<100: n*=2\nprint(n)",
            "int main(){int n=1; while(n<100) n*=2; cout<<n<<endl; return 0;}",
            ("pre_condition_loop", "assignment", "stdout_write"),
            ({"inputs": "", "output": "128"},),
        ),
        _cap(
            "Итог: repeat until",
            "repeat until накопление суммы",
            "repeat until",
            "program Demo;\nvar\n  s, x: integer;\nbegin\n  s := 0;\n  repeat\n    Readln(x);\n    s := s + x;\n  until x = 0;\n  Writeln(s);\nend.\n",
            "s=0\nwhile True:\n x=int(input())\n s+=x\n if x==0: break\nprint(s)",
            "int main(){int s=0,x; do{cin>>x;s+=x;}while(x!=0); cout<<s<<endl; return 0;}",
            ("post_condition_loop", "stdin_read", "stdout_write"),
            ({"inputs": "2\n3\n0\n", "output": "5"},),
        ),
        _cap(
            "Итог: for downto",
            "for downto — обратный счёт",
            "for downto",
            "program Demo;\nvar\n  i: integer;\nbegin\n  for i := 3 downto 1 do Writeln(i);\nend.\n",
            "for i in range(3,0,-1): print(i)",
            "int main(){for(int i=3;i>=1;i--) cout<<i<<endl; return 0;}",
            ("counted_loop", "stdout_write"),
            ({"inputs": "", "output": "3\n2\n1"},),
        ),
    ),
    "functions": (
        _cap(
            "Итог: function sqr",
            "function с Result",
            "function; result",
            "program Demo;\nvar\n  n: integer;\nfunction Sqr(x: integer): integer;\nbegin\n  Sqr := x * x;\nend;\nbegin\n  Readln(n);\n  Writeln(Sqr(n));\nend.\n",
            "def sqr(x): return x*x\nprint(sqr(int(input())))",
            "int sqr(int x){return x*x;} int main(){int n;cin>>n;cout<<sqr(n)<<endl;return 0;}",
            ("function_definition", "return_flow", "function_invocation", "stdin_read", "stdout_write"),
            ({"inputs": "4\n", "output": "16"},),
        ),
        _cap(
            "Итог: function max2",
            "function max из двух",
            "function; result; if",
            "program Demo;\nvar\n  a, b: integer;\nfunction Max2(x, y: integer): integer;\nbegin\n  if x > y then Max2 := x else Max2 := y;\nend;\nbegin\n  Readln(a);\n  Readln(b);\n  Writeln(Max2(a, b));\nend.\n",
            "def max2(x,y): return x if x>y else y\na,b=map(int,input().split())\nprint(max2(a,b))",
            "int max2(int x,int y){return x>y?x:y;} int main(){int a,b;cin>>a>>b;cout<<max2(a,b)<<endl;return 0;}",
            ("function_definition", "simple_branch", "return_flow", "function_invocation"),
            ({"inputs": "2\n9\n", "output": "9"},),
        ),
        _cap(
            "Итог: factorial function",
            "function fact с Result",
            "function; result; for",
            "program Demo;\nvar\n  n: integer;\nfunction Fact(k: integer): integer;\nvar i, r: integer;\nbegin\n  r := 1;\n  for i := 1 to k do r := r * i;\n  Fact := r;\nend;\nbegin\n  Readln(n);\n  Writeln(Fact(n));\nend.\n",
            "def fact(k):\n r=1\n for i in range(1,k+1): r*=i\n return r\nprint(fact(int(input())))",
            "int fact(int k){int r=1; for(int i=1;i<=k;i++) r*=i; return r;} int main(){int n;cin>>n;cout<<fact(n)<<endl;return 0;}",
            ("function_definition", "counted_loop", "return_flow"),
            ({"inputs": "5\n", "output": "120"},),
        ),
        _cap(
            "Итог: Result во всех ветках",
            "Добавить Result в else",
            "function; result",
            "program Demo;\nfunction Sign(x: integer): integer;\nbegin\n  if x > 0 then Sign := 1 else Sign := -1;\nend;\nbegin\n  Writeln(Sign(-3));\nend.\n",
            "def sign(x): return 1 if x>0 else -1\nprint(sign(-3))",
            "int sign(int x){return x>0?1:-1;} int main(){cout<<sign(-3)<<endl;return 0;}",
            ("function_definition", "return_flow", "simple_branch"),
            ({"inputs": "", "output": "-1"},),
            task_format="исправление",
            starter="program Demo;\nfunction Sign(x: integer): integer;\nbegin\n  if x > 0 then Sign := 1;\nend;\nbegin\n  Writeln(Sign(-3));\nend.\n",
        ),
    ),
    "procedures": (
        _cap(
            "Итог: procedure Swap",
            "procedure с var-параметрами",
            "procedure; var",
            "program Demo;\nvar\n  a, b: integer;\nprocedure Swap(var x, y: integer);\nvar t: integer;\nbegin\n  t := x; x := y; y := t;\nend;\nbegin\n  a := 1; b := 2;\n  Swap(a, b);\n  Writeln(a, ' ', b);\nend.\n",
            "def swap(a,b): return b,a\na,b=1,2\na,b=swap(a,b)\nprint(a,b)",
            "void swap(int&x,int&y){int t=x;x=y;y=t;} int main(){int a=1,b=2; swap(a,b); cout<<a<<' '<<b<<endl;return 0;}",
            ("parameter_passing", "assignment", "stdout_write"),
            ({"inputs": "", "output": "2 1"},),
        ),
        _cap(
            "Итог: procedure PrintTwice",
            "procedure без возврата",
            "procedure; writeln",
            "program Demo;\nprocedure PrintTwice(x: integer);\nbegin\n  Writeln(x);\n  Writeln(x);\nend;\nbegin\n  PrintTwice(7);\nend.\n",
            "def pt(x):\n print(x); print(x)\npt(7)",
            "void pt(int x){cout<<x<<endl<<x<<endl;} int main(){pt(7);return 0;}",
            ("parameter_passing", "stdout_write", "function_invocation"),
            ({"inputs": "", "output": "7\n7"},),
        ),
        _cap(
            "Итог: const-параметр",
            "procedure с const",
            "procedure; const",
            "program Demo;\nprocedure Show(const msg: string);\nbegin\n  Writeln(msg);\nend;\nbegin\n  Show('hi');\nend.\n",
            "def show(msg): print(msg)\nshow('hi')",
            "void show(const string& msg){cout<<msg<<endl;} int main(){show(\"hi\");return 0;}",
            ("parameter_passing", "stdout_write"),
            ({"inputs": "", "output": "hi"},),
        ),
        _cap(
            "Итог: Swap без var",
            "Добавить var к параметрам Swap",
            "procedure; var",
            "program Demo;\nvar a,b: integer;\nprocedure Swap(var x,y: integer); var t:integer; begin t:=x;x:=y;y:=t; end;\nbegin a:=3;b:=4; Swap(a,b); Writeln(a,' ',b); end.\n",
            "Same swap fix",
            "void swap(int&x,int&y){int t=x;x=y;y=t;}",
            ("parameter_passing", "assignment"),
            ({"inputs": "", "output": "4 3"},),
            task_format="исправление",
            starter="program Demo;\nvar a,b: integer;\nprocedure Swap(x,y: integer); var t:integer; begin t:=x;x:=y;y:=t; end;\nbegin a:=3;b:=4; Swap(a,b); Writeln(a,' ',b); end.\n",
        ),
    ),
    "static_arrays": (
        _cap(
            "Итог: заполнить массив",
            "array[1..n] и цикл for",
            "array; for",
            "program Demo;\nvar\n  a: array[1..3] of integer;\n  i: integer;\nbegin\n  for i := 1 to 3 do a[i] := i * 2;\n  Writeln(a[2]);\nend.\n",
            "a=[i*2 for i in range(1,4)]\nprint(a[1])",
            "int main(){int a[4]; for(int i=1;i<=3;i++) a[i]=i*2; cout<<a[2]<<endl;return 0;}",
            ("indexed_sequence", "counted_loop", "assignment", "stdout_write"),
            ({"inputs": "", "output": "4"},),
        ),
        _cap(
            "Итог: сумма массива",
            "Обход Low..High",
            "array; for; low; high",
            "program Demo;\nvar\n  a: array[1..4] of integer;\n  i, s: integer;\nbegin\n  for i := 1 to 4 do a[i] := i;\n  s := 0;\n  for i := Low(a) to High(a) do s := s + a[i];\n  Writeln(s);\nend.\n",
            "a=list(range(1,5))\nprint(sum(a))",
            "int main(){int a[5],s=0; for(int i=1;i<=4;i++){a[i]=i;s+=a[i];} cout<<s<<endl;return 0;}",
            ("indexed_sequence", "counted_loop", "arithmetic_ops"),
            ({"inputs": "", "output": "10"},),
        ),
        _cap(
            "Итог: max в массиве",
            "Поиск максимума в array",
            "array; for; if",
            "program Demo;\nvar\n  a: array[1..3] of integer;\n  i, m: integer;\nbegin\n  a[1]:=2; a[2]:=9; a[3]:=5;\n  m := a[1];\n  for i := 2 to 3 do if a[i] > m then m := a[i];\n  Writeln(m);\nend.\n",
            "a=[2,9,5]\nprint(max(a))",
            "int main(){int a[]={0,2,9,5}; int m=a[1]; for(int i=2;i<=3;i++) if(a[i]>m)m=a[i]; cout<<m<<endl;return 0;}",
            ("indexed_sequence", "simple_branch", "counted_loop"),
            ({"inputs": "", "output": "9"},),
        ),
        _cap(
            "Итог: индекс 1-based",
            "Исправить a[0] на a[1]",
            "array",
            "program Demo;\nvar a: array[1..2] of integer;\nbegin a[1]:=1; a[2]:=2; Writeln(a[1]); end.\n",
            "a=[1,2]; print(a[0])",
            "int a[]={0,1,2}; cout<<a[1]<<endl;",
            ("indexed_sequence", "stdout_write"),
            ({"inputs": "", "output": "1"},),
            task_format="исправление",
            starter="program Demo;\nvar a: array[1..2] of integer;\nbegin a[0]:=1; Writeln(a[0]); end.\n",
        ),
    ),
    "dynamic_arrays": (
        _cap(
            "Итог: SetLength и запись",
            "dynamic array + SetLength",
            "setlength; array",
            "program Demo;\nvar\n  a: array of integer;\nbegin\n  SetLength(a, 3);\n  a[0] := 5;\n  a[1] := 6;\n  a[2] := 7;\n  Writeln(a[1]);\nend.\n",
            "a=[0]*3\na[0]=5;a[1]=6;a[2]=7\nprint(a[1])",
            "int main(){vector<int>a(3); a[0]=5;a[1]=6;a[2]=7; cout<<a[1]<<endl;return 0;}",
            ("dynamic_array", "indexed_sequence", "stdout_write"),
            ({"inputs": "", "output": "6"},),
        ),
        _cap(
            "Итог: рост массива в цикле",
            "SetLength в цикле",
            "setlength; for",
            "program Demo;\nvar\n  a: array of integer;\n  i: integer;\nbegin\n  SetLength(a, 0);\n  for i := 1 to 3 do\n  begin\n    SetLength(a, Length(a) + 1);\n    a[Length(a)-1] := i;\n  end;\n  Writeln(Length(a), ' ', a[2]);\nend.\n",
            "a=[]\nfor i in range(1,4): a.append(i)\nprint(len(a), a[2])",
            "int main(){vector<int>a; for(int i=1;i<=3;i++) a.push_back(i); cout<<a.size()<<' '<<a[2]<<endl;return 0;}",
            ("dynamic_array", "counted_loop"),
            ({"inputs": "", "output": "3 3"},),
        ),
        _cap(
            "Итог: Copy среза",
            "Copy для dynamic array",
            "copy; setlength",
            "program Demo;\nvar\n  a, b: array of integer;\n  i: integer;\nbegin\n  SetLength(a, 4);\n  for i := 0 to 3 do a[i] := i + 1;\n  b := Copy(a, 1, 2);\n  Writeln(Length(b), ' ', b[0], b[1]);\nend.\n",
            "a=list(range(1,5))\nb=a[1:3]\nprint(len(b), b[0], b[1])",
            "int main(){vector<int>a={1,2,3,4}; vector<int>b(a.begin()+1,a.begin()+3); cout<<b.size()<<' '<<b[0]<<' '<<b[1]<<endl;return 0;}",
            ("dynamic_array", "string_sequence"),
            ({"inputs": "", "output": "2 2 3"},),
        ),
        _cap(
            "Итог: SetLength off-by-one",
            "Исправить индекс после SetLength",
            "setlength",
            "program Demo;\nvar a: array of integer;\nbegin SetLength(a,1); a[0]:=9; Writeln(a[0]); end.\n",
            "a=[9]; print(a[0])",
            "vector<int>a(1); a[0]=9; cout<<a[0];",
            ("dynamic_array", "indexed_sequence"),
            ({"inputs": "", "output": "9"},),
            task_format="исправление",
            starter="program Demo;\nvar a: array of integer;\nbegin SetLength(a,1); a[1]:=9; Writeln(a[1]); end.\n",
        ),
    ),
    "strings": (
        _cap(
            "Итог: Length строки",
            "Length(s) и вывод",
            "string; length",
            "program Demo;\nvar s: string;\nbegin s := 'abcd'; Writeln(Length(s)); end.\n",
            "s='abcd'\nprint(len(s))",
            "int main(){string s=\"abcd\"; cout<<s.size()<<endl;return 0;}",
            ("string_sequence", "stdout_write"),
            ({"inputs": "", "output": "4"},),
        ),
        _cap(
            "Итог: цикл по строке",
            "for i := 1 to Length(s)",
            "string; for; length",
            "program Demo;\nvar s: string; i: integer;\nbegin s:='ab'; for i:=1 to Length(s) do Write(s[i]); Writeln; end.\n",
            "s='ab'\nprint(''.join(s))",
            "int main(){string s=\"ab\"; for(char c:s) cout<<c; cout<<endl;return 0;}",
            ("string_sequence", "counted_loop", "stdout_write"),
            ({"inputs": "", "output": "ab"},),
        ),
        _cap(
            "Итог: Copy подстроки",
            "Copy(s, start, count)",
            "copy; string",
            "program Demo;\nvar s: string;\nbegin s:='hello'; Writeln(Copy(s,2,3)); end.\n",
            "s='hello'\nprint(s[1:4])",
            "int main(){string s=\"hello\"; cout<<s.substr(1,3)<<endl;return 0;}",
            ("string_sequence", "stdout_write"),
            ({"inputs": "", "output": "ell"},),
        ),
        _cap(
            "Итог: последний символ",
            "s[Length(s)] вместо s[0]",
            "string; length",
            "program Demo;\nvar s:string;\nbegin s:='cat'; Writeln(s[Length(s)]); end.\n",
            "s='cat'; print(s[-1])",
            "string s=\"cat\"; cout<<s[s.size()-1];",
            ("string_sequence",),
            ({"inputs": "", "output": "t"},),
            task_format="исправление",
            starter="program Demo;\nvar s:string;\nbegin s:='cat'; Writeln(s[0]); end.\n",
        ),
    ),
    "records": (
        _cap(
            "Итог: record Person",
            "record с полями и вывод",
            "record",
            "program Demo;\ntype\n  TPerson = record\n    name: string;\n    age: integer;\n  end;\nvar p: TPerson;\nbegin\n  p.name := 'Ann';\n  p.age := 20;\n  Writeln(p.name, ' ', p.age);\nend.\n",
            "p={'name':'Ann','age':20}\nprint(p['name'], p['age'])",
            "struct P{string name; int age;}; int main(){P p{\"Ann\",20}; cout<<p.name<<' '<<p.age<<endl;return 0;}",
            ("key_value_map", "typed_declaration", "stdout_write"),
            ({"inputs": "", "output": "Ann 20"},),
        ),
        _cap(
            "Итог: with record",
            "with p do для доступа к полям",
            "with; record",
            "program Demo;\ntype T=record x:integer; end;\nvar r:T;\nbegin r.x:=5; with r do Writeln(x); end.\n",
            "r={'x':5}\nprint(r['x'])",
            "struct T{int x;}; int main(){T r{5}; cout<<r.x<<endl;return 0;}",
            ("key_value_map", "stdout_write"),
            ({"inputs": "", "output": "5"},),
        ),
        _cap(
            "Итог: обмен полей",
            "Swap полей record через временную переменную",
            "record; assignment",
            "program Demo;\ntype T=record a,b:integer; end;\nvar r:T; t:integer;\nbegin r.a:=1;r.b:=2; t:=r.a; r.a:=r.b; r.b:=t; Writeln(r.a,' ',r.b); end.\n",
            "swap record fields with temp",
            "swap with temp",
            ("key_value_map", "assignment", "stdout_write"),
            ({"inputs": "", "output": "2 1"},),
            task_format="исправление",
            starter="program Demo;\ntype T=record a,b:integer; end;\nvar r:T;\nbegin r.a:=1;r.b:=2; r.a:=r.b; r.b:=r.a; Writeln(r.a,' ',r.b); end.\n",
        ),
        _cap(
            "Итог: указатель на record",
            "New и p^ для record",
            "record; new; ^",
            "program Demo;\ntype T=record v:integer; end;\nvar p: ^T;\nbegin New(p); p^.v:=7; Writeln(p^.v); Dispose(p); end.\n",
            "class T: v=0\np=T(); p.v=7; print(p.v)",
            "struct T{int v;}; int main(){T* p=new T(); p->v=7; cout<<p->v<<endl; delete p;return 0;}",
            ("key_value_map", "stdout_write"),
            ({"inputs": "", "output": "7"},),
        ),
    ),
    "files": (
        _cap(
            "Итог: запись в файл",
            "Assign/Rewrite/Writeln/CloseFile",
            "textfile; rewrite",
            "program Demo;\nvar f: text;\nbegin Assign(f,'out.txt'); Rewrite(f); Writeln(f,'ok'); CloseFile(f); Writeln('done'); end.\n",
            "open('out.txt','w').write('ok')\nprint('done')",
            "ofstream f(\"out.txt\"); f<<\"ok\"; f.close(); cout<<\"done\";",
            ("file_read", "stdout_write"),
            ({"inputs": "", "output": "done"},),
        ),
        _cap(
            "Итог: чтение строки (шаблон)",
            "Записать шаблон Reset/Readln/CloseFile",
            "textfile; reset; closefile",
            "program Demo;\nvar f: text; s: string;\nbegin\n  { Assign(f,'data.txt'); Reset(f); Readln(f,s); CloseFile(f); }\n  s := 'line';\n  Writeln(s);\nend.\n",
            "s='line'\nprint(s)",
            "string s=\"line\"; cout<<s;",
            ("file_read", "stdout_write", "string_sequence"),
            ({"inputs": "", "output": "line"},),
        ),
        _cap(
            "Итог: подсчёт строк (шаблон)",
            "Цикл while not Eof — учебный шаблон",
            "eof; while; textfile",
            "program Demo;\nvar n: integer;\nbegin\n  n := 0;\n  { while not Eof(f) do Inc(n); }\n  n := 3;\n  Writeln(n);\nend.\n",
            "print(3)",
            "cout<<3;",
            ("file_read", "pre_condition_loop", "stdout_write"),
            ({"inputs": "", "output": "3"},),
        ),
        _cap(
            "Итог: CloseFile",
            "Добавить CloseFile после записи",
            "closefile; textfile",
            "program Demo;\nvar f:text;\nbegin Assign(f,'o.txt'); Rewrite(f); Writeln(f,'x'); CloseFile(f); Writeln('ok'); end.\n",
            "write file close",
            "rewrite close",
            ("file_read", "stdout_write"),
            ({"inputs": "", "output": "ok"},),
            task_format="исправление",
            starter="program Demo;\nvar f:text;\nbegin Assign(f,'o.txt'); Rewrite(f); Writeln(f,'x'); Writeln('ok'); end.\n",
        ),
    ),
    "units": (
        _cap(
            "Итог: program с uses",
            "uses SysUtils в program",
            "uses; program",
            "program Demo;\nuses SysUtils;\nbegin Writeln('ok'); end.\n",
            "import math\nprint('ok')",
            "int main(){cout<<\"ok\"<<endl;return 0;}",
            ("import_dependency", "program_entry", "stdout_write"),
            ({"inputs": "", "output": "ok"},),
        ),
        _cap(
            "Итог: unit interface (фрагмент)",
            "Записать заголовок unit и interface",
            "unit; interface",
            "unit DemoUnit;\ninterface\nprocedure Hello;\nimplementation\nprocedure Hello;\nbegin\n  Writeln('hi');\nend.\nend.\n",
            "# unit fragment",
            "unit DemoUnit; interface void Hello();",
            ("import_dependency", "parameter_passing"),
            ({"inputs": "", "output": ""},),
            task_format="перевод_фрагмента",
        ),
        _cap(
            "Итог: экспорт procedure (фрагмент)",
            "procedure в interface unit",
            "interface; procedure",
            "unit U;\ninterface\nprocedure P;\nimplementation\nprocedure P;\nbegin\n  Writeln(1);\nend;\nend.\n",
            "export procedure",
            "export proc",
            ("import_dependency", "parameter_passing", "stdout_write"),
            ({"inputs": "", "output": ""},),
            task_format="перевод_фрагмента",
        ),
        _cap(
            "Итог: uses после begin — ошибка",
            "Переместить uses в заголовок",
            "uses",
            "program Demo;\nuses SysUtils;\nbegin Writeln(1); end.\n",
            "fix uses placement",
            "fix uses",
            ("import_dependency", "program_entry"),
            ({"inputs": "", "output": "1"},),
            task_format="исправление",
            starter="program Demo;\nbegin\nuses SysUtils;\nWriteln(1);\nend.\n",
        ),
    ),
    "recursion": (
        _cap(
            "Итог: factorial recursive",
            "Рекурсивная function Fact",
            "recursion; function",
            "program Demo;\nvar n:integer;\nfunction Fact(k:integer):integer;\nbegin if k<=1 then Fact:=1 else Fact:=k*Fact(k-1); end;\nbegin Readln(n); Writeln(Fact(n)); end.\n",
            "def f(k): return 1 if k<=1 else k*f(k-1)",
            "int f(int k){return k<=1?1:k*f(k-1);}",
            ("recursion", "function_definition", "return_flow", "stdin_read"),
            ({"inputs": "5\n", "output": "120"},),
        ),
        _cap(
            "Итог: sum 1..n recursive",
            "Рекурсия вместо цикла",
            "recursion",
            "program Demo;\nvar n:integer;\nfunction Sum(k:integer):integer;\nbegin if k=0 then Sum:=0 else Sum:=k+Sum(k-1); end;\nbegin Readln(n); Writeln(Sum(n)); end.\n",
            "def s(k): return 0 if k==0 else k+s(k-1)",
            "int s(int k){return k==0?0:k+s(k-1);}",
            ("recursion", "function_definition"),
            ({"inputs": "4\n", "output": "10"},),
        ),
        _cap(
            "Итог: gcd recursive",
            "Рекурсивный НОД",
            "recursion; function",
            "program Demo;\nvar a,b:integer;\nfunction Gcd(x,y:integer):integer;\nbegin if y=0 then Gcd:=x else Gcd:=Gcd(y, x mod y); end;\nbegin Readln(a); Readln(b); Writeln(Gcd(a,b)); end.\n",
            "def gcd(x,y): return x if y==0 else gcd(y,x%y)",
            "int gcd(int x,int y){return y==0?x:gcd(y,x%y);}",
            ("recursion", "function_definition", "arithmetic_ops"),
            ({"inputs": "12\n8\n", "output": "4"},),
        ),
        _cap(
            "Итог: базовый случай",
            "Добавить if k<=1 в Fact",
            "recursion",
            "program Demo;\nfunction Fact(k:integer):integer;\nbegin if k<=1 then Fact:=1 else Fact:=k*Fact(k-1); end;\nbegin Writeln(Fact(4)); end.\n",
            "add base case",
            "add base",
            ("recursion", "function_definition"),
            ({"inputs": "", "output": "24"},),
            task_format="исправление",
            starter="program Demo;\nfunction Fact(k:integer):integer;\nbegin Fact:=k*Fact(k-1); end;\nbegin Writeln(Fact(4)); end.\n",
        ),
    ),
    "oop": (
        _cap(
            "Итог: class с полем",
            "class/end и поле FValue",
            "class",
            "program Demo;\ntype\n  TBox = class\n    value: integer;\n  end;\nvar b: TBox;\nbegin b := TBox.Create; b.value := 5; Writeln(b.value); b.Free; end.\n",
            "class Box: value=0\nb=Box(); b.value=5; print(b.value)",
            "class Box{public:int value;}; int main(){Box* b=new Box(); b->value=5; cout<<b->value<<endl; delete b;return 0;}",
            ("class_type", "object_instance", "stdout_write"),
            ({"inputs": "", "output": "5"},),
        ),
        _cap(
            "Итог: constructor Create",
            "constructor Create и Create",
            "constructor; class",
            "program Demo;\ntype T=class constructor Create; end;\nconstructor T.Create; begin inherited Create; end;\nvar o:T;\nbegin o:=T.Create; Writeln('ok'); o.Free; end.\n",
            "class T: pass\no=T(); print('ok')",
            "class T{}; int main(){auto* o=new T(); cout<<\"ok\"; delete o;return 0;}",
            ("class_type", "method_dispatch"),
            ({"inputs": "", "output": "ok"},),
        ),
        _cap(
            "Итог: override метод",
            "virtual/override в class",
            "virtual; override; inherited",
            "program Demo;\ntype TBase=class virtual procedure P; end;\n     TChild=class(TBase) override procedure P; end;\nprocedure TBase.P; begin Write('A'); end;\nprocedure TChild.P; begin inherited; Write('B'); end;\nvar c:TChild;\nbegin c:=TChild.Create; c.P; Writeln; c.Free; end.\n",
            "override method",
            "virtual override",
            ("class_type", "inheritance_hierarchy", "method_dispatch"),
            ({"inputs": "", "output": "AB"},),
        ),
        _cap(
            "Итог: property",
            "property read/write",
            "property; class",
            "program Demo;\ntype T=class private F:integer; public property Val:integer read F write F; end;\nvar o:T;\nbegin o:=T.Create; o.Val:=3; Writeln(o.Val); o.Free; end.\n",
            "property getter setter",
            "property class",
            ("class_type", "method_dispatch"),
            ({"inputs": "", "output": "3"},),
        ),
    ),
    "error_handling": (
        _cap(
            "Итог: try/except",
            "Перехват деления на ноль",
            "try; except",
            _prog("  try Writeln(1 div 0); except on E: Exception do Writeln('err'); end;"),
            "try/except ZeroDivisionError",
            "try { cout<<1/0; } catch(...) { cout<<\"err\"; }",
            ("exceptions", "stdout_write"),
            ({"inputs": "", "output": "err"},),
        ),
        _cap(
            "Итог: try/finally",
            "Гарантированное завершение",
            "try; finally",
            _prog("  try Writeln('work'); finally Writeln('done'); end;"),
            "try/finally",
            "try { cout<<\"work\"; } finally { cout<<\"done\"; }",
            ("exceptions", "stdout_write"),
            ({"inputs": "", "output": "work\ndone"},),
        ),
        _cap(
            "Итог: raise",
            "Проброс исключения",
            "raise",
            _prog("  raise Exception.Create('fail');"),
            "raise RuntimeError('fail')",
            "throw runtime_error(\"fail\");",
            ("exceptions",),
            [],
        ),
        _cap(
            "Итог: файл и ошибка",
            "Обработка ошибки файла",
            "try; file",
            "program Demo;\nvar F: TextFile;\nbegin\n  try Assign(F,'missing.txt'); Reset(F); CloseFile(F); except on E: EInOutError do Writeln('no file'); end;\nend.\n",
            "try open missing file",
            "try { ifstream f(\"missing.txt\"); } catch(...) { cout<<\"no file\"; }",
            ("exceptions", "file_read"),
            ({"inputs": "", "output": "no file"},),
            task_format="исправление",
        ),
    ),
    "pascal_pitfalls": (
        _cap(
            "Итог: типичная программа без ; перед else",
            "Исправить if/else",
            "if; else",
            _prog("  n := 1;\n  if n > 0 then Writeln('yes') else Writeln('no');"),
            "if else fix",
            "int main(){int n=1; if(n>0) cout<<\"yes\"; else cout<<\"no\"; return 0;}",
            ("simple_branch", "stdout_write"),
            ({"inputs": "", "output": "yes"},),
            task_format="исправление",
            starter="program Demo;\nvar n: integer;\nbegin\n  n := 1;\n  if n > 0 then;\n    Writeln('yes')\n  else\n    Writeln('no');\nend.\n",
        ),
        _cap(
            "Итог: string 1-based",
            "Исправить индекс строки",
            "string",
            "program Demo;\nvar s:string;\nbegin s:='x'; Writeln(s[1]); end.\n",
            "s='x'; print(s[0])",
            "string s=\"x\"; cout<<s[0];",
            ("string_sequence",),
            ({"inputs": "", "output": "x"},),
            task_format="исправление",
            starter="program Demo;\nvar s:string;\nbegin s:='x'; Writeln(s[0]); end.\n",
        ),
        _cap(
            "Итог: for control variable",
            "Не менять i в теле for",
            "for to",
            _prog("  for n := 1 to 3 do Writeln(n);"),
            "for i in range(1,4): print(i)",
            "for(int i=1;i<=3;i++) cout<<i<<endl;",
            ("counted_loop", "stdout_write"),
            ({"inputs": "", "output": "1\n2\n3"},),
        ),
        _cap(
            "Итог: Result initialize",
            "Инициализировать Result",
            "result; function",
            "program Demo;\nfunction F:integer; begin Result:=0; Result:=Result+1; end;\nbegin Writeln(F); end.\n",
            "init result",
            "init result",
            ("return_flow", "function_definition"),
            ({"inputs": "", "output": "1"},),
            task_format="исправление",
            starter="program Demo;\nfunction F:integer; begin Result:=Result+1; end;\nbegin Writeln(F); end.\n",
        ),
    ),
    "compiler_diagnostics": (
        _cap(
            "Итог: undeclared identifier",
            "Объявить переменную перед использованием",
            "var",
            _prog("  n := 1; Writeln(n);"),
            "n=1; print(n)",
            "int n=1; cout<<n;",
            ("typed_declaration", "assignment", "stdout_write"),
            ({"inputs": "", "output": "1"},),
            task_format="исправление",
            starter="program Demo;\nbegin\n  n := 1;\n  Writeln(n);\nend.\n",
        ),
        _cap(
            "Итог: begin после then",
            "Добавить begin/end в ветку if",
            "begin; if",
            _prog("  if 1>0 then begin Writeln('ok'); end;"),
            "if with block",
            "if block",
            ("block_scope", "simple_branch", "stdout_write"),
            ({"inputs": "", "output": "ok"},),
            task_format="исправление",
            starter="program Demo;\nbegin\n  if 1>0 then\n    Writeln('ok');\nend.\n",
        ),
        _cap(
            "Итог: type mismatch",
            "Привести real к integer через trunc",
            "types; trunc",
            "program Demo;\nvar n:integer; r:real;\nbegin r:=3.7; n:=Trunc(r); Writeln(n); end.\n",
            "n=int(3.7); print(n)",
            "int n=(int)3.7; cout<<n;",
            ("typed_declaration", "assignment", "stdout_write"),
            ({"inputs": "", "output": "3"},),
            task_format="исправление",
            starter="program Demo;\nvar n:integer; r:real;\nbegin r:=3.7; n:=r; Writeln(n); end.\n",
        ),
        _cap(
            "Итог: semicolon между операторами",
            "Добавить ; между операторами",
            "semicolon",
            _prog("  n := 1; Writeln(n);"),
            "n=1; print(n)",
            "int n=1; cout<<n;",
            ("assignment", "stdout_write"),
            ({"inputs": "", "output": "1"},),
            task_format="исправление",
            starter="program Demo;\nvar n:integer;\nbegin\n  n := 1\n  Writeln(n);\nend.\n",
        ),
    ),
}
# fmt: on


def capstone_task_rows() -> list[tuple]:
    """Return full catalog rows: (slot_id, chapter, title, format, action, pattern, goal, features, difficulty, legacy)."""
    rows: list[tuple] = []
    for chapter, specs in _CAPSTONE_BY_CHAPTER.items():
        prefix = _CHAPTER_SLOT_PREFIX[chapter]
        for idx, spec in enumerate(specs, start=1):
            slot_id = f"{prefix}_cap{idx:02d}"
            pattern = f"cap_{chapter}_{idx:02d}"
            rows.append(
                (
                    slot_id,
                    chapter,
                    f"Итоговое: {spec.title}",
                    spec.task_format,
                    spec.action,
                    pattern,
                    spec.goal,
                    spec.features,
                    spec.difficulty,
                    "",
                )
            )
    return rows


def capstone_known_code() -> dict[str, tuple[str, str, str, str]]:
    out: dict[str, tuple[str, str, str, str]] = {}
    for chapter, specs in _CAPSTONE_BY_CHAPTER.items():
        prefix = _CHAPTER_SLOT_PREFIX[chapter]
        for idx, spec in enumerate(specs, start=1):
            slot_id = f"{prefix}_cap{idx:02d}"
            java = spec.cpp.replace("cout", "System.out.println").replace("cin", "Scanner")
            csharp = spec.cpp.replace("cout", "Console.WriteLine").replace("cin", "Console.ReadLine")
            out[slot_id] = (spec.python, spec.cpp, java, csharp)
    return out


def capstone_reference_pascal() -> dict[str, str]:
    out: dict[str, str] = {}
    for chapter, specs in _CAPSTONE_BY_CHAPTER.items():
        prefix = _CHAPTER_SLOT_PREFIX[chapter]
        for idx, spec in enumerate(specs, start=1):
            out[f"{prefix}_cap{idx:02d}"] = spec.pascal
    return out


def capstone_starter_pascal() -> dict[str, str]:
    out: dict[str, str] = {}
    for chapter, specs in _CAPSTONE_BY_CHAPTER.items():
        prefix = _CHAPTER_SLOT_PREFIX[chapter]
        for idx, spec in enumerate(specs, start=1):
            if spec.starter_pascal.strip():
                out[f"{prefix}_cap{idx:02d}"] = spec.starter_pascal
    return out


def capstone_expected_concepts() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for chapter, specs in _CAPSTONE_BY_CHAPTER.items():
        prefix = _CHAPTER_SLOT_PREFIX[chapter]
        for idx, spec in enumerate(specs, start=1):
            out[f"{prefix}_cap{idx:02d}"] = list(spec.expected_concept_ids)
    return out


def capstone_test_cases() -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = {}
    for chapter, specs in _CAPSTONE_BY_CHAPTER.items():
        prefix = _CHAPTER_SLOT_PREFIX[chapter]
        for idx, spec in enumerate(specs, start=1):
            out[f"{prefix}_cap{idx:02d}"] = [dict(item) for item in spec.test_cases]
    return out


def capstone_count() -> int:
    return sum(len(specs) for specs in _CAPSTONE_BY_CHAPTER.values())
