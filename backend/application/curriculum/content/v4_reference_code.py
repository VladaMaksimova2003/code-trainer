"""Reference code for v4 tasks — all 5 languages per task."""
from __future__ import annotations

_TASK_REFERENCE_CODE: dict[str, dict[str, str]] = {
    # Task 1: Поиск максимума в массиве
    "task_001": {
        "pascal": "var n, i, score, best: integer;\nbegin\n  readln(n);\n  readln(best);\n  for i := 2 to n do\nbegin\n  readln(score);\n  if score > best then best := score;\n  end;\n  writeln(best);\nend.",
        "python": "n = int(input())\nscores = [int(input()) for _ in range(n)]\nbest = scores[0]\nfor score in scores:\n    if score > best:\n        best = score\n        print(best)",
        "cpp": "#include <iostream>#include <vector>\nint main(){\nint n; std::cin >> n;\nstd::vector<int> scores(n);\nfor(int i = 0; i < n; i++) std::cin >> scores[i];\nint best = scores[0];\nfor(int score : scores){  if(score > best) best = score;}\nstd::cout << best;return 0;\n}",
        "csharp": "using System;\nclass Program{\nstatic void Main(){\nint n = int.Parse(Console.ReadLine());\nint[] scores = new int[n];\nfor(int i = 0; i < n; i++) scores[i] = int.Parse(Console.ReadLine());\nint best = scores[0];\nforeach(int score in scores){  if(score > best) best = score;}\nConsole.WriteLine(best);\n}}",
        "java": "import java.util.*;\nclass Main{\npublic static void main(String[] args){\nScanner sc = new Scanner(System.in);\nint n = sc.nextInt();int[] scores = new int[n];\nfor(int i = 0; i < n; i++) scores[i] = sc.nextInt();\nint best = scores[0];\nfor(int score : scores){  if(score > best) best = score;}\nSystem.out.println(best);\n}}",
    },
    # Task 2: Линейный поиск элемента
    "task_002": {
        "pascal": "var n, i, code, target, position: integer;\nbegin\n  readln(n, target);\n  position := 0;\n  for i := 1 to n do\nbegin\n  readln(code);\n  if (code = target) and (position = 0) then position := i;\n  end;\n  writeln(position);\nend.",
        "python": "n, target = map(int, input().split())position = 0\nfor i in range(1, n + 1):\n    code = int(input())\n    if code == target and position == 0:\n        position = i\n        print(position)",
        "cpp": "#include <iostream>\nint main()\n{\n    int n, target, code, position = 0;\n    std::cin >> n >> target;\n    for(int i = 1; i <= n; i++)\n    {\n        std::cin >> code;\n        if(code == target && position == 0) position = i;\n    }\n    std::cout << position;\n    return 0;\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        string[] first = Console.ReadLine().Split();\n        int n = int.Parse(first[0]), target = int.Parse(first[1]);\n        int position = 0;\n        for(int i = 1; i <= n; i++)\n        {\n            int code = int.Parse(Console.ReadLine());\n            if(code == target && position == 0) position = i;\n        }\n        Console.WriteLine(position);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt(), target = sc.nextInt();\n        int position = 0;\n        for(int i = 1; i <= n; i++)\n        {\n            int code = sc.nextInt();\n            if(code == target && position == 0) position = i;\n        }\n        System.out.println(position);\n    }\n}",
    },
    # Task 3: Поиск минимума
    "task_003": {
        "pascal": "var n, i, ping, best: integer;\nbegin\n  readln(n);\n  readln(best);\n  for i := 2 to n do\nbegin\n  readln(ping);\n  if ping < best then best := ping;\n  end;\n  writeln(best);\nend.",
        "python": "n = int(input())pings = [int(input()) for _ in range(n)]best = pings[0]\nfor ping in pings:\n    if ping < best:\n        best = ping\n        print(best)",
        "cpp": "#include <iostream>\n#include <vector>\nint main()\n{\n    int n;\n    std::cin >> n;\n    std::vector<int> pings(n);\n    for(int i = 0; i < n; i++) std::cin >> pings[i];\n    int best = pings[0];\n    for(int ping : pings)\n    {\n        if(ping < best) best = ping;\n    }\n    std::cout << best;\n    return 0;\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        int n = int.Parse(Console.ReadLine());\n        int[] pings = new int[n];\n        for(int i = 0; i < n; i++) pings[i] = int.Parse(Console.ReadLine());\n        int best = pings[0];\n        foreach(int ping in pings)\n        {\n            if(ping < best) best = ping;\n        }\n        Console.WriteLine(best);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] pings = new int[n];\n        for(int i = 0; i < n; i++) pings[i] = sc.nextInt();\n        int best = pings[0];\n        for(int ping : pings)\n        {\n            if(ping < best) best = ping;\n        }\n        System.out.println(best);\n    }\n}",
    },
    # Task 4: Подсчёт положительных чисел
    "task_004": {
        "pascal": "var n, i, amount, count: integer;\nbegin\n  readln(n);\n  count := 0;\n  for i := 1 to n do\nbegin\n  readln(amount);\n  if amount > 0 then count := count + 1;\n  end;\n  writeln(count);\nend.",
        "python": "n = int(input())count = 0\nfor _ in range(n):\n    amount = int(input())\n    if amount > 0:\n        count += 1\n        print(count)",
        "cpp": "#include <iostream>\nint main()\n{\n    int n, amount, count = 0;\n    std::cin >> n;\n    for(int i = 0; i < n; i++)\n    {\n        std::cin >> amount;\n        if(amount > 0) count++;\n    }\n    std::cout << count;\n    return 0;\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        int n = int.Parse(Console.ReadLine());\n        int count = 0;\n        for(int i = 0; i < n; i++)\n        {\n            int amount = int.Parse(Console.ReadLine());\n            if(amount > 0) count++;\n        }\n        Console.WriteLine(count);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int count = 0;\n        for(int i = 0; i < n; i++)\n        {\n            int amount = sc.nextInt();\n            if(amount > 0) count++;\n        }\n        System.out.println(count);\n    }\n}",
    },
    # Task 5: Сумма элементов массива
    "task_005": {
        "pascal": "var n, i, sale, total: integer;\nbegin\n  readln(n);\n  total := 0;\n  for i := 1 to n do\nbegin\n  readln(sale);\n  total := total + sale;\n  end;\n  writeln(total);\nend.",
        "python": "n = int(input())\nsales = [int(input()) for _ in range(n)]\n\ntotal = 0\n\nfor sale in sales:\n    total += sale\n\nprint(total)",
        "cpp": "#include <iostream>\n#include <vector>\nint main(){\n  int n; std::cin >> n;\n  std::vector<int> sales(n);\n  for(int i = 0; i < n; i++) std::cin >> sales[i];\n  int total = 0;\n  for(int sale : sales) total += sale;\n  std::cout << total;\n  return 0;\n}",
        "csharp": "using System;\nclass Program{\nstatic void Main(){\nint n = int.Parse(Console.ReadLine());\nint[] sales = new int[n];\nfor(int i = 0; i < n; i++) sales[i] = int.Parse(Console.ReadLine());\nint total = 0;\nforeach(int sale in sales) total += sale;\nConsole.WriteLine(total);\n}}",
        "java": "import java.util.*;\nclass Main{\npublic static void main(String[] args){\nScanner sc = new Scanner(System.in);\nint n = sc.nextInt();int[] sales = new int[n];\nfor(int i = 0; i < n; i++) sales[i] = sc.nextInt();\nint total = 0;\nfor(int sale : sales) total += sale;\nSystem.out.println(total);\n}}",
    },
    # Task 6: Среднее значение массива
    "task_006": {
        "pascal": "var n, i, load, total: integer;\nbegin\n  readln(n);\n  total := 0;\n  for i := 1 to n do\nbegin\n  readln(load);\n  total := total + load;\n  end;\n  writeln(total div n);\nend.",
        "python": "n = int(input())\nloads = [int(input()) for _ in range(n)]\n\ntotal = 0\n\nfor load in loads:\n    total += load\n\nprint(total // n)",
        "cpp": "#include <iostream>\n#include <vector>\nint main(){\n  int n; std::cin >> n;\n  std::vector<int> loads(n);\n  for(int i = 0; i < n; i++) std::cin >> loads[i];\n  int total = 0;\n  for(int load : loads) total += load;\n  std::cout << total / n;\n  return 0;\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        int n = int.Parse(Console.ReadLine());\n        int[] loads = new int[n];\n        for(int i = 0; i < n; i++) loads[i] = int.Parse(Console.ReadLine());\n        int total = 0;\n        foreach(int load in loads) total += load;\n        Console.WriteLine(total / n);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] loads = new int[n];\n        for(int i = 0; i < n; i++) loads[i] = sc.nextInt();\n        int total = 0;\n        for(int load : loads) total += load;\n        System.out.println(total / n);\n    }\n}",
    },
    # Task 7: Ввод массива и вывод результата
    "task_007": {
        "pascal": "var n, i, x, count: integer;\nbegin\n  readln(n);\n  count := 0;\n  for i := 1 to n do\nbegin\n  readln(x);\n  if x >= 50 then count := count + 1;\n  end;\n  writeln(count);\nend.",
        "python": "n = int(input())\n\ncount = 0\n\nfor _ in range(n):\n    x = int(input())\n    if x >= 50:\n        count += 1\n\nprint(count)",
        "cpp": "#include <iostream>\nint main(){\n  int n, x, count = 0;\n  std::cin >> n;\n  for(int i = 0; i < n; i++){\n    std::cin >> x;\n    if(x >= 50) count++;\n  }\n  std::cout << count;\n  return 0;\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        int n = int.Parse(Console.ReadLine());\n        int count = 0;\n        for(int i = 0; i < n; i++)\n        {\n            int x = int.Parse(Console.ReadLine());\n            if(x >= 50) count++;\n        }\n        Console.WriteLine(count);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int count = 0;\n        for(int i = 0; i < n; i++)\n        {\n            int x = sc.nextInt();\n            if(x >= 50) count++;\n        }\n        System.out.println(count);\n    }\n}",
    },
    # Task 8: Итоговая: анализ оценок студентов
    "task_008": {
        "pascal": "var n, i, grade, best, total, passed: integer;\nbegin\n  readln(n);\n  total := 0;\n  passed := 0;\n  readln(best);\n  total := total + best;\n  if best >= 3 then passed := passed + 1;\n  for i := 2 to n do\nbegin\n  readln(grade);\n  total := total + grade;\n  if grade > best then best := grade;\n  if grade >= 3 then passed := passed + 1;\n  end;\n  writeln(best, ' ', total div n, ' ', passed);\nend.",
        "python": "n = int(input())grades = [int(input()) for _ in range(n)]best = grades[0]\ntotal = 0\npassed = 0\nfor grade in grades:\n    total += grade\n    if grade > best:\n        best = grade\n        if grade >= 3:\n            passed += 1\n            print(best, total // n, passed)",
        "cpp": "#include <iostream>\n#include <vector>\nint main()\n{\n    int n;\n    std::cin >> n;\n    std::vector<int> grades(n);\n    for(int i = 0; i < n; i++) std::cin >> grades[i];\n    int best = grades[0], total = 0, passed = 0;\n    for(int grade : grades)\n    {\n        total += grade;\n        if(grade > best) best = grade;\n        if(grade >= 3) passed++;\n    }\n    std::cout << best << ' ' << total / n << ' ' << passed;\n    return 0;\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        int n = int.Parse(Console.ReadLine());\n        int[] grades = new int[n];\n        for(int i = 0; i < n; i++) grades[i] = int.Parse(Console.ReadLine());\n        int best = grades[0], total = 0, passed = 0;\n        foreach(int grade in grades)\n        {\n            total += grade;\n            if(grade > best) best = grade;\n            if(grade >= 3) passed++;\n        }\n        Console.WriteLine($\"{best} {total / n} {passed}\");\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        int[] grades = new int[n];\n        for(int i = 0; i < n; i++) grades[i] = sc.nextInt();\n        int best = grades[0], total = 0, passed = 0;\n        for(int grade : grades)\n        {\n            total += grade;\n            if(grade > best) best = grade;\n            if(grade >= 3) passed++;\n        }\n        System.out.println(best + \" \" + (total / n) + \" \" + passed);\n    }\n}",
    },
    # Task 9: Максимум из трёх чисел
    "task_009": {
        "pascal": "var a,b,c,m: integer;\nbegin\n  readln(a,b,c);\n  m := a;\n  if b > m then m := b;\n  if c > m then m := c;\n  writeln(m);\nend.",
        "python": "a, b, c = map(int, input().split())\nm = a\nif b > m:\n    m = b\n    if c > m:\n        m = c\n        print(m)",
        "cpp": "#include <iostream>\nint main(){\nint a,b,c,m; std::cin >> a >> b >> c;\nm = a;\nif(b > m) m = b;\nif(c > m) m = c;\nstd::cout << m;\n}",
        "csharp": "using System;\nclass Program{static void Main(){\nvar p=Console.ReadLine().Split();\nint a=int.Parse(p[0]), b=int.Parse(p[1]), c=int.Parse(p[2]);\nint m=a;\nif(b>m) m=b;\nif(c>m) m=c;\nConsole.WriteLine(m);\n}}",
        "java": "import java.util.*;\nclass Main{public static void main(String[] args){\nScanner sc=new Scanner(System.in);\nint a=sc.nextInt(), b=sc.nextInt(), c=sc.nextInt();\nint m=a;\nif(b>m) m=b;\nif(c>m) m=c;\nSystem.out.println(m);\n}}",
    },
    # Task 10: Классификация температуры
    "task_010": {
        "pascal": "var t: integer;\nbegin\n  readln(t);\n  if t < 0 then\n  writeln('freezing')\nelse if t <= 25 then\n  writeln('normal')\n  else\n  writeln('hot');\nend.",
        "python": "t = int(input())\nif t <= 25:\n    print('freezing')el\n    if t <= 25:\n        print('normal')\n    else:\n        print('hot')",
        "cpp": "#include <iostream>\nint main()\n{\n    int t;\n    std::cin >> t;\n    if(t<0) std::cout<<\"freezing\";\n    else if(t<=25) std::cout<<\"normal\";\n    else std::cout<<\"hot\";\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        int t=int.Parse(Console.ReadLine());\n        if(t<0) Console.WriteLine(\"freezing\");\n        else if(t<=25) Console.WriteLine(\"normal\");\n        else Console.WriteLine(\"hot\");\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int t=sc.nextInt();\n        if(t<0) System.out.println(\"freezing\");\n        else if(t<=25) System.out.println(\"normal\");\n        else System.out.println(\"hot\");\n    }\n}",
    },
    # Task 11: Тип треугольника
    "task_011": {
        "pascal": "var a,b,c: integer;\nbegin\n  readln(a,b,c);\n  if (a = b) and (b = c) then\n  writeln('equilateral')\nelse if (a = b) or (a = c) or (b = c) then\n  writeln('isosceles')\n  else\n  writeln('scalene');\nend.",
        "python": "a, b, c = map(int, input().split())\nif a == b == c:\n    print('equilateral')el\n    if a == b or a == c or b == c:\n        print('isosceles')\n    else:\n        print('scalene')",
        "cpp": "#include <iostream>\nint main()\n{\n    int a,b,c;\n    std::cin>>a>>b>>c;\n    if(a==b && b==c) std::cout<<\"equilateral\";\n    else if(a==b || a==c || b==c) std::cout<<\"isosceles\";\n    else std::cout<<\"scalene\";\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        var p=Console.ReadLine().Split();\n        int a=int.Parse(p[0]), b=int.Parse(p[1]), c=int.Parse(p[2]);\n        if(a==b && b==c) Console.WriteLine(\"equilateral\");\n        else if(a==b || a==c || b==c) Console.WriteLine(\"isosceles\");\n        else Console.WriteLine(\"scalene\");\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int a=sc.nextInt(), b=sc.nextInt(), c=sc.nextInt();\n        if(a==b && b==c) System.out.println(\"equilateral\");\n        else if(a==b || a==c || b==c) System.out.println(\"isosceles\");\n        else System.out.println(\"scalene\");\n    }\n}",
    },
    # Task 12: Проверка корректности даты
    "task_012": {
        "pascal": "var d,m: integer;\nbegin\n  readln(d,m);\n  if (m >= 1) and (m <= 12) and (d >= 1) and (d <= 31) then\n  writeln('valid')\n  else\n  writeln('invalid');\nend.",
        "python": "d, m = map(int, input().split())\nif 1 <= m <= 12 and 1 <= d <= 31:\n    print('valid')\nelse:\n    print('invalid')",
        "cpp": "#include <iostream>\nint main()\n{\n    int d,m;\n    std::cin>>d>>m;\n    if(m>=1 && m<=12 && d>=1 && d<=31) std::cout<<\"valid\";\n    else std::cout<<\"invalid\";\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        var p=Console.ReadLine().Split();\n        int d=int.Parse(p[0]), m=int.Parse(p[1]);\n        if(m>=1 && m<=12 && d>=1 && d<=31) Console.WriteLine(\"valid\");\n        else Console.WriteLine(\"invalid\");\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int d=sc.nextInt(), m=sc.nextInt();\n        if(m>=1 && m<=12 && d>=1 && d<=31) System.out.println(\"valid\");\n        else System.out.println(\"invalid\");\n    }\n}",
    },
    # Task 13: Оценка по баллам
    "task_013": {
        "pascal": "var score: integer;\nbegin\n  readln(score);\n  if score >= 90 then\n  writeln('excellent')\nelse if score >= 70 then\n  writeln('good')\n  else\n  writeln('retry');\nend.",
        "python": "score = int(input())\nif score >= 90:\n    print('excellent')\n    el\n    if score >= 70:\n        print('good')\n    else:\n        print('retry')",
        "cpp": "#include <iostream>\nint main(){\nint score; std::cin >> score;\nif(score>=90) std::cout<<\"excellent\"; else if(score>=70) std::cout<<\"g\nood\"; else std::cout<<\"retry\";\n}",
        "csharp": "using System;\nclass Program{static void Main(){\nint score=int.Parse(Console.ReadLine());\nif(score>=90) Console.WriteLine(\"excellent\"); else if(score>=70) Conso\nle.WriteLine(\"good\"); else Console.WriteLine(\"retry\");\n}}",
        "java": "import java.util.*;\nclass Main{public static void main(String[] args){\nScanner sc=new Scanner(System.in);\nint score=sc.nextInt();\nif(score>=90) System.out.println(\"excellent\"); else if(score>=70) Syst\nem.out.println(\"good\"); else System.out.println(\"retry\");\n}}",
    },
    # Task 14: Определение сезона
    "task_014": {
        "pascal": "var m: integer;\nbegin\n  readln(m);\n  case m of 12,1,2:\n  writeln('winter');\n  3,4,5:\n  writeln('spring');\n  6,7,8:\n  writeln('summer');\n  9,10,11:\n  writeln('autumn');\n  else\n  writeln('invalid');\n  end;\nend.",
        "python": "m = int(input())\nif условие:\n    print('winter')el\n    if m in (3, 4, 5):\n        print('spring')el\n        if m in (6, 7, 8):\n            print('summer')el\n            if m in (9, 10, 11):\n                print('autumn')\n            else:\n                print('invalid')",
        "cpp": "#include <iostream>\nint main()\n{\n    int m;\n    std::cin>>m;\n    switch(m)\n    {\n        case 12: case 1: case 2: std::cout<<\"winter\";\n        break;\n        case 3: case 4: case 5: std::cout<<\"spring\";\n        break;\n        case 6: case 7: case 8: std::cout<<\"summer\";\n        break;\n        case 9: case 10: case 11: std::cout<<\"autumn\";\n        break;\n        default: std::cout<<\"invalid\";\n    }\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        int m=int.Parse(Console.ReadLine());\n        switch(m)\n        {\n            case 12: case 1: case 2: Console.WriteLine(\"winter\");\n            break;\n            case 3: case 4: case 5: Console.WriteLine(\"spring\");\n            break;\n            case 6: case 7: case 8: Console.WriteLine(\"summer\");\n            break;\n            case 9: case 10: case 11: Console.WriteLine(\"autumn\");\n            break;\n            default: Console.WriteLine(\"invalid\");\n            break;\n        }\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int m=sc.nextInt();\n        switch(m)\n        {\n            case 12: case 1: case 2: System.out.println(\"winter\");\n            break;\n            case 3: case 4: case 5: System.out.println(\"spring\");\n            break;\n            case 6: case 7: case 8: System.out.println(\"summer\");\n            break;\n            case 9: case 10: case 11: System.out.println(\"autumn\");\n            break;\n            default: System.out.println(\"invalid\");\n        }\n    }\n}",
    },
    # Task 15: Система скидок
    "task_015": {
        "pascal": "var total: integer;\nbegin\n  readln(total);\n  if total >= 10000 then\n  writeln(20)\nelse if total >= 5000 then\n  writeln(10)\n  else\n  writeln(0);\nend.",
        "python": "total = int(input())\nif total >= 10000:\n    print(20)el\n    if total >= 5000:\n        print(10)\n    else:\n        print(0)",
        "cpp": "#include <iostream>\nint main()\n{\n    int total;\n    std::cin >> total;\n    if(total>=10000) std::cout<<20;\n    else if(total>=5000) std::cout<<10;\n    else std::cout<<0;\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        int total=int.Parse(Console.ReadLine());\n        if(total>=10000) Console.WriteLine(20);\n        else if(total>=5000) Console.WriteLine(10);\n        else Console.WriteLine(0);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int total=sc.nextInt();\n        if(total>=10000) System.out.println(20);\n        else if(total>=5000) System.out.println(10);\n        else System.out.println(0);\n    }\n}",
    },
    # Task 16: Итоговая: валидация заявки
    "task_016": {
        "pascal": "var score: integer;\nbegin\n  readln(score);\n  if age >= 18 then\n  writeln('accepted')\n  else\n  writeln('rejected');\nend.",
        "python": "score = int(input())\nif age >= 18:\n    print('accepted')\nelse:\n    print('rejected')",
        "cpp": "#include <iostream>\nint main()\n{\n    int score;\n    std::cin >> score;\n    if(score>=90) std::cout<<\"excellent\";\n    else if(score>=70) std::cout<<\"good\";\n    else std::cout<<\"retry\";\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        int score=int.Parse(Console.ReadLine());\n        if(score>=90) Console.WriteLine(\"excellent\");\n        else if(score>=70) Console.WriteLine(\"good\");\n        else Console.WriteLine(\"retry\");\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int score=sc.nextInt();\n        if(score>=90) System.out.println(\"excellent\");\n        else if(score>=70) System.out.println(\"good\");\n        else System.out.println(\"retry\");\n    }\n}",
    },
    # Task 17: Сумма чисел до стоп-значения
    "task_017": {
        "pascal": "var x,total:integer;\nbegin\n  total:=0;\n  readln(x);\n  while x<>0 do\nbegin\n  to tal:=total+x;\n  readln(x);\n  end;\n  writeln(total);\nend.",
        "python": "total = 0\nx = int(input())\nwhile x != 0:\n    total += x x = int(input())\n    print(total)",
        "cpp": "#include <iostream>\nint main()\n{\n    int x,total=0;\n    std::cin>>x;\n    while(x!=0)\n    {\n        total+=x;\n        std::cin> >x;\n    }\n    std::cout<<total;\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        int total=0;\n        int x=int.Parse(Console. ReadLine());\n        while(x!=0)\n        {\n            total+=x;\n            x=int.Parse(Console.ReadLine());\n        }\n        Console.WriteLine(total);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scann er(System.in);\n        int total=0,x=sc.nextInt();\n        while(x!=0)\n        {\n            total+=x;\n            x=sc.nextInt();\n        }\n        System.out.println(total);\n    }\n}",
    },
    # Task 18: Поиск первого совпадения
    "task_018": {
        "pascal": "var i,n,total: integer;\n  a: array[1..100] of integer;\nbegin\n  readln(n);\n  total:=0;\n  for i:=1 to n do\nbegin\n  readln(a[i]);\n  total:=total+a[i];\n  end;\n  writeln(total);\nend.",
        "python": "a = list(map(int, input().split()))\nprint(sum(a))",
        "cpp": "#include <iostream>\n#include <vector>\nint main()\n{\n    int n;\n    std::cin>>n;\n    std::vector<int>a(n);\n    for(int i=0;i<n;i++) std::cin>>a[i];\n    int total=0;\n    for(int x:a) total+=x;\n    std::cout<<total;\n}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine());\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=int.Parse(Console.ReadLine());\n        int total=0;\n        foreach(int x in a) total+=x;\n        Console.Write(total;\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt();\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n        /* Поиск первого совпадения */ for(int x:a) System.out.print(x+\" \" );\n    }\n}",
    },
    # Task 19: Проверка простого числа
    "task_019": {
        "pascal": "var n,i:integer;\n  prime:boolean;\nbegin\n  readln(n);\n  prime:=n>1;\n  i:=2;\n  while i*i<=n do\nbegin\n  if n mod i=0 then prime:=false;\n  i:=i+1;\n  end;\n  if prime then\n  writeln('prime')\n  else\n  writeln('composite');\nend.",
        "python": "n = int(input())prime = n > 1\ni = 2\nwhile i * i <= n:\n    if n % i == 0:\n        prime = False i += 1\n        print('prime'\n        if prime\n        else 'composite')",
        "cpp": "#include <iostream>\nint main()\n{\n    int n;\n    std::cin>>n;\n    bool prime=n>1;\n    for(int i=2;i*i<=n;i++) if(n%i==0) prime=false;\n    std::cout<<(prime?\"prime\":\"composite\");\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine());\n        bool prime=n>1;\n        for(int i=2;i*i<=n;i++) if(n%i==0) prime=false;\n        Console.WriteLine(prime?\"prime\":\"composite\");\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt();\n        boolean prime=n>1;\n        for(int i=2;i*i<=n;i++) if(n%i==0) prime=false;\n        System.out.println(prime?\"prime\":\"composite\");\n    }\n}",
    },
    # Task 20: Пропуск отрицательных значений
    "task_020": {
        "pascal": "var n,i,x,total:integer;\nbegin\n  readln(n);\n  total:=0;\n  for i:=1 to n do\nbegin\n  readln(x);\n  if x>=0 then total:=total+x;\n  end;\n  writeln(total);\nend.",
        "python": "n = int(input())total = 0\nfor _ in range(n):\n    x = int(input())\n    if x >= 0:\n        total += x\n        print(total)",
        "cpp": "#include <iostream>\nint main()\n{\n    int n,x,total=0;\n    std::cin>>n;\n    for(int i=0;i<n;i++)\n    {\n        std::cin>>x;\n        if(x>=0) total+=x;\n    }\n    std::cout<<total;\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine()), total=0;\n        for(int i=0;i<n;i++)\n        {\n            int x=int.Parse(Console.ReadLine());\n            if(x>=0) total+=x;\n        }\n        Console.WriteLine(total);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt(), total=0;\n        for(int i=0;i<n;i++)\n        {\n            int x=sc.nextInt();\n            if(x>=0) total+=x;\n        }\n        System.out.println(total);\n    }\n}",
    },
    # Task 21: Таблица умножения
    "task_021": {
        "pascal": "var n,i:integer;\nbegin\n  readln(n);\n  for i:=1 to 10 do\n  writeln(n*i);\nend.",
        "python": "n = int(input())\nfor i in range(1, 11):\n    print(n * i)",
        "cpp": "#include <iostream>\nint main()\n{\n    int n;\n    std::cin>>n;\n    for(int i=1;i<=10;i++) std::cout<<n*i<<' ';\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine());\n        for(int i=1;i<=10;i++) Console.Write(n*i+\" \" );\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scann er(System.in);\n        int n=sc.nextInt();\n        for(int i=1;i<=10;i++) System.out.print(n*i+\" \" );\n    }\n}",
    },
    # Task 22: Поиск последнего совпадения
    "task_022": {
        "pascal": "var i,n,total: integer;\n  a: array[1..100] of integer;\nbegin\n  readln(n);\n  total:=0;\n  for i:=1 to n do\nbegin\n  readln(a[i]);\n  total:=total+a[i];\n  end;\n  writeln(total);\nend.",
        "python": "a = list(map(int, input().split()))\nprint(sum(a))",
        "cpp": "#include <iostream>\n#include <vector>\nint main()\n{\n    int n;\n    std::cin>>n;\n    std::vector<int>a(n);\n    for(int i=0;i<n;i++) std::cin>>a[i];\n    int total=0;\n    for(int x:a) total+=x;\n    std::cout<<total;\n}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine());\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=int.Parse(Console.ReadLine());\n        int total=0;\n        foreach(int x in a) total+=x;\n        Console.Write(total;\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt();\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n        /* Поиск последнего совпадения */ for(int x:a) System.out.print(x+\" \" );\n    }\n}",
    },
    # Task 23: Гистограмма частот
    "task_023": {
        "pascal": "var n,i,x,total:integer;\nbegin\n  readln(n);\n  total:=0;\n  for i:=1 to n do\nbegin\n  readln(x);\n  if x>=0 then total:=total+x;\n  end;\n  writeln(total);\nend.",
        "python": "n = int(input())total = 0\nfor _ in range(n):\n    x = int(input())\n    if x >= 0:\n        total += x\n        print(total)",
        "cpp": "#include <iostream>\nint main()\n{\n    int n,x,total=0;\n    std::cin>>n;\n    for(int i=0;i<n;i++)\n    {\n        std::cin>>x;\n        if(x>=0) total+=x;\n    }\n    std::cout<<total;\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine()), total=0;\n        for(int i=0;i<n;i++)\n        {\n            int x=int.Parse(Console.ReadLine());\n            if(x>=0) total+=x;\n        }\n        Console.WriteLine(total);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt(), total=0;\n        for(int i=0;i<n;i++)\n        {\n            int x=sc.nextInt();\n            if(x>=0) total+=x;\n        }\n        System.out.println(total);\n    }\n}",
    },
    # Task 24: Итоговая: статистика последовательности
    "task_024": {
        "pascal": "var i,n,x,total:integer;\nbegin\n  readln(n);\n  total:=0;\n  for i:=1 to n do\nbegin\n  readln(x);\n  total:=total+x;\n  end;\n  writeln(total);\nend.",
        "python": "n = int(input())total = 0\nfor _ in range(n):\n    total += int(input())\n    print(total)",
        "cpp": "#include <iostream>\nint main()\n{\n    int n,x,total=0;\n    std::cin>>n;\n    for(int i=0;i<n;i++)\n    {\n        std::cin>>x;\n        total+=x;\n    }\n    std::cout<<total;\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine()), total=0;\n        for(int i=0;i<n;i++) total+=int.Parse(Console.ReadLine());\n        Console.WriteLine(total);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt(), total=0;\n        for(int i=0;i<n;i++) total+=sc.nextInt();\n        System.out.println(total);\n    }\n}",
    },
    # Task 25: Разворот массива
    "task_025": {
        "pascal": "var i,n: integer;\n  a: array[1..100] of integer;\nbegin\n  readln(n);\n  for i:=1 to n do\n  readln(a[i]);\n  for i:=n downto 1 do w rite(a[i], ' ');\nend.",
        "python": "a = list(map(int, input().split()))\nfor x in reversed(a):\n    print(x, end=' ')",
        "cpp": "#include <iostream>\n#include <vector>\nint main(){int n; std::cin>>n; std::vector<int>a(n); for(int i=0;i<n;i\n++) std::cin>>a[i]; for(int i=n-1;i>=0;i--) std::cout<<a[i]<<\" \";}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine());\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=int.Parse(Console.ReadLine());\n        for(int i=n-1;i>=0;i--) Console.Write(a[i]<<\" \");\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scann er(System.in);\n        int n=sc.nextInt();\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n        /* Разворот массива */ for(int x:a) System.out.print(x+\" \" );\n    }\n}",
    },
    # Task 26: Циклический сдвиг
    "task_026": {
        "pascal": "var i,n,last: integer;\n  a: array[1..100] of integer;\nbegin\n  readln(n);\n  for i:=1 to n do\n  readln(a[i]);\n  last:=a[n];\n  for i:=n downto 2 do a[i]:=a[i-1];\n  a[1]:=last;\n  for i:=1 to n do\n  write(a[i],' ');\nend.",
        "python": "a = list(map(int, input().split()))last = a[-1]\nfor i in range(len(a)-1, 0, -1):\n    a[i] = a[i-1]\n    a[0] = last\n    print(*a)",
        "cpp": "#include <iostream>\n#include <vector>\nint main()\n{\n    int n;\n    std::cin>>n;\n    std::vector<int>a(n);\n    for(int i=0;i<n;i++) std::cin>>a[i];\n    int last=a[n-1];\n    for(int i=n-1;i>0;i--) a[i]=a[i-1];\n    a[0]=last;\n    for(int x:a) std::cout<<x<<\" \";\n}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine());\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=int.Parse(Console.ReadLine());\n        int last=a[n-1];\n        for(int i=n-1;i>0;i--) a[i]=a[i-1];\n        a[0]=last;\n        foreach(int x in a) Console.Write(x<<\" \");\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt();\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n        /* Циклический сдвиг */ for(int x:a) System.out.print(x+\" \" );\n    }\n}",
    },
    # Task 27: Удаление элемента
    "task_027": {
        "pascal": "var i,n,pos: integer;\n  a: array[1..100] of integer;\nbegin\n  readln(n);\n  for i:=1 to n do\n  readln(a[i]);\n  readln(pos);\n  for i:=pos to n-1 do a[i]:=a[i+1];\n  for i:=1 to n-1 do\n  write(a[i],' ');\nend.",
        "python": "a = list(map(int, input().split()))pos = int(input())del a[pos]\nprint(*a)",
        "cpp": "#include <iostream>\n#include <vector>\nint main()\n{\n    int n;\n    std::cin>>n;\n    std::vector<int>a(n);\n    for(int i=0;i<n;i++) std::cin>>a[i];\n    int pos;\n    std::cin>>pos;\n    for(int i=pos;i<n-1;i++) a[i]=a[i+1];\n    for(int i=0;i<n-1;i++) std::cout<<a[i]<<\" \";\n}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine());\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=int.Parse(Console.ReadLine());\n        int pos;\n        std::cin>>pos;\n        for(int i=pos;i<n-1;i++) a[i]=a[i+1];\n        for(int i=0;i<n-1;i++) Console.Write(a[i]<<\" \");\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt();\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n        /* Удаление элемента */ for(int x:a) System.out.print(x+\" \" );\n    }\n}",
    },
    # Task 28: Вставка элемента
    "task_028": {
        "pascal": "var i,n,pos,value: integer;\n  a: array[1..101] of integer;\nbegin\n  readln(n);\n  for i:=1 to n do\n  readln(a[i]);\n  readln(pos,value);\n  for i:=n downto pos do a[i+1]:=a[i];\n  a[pos]:=value;\n  for i:=1 to n+1 do\n  write(a[i],' ');\nend.",
        "python": "a = list(map(int, input().split()))pos, value = map(int, input().split())a.insert(pos, value)\nprint(*a)",
        "cpp": "#include <iostream>\n#include <vector>\nint main()\n{\n    int n;\n    std::cin>>n;\n    std::vector<int>a(n);\n    for(int i=0;i<n;i++) std::cin>>a[i];\n    int pos,value;\n    std::cin>>pos>>value;\n    a.insert(a.begin()+pos,value);\n    for(int x:a) std::cout<<x<<\" \";\n}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine());\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=int.Parse(Console.ReadLine());\n        int pos,value;\n        std::cin>>pos>>value;\n        a.insert(a.begin()+pos,value);\n        foreach(int x in a) Console.Write(x<<\" \");\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt();\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n        /* Вставка элемента */ for(int x:a) System.out.print(x+\" \" );\n    }\n}",
    },
    # Task 29: Объединение двух массивов
    "task_029": {
        "pascal": "var i,n,m: integer;\n  a,b: array[1..100] of integer;\nbegin\n  readln(n);\n  for i:=1 to n do\n  readln(a[i]);\n  readln(m);\n  for i:=1 to m do\n  readln(b[i]);\n  for i:=1 to n do\n  write(a[i],' ');\n  for i:=1 to m do\n  write(b[i],' ');\nend.",
        "python": "a = list(map(int, input().split()))\nb = list(map(int, input().split()))\nprint(*(a + b))",
        "cpp": "#include <iostream>\n#include <vector>\nint main(){int n; std::cin>>n; std::vector<int>a(n); for(int i=0;i<n;i\n++) std::cin>>a[i]; int m; std::cin>>m; std::vector<int>b(m); for(int i=0;i<m;i++) std::cin>>b[i]; for(int x:a) std::cout<<x<<\" \"; for(int x:b) std::cout<<x<<\" \";}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine());\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=int.Parse(Console.ReadLine());\n        int m;\n        std::cin>>m;\n        std::vector<int>b(m);\n        for(int i=0;i<m;i++) std::cin>>b[i];\n        foreach(int x in a) Console.Write(x<<\" \");\n        for(int x:b) Console.Write(x<<\" \");\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scann er(System.in);\n        int n=sc.nextInt();\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n        /* Объединение двух массивов */ for(int x:a) System.out.print(x+\" \" );\n    }\n}",
    },
    # Task 30: Поиск дубликатов
    "task_030": {
        "pascal": "var i,j,n: integer;\n  a: array[1..100] of integer;\n  found:boolean;\nbegin\n  readln(n);\n  for i:=1 to n do\n  readln(a[i]);\n  found:=false;\n  for i:=1 to n do\n  for j:=i+1 to n do\n    if found then\n  writeln('yes'):=true;\n  if found then\n  writeln('yes')\n  else\n  writeln('no');\nend.",
        "python": "a = list(map(int, input().split()))seen = False\nfor i in range(len(a)):\n    for j in range(i + 1, len(a)):\n        if\n        for i in range(len(a)):\n            : seen = True\n            print('yes'\n            if seen\n            else 'no')",
        "cpp": "#include <iostream>\n#include <vector>\nint main()\n{\n    int n;\n    std::cin>>n;\n    std::vector<int>a(n);\n    for(int i=0;i<n;i++) std::cin>>a[i];\n    bool found=false;\n    for(int i=0;i<n;i++) for(int j=i+1;j<n;j++) if(a[i]==a[j]) found=true;\n    std::cout<<(found?\"yes\":\"no\");\n}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine());\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=int.Parse(Console.ReadLine());\n        bool found=false;\n        for(int i=0;i<n;i++) for(int j=i+1;j<n;j++) if(a[i]==a[j]) found=true;\n        Console.Write((found?\"yes\":\"no\");\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt();\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n        /* Поиск дубликатов */ for(int x:a) System.out.print(x+\" \" );\n    }\n}",
    },
    # Task 31: Максимум в матрице
    "task_031": {
        "pascal": "var i,j,n,m,best,x: integer;\nbegin\n  readln(n,m);\n  readln(best);\n  for i:=1 to n do\n  for j:=1 to m do\nbegin\n  if not ((i=1) and (j=1)) then\n  readln(x)\nelse x:=best;\n  if x > best then best := x;\n  end;\n  writeln(best);\nend.",
        "python": "n, m = map(int, input().split())best = None\nfor _ in range(n):\n    row = list(map(int, input().split()))\n    for x in row:\n        if best is None or x > best:\n            best = x\n            print(best)",
        "cpp": "#include <iostream>\nint main()\n{\n    int n,m,x,best;\n    std::cin>>n>>m>>best;\n    for(int i=0;i<n;i++) for(int j=0;j<m;j++)\n    {\n        if(i!=0 || j!=0) std::cin>>x;\n        else x=best;\n        if(x>best) best=x;\n    }\n    std::cout<<best;\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        var nm=Console.ReadLine().Split();\n        int n=int.Parse(nm[0]), m=int.Parse(nm[1]);\n        int best=int.Parse(Console.ReadLine());\n        for(int i=0;i<n;i++) for(int j=0;j<m;j++)\n        {\n            int x=(i==0&&j==0)?best:int.Parse(Console.ReadLine());\n            if(x>best) best=x;\n        }\n        Console.WriteLine(best);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt(),m=sc.nextInt(),best=sc.nextInt();\n        for(int i=0;i<n;i++) for(int j=0;j<m;j++)\n        {\n            int x=(i==0&&j==0)?best:sc.nextInt();\n            if(x>best) best=x;\n        }\n        System.out.println(best);\n    }\n}",
    },
    # Task 32: Итоговая: анализ игровой карты
    "task_032": {
        "pascal": "var i,n,total: integer;\n  a: array[1..100] of integer;\nbegin\n  readln(n);\n  total:=0;\n  for i:=1 to n do\nbegin\n  readln(a[i]);\n  total:=total+a[i];\n  end;\n  writeln(total);\nend.",
        "python": "a = list(map(int, input().split()))\nprint(sum(a))",
        "cpp": "#include <iostream>\n#include <vector>\nint main()\n{\n    int n;\n    std::cin>>n;\n    std::vector<int>a(n);\n    for(int i=0;i<n;i++) std::cin>>a[i];\n    int total=0;\n    for(int x:a) total+=x;\n    std::cout<<total;\n}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine());\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=int.Parse(Console.ReadLine());\n        int total=0;\n        foreach(int x in a) total+=x;\n        Console.Write(total;\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt();\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n        /* Итоговая: анализ игровой карты */ for(int x:a) System.out.print(x+\" \" );\n    }\n}",
    },
    # Task 33: Подсчёт символов
    "task_033": {
        "pascal": "var s:string;\n  ch:char;\n  i,count:integer;\nbegin\n  readln(s);\n  readln(ch);\n  c ount:=0;\n  for i:=1 to length(s) do\n    if s[i]=ch then count:=count+1;\n  writeln(count);\nend.",
        "python": "s =\ninput()\nch =\ninput()\ncount = 0\nfor c in s:\n    if c == ch:\n        count += 1\n        print(count)",
        "cpp": "#include <iostream>\n#include <string>\n#include <algorithm>\nint main(){std::string s; std::getline(std::cin,s); std::reverse(s.beg\nin(),s.end()); std::cout<<s;}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        string s=Console.ReadLine();\n        Console. WriteLine(new string(s.Reverse().ToArray()));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scann er(System.in);\n        String s=sc.nextLine();\n        System.out.println(new StringBuilder(s).reverse().toString());\n    }\n}",
    },
    # Task 34: Разворот строки
    "task_034": {
        "pascal": "var s,r:string;\n  i:integer;\nbegin\n  readln(s);\n  r:='';\n  for i:=length(s) downto 1 do r:=r+s[i];\n  writeln(r);\nend.",
        "python": "s =\ninput()\nprint(s[:\n    :-1])",
        "cpp": "#include <iostream>\n#include <string>\n#include <algorithm>\nint main()\n{\n    std::string s;\n    std::getline(std::cin,s);\n    std::reverse(s.begin(),s.end());\n    std::cout<<s;\n}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        string s=Console.ReadLine();\n        Console.WriteLine(new string(s.Reverse().ToArray()));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        String s=sc.nextLine();\n        System.out.println(new StringBuilder(s).reverse().toString());\n    }\n}",
    },
    # Task 35: Проверка палиндрома
    "task_035": {
        "pascal": "var s:string;\n  i:integer;\n  ok:boolean;\nbegin\n  readln(s);\n  ok:=true;\n  for i:=1 to length(s) do\n    if s[i]<>s[length(s)-i+1] then ok:=false;\n  if ok then\n  writeln('yes')\n  else\n  writeln('no');\nend.",
        "python": "s =\ninput()\nprint('yes'\nif s == s[:\n    :-1]\n    else 'no')",
        "cpp": "#include <iostream>\n#include <string>\n#include <algorithm>\nint main()\n{\n    std::string s;\n    std::getline(std::cin,s);\n    std::reverse(s.begin(),s.end());\n    std::cout<<s;\n}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        string s=Console.ReadLine();\n        Console.WriteLine(new string(s.Reverse().ToArray()));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        String s=sc.nextLine();\n        System.out.println(new StringBuilder(s).reverse().toString());\n    }\n}",
    },
    # Task 36: Поиск подстроки
    "task_036": {
        "pascal": "var i,n,total: integer;\n  a: array[1..100] of integer;\nbegin\n  readln(n);\n  total:=0;\n  for i:=1 to n do\nbegin\n  readln(a[i]);\n  total:=total+a[i];\n  end;\n  writeln(total);\nend.",
        "python": "a = list(map(int, input().split()))\nprint(sum(a))",
        "cpp": "#include <iostream>\n#include <vector>\nint main()\n{\n    int n;\n    std::cin>>n;\n    std::vector<int>a(n);\n    for(int i=0;i<n;i++) std::cin>>a[i];\n    int total=0;\n    for(int x:a) total+=x;\n    std::cout<<total;\n}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine());\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=int.Parse(Console.ReadLine());\n        int total=0;\n        foreach(int x in a) total+=x;\n        Console.Write(total;\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt();\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n        /* Поиск подстроки */ for(int x:a) System.out.print(x+\" \" );\n    }\n}",
    },
    # Task 37: Подсчёт слов
    "task_037": {
        "pascal": "var s:string;\n  i,count:integer;\n  inWord:boolean;\nbegin\n  readln(s);\n  count: =0;\n  inWord:=false;\n  for i:=1 to length(s) do\n    if s[i]<>' ' then\nbegin\n  if not inWord then count:=count+1;\n  inWord:=true;\n  end\nelse inWord:=false;\n  writeln(count);\nend.",
        "python": "s =\ninput().strip()\nprint(0\nif s == ''\nelse len(s.split()))",
        "cpp": "#include <iostream>\n#include <string>\n#include <algorithm>\nint main(){std::string s; std::getline(std::cin,s); std::reverse(s.beg\nin(),s.end()); std::cout<<s;}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        string s=Console.ReadLine();\n        Console. WriteLine(new string(s.Reverse().ToArray()));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scann er(System.in);\n        String s=sc.nextLine();\n        System.out.println(new StringBuilder(s).reverse().toString());\n    }\n}",
    },
    # Task 38: Проверка анаграммы
    "task_038": {
        "pascal": "var a,b:string;\nbegin\n  readln(a);\n  readln(b);\n  if length(a)=length(b) then\n  writeln('check')\n  else\n  writeln('no');\nend.",
        "python": "a = ''.join(sorted(input()))b = ''.join(sorted(input()))\nprint('yes'\nif a == b\nelse 'no')",
        "cpp": "#include <iostream>\n#include <string>\n#include <algorithm>\nint main()\n{\n    std::string s;\n    std::getline(std::cin,s);\n    std::reverse(s.begin(),s.end());\n    std::cout<<s;\n}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        string s=Console.ReadLine();\n        Console.WriteLine(new string(s.Reverse().ToArray()));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        String s=sc.nextLine();\n        System.out.println(new StringBuilder(s).reverse().toString());\n    }\n}",
    },
    # Task 39: RLE-сжатие строки
    "task_039": {
        "pascal": "var s,res:string;\n  i,count:integer;\nbegin\n  readln(s);\n  res:='';\n  count:=1;\n  for i:=2 to length(s)+1 do\nbegin\n  if (i<=length(s)) and (s[i]=s[i-1]) then count:=count+1\nelse begin\n  res:=res+s[i-1]+IntToStr(count);\n  count:=1;\n  end;\n  end;\n  writeln(res);\nend.",
        "python": "s =\ninput()res = ''count = 1\nfor i in range(1, len(s)+1):\n    if i < len(s)\n    and s[i] == s[i-1]:\n        count += 1\n    else:\n        res += s[i-1] + str(count)\n        count = 1\n        print(res)",
        "cpp": "#include <iostream>\n#include <string>\n#include <algorithm>\nint main()\n{\n    std::string s;\n    std::getline(std::cin,s);\n    std::reverse(s.begin(),s.end());\n    std::cout<<s;\n}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        string s=Console.ReadLine();\n        Console.WriteLine(new string(s.Reverse().ToArray()));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        String s=sc.nextLine();\n        System.out.println(new StringBuilder(s).reverse().toString());\n    }\n}",
    },
    # Task 40: Итоговая: анализ текста
    "task_040": {
        "pascal": "var s:string;\n  ch:char;\n  i,count:integer;\nbegin\n  readln(s);\n  readln(ch);\n  count:=0;\n  for i:=1 to length(s) do\n    if s[i]=ch then count:=count+1;\n  writeln(count);\nend.",
        "python": "s =\ninput()ch =\ninput()count = 0\nfor c in s:\n    if c == ch:\n        count += 1\n        print(count)",
        "cpp": "#include <iostream>\n#include <string>\n#include <algorithm>\nint main()\n{\n    std::string s;\n    std::getline(std::cin,s);\n    std::reverse(s.begin(),s.end());\n    std::cout<<s;\n}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        string s=Console.ReadLine();\n        Console.WriteLine(new string(s.Reverse().ToArray()));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        String s=sc.nextLine();\n        System.out.println(new StringBuilder(s).reverse().toString());\n    }\n}",
    },
    # Task 41: Функция поиска максимума
    "task_041": {
        "pascal": "function solve(a,b: integer): integer;\nbegin\n  if a>b then solve:=a\nelse solve:=b;\n  end;\nvar a,b:integer;\nbegin\n  readln(a,b);\n  writeln(solve(a,b));\nend.",
        "python": "def solve(a, b):\n    return a\nif a > b\nelse b a, b = map(int, input().split())\nprint(solve(a, b))",
        "cpp": "#include <iostream>\nint solve(int a,int b)\n{\n    return a>b?a:b;\n}\nint main()\n{\n    int a,b;\n    std::cin>>a>>b;\n    std::cout<<solve(a,b);\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static int Solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    static vo id Main()\n    {\n        var p=Console.ReadLine().Split();\n        Console.WriteLine(Solve(int.Parse(p[0]),int.Parse(p[1])));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    static int solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    public stati c void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        System.out.println(solve(sc.nextInt(),sc.nextInt()));\n    }\n}",
    },
    # Task 42: Функция проверки простого числа
    "task_042": {
        "pascal": "function solve(a,b: integer): integer;\nbegin\n  if условие:=a\nelse solve:=b;\n  end;\nvar a,b:integer;\nbegin\n  readln(a,b);\n  writeln(solve(a,b));\nend.",
        "python": "def solve(a, b):\n    return a\nif a > b\nelse ba, b = map(int, input().split())\nprint(solve(a, b))",
        "cpp": "#include <iostream>\nint solve(int a,int b)\n{\n    return a>b?a:b;\n}\nint main()\n{\n    int a,b;\n    std::cin>>a>>b;\n    std::cout<<solve(a,b);\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static int Solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    static void Main()\n    {\n        var p=Console.ReadLine().Split();\n        Console.WriteLine(Solve(int.Parse(p[0]),int.Parse(p[1])));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    static int solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        System.out.println(solve(sc.nextInt(),sc.nextInt()));\n    }\n}",
    },
    # Task 43: Функция GCD
    "task_043": {
        "pascal": "function solve(a,b: integer): integer;\nbegin\n  if a>b then solve:=a\nelse solve:=b;\n  end;\nvar a,b:integer;\nbegin\n  readln(a,b);\n  writeln(solve(a,b));\nend.",
        "python": "def solve(a, b):\n    return a\nif a > b\nelse ba, b = map(int, input().split())\nprint(solve(a, b))",
        "cpp": "#include <iostream>\nint solve(int a,int b)\n{\n    return a>b?a:b;\n}\nint main()\n{\n    int a,b;\n    std::cin>>a>>b;\n    std::cout<<solve(a,b);\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static int Solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    static void Main()\n    {\n        var p=Console.ReadLine().Split();\n        Console.WriteLine(Solve(int.Parse(p[0]),int.Parse(p[1])));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    static int solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        System.out.println(solve(sc.nextInt(),sc.nextInt()));\n    }\n}",
    },
    # Task 44: Функция нормализации строки
    "task_044": {
        "pascal": "function solve(a,b: integer): integer;\nbegin\n  if a>b then solve:=a\nelse solve:=b;\n  end;\nvar a,b:integer;\nbegin\n  readln(a,b);\n  writeln(solve(a,b));\nend.",
        "python": "def solve(a, b):\n    return a\nif a > b\nelse ba, b = map(int, input().split())\nprint(solve(a, b))",
        "cpp": "#include <iostream>\nint solve(int a,int b)\n{\n    return a>b?a:b;\n}\nint main()\n{\n    int a,b;\n    std::cin>>a>>b;\n    std::cout<<solve(a,b);\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static int Solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    static void Main()\n    {\n        var p=Console.ReadLine().Split();\n        Console.WriteLine(Solve(int.Parse(p[0]),int.Parse(p[1])));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    static int solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        System.out.println(solve(sc.nextInt(),sc.nextInt()));\n    }\n}",
    },
    # Task 45: Функция бинарного поиска
    "task_045": {
        "pascal": "function solve(a,b: integer): integer;\nbegin\n  if a>b then solve:=a\nelse solve:=b;\n  end;\nvar a,b:integer;\nbegin\n  readln(a,b);\n  writeln(solve(a,b));\nend.",
        "python": "def solve(a, b):\n    return a\nif a > b\nelse b a, b = map(int, input().split())\nprint(solve(a, b))",
        "cpp": "#include <iostream>\nint solve(int a,int b)\n{\n    return a>b?a:b;\n}\nint main()\n{\n    int a,b;\n    std::cin>>a>>b;\n    std::cout<<solve(a,b);\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static int Solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    static vo id Main()\n    {\n        var p=Console.ReadLine().Split();\n        Console.WriteLine(Solve(int.Parse(p[0]),int.Parse(p[1])));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    static int solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    public stati c void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        System.out.println(solve(sc.nextInt(),sc.nextInt()));\n    }\n}",
    },
    # Task 46: Функция проверки палиндрома
    "task_046": {
        "pascal": "function solve(a,b: integer): integer;\nbegin\n  if условие:=a\nelse solve:=b;\n  end;\nvar a,b:integer;\nbegin\n  readln(a,b);\n  writeln(solve(a,b));\nend.",
        "python": "def solve(a, b):\n    return a\nif a > b\nelse ba, b = map(int, input().split())\nprint(solve(a, b))",
        "cpp": "#include <iostream>\nint solve(int a,int b)\n{\n    return a>b?a:b;\n}\nint main()\n{\n    int a,b;\n    std::cin>>a>>b;\n    std::cout<<solve(a,b);\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static int Solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    static void Main()\n    {\n        var p=Console.ReadLine().Split();\n        Console.WriteLine(Solve(int.Parse(p[0]),int.Parse(p[1])));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    static int solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        System.out.println(solve(sc.nextInt(),sc.nextInt()));\n    }\n}",
    },
    # Task 47: Передача массива в функцию
    "task_047": {
        "pascal": "function solve(a,b: integer): integer;\nbegin\n  if a>b then solve:=a\nelse solve:=b;\n  end;\nvar a,b:integer;\nbegin\n  readln(a,b);\n  writeln(solve(a,b));\nend.",
        "python": "def solve(a, b):\n    return a\nif a > b\nelse ba, b = map(int, input().split())\nprint(solve(a, b))",
        "cpp": "#include <iostream>\nint solve(int a,int b)\n{\n    return a>b?a:b;\n}\nint main()\n{\n    int a,b;\n    std::cin>>a>>b;\n    std::cout<<solve(a,b);\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static int Solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    static void Main()\n    {\n        var p=Console.ReadLine().Split();\n        Console.WriteLine(Solve(int.Parse(p[0]),int.Parse(p[1])));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    static int solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        System.out.println(solve(sc.nextInt(),sc.nextInt()));\n    }\n}",
    },
    # Task 48: Итоговая: библиотека алгоритмов
    "task_048": {
        "pascal": "function solve(a,b: integer): integer;\nbegin\n  if a>b then solve:=a\nelse solve:=b;\n  end;\nvar a,b:integer;\nbegin\n  readln(a,b);\n  writeln(solve(a,b));\nend.",
        "python": "def solve(a, b):\n    return a\nif a > b\nelse ba, b = map(int, input().split())\nprint(solve(a, b))",
        "cpp": "#include <iostream>\nint solve(int a,int b)\n{\n    return a>b?a:b;\n}\nint main()\n{\n    int a,b;\n    std::cin>>a>>b;\n    std::cout<<solve(a,b);\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static int Solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    static void Main()\n    {\n        var p=Console.ReadLine().Split();\n        Console.WriteLine(Solve(int.Parse(p[0]),int.Parse(p[1])));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    static int solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        System.out.println(solve(sc.nextInt(),sc.nextInt()));\n    }\n}",
    },
    # Task 49: Факториал
    "task_049": {
        "pascal": "function factorial(n: integer): integer;\nbegin\n  if n <= 1 then factorial := 1\nelse factorial := n * factorial(n-1);\n  end;\nvar n: integer;\nbegin\n  readln(n);\n  writeln(factorial(n));\nend.",
        "python": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\nn = int(input())\nprint(factorial(n))",
        "cpp": "#include <iostream>\nint solve(int a,int b)\n{\n    return a>b?a:b;\n}\nint main()\n{\n    int a,b;\n    std::cin>>a>>b;\n    std::cout<<solve(a,b);\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static int Solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    static vo id Main()\n    {\n        var p=Console.ReadLine().Split();\n        Console.WriteLine(Solve(int.Parse(p[0]),int.Parse(p[1])));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    static int solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    public stati c void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        System.out.println(solve(sc.nextInt(),sc.nextInt()));\n    }\n}",
    },
    # Task 50: Fibonacci
    "task_050": {
        "pascal": "function fib(n: integer): integer;\nbegin\n  if условие:= 1\nelse fib := n * fib(n-1);\n  end;\nvar n: integer;\nbegin\n  readln(n);\n  writeln(fib(n));\nend.",
        "python": "def fib(n):\n    if условие:\n        return 1\n    return n * fib(n - 1)n = int(input())\nprint(fib(n))",
        "cpp": "#include <iostream>\nint solve(int a,int b)\n{\n    return a>b?a:b;\n}\nint main()\n{\n    int a,b;\n    std::cin>>a>>b;\n    std::cout<<solve(a,b);\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static int Solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    static void Main()\n    {\n        var p=Console.ReadLine().Split();\n        Console.WriteLine(Solve(int.Parse(p[0]),int.Parse(p[1])));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    static int solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        System.out.println(solve(sc.nextInt(),sc.nextInt()));\n    }\n}",
    },
    # Task 51: Рекурсивная сумма массива
    "task_051": {
        "pascal": "function solve(n: integer): integer;\nbegin\n  if n <= 1 then solve := 1\nelse solve := n * solve(n-1);\n  end;\nvar n: integer;\nbegin\n  readln(n);\n  writeln(solve(n));\nend.",
        "python": "def solve(n):\n    if n <= 1:\n        return 1\n    return n * solve(n - 1)n = int(input())\nprint(solve(n))",
        "cpp": "#include <iostream>\nint solve(int a,int b)\n{\n    return a>b?a:b;\n}\nint main()\n{\n    int a,b;\n    std::cin>>a>>b;\n    std::cout<<solve(a,b);\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static int Solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    static void Main()\n    {\n        var p=Console.ReadLine().Split();\n        Console.WriteLine(Solve(int.Parse(p[0]),int.Parse(p[1])));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    static int solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        System.out.println(solve(sc.nextInt(),sc.nextInt()));\n    }\n}",
    },
    # Task 52: Быстрое возведение в степень
    "task_052": {
        "pascal": "function solve(n: integer): integer;\nbegin\n  if n <= 1 then solve := 1\nelse solve := n * solve(n-1);\n  end;\nvar n: integer;\nbegin\n  readln(n);\n  writeln(solve(n));\nend.",
        "python": "def solve(n):\n    if n <= 1:\n        return 1\n    return n * solve(n - 1)n = int(input())\nprint(solve(n))",
        "cpp": "#include <iostream>\nint solve(int a,int b)\n{\n    return a>b?a:b;\n}\nint main()\n{\n    int a,b;\n    std::cin>>a>>b;\n    std::cout<<solve(a,b);\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static int Solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    static void Main()\n    {\n        var p=Console.ReadLine().Split();\n        Console.WriteLine(Solve(int.Parse(p[0]),int.Parse(p[1])));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    static int solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        System.out.println(solve(sc.nextInt(),sc.nextInt()));\n    }\n}",
    },
    # Task 53: Рекурсивный разворот строки
    "task_053": {
        "pascal": "function solve(n: integer): integer;\nbegin\n  if n <= 1 then solve := 1\nelse solve := n * solve(n-1);\n  end;\nvar n: integer;\nbegin\n  readln(n);\n  writeln(solve(n));\nend.",
        "python": "def solve(n):\n    if n <= 1:\n        return 1\n    return n * solve(n - 1)\nn = int(input())\nprint(solve(n))",
        "cpp": "#include <iostream>\nint solve(int a,int b)\n{\n    return a>b?a:b;\n}\nint main()\n{\n    int a,b;\n    std::cin>>a>>b;\n    std::cout<<solve(a,b);\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static int Solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    static vo id Main()\n    {\n        var p=Console.ReadLine().Split();\n        Console.WriteLine(Solve(int.Parse(p[0]),int.Parse(p[1])));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    static int solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    public stati c void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        System.out.println(solve(sc.nextInt(),sc.nextInt()));\n    }\n}",
    },
    # Task 54: Бинарный поиск рекурсией
    "task_054": {
        "pascal": "function solve(n: integer): integer;\nbegin\n  if условие:= 1\nelse solve := n * solve(n-1);\n  end;\nvar n: integer;\nbegin\n  readln(n);\n  writeln(solve(n));\nend.",
        "python": "def solve(n):\n    if условие:\n        return 1\n    return n * solve(n - 1)n = int(input())\nprint(solve(n))",
        "cpp": "#include <iostream>\nint solve(int a,int b)\n{\n    return a>b?a:b;\n}\nint main()\n{\n    int a,b;\n    std::cin>>a>>b;\n    std::cout<<solve(a,b);\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static int Solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    static void Main()\n    {\n        var p=Console.ReadLine().Split();\n        Console.WriteLine(Solve(int.Parse(p[0]),int.Parse(p[1])));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    static int solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        System.out.println(solve(sc.nextInt(),sc.nextInt()));\n    }\n}",
    },
    # Task 55: Quicksort
    "task_055": {
        "pascal": "function solve(n: integer): integer;\nbegin\n  if n <= 1 then solve := 1\nelse solve := n * solve(n-1);\n  end;\nvar n: integer;\nbegin\n  readln(n);\n  writeln(solve(n));\nend.",
        "python": "def solve(n):\n    if n <= 1:\n        return 1\n    return n * solve(n - 1)n = int(input())\nprint(solve(n))",
        "cpp": "#include <iostream>\nint solve(int a,int b)\n{\n    return a>b?a:b;\n}\nint main()\n{\n    int a,b;\n    std::cin>>a>>b;\n    std::cout<<solve(a,b);\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static int Solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    static void Main()\n    {\n        var p=Console.ReadLine().Split();\n        Console.WriteLine(Solve(int.Parse(p[0]),int.Parse(p[1])));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    static int solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        System.out.println(solve(sc.nextInt(),sc.nextInt()));\n    }\n}",
    },
    # Task 56: Итоговая: рекурсивный обход каталога
    "task_056": {
        "pascal": "function solve(n: integer): integer;\nbegin\n  if n <= 1 then solve := 1\nelse solve := n * solve(n-1);\n  end;\nvar n: integer;\nbegin\n  readln(n);\n  writeln(solve(n));\nend.",
        "python": "def solve(n):\n    if n <= 1:\n        return 1\n    return n * solve(n - 1)n = int(input())\nprint(solve(n))",
        "cpp": "#include <iostream>\nint solve(int a,int b)\n{\n    return a>b?a:b;\n}\nint main()\n{\n    int a,b;\n    std::cin>>a>>b;\n    std::cout<<solve(a,b);\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static int Solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    static void Main()\n    {\n        var p=Console.ReadLine().Split();\n        Console.WriteLine(Solve(int.Parse(p[0]),int.Parse(p[1])));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    static int solve(int a,int b)\n    {\n        return a>b?a:b;\n    }\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        System.out.println(solve(sc.nextInt(),sc.nextInt()));\n    }\n}",
    },
    # Task 57: Линейный поиск
    "task_057": {
        "pascal": "var i,n,total: integer;\n  a: array[1..100] of integer;\nbegin\n  readln(n);\n  total:=0;\n  for i:=1 to n do\nbegin\n  readln(a[i]);\n  total: =total+a[i];\n  end;\n  writeln(total);\nend.",
        "python": "a = list(map(int, input().split()))\nprint(sum(a))",
        "cpp": "#include <iostream>\n#include <vector>\nint main(){int n; std::cin>>n; std::vector<int>a(n); for(int i=0;i<n;i\n++) std::cin>>a[i]; int total=0; for(int x:a) total+=x; std::cout<<total;}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine());\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=int.Parse(Console.ReadLine());\n        int total=0;\n        foreach(int x in a) total+=x;\n        Console.Write(total;\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scann er(System.in);\n        int n=sc.nextInt();\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n        /* Линейный поиск */ for(int x:a) System.out.print(x+\" \" );\n    }\n}",
    },
    # Task 58: Бинарный поиск
    "task_058": {
        "pascal": "var i,n,total: integer;\n  a: array[1..100] of integer;\nbegin\n  readln(n);\n  total:=0;\n  for i:=1 to n do\nbegin\n  readln(a[i]);\n  total:=total+a[i];\n  end;\n  writeln(total);\nend.",
        "python": "a = list(map(int, input().split()))\nprint(sum(a))",
        "cpp": "#include <iostream>\n#include <vector>\nint main()\n{\n    int n;\n    std::cin>>n;\n    std::vector<int>a(n);\n    for(int i=0;i<n;i++) std::cin>>a[i];\n    int total=0;\n    for(int x:a) total+=x;\n    std::cout<<total;\n}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine());\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=int.Parse(Console.ReadLine());\n        int total=0;\n        foreach(int x in a) total+=x;\n        Console.Write(total;\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt();\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n        /* Бинарный поиск */ for(int x:a) System.out.print(x+\" \" );\n    }\n}",
    },
    # Task 59: Selection Sort
    "task_059": {
        "pascal": "var i,j,n,t:integer;\n  a:array[1..100] of integer;\nbegin\n  readln(n);\n  for i:=1 to n do\n  readln(a[i]);\n  for i:=1 to n do\n  for j:=i+1 to n do\n    if a[j]<a[i] then\nbegin\n  t:=a[i];\n  a[i]:=a[j];\n  a[j]:=t;\n  end;\n  for i:=1 to n do\n  write(a[i],' ');\nend.",
        "python": "a = list(map(int, input().split()))a.sort()\nprint(*a)",
        "cpp": "#include <iostream>\n#include <vector>\n#include <algorithm>\nint main()\n{\n    int n;\n    std::cin>>n;\n    std::vector<int>a(n);\n    for(int&i:a) std::cin>>i;\n    std::sort(a.begin(),a.end());\n    for(int x:a) std::cout<<x<<' ';\n}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine());\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=int.Parse(Console.ReadLine());\n        Array.Sort(a);\n        Console.WriteLine(string.Join(\" \",a));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt();\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n        Arrays.sort(a);\n        for(int x:a) System.out.print(x+\" \" );\n    }\n}",
    },
    # Task 60: Bubble Sort
    "task_060": {
        "pascal": "var i,j,n,t:integer;\n  a:array[1..100] of integer;\nbegin\n  readln(n);\n  for i:=1 to n do\n  readln(a[i]);\n  for i:=1 to n do\n  for j:=i+1 to n do\n    if a[j]<a[i] then\nbegin\n  t:=a[i];\n  a[i]:=a[j];\n  a[j]:=t;\n  end;\n  for i:=1 to n do\n  write(a[i],' ');\nend.",
        "python": "a = list(map(int, input().split()))a.sort()\nprint(*a)",
        "cpp": "#include <iostream>\n#include <vector>\n#include <algorithm>\nint main()\n{\n    int n;\n    std::cin>>n;\n    std::vector<int>a(n);\n    for(int&i:a) std::cin>>i;\n    std::sort(a.begin(),a.end());\n    for(int x:a) std::cout<<x<<' ';\n}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine());\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=int.Parse(Console.ReadLine());\n        Array.Sort(a);\n        Console.WriteLine(string.Join(\" \",a));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt();\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n        Arrays.sort(a);\n        for(int x:a) System.out.print(x+\" \" );\n    }\n}",
    },
    # Task 61: Insertion Sort
    "task_061": {
        "pascal": "var i,j,n,t:integer;\n  a:array[1..100] of integer;\nbegin\n  readln(n);\n  for i:=1 to n do\n  readln(a[i]);\n  for i:=1 to n do\n  for j:=i+1 to n do\n    if a[j]<a[i] then\nbegin\n  t:=a[i];\n  a[i]:=a[j];\n  a[j]:=t;\n  end;\n  for i:=1 to n do\n  write(a[i],' ');\nend.",
        "python": "a = list(map(int, input().split()))\na.sort()\nprint(*a)",
        "cpp": "#include <iostream>\n#include <vector>\n#include <algorithm>\nint main(){int n; std::cin>>n; std::vector<int>a(n); for(int&i:a) std:\n:cin>>i; std::sort(a.begin(),a.end()); for(int x:a) std::cout<<x<<' ';}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine());\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=int.Parse(Console.ReadLine());\n        Array.Sort(a);\n        Console.WriteLine(string.Join(\" \",a));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scann er(System.in);\n        int n=sc.nextInt();\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n        Arrays.sort(a);\n        for(int x:a) System.out.print(x+\" \" );\n    }\n}",
    },
    # Task 62: Сортировка строк
    "task_062": {
        "pascal": "var i,j,n,t:integer;\n  a:array[1..100] of integer;\nbegin\n  readln(n);\n  for i:=1 to n do\n  readln(a[i]);\n  for i:=1 to n do\n  for j:=i+1 to n do\n    if for i:=1 to n do:=a[i];\n  a[i]:=a[j];\n  a[j]:=t;\n  end;\n  for i:=1 to n do\n  write(a[i],' ');\nend.",
        "python": "a = list(map(int, input().split()))a.sort()\nprint(*a)",
        "cpp": "#include <iostream>\n#include <vector>\n#include <algorithm>\nint main()\n{\n    int n;\n    std::cin>>n;\n    std::vector<int>a(n);\n    for(int&i:a) std::cin>>i;\n    std::sort(a.begin(),a.end());\n    for(int x:a) std::cout<<x<<' ';\n}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine());\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=int.Parse(Console.ReadLine());\n        Array.Sort(a);\n        Console.WriteLine(string.Join(\" \",a));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt();\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n        Arrays.sort(a);\n        for(int x:a) System.out.print(x+\" \" );\n    }\n}",
    },
    # Task 63: Сортировка объектов/записей
    "task_063": {
        "pascal": "var i,j,n,t:integer;\n  a:array[1..100] of integer;\nbegin\n  readln(n);\n  for i:=1 to n do\n  readln(a[i]);\n  for i:=1 to n do\n  for j:=i+1 to n do\n    if a[j]<a[i] then\nbegin\n  t:=a[i];\n  a[i]:=a[j];\n  a[j]:=t;\n  end;\n  for i:=1 to n do\n  write(a[i],' ');\nend.",
        "python": "a = list(map(int, input().split()))a.sort()\nprint(*a)",
        "cpp": "#include <iostream>\n#include <vector>\n#include <algorithm>\nint main()\n{\n    int n;\n    std::cin>>n;\n    std::vector<int>a(n);\n    for(int&i:a) std::cin>>i;\n    std::sort(a.begin(),a.end());\n    for(int x:a) std::cout<<x<<' ';\n}",
        "csharp": "using System;\nusing System.Linq;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine());\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=int.Parse(Console.ReadLine());\n        Array.Sort(a);\n        Console.WriteLine(string.Join(\" \",a));\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt();\n        int[] a=new int[n];\n        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n        Arrays.sort(a);\n        for(int x:a) System.out.print(x+\" \" );\n    }\n}",
    },
    # Task 64: Итоговая: таблица лидеров
    "task_064": {
        "pascal": "var i,n,x,total:integer;\nbegin\n  readln(n);\n  total:=0;\n  for i:=1 to n do\nbegin\n  readln(x);\n  total:=total+x;\n  end;\n  writeln(total);\nend.",
        "python": "n = int(input())total = 0\nfor _ in range(n):\n    total += int(input())\n    print(total)",
        "cpp": "#include <iostream>\nint main()\n{\n    int n,x,total=0;\n    std::cin>>n;\n    for(int i=0;i<n;i++)\n    {\n        std::cin>>x;\n        total+=x;\n    }\n    std::cout<<total;\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine()), total=0;\n        for(int i=0;i<n;i++) total+=int.Parse(Console.ReadLine());\n        Console.WriteLine(total);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt(), total=0;\n        for(int i=0;i<n;i++) total+=sc.nextInt();\n        System.out.println(total);\n    }\n}",
    },
    # Task 65: Сумма продаж
    "task_065": {
        "pascal": "var i,n,x,total:integer;\nbegin\n  readln(n);\n  total:=0;\n  for i:=1 to n do b egin\n  readln(x);\n  total:=total+x;\n  end;\n  writeln(total);\nend.",
        "python": "n = int(input())\ntotal = 0\nfor _ in range(n):\n    total += int(input())\n    print(total)",
        "cpp": "#include <iostream>\nint main()\n{\n    int n,x,total=0;\n    std::cin>>n;\n    for(int i=0;i<n;i++)\n    {\n        std::cin >>x;\n        total+=x;\n    }\n    std::cout<<total;\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine()), total=0;\n        for(int i=0;i<n;i++) total+=int.Parse(Console.ReadLine());\n        Console.WriteLine(total);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scann er(System.in);\n        int n=sc.nextInt(), total=0;\n        for(int i=0;i<n;i++) total+=sc.nextInt();\n        System.out.println(total);\n    }\n}",
    },
    # Task 66: Среднее значение
    "task_066": {
        "pascal": "var i,n,x,total:integer;\nbegin\n  readln(n);\n  total:=0;\n  for i:=1 to n do\nbegin\n  readln(x);\n  total:=total+x;\n  end;\n  writeln(total);\nend.",
        "python": "n = int(input())total = 0\nfor _ in range(n):\n    total += int(input())\n    print(total)",
        "cpp": "#include <iostream>\nint main()\n{\n    int n,x,total=0;\n    std::cin>>n;\n    for(int i=0;i<n;i++)\n    {\n        std::cin>>x;\n        total+=x;\n    }\n    std::cout<<total;\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine()), total=0;\n        for(int i=0;i<n;i++) total+=int.Parse(Console.ReadLine());\n        Console.WriteLine(total);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt(), total=0;\n        for(int i=0;i<n;i++) total+=sc.nextInt();\n        System.out.println(total);\n    }\n}",
    },
    # Task 67: Фильтр положительных чисел
    "task_067": {
        "pascal": "var i,n,x:integer;\nbegin\n  readln(n);\n  for i:=1 to n do\nbegin\n  readln(x);\n  if x>0 then\n  write(x,' ');\n  end;\nend.",
        "python": "a = list(map(int, input().split()))filtered = []\nfor x in a:\n    if x > 0:\n        filtered.append(x)\n        print(*filtered)",
        "cpp": "#include <iostream>\nint main()\n{\n    int n,x;\n    std::cin>>n;\n    for(int i=0;i<n;i++)\n    {\n        std::cin>>x;\n        if(x>0) std::cout<<x<<' ';\n    }\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine());\n        for(int i=0;i<n;i++)\n        {\n            int x=int.Parse(Console.ReadLine());\n            if(x>0) Console.Write(x+\" \" );\n        }\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt();\n        for(int i=0;i<n;i++)\n        {\n            int x=sc.nextInt();\n            if(x>0) System.out.print(x+\" \" );\n        }\n    }\n}",
    },
    # Task 68: Фильтр заказов по статусу
    "task_068": {
        "pascal": "var i,n,x:integer;\nbegin\n  readln(n);\n  for i:=1 to n do\nbegin\n  readln(x);\n  if x>0 then\n  write(x,' ');\n  end;\nend.",
        "python": "a = list(map(int, input().split()))filtered = []\nfor x in a:\n    if x > 0:\n        filtered.append(x)\n        print(*filtered)",
        "cpp": "#include <iostream>\nint main()\n{\n    int n,x;\n    std::cin>>n;\n    for(int i=0;i<n;i++)\n    {\n        std::cin>>x;\n        if(x>0) std::cout<<x<<' ';\n    }\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine());\n        for(int i=0;i<n;i++)\n        {\n            int x=int.Parse(Console.ReadLine());\n            if(x>0) Console.Write(x+\" \" );\n        }\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt();\n        for(int i=0;i<n;i++)\n        {\n            int x=sc.nextInt();\n            if(x>0) System.out.print(x+\" \" );\n        }\n    }\n}",
    },
    # Task 69: Подсчёт голосов
    "task_069": {
        "pascal": "var s:string;\n  i:integer;\n  count: array['a'..'z'] of integer;\nbegin\n  read ln(s);\n  for i:=1 to length(s) do\n    if (s[i]>='a') and (s[i]<='z') then count[s[i]]:=count[s[i]]+1;\n  writeln(count['a']);\nend.",
        "python": "data =\ninput().split()\nfreq = {}\nfor item in data:\n    freq[item] = freq.get(item, 0) + 1\n    for key in sorted(freq):\n        print(key, freq[key])",
        "cpp": "#include <iostream>\n#include <map>\n#include <string>\nint main(){std::map<std::string,int> freq; std::string x; while(std::c\nin>>x) freq[x]++; for(auto &p:freq) std::cout<<p.first<<' '<<p.second<<' ';}",
        "csharp": "using System;\nusing System.Collections.Generic;\n\nclass Program\n{\n    static void Main()\n    {\n        var freq=new Dictionary<string,int>();\n        foreach(var x in Console.ReadLine().Split())\n        {\n            freq[x]=freq.ContainsKey(x)?freq[x]+1:1;\n        }\n        foreach(var p in freq) Console.WriteLine(p.Key+\" \"+p.Value);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scann er(System.in);\n        Map<String,Integer> freq=new TreeMap<>();\n        while(sc.hasNext())\n        {\n            String x=sc.next();\n            freq.put(x, freq.getOrDefault(x,0)+1);\n        }\n        for(String k:freq.keySet()) System.out.println(k+\" \"+freq.get(k));\n    }\n}",
    },
    # Task 70: Топ N элементов
    "task_070": {
        "pascal": "var i,n,x,total:integer;\nbegin\n  readln(n);\n  total:=0;\n  for i:=1 to n do\nbegin\n  readln(x);\n  total:=total+x;\n  end;\n  writeln(total);\nend.",
        "python": "n = int(input())total = 0\nfor _ in range(n):\n    total += int(input())\n    print(total)",
        "cpp": "#include <iostream>\nint main()\n{\n    int n,x,total=0;\n    std::cin>>n;\n    for(int i=0;i<n;i++)\n    {\n        std::cin>>x;\n        total+=x;\n    }\n    std::cout<<total;\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine()), total=0;\n        for(int i=0;i<n;i++) total+=int.Parse(Console.ReadLine());\n        Console.WriteLine(total);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt(), total=0;\n        for(int i=0;i<n;i++) total+=sc.nextInt();\n        System.out.println(total);\n    }\n}",
    },
    # Task 71: Группировка данных
    "task_071": {
        "pascal": "var s:string;\n  i:integer;\n  count: array['a'..'z'] of integer;\nbegin\n  readln(s);\n  for i:=1 to length(s) do\n    if (s[i]>='a') and (s[i]<='z') then count[s[i]]:=count[s[i]]+1;\n  writeln(count['a']);\nend.",
        "python": "data =\ninput().split()freq = {}\nfor item in data:\n    freq[item] = freq.get(item, 0) + 1\n    for key in sorted(freq):\n        print(key, freq[key])",
        "cpp": "#include <iostream>\n#include <map>\n#include <string>\nint main()\n{\n    std::map<std::string,int> freq;\n    std::string x;\n    while(std::cin>>x) freq[x]++;\n    for(auto &p:freq) std::cout<<p.first<<' '<<p.second<<' ';\n}",
        "csharp": "using System;\nusing System.Collections.Generic;\n\nclass Program\n{\n    static void Main()\n    {\n        var freq=new Dictionary<string,int>();\n        foreach(var x in Console.ReadLine().Split())\n        {\n            freq[x]=freq.ContainsKey(x)?freq[x]+1:1;\n        }\n        foreach(var p in freq) Console.WriteLine(p.Key+\" \"+p.Value);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        Map<String,Integer> freq=new TreeMap<>();\n        while(sc.hasNext())\n        {\n            String x=sc.next();\n            freq.put(x, freq.getOrDefault(x,0)+1);\n        }\n        for(String k:freq.keySet()) System.out.println(k+\" \"+freq.get(k));\n    }\n}",
    },
    # Task 72: Итоговая: аналитика магазина
    "task_072": {
        "pascal": "var i,n,x,total:integer;\nbegin\n  readln(n);\n  total:=0;\n  for i:=1 to n do\nbegin\n  readln(x);\n  total:=total+x;\n  end;\n  writeln(total);\nend.",
        "python": "n = int(input())total = 0\nfor _ in range(n):\n    total += int(input())\n    print(total)",
        "cpp": "#include <iostream>\nint main()\n{\n    int n,x,total=0;\n    std::cin>>n;\n    for(int i=0;i<n;i++)\n    {\n        std::cin>>x;\n        total+=x;\n    }\n    std::cout<<total;\n}",
        "csharp": "using System;\n\nclass Program\n{\n    static void Main()\n    {\n        int n=int.Parse(Console.ReadLine()), total=0;\n        for(int i=0;i<n;i++) total+=int.Parse(Console.ReadLine());\n        Console.WriteLine(total);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        int n=sc.nextInt(), total=0;\n        for(int i=0;i<n;i++) total+=sc.nextInt();\n        System.out.println(total);\n    }\n}",
    },
    # Task 73: Частотный словарь символов
    "task_073": {
        "pascal": "var s:string;\n  i:integer;\n  count: array['a'..'z'] of integer;\nbegin\n  read ln(s);\n  for i:=1 to length(s) do\n    if (s[i]>='a') and (s[i]<='z') then count[s[i]]:=count[s[i]]+1;\n  writeln(count['a']);\nend.",
        "python": "data =\ninput().split()\nfreq = {}\nfor item in data:\n    freq[item] = freq.get(item, 0) + 1\n    for key in sorted(freq):\n        print(key, freq[key])",
        "cpp": "#include <iostream>\n#include <map>\n#include <string>\nint main(){std::map<std::string,int> freq; std::string x; while(std::c\nin>>x) freq[x]++; for(auto &p:freq) std::cout<<p.first<<' '<<p.second<<' ';}",
        "csharp": "using System;\nusing System.Collections.Generic;\n\nclass Program\n{\n    static void Main()\n    {\n        var freq=new Dictionary<string,int>();\n        foreach(var x in Console.ReadLine().Split())\n        {\n            freq[x]=freq.ContainsKey(x)?freq[x]+1:1;\n        }\n        foreach(var p in freq) Console.WriteLine(p.Key+\" \"+p.Value);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scann er(System.in);\n        Map<String,Integer> freq=new TreeMap<>();\n        while(sc.hasNext())\n        {\n            String x=sc.next();\n            freq.put(x, freq.getOrDefault(x,0)+1);\n        }\n        for(String k:freq.keySet()) System.out.println(k+\" \"+freq.get(k));\n    }\n}",
    },
    # Task 74: Подсчёт слов
    "task_074": {
        "pascal": "var s:string;\n  i:integer;\n  count: array['a'..'z'] of integer;\nbegin\n  readln(s);\n  for i:=1 to length(s) do\n    if ((((цикл по данным) and (s[i]<='z') then count[s[i]]:=count[s[i]]+1) and (s[i]<='z') then count[s[i]]:=count[s[i]]+1) and (s[i]<='z') then count[s[i]]:=count[s[i]]+1) and (s[i]<='z') then count[s[i]]:=count[s[i]]+1;\n  writeln(count['a']);\nend.",
        "python": "data =\ninput().split()freq = {}\nfor item in data:\n    freq[item] = freq.get(item, 0) + 1\n    for key in sorted(freq):\n        print(key, freq[key])",
        "cpp": "#include <iostream>\n#include <map>\n#include <string>\nint main()\n{\n    std::map<std::string,int> freq;\n    std::string x;\n    while(std::cin>>x) freq[x]++;\n    for(auto &p:freq) std::cout<<p.first<<' '<<p.second<<' ';\n}",
        "csharp": "using System;\nusing System.Collections.Generic;\n\nclass Program\n{\n    static void Main()\n    {\n        var freq=new Dictionary<string,int>();\n        foreach(var x in Console.ReadLine().Split())\n        {\n            freq[x]=freq.ContainsKey(x)?freq[x]+1:1;\n        }\n        foreach(var p in freq) Console.WriteLine(p.Key+\" \"+p.Value);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        Map<String,Integer> freq=new TreeMap<>();\n        while(sc.hasNext())\n        {\n            String x=sc.next();\n            freq.put(x, freq.getOrDefault(x,0)+1);\n        }\n        for(String k:freq.keySet()) System.out.println(k+\" \"+freq.get(k));\n    }\n}",
    },
    # Task 75: Телефонная книга
    "task_075": {
        "pascal": "var s:string;\n  i:integer;\n  count: array['a'..'z'] of integer;\nbegin\n  readln(s);\n  for i:=1 to length(s) do\n    if (s[i]>='a') and (s[i]<='z') then count[s[i]]:=count[s[i]]+1;\n  writeln(count['a']);\nend.",
        "python": "data =\ninput().split()freq = {}\nfor item in data:\n    freq[item] = freq.get(item, 0) + 1\n    for key in sorted(freq):\n        print(key, freq[key])",
        "cpp": "#include <iostream>\n#include <map>\n#include <string>\nint main()\n{\n    std::map<std::string,int> freq;\n    std::string x;\n    while(std::cin>>x) freq[x]++;\n    for(auto &p:freq) std::cout<<p.first<<' '<<p.second<<' ';\n}",
        "csharp": "using System;\nusing System.Collections.Generic;\n\nclass Program\n{\n    static void Main()\n    {\n        var freq=new Dictionary<string,int>();\n        foreach(var x in Console.ReadLine().Split())\n        {\n            freq[x]=freq.ContainsKey(x)?freq[x]+1:1;\n        }\n        foreach(var p in freq) Console.WriteLine(p.Key+\" \"+p.Value);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        Map<String,Integer> freq=new TreeMap<>();\n        while(sc.hasNext())\n        {\n            String x=sc.next();\n            freq.put(x, freq.getOrDefault(x,0)+1);\n        }\n        for(String k:freq.keySet()) System.out.println(k+\" \"+freq.get(k));\n    }\n}",
    },
    # Task 76: Индекс студентов по ID
    "task_076": {
        "pascal": "var s:string;\n  i:integer;\n  count: array['a'..'z'] of integer;\nbegin\n  readln(s);\n  for i:=1 to length(s) do\n    if (s[i]>='a') and (s[i]<='z') then count[s[i]]:=count[s[i]]+1;\n  writeln(count['a']);\nend.",
        "python": "data =\ninput().split()freq = {}\nfor item in data:\n    freq[item] = freq.get(item, 0) + 1\n    for key in sorted(freq):\n        print(key, freq[key])",
        "cpp": "#include <iostream>\n#include <map>\n#include <string>\nint main()\n{\n    std::map<std::string,int> freq;\n    std::string x;\n    while(std::cin>>x) freq[x]++;\n    for(auto &p:freq) std::cout<<p.first<<' '<<p.second<<' ';\n}",
        "csharp": "using System;\nusing System.Collections.Generic;\n\nclass Program\n{\n    static void Main()\n    {\n        var freq=new Dictionary<string,int>();\n        foreach(var x in Console.ReadLine().Split())\n        {\n            freq[x]=freq.ContainsKey(x)?freq[x]+1:1;\n        }\n        foreach(var p in freq) Console.WriteLine(p.Key+\" \"+p.Value);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        Map<String,Integer> freq=new TreeMap<>();\n        while(sc.hasNext())\n        {\n            String x=sc.next();\n            freq.put(x, freq.getOrDefault(x,0)+1);\n        }\n        for(String k:freq.keySet()) System.out.println(k+\" \"+freq.get(k));\n    }\n}",
    },
    # Task 77: Кэш запросов
    "task_077": {
        "pascal": "var s:string;\n  i:integer;\n  count: array['a'..'z'] of integer;\nbegin\n  read ln(s);\n  for i:=1 to length(s) do\n    if (s[i]>='a') and (s[i]<='z') then count[s[i]]:=count[s[i]]+1;\n  writeln(count['a']);\nend.",
        "python": "data =\ninput().split()\nfreq = {}\nfor item in data:\n    freq[item] = freq.get(item, 0) + 1\n    for key in sorted(freq):\n        print(key, freq[key])",
        "cpp": "#include <iostream>\n#include <map>\n#include <string>\nint main(){std::map<std::string,int> freq; std::string x; while(std::c\nin>>x) freq[x]++; for(auto &p:freq) std::cout<<p.first<<' '<<p.second<<' ';}",
        "csharp": "using System;\nusing System.Collections.Generic;\n\nclass Program\n{\n    static void Main()\n    {\n        var freq=new Dictionary<string,int>();\n        foreach(var x in Console.ReadLine().Split())\n        {\n            freq[x]=freq.ContainsKey(x)?freq[x]+1:1;\n        }\n        foreach(var p in freq) Console.WriteLine(p.Key+\" \"+p.Value);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scann er(System.in);\n        Map<String,Integer> freq=new TreeMap<>();\n        while(sc.hasNext())\n        {\n            String x=sc.next();\n            freq.put(x, freq.getOrDefault(x,0)+1);\n        }\n        for(String k:freq.keySet()) System.out.println(k+\" \"+freq.get(k));\n    }\n}",
    },
    # Task 78: Группировка товаров по категории
    "task_078": {
        "pascal": "var s:string;\n  i:integer;\n  count: array['a'..'z'] of integer;\nbegin\n  readln(s);\n  for i:=1 to length(s) do\n    if ((((цикл по данным) and (s[i]<='z') then count[s[i]]:=count[s[i]]+1) and (s[i]<='z') then count[s[i]]:=count[s[i]]+1) and (s[i]<='z') then count[s[i]]:=count[s[i]]+1) and (s[i]<='z') then count[s[i]]:=count[s[i]]+1;\n  writeln(count['a']);\nend.",
        "python": "data =\ninput().split()freq = {}\nfor item in data:\n    freq[item] = freq.get(item, 0) + 1\n    for key in sorted(freq):\n        print(key, freq[key])",
        "cpp": "#include <iostream>\n#include <map>\n#include <string>\nint main()\n{\n    std::map<std::string,int> freq;\n    std::string x;\n    while(std::cin>>x) freq[x]++;\n    for(auto &p:freq) std::cout<<p.first<<' '<<p.second<<' ';\n}",
        "csharp": "using System;\nusing System.Collections.Generic;\n\nclass Program\n{\n    static void Main()\n    {\n        var freq=new Dictionary<string,int>();\n        foreach(var x in Console.ReadLine().Split())\n        {\n            freq[x]=freq.ContainsKey(x)?freq[x]+1:1;\n        }\n        foreach(var p in freq) Console.WriteLine(p.Key+\" \"+p.Value);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        Map<String,Integer> freq=new TreeMap<>();\n        while(sc.hasNext())\n        {\n            String x=sc.next();\n            freq.put(x, freq.getOrDefault(x,0)+1);\n        }\n        for(String k:freq.keySet()) System.out.println(k+\" \"+freq.get(k));\n    }\n}",
    },
    # Task 79: Объединение двух словарей
    "task_079": {
        "pascal": "var s:string;\n  i:integer;\n  count: array['a'..'z'] of integer;\nbegin\n  readln(s);\n  for i:=1 to length(s) do\n    if (s[i]>='a') and (s[i]<='z') then count[s[i]]:=count[s[i]]+1;\n  writeln(count['a']);\nend.",
        "python": "data =\ninput().split()freq = {}\nfor item in data:\n    freq[item] = freq.get(item, 0) + 1\n    for key in sorted(freq):\n        print(key, freq[key])",
        "cpp": "#include <iostream>\n#include <map>\n#include <string>\nint main()\n{\n    std::map<std::string,int> freq;\n    std::string x;\n    while(std::cin>>x) freq[x]++;\n    for(auto &p:freq) std::cout<<p.first<<' '<<p.second<<' ';\n}",
        "csharp": "using System;\nusing System.Collections.Generic;\n\nclass Program\n{\n    static void Main()\n    {\n        var freq=new Dictionary<string,int>();\n        foreach(var x in Console.ReadLine().Split())\n        {\n            freq[x]=freq.ContainsKey(x)?freq[x]+1:1;\n        }\n        foreach(var p in freq) Console.WriteLine(p.Key+\" \"+p.Value);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        Map<String,Integer> freq=new TreeMap<>();\n        while(sc.hasNext())\n        {\n            String x=sc.next();\n            freq.put(x, freq.getOrDefault(x,0)+1);\n        }\n        for(String k:freq.keySet()) System.out.println(k+\" \"+freq.get(k));\n    }\n}",
    },
    # Task 80: Итоговая: анализ текста через словарь
    "task_080": {
        "pascal": "var s:string;\n  i:integer;\n  count: array['a'..'z'] of integer;\nbegin\n  readln(s);\n  for i:=1 to length(s) do\n    if (s[i]>='a') and (s[i]<='z') then count[s[i]]:=count[s[i]]+1;\n  writeln(count['a']);\nend.",
        "python": "data =\ninput().split()freq = {}\nfor item in data:\n    freq[item] = freq.get(item, 0) + 1\n    for key in sorted(freq):\n        print(key, freq[key])",
        "cpp": "#include <iostream>\n#include <map>\n#include <string>\nint main()\n{\n    std::map<std::string,int> freq;\n    std::string x;\n    while(std::cin>>x) freq[x]++;\n    for(auto &p:freq) std::cout<<p.first<<' '<<p.second<<' ';\n}",
        "csharp": "using System;\nusing System.Collections.Generic;\n\nclass Program\n{\n    static void Main()\n    {\n        var freq=new Dictionary<string,int>();\n        foreach(var x in Console.ReadLine().Split())\n        {\n            freq[x]=freq.ContainsKey(x)?freq[x]+1:1;\n        }\n        foreach(var p in freq) Console.WriteLine(p.Key+\" \"+p.Value);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        Map<String,Integer> freq=new TreeMap<>();\n        while(sc.hasNext())\n        {\n            String x=sc.next();\n            freq.put(x, freq.getOrDefault(x,0)+1);\n        }\n        for(String k:freq.keySet()) System.out.println(k+\" \"+freq.get(k));\n    }\n}",
    },
    # Task 81: Чтение чисел из файла
    "task_081": {
        "pascal": "var f:text;\n  x,total:integer;\nbegin\n  assign(f,'input.txt');\n  reset(f);\n  to tal:=0;\n  while not eof(f) do\nbegin\n  readln(f,x);\n  total:=total+x;\n  end;\n  close(f);\n  writeln(total);\nend.",
        "python": "with open('input.txt')\nas f:\n    lines = f.readlines()\n    print(len(lines))",
        "cpp": "#include <fstream>\n#include <iostream>\nint main(){std::ifstream f(\"input.txt\"); std::string line; int count=0\n; while(std::getline(f,line)) count++; std::cout<<count;}",
        "csharp": "using System;\nusing System.IO;\n\nclass Program\n{\n    static void Main()\n    {\n        Console.WriteLine(File.ReadAllLines(\" input.txt\").Length);\n    }\n}",
        "java": "import java.nio.file.*;\n\nclass Main\n{\n    public static void main(String[] args) throws Exception\n    {\n        Sys tem.out.println(Files.readAllLines(Path.of(\"input.txt\")).size());\n    }\n}",
    },
    # Task 82: Подсчёт строк файла
    "task_082": {
        "pascal": "var f:text;\n  x,total:integer;\nbegin\n  assign(f,'input.txt');\n  reset(f);\n  total:=0;\n  while not eof(f) do\nbegin\n  readln(f,x);\n  total:=total+x;\n  end;\n  close(f);\n  writeln(total);\nend.",
        "python": "with open('input.txt')\nas f:\n    lines = f.readlines()\n    print(len(lines))",
        "cpp": "#include <fstream>\n#include <iostream>\nint main()\n{\n    std::ifstream f(\"input.txt\");\n    std::string line;\n    int count=0;\n    while(std::getline(f,line)) count++;\n    std::cout<<count;\n}",
        "csharp": "using System;\nusing System.IO;\n\nclass Program\n{\n    static void Main()\n    {\n        Console.WriteLine(File.ReadAllLines(\"input.txt\").Length);\n    }\n}",
        "java": "import java.nio.file.*;\n\nclass Main\n{\n    public static void main(String[] args) throws Exception\n    {\n        System.out.println(Files.readAllLines(Path.of(\"input.txt\")).size());\n    }\n}",
    },
    # Task 83: Анализ CSV
    "task_083": {
        "pascal": "var f:text;\n  x,total:integer;\nbegin\n  assign(f,'input.txt');\n  reset(f);\n  total:=0;\n  while not eof(f) do\nbegin\n  readln(f,x);\n  total:=total+x;\n  end;\n  close(f);\n  writeln(total);\nend.",
        "python": "with open('input.txt')\nas f:\n    lines = f.readlines()\n    print(len(lines))",
        "cpp": "#include <fstream>\n#include <iostream>\nint main()\n{\n    std::ifstream f(\"input.txt\");\n    std::string line;\n    int count=0;\n    while(std::getline(f,line)) count++;\n    std::cout<<count;\n}",
        "csharp": "using System;\nusing System.IO;\n\nclass Program\n{\n    static void Main()\n    {\n        Console.WriteLine(File.ReadAllLines(\"input.txt\").Length);\n    }\n}",
        "java": "import java.nio.file.*;\n\nclass Main\n{\n    public static void main(String[] args) throws Exception\n    {\n        System.out.println(Files.readAllLines(Path.of(\"input.txt\")).size());\n    }\n}",
    },
    # Task 84: Запись отчёта
    "task_084": {
        "pascal": "var f:text;\n  x,total:integer;\nbegin\n  assign(f,'input.txt');\n  reset(f);\n  total:=0;\n  while not eof(f) do\nbegin\n  readln(f,x);\n  total:=total+x;\n  end;\n  close(f);\n  writeln(total);\nend.",
        "python": "with open('input.txt')\nas f:\n    lines = f.readlines()\n    print(len(lines))",
        "cpp": "#include <fstream>\n#include <iostream>\nint main()\n{\n    std::ifstream f(\"input.txt\");\n    std::string line;\n    int count=0;\n    while(std::getline(f,line)) count++;\n    std::cout<<count;\n}",
        "csharp": "using System;\nusing System.IO;\n\nclass Program\n{\n    static void Main()\n    {\n        Console.WriteLine(File.ReadAllLines(\"input.txt\").Length);\n    }\n}",
        "java": "import java.nio.file.*;\n\nclass Main\n{\n    public static void main(String[] args) throws Exception\n    {\n        System.out.println(Files.readAllLines(Path.of(\"input.txt\")).size());\n    }\n}",
    },
    # Task 85: Логирование событий
    "task_085": {
        "pascal": "var f:text;\n  x,total:integer;\nbegin\n  assign(f,'input.txt');\n  reset(f);\n  to tal:=0;\n  while not eof(f) do\nbegin\n  readln(f,x);\n  total:=total+x;\n  end;\n  close(f);\n  writeln(total);\nend.",
        "python": "with open('input.txt')\nas f:\n    lines = f.readlines()\n    print(len(lines))",
        "cpp": "#include <fstream>\n#include <iostream>\nint main(){std::ifstream f(\"input.txt\"); std::string line; int count=0\n; while(std::getline(f,line)) count++; std::cout<<count;}",
        "csharp": "using System;\nusing System.IO;\n\nclass Program\n{\n    static void Main()\n    {\n        Console.WriteLine(File.ReadAllLines(\" input.txt\").Length);\n    }\n}",
        "java": "import java.nio.file.*;\n\nclass Main\n{\n    public static void main(String[] args) throws Exception\n    {\n        Sys tem.out.println(Files.readAllLines(Path.of(\"input.txt\")).size());\n    }\n}",
    },
    # Task 86: Модуль сортировок
    "task_086": {
        "pascal": "var f:text;\n  x,total:integer;\nbegin\n  assign(f,'input.txt');\n  reset(f);\n  total:=0;\n  while not eof(f) do\nbegin\n  readln(f,x);\n  total:=total+x;\n  end;\n  close(f);\n  writeln(total);\nend.",
        "python": "with open('input.txt')\nas f:\n    lines = f.readlines()\n    print(len(lines))",
        "cpp": "#include <fstream>\n#include <iostream>\nint main()\n{\n    std::ifstream f(\"input.txt\");\n    std::string line;\n    int count=0;\n    while(std::getline(f,line)) count++;\n    std::cout<<count;\n}",
        "csharp": "using System;\nusing System.IO;\n\nclass Program\n{\n    static void Main()\n    {\n        Console.WriteLine(File.ReadAllLines(\"input.txt\").Length);\n    }\n}",
        "java": "import java.nio.file.*;\n\nclass Main\n{\n    public static void main(String[] args) throws Exception\n    {\n        System.out.println(Files.readAllLines(Path.of(\"input.txt\")).size());\n    }\n}",
    },
    # Task 87: Конфликт имён в модулях
    "task_087": {
        "pascal": "var f:text;\n  x,total:integer;\nbegin\n  assign(f,'input.txt');\n  reset(f);\n  total:=0;\n  while not eof(f) do\nbegin\n  readln(f,x);\n  total:=total+x;\n  end;\n  close(f);\n  writeln(total);\nend.",
        "python": "with open('input.txt')\nas f:\n    lines = f.readlines()\n    print(len(lines))",
        "cpp": "#include <fstream>\n#include <iostream>\nint main()\n{\n    std::ifstream f(\"input.txt\");\n    std::string line;\n    int count=0;\n    while(std::getline(f,line)) count++;\n    std::cout<<count;\n}",
        "csharp": "using System;\nusing System.IO;\n\nclass Program\n{\n    static void Main()\n    {\n        Console.WriteLine(File.ReadAllLines(\"input.txt\").Length);\n    }\n}",
        "java": "import java.nio.file.*;\n\nclass Main\n{\n    public static void main(String[] args) throws Exception\n    {\n        System.out.println(Files.readAllLines(Path.of(\"input.txt\")).size());\n    }\n}",
    },
    # Task 88: Итоговая: обработчик логов
    "task_088": {
        "pascal": "var f:text;\n  x,total:integer;\nbegin\n  assign(f,'input.txt');\n  reset(f);\n  total:=0;\n  while not eof(f) do\nbegin\n  readln(f,x);\n  total:=total+x;\n  end;\n  close(f);\n  writeln(total);\nend.",
        "python": "with open('input.txt')\nas f:\n    lines = f.readlines()\n    print(len(lines))",
        "cpp": "#include <fstream>\n#include <iostream>\nint main()\n{\n    std::ifstream f(\"input.txt\");\n    std::string line;\n    int count=0;\n    while(std::getline(f,line)) count++;\n    std::cout<<count;\n}",
        "csharp": "using System;\nusing System.IO;\n\nclass Program\n{\n    static void Main()\n    {\n        Console.WriteLine(File.ReadAllLines(\"input.txt\").Length);\n    }\n}",
        "java": "import java.nio.file.*;\n\nclass Main\n{\n    public static void main(String[] args) throws Exception\n    {\n        System.out.println(Files.readAllLines(Path.of(\"input.txt\")).size());\n    }\n}",
    },
    # Task 89: Проверка скобок
    "task_089": {
        "pascal": "var s:string;\n  i,top:integer;\n  st:array[1..100] of char;\n  ok:boolean;\n  beg in\n  readln(s);\n  top:=0;\n  ok:=true;\n  for i:=1 to length(s) do\nbegin\n  if s[i]='(' then\nbegin\n  top:=top+1;\n  st[top]:='(';\n  end;\n  if s[i]=')' then\n  if top=0 then ok:=false\nelse top:=top-1;\n  end;\n  if ok and (top=0) then\n  writeln('ok')\n  else\n  writeln('bad');\nend.",
        "python": "stack = []\nfor ch in\ninput():\n    if ch == '(':\n        stack.append(ch)\n        el\n        if ch == ')':\n            if not stack:\n                print('bad');\n                break stack.pop()\n        else:\n            print('ok'\n            if not stack\n            else 'bad')",
        "cpp": "#include <iostream>\n#include <stack>\nint main(){std::string s; std::cin>>s; std::stack<char> st; bool ok=tr\nue; for(char c:s){if(c=='(') st.push(c); if(c==')'){if(st.empty()) ok=false; else st.pop();}} std::cout<<(ok&&st.empty()?\"ok\":\"bad\");}",
        "csharp": "using System;\nusing System.Collections.Generic;\n\nclass Program\n{\n    static void Main()\n    {\n        var st=new Stack<char>();\n        bool ok=tru e;\n        foreach(char c in Console.ReadLine())\n        {\n            if(c=='(') st.Push(c); if(c==')')\n            {\n                if(st.Count==0) ok=false;\n                else st.Pop();\n            }\n        }\n        Console.WriteLine(ok&&st.Count==0?\"ok\":\"bad\");\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scann er(System.in);\n        Stack<Character> st=new Stack<>();\n        boolean ok=true;\n        for(char c:sc.next().toCharArray())\n        {\n            if(c=='(') st.push(c); if(c==')')\n            {\n                if(st.empty()) ok=false;\n                else st.pop();\n            }\n        }\n        System.out.println(ok&&st.empty()?\"ok\":\"bad\");\n    }\n}",
    },
    # Task 90: История браузера
    "task_090": {
        "pascal": "var s:string;\n  i,top:integer;\n  st:array[1..100] of char;\n  ok:boolean;\nbegin\n  readln(s);\n  top:=0;\n  ok:=true;\n  for i:=1 to length(s) do\nbegin\n  if s[i]=')' then\n  if top=0 then ok:=false:=top+1;\n  st[top]:='(';\n  end;\n  if s[i]=')' then\n  if top=0 then ok:=false\nelse top:=top-1;\n  end;\n  if ok and (top=0) then\n  writeln('ok')\n  else\n  writeln('bad');\nend.",
        "python": "stack = []\nfor ch in\ninput():\n    if цикл по данным:\n        stack.append(ch)\n        el\n        if ch == ')':\n            if not stack:\n                print('bad');\n                break stack.pop()\n        else:\n            print('ok'\n            if not stack\n            else 'bad')",
        "cpp": "#include <iostream>\n#include <stack>\nint main()\n{\n    std::string s;\n    std::cin>>s;\n    std::stack<char> st;\n    bool ok=true;\n    for(char c:s)\n    {\n        if(c=='(') st.push(c); if(c==')')\n        {\n            if(st.empty()) ok=false;\n            else st.pop();\n        }\n    }\n    std::cout<<(ok&&st.empty()?\"ok\":\"bad\");\n}",
        "csharp": "using System;\nusing System.Collections.Generic;\n\nclass Program\n{\n    static void Main()\n    {\n        var st=new Stack<char>();\n        bool ok=true;\n        foreach(char c in Console.ReadLine())\n        {\n            if(c=='(') st.Push(c); if(c==')')\n            {\n                if(st.Count==0) ok=false;\n                else st.Pop();\n            }\n        }\n        Console.WriteLine(ok&&st.Count==0?\"ok\":\"bad\");\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        Stack<Character> st=new Stack<>();\n        boolean ok=true;\n        for(char c:sc.next().toCharArray())\n        {\n            if(c=='(') st.push(c); if(c==')')\n            {\n                if(st.empty()) ok=false;\n                else st.pop();\n            }\n        }\n        System.out.println(ok&&st.empty()?\"ok\":\"bad\");\n    }\n}",
    },
    # Task 91: Очередь задач
    "task_091": {
        "pascal": "var s:string;\n  i,top:integer;\n  st:array[1..100] of char;\n  ok:boolean;\nbegin\n  readln(s);\n  top:=0;\n  ok:=true;\n  for i:=1 to length(s) do\nbegin\n  if s[i]='(' then\nbegin\n  top:=top+1;\n  st[top]:='(';\n  end;\n  if s[i]=')' then\n  if top=0 then ok:=false\nelse top:=top-1;\n  end;\n  if ok and (top=0) then\n  writeln('ok')\n  else\n  writeln('bad');\nend.",
        "python": "stack = []\nfor ch in\ninput():\n    if ch == '(':\n        stack.append(ch)\n        el\n        if ch == ')':\n            if not stack:\n                print('bad');\n                break stack.pop()\n        else:\n            print('ok'\n            if not stack\n            else 'bad')",
        "cpp": "#include <iostream>\n#include <stack>\nint main()\n{\n    std::string s;\n    std::cin>>s;\n    std::stack<char> st;\n    bool ok=true;\n    for(char c:s)\n    {\n        if(c=='(') st.push(c); if(c==')')\n        {\n            if(st.empty()) ok=false;\n            else st.pop();\n        }\n    }\n    std::cout<<(ok&&st.empty()?\"ok\":\"bad\");\n}",
        "csharp": "using System;\nusing System.Collections.Generic;\n\nclass Program\n{\n    static void Main()\n    {\n        var st=new Stack<char>();\n        bool ok=true;\n        foreach(char c in Console.ReadLine())\n        {\n            if(c=='(') st.Push(c); if(c==')')\n            {\n                if(st.Count==0) ok=false;\n                else st.Pop();\n            }\n        }\n        Console.WriteLine(ok&&st.Count==0?\"ok\":\"bad\");\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        Stack<Character> st=new Stack<>();\n        boolean ok=true;\n        for(char c:sc.next().toCharArray())\n        {\n            if(c=='(') st.push(c); if(c==')')\n            {\n                if(st.empty()) ok=false;\n                else st.pop();\n            }\n        }\n        System.out.println(ok&&st.empty()?\"ok\":\"bad\");\n    }\n}",
    },
    # Task 92: Отмена действий
    "task_092": {
        "pascal": "var s:string;\n  i,top:integer;\n  st:array[1..100] of char;\n  ok:boolean;\nbegin\n  readln(s);\n  top:=0;\n  ok:=true;\n  for i:=1 to length(s) do\nbegin\n  if s[i]='(' then\nbegin\n  top:=top+1;\n  st[top]:='(';\n  end;\n  if s[i]=')' then\n  if top=0 then ok:=false\nelse top:=top-1;\n  end;\n  if ok and (top=0) then\n  writeln('ok')\n  else\n  writeln('bad');\nend.",
        "python": "stack = []\nfor ch in\ninput():\n    if ch == '(':\n        stack.append(ch)\n        el\n        if ch == ')':\n            if not stack:\n                print('bad');\n                break stack.pop()\n        else:\n            print('ok'\n            if not stack\n            else 'bad')",
        "cpp": "#include <iostream>\n#include <stack>\nint main()\n{\n    std::string s;\n    std::cin>>s;\n    std::stack<char> st;\n    bool ok=true;\n    for(char c:s)\n    {\n        if(c=='(') st.push(c); if(c==')')\n        {\n            if(st.empty()) ok=false;\n            else st.pop();\n        }\n    }\n    std::cout<<(ok&&st.empty()?\"ok\":\"bad\");\n}",
        "csharp": "using System;\nusing System.Collections.Generic;\n\nclass Program\n{\n    static void Main()\n    {\n        var st=new Stack<char>();\n        bool ok=true;\n        foreach(char c in Console.ReadLine())\n        {\n            if(c=='(') st.Push(c); if(c==')')\n            {\n                if(st.Count==0) ok=false;\n                else st.Pop();\n            }\n        }\n        Console.WriteLine(ok&&st.Count==0?\"ok\":\"bad\");\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        Stack<Character> st=new Stack<>();\n        boolean ok=true;\n        for(char c:sc.next().toCharArray())\n        {\n            if(c=='(') st.push(c); if(c==')')\n            {\n                if(st.empty()) ok=false;\n                else st.pop();\n            }\n        }\n        System.out.println(ok&&st.empty()?\"ok\":\"bad\");\n    }\n}",
    },
    # Task 93: Очередь печати
    "task_093": {
        "pascal": "var s:string;\n  i,top:integer;\n  st:array[1..100] of char;\n  ok:boolean;\n  beg in\n  readln(s);\n  top:=0;\n  ok:=true;\n  for i:=1 to length(s) do\nbegin\n  if s[i]='(' then\nbegin\n  top:=top+1;\n  st[top]:='(';\n  end;\n  if s[i]=')' then\n  if top=0 then ok:=false\nelse top:=top-1;\n  end;\n  if ok and (top=0) then\n  writeln('ok')\n  else\n  writeln('bad');\nend.",
        "python": "stack = []\nfor ch in\ninput():\n    if ch == '(':\n        stack.append(ch)\n        el\n        if ch == ')':\n            if not stack:\n                print('bad');\n                break stack.pop()\n        else:\n            print('ok'\n            if not stack\n            else 'bad')",
        "cpp": "#include <iostream>\n#include <stack>\nint main(){std::string s; std::cin>>s; std::stack<char> st; bool ok=tr\nue; for(char c:s){if(c=='(') st.push(c); if(c==')'){if(st.empty()) ok=false; else st.pop();}} std::cout<<(ok&&st.empty()?\"ok\":\"bad\");}",
        "csharp": "using System;\nusing System.Collections.Generic;\n\nclass Program\n{\n    static void Main()\n    {\n        var st=new Stack<char>();\n        bool ok=tru e;\n        foreach(char c in Console.ReadLine())\n        {\n            if(c=='(') st.Push(c); if(c==')')\n            {\n                if(st.Count==0) ok=false;\n                else st.Pop();\n            }\n        }\n        Console.WriteLine(ok&&st.Count==0?\"ok\":\"bad\");\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scann er(System.in);\n        Stack<Character> st=new Stack<>();\n        boolean ok=true;\n        for(char c:sc.next().toCharArray())\n        {\n            if(c=='(') st.push(c); if(c==')')\n            {\n                if(st.empty()) ok=false;\n                else st.pop();\n            }\n        }\n        System.out.println(ok&&st.empty()?\"ok\":\"bad\");\n    }\n}",
    },
    # Task 94: BFS через очередь
    "task_094": {
        "pascal": "var s:string;\n  i,top:integer;\n  st:array[1..100] of char;\n  ok:boolean;\nbegin\n  readln(s);\n  top:=0;\n  ok:=true;\n  for i:=1 to length(s) do\nbegin\n  if s[i]=')' then\n  if top=0 then ok:=false:=top+1;\n  st[top]:='(';\n  end;\n  if s[i]=')' then\n  if top=0 then ok:=false\nelse top:=top-1;\n  end;\n  if ok and (top=0) then\n  writeln('ok')\n  else\n  writeln('bad');\nend.",
        "python": "stack = []\nfor ch in\ninput():\n    if цикл по данным:\n        stack.append(ch)\n        el\n        if ch == ')':\n            if not stack:\n                print('bad');\n                break stack.pop()\n        else:\n            print('ok'\n            if not stack\n            else 'bad')",
        "cpp": "#include <iostream>\n#include <stack>\nint main()\n{\n    std::string s;\n    std::cin>>s;\n    std::stack<char> st;\n    bool ok=true;\n    for(char c:s)\n    {\n        if(c=='(') st.push(c); if(c==')')\n        {\n            if(st.empty()) ok=false;\n            else st.pop();\n        }\n    }\n    std::cout<<(ok&&st.empty()?\"ok\":\"bad\");\n}",
        "csharp": "using System;\nusing System.Collections.Generic;\n\nclass Program\n{\n    static void Main()\n    {\n        var st=new Stack<char>();\n        bool ok=true;\n        foreach(char c in Console.ReadLine())\n        {\n            if(c=='(') st.Push(c); if(c==')')\n            {\n                if(st.Count==0) ok=false;\n                else st.Pop();\n            }\n        }\n        Console.WriteLine(ok&&st.Count==0?\"ok\":\"bad\");\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        Stack<Character> st=new Stack<>();\n        boolean ok=true;\n        for(char c:sc.next().toCharArray())\n        {\n            if(c=='(') st.push(c); if(c==')')\n            {\n                if(st.empty()) ok=false;\n                else st.pop();\n            }\n        }\n        System.out.println(ok&&st.empty()?\"ok\":\"bad\");\n    }\n}",
    },
    # Task 95: Калькулятор выражений
    "task_095": {
        "pascal": "var s:string;\n  i,top:integer;\n  st:array[1..100] of char;\n  ok:boolean;\nbegin\n  readln(s);\n  top:=0;\n  ok:=true;\n  for i:=1 to length(s) do\nbegin\n  if s[i]='(' then\nbegin\n  top:=top+1;\n  st[top]:='(';\n  end;\n  if s[i]=')' then\n  if top=0 then ok:=false\nelse top:=top-1;\n  end;\n  if ok and (top=0) then\n  writeln('ok')\n  else\n  writeln('bad');\nend.",
        "python": "stack = []\nfor ch in\ninput():\n    if ch == '(':\n        stack.append(ch)\n        el\n        if ch == ')':\n            if not stack:\n                print('bad');\n                break stack.pop()\n        else:\n            print('ok'\n            if not stack\n            else 'bad')",
        "cpp": "#include <iostream>\n#include <stack>\nint main()\n{\n    std::string s;\n    std::cin>>s;\n    std::stack<char> st;\n    bool ok=true;\n    for(char c:s)\n    {\n        if(c=='(') st.push(c); if(c==')')\n        {\n            if(st.empty()) ok=false;\n            else st.pop();\n        }\n    }\n    std::cout<<(ok&&st.empty()?\"ok\":\"bad\");\n}",
        "csharp": "using System;\nusing System.Collections.Generic;\n\nclass Program\n{\n    static void Main()\n    {\n        var st=new Stack<char>();\n        bool ok=true;\n        foreach(char c in Console.ReadLine())\n        {\n            if(c=='(') st.Push(c); if(c==')')\n            {\n                if(st.Count==0) ok=false;\n                else st.Pop();\n            }\n        }\n        Console.WriteLine(ok&&st.Count==0?\"ok\":\"bad\");\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        Stack<Character> st=new Stack<>();\n        boolean ok=true;\n        for(char c:sc.next().toCharArray())\n        {\n            if(c=='(') st.push(c); if(c==')')\n            {\n                if(st.empty()) ok=false;\n                else st.pop();\n            }\n        }\n        System.out.println(ok&&st.empty()?\"ok\":\"bad\");\n    }\n}",
    },
    # Task 96: Итоговая: обработчик команд
    "task_096": {
        "pascal": "var s:string;\n  i,top:integer;\n  st:array[1..100] of char;\n  ok:boolean;\nbegin\n  readln(s);\n  top:=0;\n  ok:=true;\n  for i:=1 to length(s) do\nbegin\n  if s[i]='(' then\nbegin\n  top:=top+1;\n  st[top]:='(';\n  end;\n  if s[i]=')' then\n  if top=0 then ok:=false\nelse top:=top-1;\n  end;\n  if ok and (top=0) then\n  writeln('ok')\n  else\n  writeln('bad');\nend.",
        "python": "stack = []\nfor ch in\ninput():\n    if ch == '(':\n        stack.append(ch)\n        el\n        if ch == ')':\n            if not stack:\n                print('bad');\n                break stack.pop()\n        else:\n            print('ok'\n            if not stack\n            else 'bad')",
        "cpp": "#include <iostream>\n#include <stack>\nint main()\n{\n    std::string s;\n    std::cin>>s;\n    std::stack<char> st;\n    bool ok=true;\n    for(char c:s)\n    {\n        if(c=='(') st.push(c); if(c==')')\n        {\n            if(st.empty()) ok=false;\n            else st.pop();\n        }\n    }\n    std::cout<<(ok&&st.empty()?\"ok\":\"bad\");\n}",
        "csharp": "using System;\nusing System.Collections.Generic;\n\nclass Program\n{\n    static void Main()\n    {\n        var st=new Stack<char>();\n        bool ok=true;\n        foreach(char c in Console.ReadLine())\n        {\n            if(c=='(') st.Push(c); if(c==')')\n            {\n                if(st.Count==0) ok=false;\n                else st.Pop();\n            }\n        }\n        Console.WriteLine(ok&&st.Count==0?\"ok\":\"bad\");\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        Stack<Character> st=new Stack<>();\n        boolean ok=true;\n        for(char c:sc.next().toCharArray())\n        {\n            if(c=='(') st.push(c); if(c==')')\n            {\n                if(st.empty()) ok=false;\n                else st.pop();\n            }\n        }\n        System.out.println(ok&&st.empty()?\"ok\":\"bad\");\n    }\n}",
    },
    # Task 97: Создание узла
    "task_097": {
        "pascal": "type PNode=^TNode;\n  TNode=record value:integer;\n  next:PNode;\n  end;\nvar he ad:PNode;\nbegin\n  new(head);\n  head^.value:=10;\n  writeln(head^.value);\nend.",
        "python": "class Node:\n    def __init__(self, value):\n        self.value = value self.next = None head = Node(10)\n        print(head.value)",
        "cpp": "#include <iostream>\nstruct Node\n{\n    int value;\n    Node* next;\n}\nint main()\n{\n    Node head\n    {\n        10,nullptr\n    }\n    std::cout<<head.value;\n}",
        "csharp": "using System;\n\nclass Node\n{\n    public int Value;\n    public Node Next;\n    public Node(int value)\n    {\n        Value=value;\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        Node head=new Node(10);\n        Console.WriteLine(head.Value);\n    }\n}",
        "java": "class Node\n{\n    int value;\n    Node next;\n    Node(int value)\n    {\n        this.value=value;\n    }\n}\nc lass Main\n{\n    public static void main(String[] args)\n    {\n        Node head=new Node(10);\n        System.out.println(head.value);\n    }\n}",
    },
    # Task 98: Добавление в начало
    "task_098": {
        "pascal": "type PNode=^TNode;\n  TNode=record value:integer;\n  next:PNode;\n  end;\nvar head:PNode;\nbegin\n  new(head);\n  head^.value:=10;\n  writeln(head^.value);\nend.",
        "python": "class Node:\n    def __init__(self, value):\n        self.value = value self.next = Nonehead = Node(10)\n        print(head.value)",
        "cpp": "#include <iostream>\nstruct Node\n{\n    int value;\n    Node* next;\n}\nint main()\n{\n    Node head\n    {\n        10,nullptr\n    }\n    std::cout<<head.value;\n}",
        "csharp": "using System;\n\nclass Node\n{\n    public int Value;\n    public Node Next;\n    public Node(int value)\n    {\n        Value=value;\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        Node head=new Node(10);\n        Console.WriteLine(head.Value);\n    }\n}",
        "java": "class Node\n{\n    int value;\n    Node next;\n    Node(int value)\n    {\n        this.value=value;\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Node head=new Node(10);\n        System.out.println(head.value);\n    }\n}",
    },
    # Task 99: Добавление в конец
    "task_099": {
        "pascal": "type PNode=^TNode;\n  TNode=record value:integer;\n  next:PNode;\n  end;\nvar head:PNode;\nbegin\n  new(head);\n  head^.value:=10;\n  writeln(head^.value);\nend.",
        "python": "class Node:\n    def __init__(self, value):\n        self.value = value self.next = Nonehead = Node(10)\n        print(head.value)",
        "cpp": "#include <iostream>\nstruct Node\n{\n    int value;\n    Node* next;\n}\nint main()\n{\n    Node head\n    {\n        10,nullptr\n    }\n    std::cout<<head.value;\n}",
        "csharp": "using System;\n\nclass Node\n{\n    public int Value;\n    public Node Next;\n    public Node(int value)\n    {\n        Value=value;\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        Node head=new Node(10);\n        Console.WriteLine(head.Value);\n    }\n}",
        "java": "class Node\n{\n    int value;\n    Node next;\n    Node(int value)\n    {\n        this.value=value;\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Node head=new Node(10);\n        System.out.println(head.value);\n    }\n}",
    },
    # Task 100: Поиск узла
    "task_100": {
        "pascal": "type PNode=^TNode;\n  TNode=record value:integer;\n  next:PNode;\n  end;\nvar head:PNode;\nbegin\n  new(head);\n  head^.value:=10;\n  writeln(head^.value);\nend.",
        "python": "class Node:\n    def __init__(self, value):\n        self.value = value self.next = Nonehead = Node(10)\n        print(head.value)",
        "cpp": "#include <iostream>\nstruct Node\n{\n    int value;\n    Node* next;\n}\nint main()\n{\n    Node head\n    {\n        10,nullptr\n    }\n    std::cout<<head.value;\n}",
        "csharp": "using System;\n\nclass Node\n{\n    public int Value;\n    public Node Next;\n    public Node(int value)\n    {\n        Value=value;\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        Node head=new Node(10);\n        Console.WriteLine(head.Value);\n    }\n}",
        "java": "class Node\n{\n    int value;\n    Node next;\n    Node(int value)\n    {\n        this.value=value;\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Node head=new Node(10);\n        System.out.println(head.value);\n    }\n}",
    },
    # Task 101: Удаление узла
    "task_101": {
        "pascal": "type PNode=^TNode;\n  TNode=record value:integer;\n  next:PNode;\n  end;\nvar he ad:PNode;\nbegin\n  new(head);\n  head^.value:=10;\n  writeln(head^.value);\nend.",
        "python": "class Node:\n    def __init__(self, value):\n        self.value = value self.next = None head = Node(10)\n        print(head.value)",
        "cpp": "#include <iostream>\nstruct Node\n{\n    int value;\n    Node* next;\n}\nint main()\n{\n    Node head\n    {\n        10,nullptr\n    }\n    std::cout<<head.value;\n}",
        "csharp": "using System;\n\nclass Node\n{\n    public int Value;\n    public Node Next;\n    public Node(int value)\n    {\n        Value=value;\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        Node head=new Node(10);\n        Console.WriteLine(head.Value);\n    }\n}",
        "java": "class Node\n{\n    int value;\n    Node next;\n    Node(int value)\n    {\n        this.value=value;\n    }\n}\nc lass Main\n{\n    public static void main(String[] args)\n    {\n        Node head=new Node(10);\n        System.out.println(head.value);\n    }\n}",
    },
    # Task 102: Разворот списка
    "task_102": {
        "pascal": "type PNode=^TNode;\n  TNode=record value:integer;\n  next:PNode;\n  end;\nvar head:PNode;\nbegin\n  new(head);\n  head^.value:=10;\n  writeln(head^.value);\nend.",
        "python": "class Node:\n    def __init__(self, value):\n        self.value = value self.next = Nonehead = Node(10)\n        print(head.value)",
        "cpp": "#include <iostream>\nstruct Node\n{\n    int value;\n    Node* next;\n}\nint main()\n{\n    Node head\n    {\n        10,nullptr\n    }\n    std::cout<<head.value;\n}",
        "csharp": "using System;\n\nclass Node\n{\n    public int Value;\n    public Node Next;\n    public Node(int value)\n    {\n        Value=value;\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        Node head=new Node(10);\n        Console.WriteLine(head.Value);\n    }\n}",
        "java": "class Node\n{\n    int value;\n    Node next;\n    Node(int value)\n    {\n        this.value=value;\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Node head=new Node(10);\n        System.out.println(head.value);\n    }\n}",
    },
    # Task 103: Слияние двух списков
    "task_103": {
        "pascal": "type PNode=^TNode;\n  TNode=record value:integer;\n  next:PNode;\n  end;\nvar head:PNode;\nbegin\n  new(head);\n  head^.value:=10;\n  writeln(head^.value);\nend.",
        "python": "class Node:\n    def __init__(self, value):\n        self.value = value self.next = Nonehead = Node(10)\n        print(head.value)",
        "cpp": "#include <iostream>\nstruct Node\n{\n    int value;\n    Node* next;\n}\nint main()\n{\n    Node head\n    {\n        10,nullptr\n    }\n    std::cout<<head.value;\n}",
        "csharp": "using System;\n\nclass Node\n{\n    public int Value;\n    public Node Next;\n    public Node(int value)\n    {\n        Value=value;\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        Node head=new Node(10);\n        Console.WriteLine(head.Value);\n    }\n}",
        "java": "class Node\n{\n    int value;\n    Node next;\n    Node(int value)\n    {\n        this.value=value;\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Node head=new Node(10);\n        System.out.println(head.value);\n    }\n}",
    },
    # Task 104: Итоговая: плейлист
    "task_104": {
        "pascal": "type PNode=^TNode;\n  TNode=record value:integer;\n  next:PNode;\n  end;\nvar head:PNode;\nbegin\n  new(head);\n  head^.value:=10;\n  writeln(head^.value);\nend.",
        "python": "class Node:\n    def __init__(self, value):\n        self.value = value self.next = Nonehead = Node(10)\n        print(head.value)",
        "cpp": "#include <iostream>\nstruct Node\n{\n    int value;\n    Node* next;\n}\nint main()\n{\n    Node head\n    {\n        10,nullptr\n    }\n    std::cout<<head.value;\n}",
        "csharp": "using System;\n\nclass Node\n{\n    public int Value;\n    public Node Next;\n    public Node(int value)\n    {\n        Value=value;\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        Node head=new Node(10);\n        Console.WriteLine(head.Value);\n    }\n}",
        "java": "class Node\n{\n    int value;\n    Node next;\n    Node(int value)\n    {\n        this.value=value;\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Node head=new Node(10);\n        System.out.println(head.value);\n    }\n}",
    },
    # Task 105: Создание дерева
    "task_105": {
        "pascal": "type PNode=^TNode;\n  TNode=record value:integer;\n  next:PNode;\n  end;\nvar he ad:PNode;\nbegin\n  new(head);\n  head^.value:=10;\n  writeln(head^.value);\nend.",
        "python": "class Node:\n    def __init__(self, value):\n        self.value = value self.next = None head = Node(10)\n        print(head.value)",
        "cpp": "#include <iostream>\nstruct Node\n{\n    int value;\n    Node* next;\n}\nint main()\n{\n    Node head\n    {\n        10,nullptr\n    }\n    std::cout<<head.value;\n}",
        "csharp": "using System;\n\nclass Node\n{\n    public int Value;\n    public Node Next;\n    public Node(int value)\n    {\n        Value=value;\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        Node head=new Node(10);\n        Console.WriteLine(head.Value);\n    }\n}",
        "java": "class Node\n{\n    int value;\n    Node next;\n    Node(int value)\n    {\n        this.value=value;\n    }\n}\nc lass Main\n{\n    public static void main(String[] args)\n    {\n        Node head=new Node(10);\n        System.out.println(head.value);\n    }\n}",
    },
    # Task 106: DFS дерева
    "task_106": {
        "pascal": "type PNode=^TNode;\n  TNode=record value:integer;\n  next:PNode;\n  end;\nvar head:PNode;\nbegin\n  new(head);\n  head^.value:=10;\n  writeln(head^.value);\nend.",
        "python": "class Node:\n    def __init__(self, value):\n        self.value = value self.next = Nonehead = Node(10)\n        print(head.value)",
        "cpp": "#include <iostream>\nstruct Node\n{\n    int value;\n    Node* next;\n}\nint main()\n{\n    Node head\n    {\n        10,nullptr\n    }\n    std::cout<<head.value;\n}",
        "csharp": "using System;\n\nclass Node\n{\n    public int Value;\n    public Node Next;\n    public Node(int value)\n    {\n        Value=value;\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        Node head=new Node(10);\n        Console.WriteLine(head.Value);\n    }\n}",
        "java": "class Node\n{\n    int value;\n    Node next;\n    Node(int value)\n    {\n        this.value=value;\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Node head=new Node(10);\n        System.out.println(head.value);\n    }\n}",
    },
    # Task 107: BFS дерева
    "task_107": {
        "pascal": "type PNode=^TNode;\n  TNode=record value:integer;\n  next:PNode;\n  end;\nvar head:PNode;\nbegin\n  new(head);\n  head^.value:=10;\n  writeln(head^.value);\nend.",
        "python": "class Node:\n    def __init__(self, value):\n        self.value = value self.next = Nonehead = Node(10)\n        print(head.value)",
        "cpp": "#include <iostream>\nstruct Node\n{\n    int value;\n    Node* next;\n}\nint main()\n{\n    Node head\n    {\n        10,nullptr\n    }\n    std::cout<<head.value;\n}",
        "csharp": "using System;\n\nclass Node\n{\n    public int Value;\n    public Node Next;\n    public Node(int value)\n    {\n        Value=value;\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        Node head=new Node(10);\n        Console.WriteLine(head.Value);\n    }\n}",
        "java": "class Node\n{\n    int value;\n    Node next;\n    Node(int value)\n    {\n        this.value=value;\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Node head=new Node(10);\n        System.out.println(head.value);\n    }\n}",
    },
    # Task 108: Поиск узла дерева
    "task_108": {
        "pascal": "type PNode=^TNode;\n  TNode=record value:integer;\n  next:PNode;\n  end;\nvar head:PNode;\nbegin\n  new(head);\n  head^.value:=10;\n  writeln(head^.value);\nend.",
        "python": "class Node:\n    def __init__(self, value):\n        self.value = value self.next = Nonehead = Node(10)\n        print(head.value)",
        "cpp": "#include <iostream>\nstruct Node\n{\n    int value;\n    Node* next;\n}\nint main()\n{\n    Node head\n    {\n        10,nullptr\n    }\n    std::cout<<head.value;\n}",
        "csharp": "using System;\n\nclass Node\n{\n    public int Value;\n    public Node Next;\n    public Node(int value)\n    {\n        Value=value;\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        Node head=new Node(10);\n        Console.WriteLine(head.Value);\n    }\n}",
        "java": "class Node\n{\n    int value;\n    Node next;\n    Node(int value)\n    {\n        this.value=value;\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Node head=new Node(10);\n        System.out.println(head.value);\n    }\n}",
    },
    # Task 109: Представление графа
    "task_109": {
        "pascal": "var s:string;\n  i:integer;\n  count: array['a'..'z'] of integer;\nbegin\n  read ln(s);\n  for i:=1 to length(s) do\n    if (s[i]>='a') and (s[i]<='z') then count[s[i]]:=count[s[i]]+1;\n  writeln(count['a']);\nend.",
        "python": "data =\ninput().split()\nfreq = {}\nfor item in data:\n    freq[item] = freq.get(item, 0) + 1\n    for key in sorted(freq):\n        print(key, freq[key])",
        "cpp": "#include <iostream>\n#include <map>\n#include <string>\nint main(){std::map<std::string,int> freq; std::string x; while(std::c\nin>>x) freq[x]++; for(auto &p:freq) std::cout<<p.first<<' '<<p.second<<' ';}",
        "csharp": "using System;\nusing System.Collections.Generic;\n\nclass Program\n{\n    static void Main()\n    {\n        var freq=new Dictionary<string,int>();\n        foreach(var x in Console.ReadLine().Split())\n        {\n            freq[x]=freq.ContainsKey(x)?freq[x]+1:1;\n        }\n        foreach(var p in freq) Console.WriteLine(p.Key+\" \"+p.Value);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scann er(System.in);\n        Map<String,Integer> freq=new TreeMap<>();\n        while(sc.hasNext())\n        {\n            String x=sc.next();\n            freq.put(x, freq.getOrDefault(x,0)+1);\n        }\n        for(String k:freq.keySet()) System.out.println(k+\" \"+freq.get(k));\n    }\n}",
    },
    # Task 110: DFS графа
    "task_110": {
        "pascal": "var s:string;\n  i:integer;\n  count: array['a'..'z'] of integer;\nbegin\n  readln(s);\n  for i:=1 to length(s) do\n    if ((((цикл по данным) and (s[i]<='z') then count[s[i]]:=count[s[i]]+1) and (s[i]<='z') then count[s[i]]:=count[s[i]]+1) and (s[i]<='z') then count[s[i]]:=count[s[i]]+1) and (s[i]<='z') then count[s[i]]:=count[s[i]]+1;\n  writeln(count['a']);\nend.",
        "python": "data =\ninput().split()freq = {}\nfor item in data:\n    freq[item] = freq.get(item, 0) + 1\n    for key in sorted(freq):\n        print(key, freq[key])",
        "cpp": "#include <iostream>\n#include <map>\n#include <string>\nint main()\n{\n    std::map<std::string,int> freq;\n    std::string x;\n    while(std::cin>>x) freq[x]++;\n    for(auto &p:freq) std::cout<<p.first<<' '<<p.second<<' ';\n}",
        "csharp": "using System;\nusing System.Collections.Generic;\n\nclass Program\n{\n    static void Main()\n    {\n        var freq=new Dictionary<string,int>();\n        foreach(var x in Console.ReadLine().Split())\n        {\n            freq[x]=freq.ContainsKey(x)?freq[x]+1:1;\n        }\n        foreach(var p in freq) Console.WriteLine(p.Key+\" \"+p.Value);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        Map<String,Integer> freq=new TreeMap<>();\n        while(sc.hasNext())\n        {\n            String x=sc.next();\n            freq.put(x, freq.getOrDefault(x,0)+1);\n        }\n        for(String k:freq.keySet()) System.out.println(k+\" \"+freq.get(k));\n    }\n}",
    },
    # Task 111: BFS графа
    "task_111": {
        "pascal": "var s:string;\n  i:integer;\n  count: array['a'..'z'] of integer;\nbegin\n  readln(s);\n  for i:=1 to length(s) do\n    if (s[i]>='a') and (s[i]<='z') then count[s[i]]:=count[s[i]]+1;\n  writeln(count['a']);\nend.",
        "python": "data =\ninput().split()freq = {}\nfor item in data:\n    freq[item] = freq.get(item, 0) + 1\n    for key in sorted(freq):\n        print(key, freq[key])",
        "cpp": "#include <iostream>\n#include <map>\n#include <string>\nint main()\n{\n    std::map<std::string,int> freq;\n    std::string x;\n    while(std::cin>>x) freq[x]++;\n    for(auto &p:freq) std::cout<<p.first<<' '<<p.second<<' ';\n}",
        "csharp": "using System;\nusing System.Collections.Generic;\n\nclass Program\n{\n    static void Main()\n    {\n        var freq=new Dictionary<string,int>();\n        foreach(var x in Console.ReadLine().Split())\n        {\n            freq[x]=freq.ContainsKey(x)?freq[x]+1:1;\n        }\n        foreach(var p in freq) Console.WriteLine(p.Key+\" \"+p.Value);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        Map<String,Integer> freq=new TreeMap<>();\n        while(sc.hasNext())\n        {\n            String x=sc.next();\n            freq.put(x, freq.getOrDefault(x,0)+1);\n        }\n        for(String k:freq.keySet()) System.out.println(k+\" \"+freq.get(k));\n    }\n}",
    },
    # Task 112: Итоговая: поиск пути на карте
    "task_112": {
        "pascal": "var s:string;\n  i:integer;\n  count: array['a'..'z'] of integer;\nbegin\n  readln(s);\n  for i:=1 to length(s) do\n    if (s[i]>='a') and (s[i]<='z') then count[s[i]]:=count[s[i]]+1;\n  writeln(count['a']);\nend.",
        "python": "data =\ninput().split()freq = {}\nfor item in data:\n    freq[item] = freq.get(item, 0) + 1\n    for key in sorted(freq):\n        print(key, freq[key])",
        "cpp": "#include <iostream>\n#include <map>\n#include <string>\nint main()\n{\n    std::map<std::string,int> freq;\n    std::string x;\n    while(std::cin>>x) freq[x]++;\n    for(auto &p:freq) std::cout<<p.first<<' '<<p.second<<' ';\n}",
        "csharp": "using System;\nusing System.Collections.Generic;\n\nclass Program\n{\n    static void Main()\n    {\n        var freq=new Dictionary<string,int>();\n        foreach(var x in Console.ReadLine().Split())\n        {\n            freq[x]=freq.ContainsKey(x)?freq[x]+1:1;\n        }\n        foreach(var p in freq) Console.WriteLine(p.Key+\" \"+p.Value);\n    }\n}",
        "java": "import java.util.*;\n\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Scanner sc=new Scanner(System.in);\n        Map<String,Integer> freq=new TreeMap<>();\n        while(sc.hasNext())\n        {\n            String x=sc.next();\n            freq.put(x, freq.getOrDefault(x,0)+1);\n        }\n        for(String k:freq.keySet()) System.out.println(k+\" \"+freq.get(k));\n    }\n}",
    },
    # Task 113: Класс User
    "task_113": {
        "pascal": "type TUser = class name:string;\n  constructor Create(n:string);\n  procedur e Print;\n  end;\n  constructor TUser.Create(n:string);\nbegin\n  name:=n;\n  end;\n  procedure TUser.Print;\nbegin\n  writeln(name);\n  end;\nvar u:TUser;\nbegin\n  u:=TUser.Create('Alex');\n  u.Print;\nend.",
        "python": "class User:\n    def __init__(self, name):\n        self.name = name\n        def print_name(self):\n            print(self.name)\n            u = User('Alex')\n            u.print_name()",
        "cpp": "#include <iostream>\n#include <string>\nclass User{std::string name; public: User(std::string n):name(n){} voi\nd print(){std::cout<<name;}}; int main(){User u(\"Alex\"); u.print();}",
        "csharp": "using System;\n\nclass User\n{\n    string name;\n    public User(string n)\n    {\n        name=n;\n    }\n    public void Pri nt()\n    {\n        Console.WriteLine(name);\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        User u=new User(\"Alex\");\n        u.Print();\n    }\n}",
        "java": "class User\n{\n    String name;\n    User(String n)\n    {\n        name=n;\n    }\n    void print()\n    {\n        System.ou t.println(name);\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        User u=new User(\"Alex\");\n        u.print();\n    }\n}",
    },
    # Task 114: Банковский счёт
    "task_114": {
        "pascal": "type TUser = class name:string;\n  constructor Create(n:string);\n  procedure Print;\n  end;\n  constructor TUser.Create(n:string);\nbegin\n  name:=n;\n  end;\n  procedure TUser.Print;\nbegin\n  writeln(name);\n  end;\nvar u:TUser;\nbegin\n  u:=TUser.Create('Alex');\n  u.Print;\nend.",
        "python": "class User:\n    def __init__(self, name):\n        self.name = name\n        def print_name(self):\n            print(self.name)u = User('Alex')u.print_name()",
        "cpp": "#include <iostream>\n#include <string>\nclass User\n{\n    std::string name;\n    public: User(std::string n):name(n)\n    {\n    }\n    void print()\n    {\n        std::cout<<name;\n    }\n}\nint main()\n{\n    User u(\"Alex\");\n    u. print();\n}",
        "csharp": "using System;\n\nclass User\n{\n    string name;\n    public User(string n)\n    {\n        name=n;\n    }\n    public void Print()\n    {\n        Console.WriteLine(name);\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        User u=new User(\"Alex\");\n        u. Print();\n    }\n}",
        "java": "class User\n{\n    String name;\n    User(String n)\n    {\n        name=n;\n    }\n    void print()\n    {\n        System.out.println(name);\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        User u=new User(\"Alex\");\n        u. print();\n    }\n}",
    },
    # Task 115: Класс Product
    "task_115": {
        "pascal": "type TUser = class name:string;\n  constructor Create(n:string);\n  procedure Print;\n  end;\n  constructor TUser.Create(n:string);\nbegin\n  name:=n;\n  end;\n  procedure TUser.Print;\nbegin\n  writeln(name);\n  end;\nvar u:TUser;\nbegin\n  u:=TUser.Create('Alex');\n  u.Print;\nend.",
        "python": "class User:\n    def __init__(self, name):\n        self.name = name\n        def print_name(self):\n            print(self.name)u = User('Alex')u.print_name()",
        "cpp": "#include <iostream>\n#include <string>\nclass User\n{\n    std::string name;\n    public: User(std::string n):name(n)\n    {\n    }\n    void print()\n    {\n        std::cout<<name;\n    }\n}\nint main()\n{\n    User u(\"Alex\");\n    u.print();\n}",
        "csharp": "using System;\n\nclass User\n{\n    string name;\n    public User(string n)\n    {\n        name=n;\n    }\n    public void Print()\n    {\n        Console.WriteLine(name);\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        User u=new User(\"Alex\");\n        u.Print();\n    }\n}",
        "java": "class User\n{\n    String name;\n    User(String n)\n    {\n        name=n;\n    }\n    void print()\n    {\n        System.out.println(name);\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        User u=new User(\"Alex\");\n        u.print();\n    }\n}",
    },
    # Task 116: Ошибка в методе объекта
    "task_116": {
        "pascal": "type TUser = class name:string;\n  constructor Create(n:string);\n  procedure Print;\n  end;\n  constructor TUser.Create(n:string);\nbegin\n  name:=n;\n  end;\n  procedure TUser.Print;\nbegin\n  writeln(name);\n  end;\nvar u:TUser;\nbegin\n  u:=TUser.Create('Alex');\n  u.Print;\nend.",
        "python": "class User:\n    def __init__(self, name):\n        self.name = name\n        def print_name(self):\n            print(self.name)u = User('Alex')u.print_name()",
        "cpp": "#include <iostream>\n#include <string>\nclass User\n{\n    std::string name;\n    public: User(std::string n):name(n)\n    {\n    }\n    void print()\n    {\n        std::cout<<name;\n    }\n}\nint main()\n{\n    User u(\"Alex\");\n    u.print();\n}",
        "csharp": "using System;\n\nclass User\n{\n    string name;\n    public User(string n)\n    {\n        name=n;\n    }\n    public void Print()\n    {\n        Console.WriteLine(name);\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        User u=new User(\"Alex\");\n        u.Print();\n    }\n}",
        "java": "class User\n{\n    String name;\n    User(String n)\n    {\n        name=n;\n    }\n    void print()\n    {\n        System.out.println(name);\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        User u=new User(\"Alex\");\n        u.print();\n    }\n}",
    },
    # Task 117: Каталог книг
    "task_117": {
        "pascal": "type TUser = class name:string;\n  constructor Create(n:string);\n  procedur e Print;\n  end;\n  constructor TUser.Create(n:string);\nbegin\n  name:=n;\n  end;\n  procedure TUser.Print;\nbegin\n  writeln(name);\n  end;\nvar u:TUser;\nbegin\n  u:=TUser.Create('Alex');\n  u.Print;\nend.",
        "python": "class User:\n    def __init__(self, name):\n        self.name = name\n        def print_name(self):\n            print(self.name)\n            u = User('Alex')\n            u.print_name()",
        "cpp": "#include <iostream>\n#include <string>\nclass User{std::string name; public: User(std::string n):name(n){} voi\nd print(){std::cout<<name;}}; int main(){User u(\"Alex\"); u.print();}",
        "csharp": "using System;\n\nclass User\n{\n    string name;\n    public User(string n)\n    {\n        name=n;\n    }\n    public void Pri nt()\n    {\n        Console.WriteLine(name);\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        User u=new User(\"Alex\");\n        u.Print();\n    }\n}",
        "java": "class User\n{\n    String name;\n    User(String n)\n    {\n        name=n;\n    }\n    void print()\n    {\n        System.ou t.println(name);\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        User u=new User(\"Alex\");\n        u.print();\n    }\n}",
    },
    # Task 118: Заказ и список товаров
    "task_118": {
        "pascal": "type TUser = class name:string;\n  constructor Create(n:string);\n  procedure Print;\n  end;\n  constructor TUser.Create(n:string);\nbegin\n  name:=n;\n  end;\n  procedure TUser.Print;\nbegin\n  writeln(name);\n  end;\nvar u:TUser;\nbegin\n  u:=TUser.Create('Alex');\n  u.Print;\nend.",
        "python": "class User:\n    def __init__(self, name):\n        self.name = name\n        def print_name(self):\n            print(self.name)u = User('Alex')u.print_name()",
        "cpp": "#include <iostream>\n#include <string>\nclass User\n{\n    std::string name;\n    public: User(std::string n):name(n)\n    {\n    }\n    void print()\n    {\n        std::cout<<name;\n    }\n}\nint main()\n{\n    User u(\"Alex\");\n    u. print();\n}",
        "csharp": "using System;\n\nclass User\n{\n    string name;\n    public User(string n)\n    {\n        name=n;\n    }\n    public void Print()\n    {\n        Console.WriteLine(name);\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        User u=new User(\"Alex\");\n        u. Print();\n    }\n}",
        "java": "class User\n{\n    String name;\n    User(String n)\n    {\n        name=n;\n    }\n    void print()\n    {\n        System.out.println(name);\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        User u=new User(\"Alex\");\n        u. print();\n    }\n}",
    },
    # Task 119: Вызов методов объектов
    "task_119": {
        "pascal": "type TUser = class name:string;\n  constructor Create(n:string);\n  procedure Print;\n  end;\n  constructor TUser.Create(n:string);\nbegin\n  name:=n;\n  end;\n  procedure TUser.Print;\nbegin\n  writeln(name);\n  end;\nvar u:TUser;\nbegin\n  u:=TUser.Create('Alex');\n  u.Print;\nend.",
        "python": "class User:\n    def __init__(self, name):\n        self.name = name\n        def print_name(self):\n            print(self.name)u = User('Alex')u.print_name()",
        "cpp": "#include <iostream>\n#include <string>\nclass User\n{\n    std::string name;\n    public: User(std::string n):name(n)\n    {\n    }\n    void print()\n    {\n        std::cout<<name;\n    }\n}\nint main()\n{\n    User u(\"Alex\");\n    u.print();\n}",
        "csharp": "using System;\n\nclass User\n{\n    string name;\n    public User(string n)\n    {\n        name=n;\n    }\n    public void Print()\n    {\n        Console.WriteLine(name);\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        User u=new User(\"Alex\");\n        u.Print();\n    }\n}",
        "java": "class User\n{\n    String name;\n    User(String n)\n    {\n        name=n;\n    }\n    void print()\n    {\n        System.out.println(name);\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        User u=new User(\"Alex\");\n        u.print();\n    }\n}",
    },
    # Task 120: Итоговая: мини-CRM
    "task_120": {
        "pascal": "type TUser = class name:string;\n  constructor Create(n:string);\n  procedure Print;\n  end;\n  constructor TUser.Create(n:string);\nbegin\n  name:=n;\n  end;\n  procedure TUser.Print;\nbegin\n  writeln(name);\n  end;\nvar u:TUser;\nbegin\n  u:=TUser.Create('Alex');\n  u.Print;\nend.",
        "python": "class User:\n    def __init__(self, name):\n        self.name = name\n        def print_name(self):\n            print(self.name)u = User('Alex')u.print_name()",
        "cpp": "#include <iostream>\n#include <string>\nclass User\n{\n    std::string name;\n    public: User(std::string n):name(n)\n    {\n    }\n    void print()\n    {\n        std::cout<<name;\n    }\n}\nint main()\n{\n    User u(\"Alex\");\n    u.print();\n}",
        "csharp": "using System;\n\nclass User\n{\n    string name;\n    public User(string n)\n    {\n        name=n;\n    }\n    public void Print()\n    {\n        Console.WriteLine(name);\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        User u=new User(\"Alex\");\n        u.Print();\n    }\n}",
        "java": "class User\n{\n    String name;\n    User(String n)\n    {\n        name=n;\n    }\n    void print()\n    {\n        System.out.println(name);\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        User u=new User(\"Alex\");\n        u.print();\n    }\n}",
    },
    # Task 121: Базовый класс Animal
    "task_121": {
        "pascal": "type TAnimal = class procedure Speak;\n  virtual;\n  end;\n  procedure TAnimal. Speak;\nbegin\n  writeln('sound');\n  end;\nvar a:TAnimal;\nbegin\n  a:=TAnimal.Create;\n  a.Speak;\nend.",
        "python": "class Animal:\n    def speak(self):\n        return 'sound'\n    class Dog(Animal):\n        def speak(self):\n            return 'woof' pet = Dog()\n        print(pet.speak())",
        "cpp": "#include <iostream>\nclass Animal\n{\n    public: virtual void speak()\n    {\n        std::cout<<\"sound\";\n    }\n}\nclass Dog: public Animal\n{\n    public: void speak() override\n    {\n        std::cout<<\"woof\";\n    }\n}\nint main()\n{\n    Dog d;\n    d.speak();\n}",
        "csharp": "using System;\n\nclass Animal\n{\n    public virtual string Speak()\n    {\n        return \"sound\";\n    }\n}\nclass Dog :Animal\n{\n    public override string Speak()\n    {\n        return \"woof\";\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        Animal a=new Dog();\n        Console.WriteLine(a.Speak());\n    }\n}",
        "java": "class Animal\n{\n    String speak()\n    {\n        return \"sound\";\n    }\n}\nclass Dog extends Animal\n{\n    String speak()\n    {\n        return \"woof\";\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Animal a=new Dog();\n        System.out.println(a.speak());\n    }\n}",
    },
    # Task 122: Иерархия транспорта
    "task_122": {
        "pascal": "type TAnimal = class procedure Speak;\n  virtual;\n  end;\n  procedure TAnimal.Speak;\nbegin\n  writeln('sound');\n  end;\nvar a:TAnimal;\nbegin\n  a:=TAnimal.Create;\n  a.Speak;\nend.",
        "python": "class Animal:\n    def speak(self):\n        return 'sound'\n    class Dog(Animal):\n        def speak(self):\n            return 'woof'pet = Dog()\n        print(pet.speak())",
        "cpp": "#include <iostream>\nclass Animal\n{\n    public: virtual void speak()\n    {\n        std::cout<<\"sound\";\n    }\n}\nclass Dog: public Animal\n{\n    public: void speak() override\n    {\n        std::cout<<\"woof\";\n    }\n}\nint main()\n{\n    Dog d;\n    d.speak();\n}",
        "csharp": "using System;\n\nclass Animal\n{\n    public virtual string Speak()\n    {\n        return \"sound\";\n    }\n}\nclass Dog:Animal\n{\n    public override string Speak()\n    {\n        return \"woof\";\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        Animal a=new Dog();\n        Console.WriteLine(a.Speak());\n    }\n}",
        "java": "class Animal\n{\n    String speak()\n    {\n        return \"sound\";\n    }\n}\nclass Dog extends Animal\n{\n    String speak()\n    {\n        return \"woof\";\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Animal a=new Dog();\n        System.out.println(a.speak());\n    }\n}",
    },
    # Task 123: Сотрудники разных типов
    "task_123": {
        "pascal": "type TAnimal = class procedure Speak;\n  virtual;\n  end;\n  procedure TAnimal.Speak;\nbegin\n  writeln('sound');\n  end;\nvar a:TAnimal;\nbegin\n  a:=TAnimal.Create;\n  a.Speak;\nend.",
        "python": "class Animal:\n    def speak(self):\n        return 'sound'\n    class Dog(Animal):\n        def speak(self):\n            return 'woof'pet = Dog()\n        print(pet.speak())",
        "cpp": "#include <iostream>\nclass Animal\n{\n    public: virtual void speak()\n    {\n        std::cout<<\"sound\";\n    }\n}\nclass Dog: public Animal\n{\n    public: void speak() override\n    {\n        std::cout<<\"woof\";\n    }\n}\nint main()\n{\n    Dog d;\n    d.speak();\n}",
        "csharp": "using System;\n\nclass Animal\n{\n    public virtual string Speak()\n    {\n        return \"sound\";\n    }\n}\nclass Dog:Animal\n{\n    public override string Speak()\n    {\n        return \"woof\";\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        Animal a=new Dog();\n        Console.WriteLine(a.Speak());\n    }\n}",
        "java": "class Animal\n{\n    String speak()\n    {\n        return \"sound\";\n    }\n}\nclass Dog extends Animal\n{\n    String speak()\n    {\n        return \"woof\";\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Animal a=new Dog();\n        System.out.println(a.speak());\n    }\n}",
    },
    # Task 124: Ошибка переопределения метода
    "task_124": {
        "pascal": "type TAnimal = class procedure Speak;\n  virtual;\n  end;\n  procedure TAnimal.Speak;\nbegin\n  writeln('sound');\n  end;\nvar a:TAnimal;\nbegin\n  a:=TAnimal.Create;\n  a.Speak;\nend.",
        "python": "class Animal:\n    def speak(self):\n        return 'sound'\n    class Dog(Animal):\n        def speak(self):\n            return 'woof'pet = Dog()\n        print(pet.speak())",
        "cpp": "#include <iostream>\nclass Animal\n{\n    public: virtual void speak()\n    {\n        std::cout<<\"sound\";\n    }\n}\nclass Dog: public Animal\n{\n    public: void speak() override\n    {\n        std::cout<<\"woof\";\n    }\n}\nint main()\n{\n    Dog d;\n    d.speak();\n}",
        "csharp": "using System;\n\nclass Animal\n{\n    public virtual string Speak()\n    {\n        return \"sound\";\n    }\n}\nclass Dog:Animal\n{\n    public override string Speak()\n    {\n        return \"woof\";\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        Animal a=new Dog();\n        Console.WriteLine(a.Speak());\n    }\n}",
        "java": "class Animal\n{\n    String speak()\n    {\n        return \"sound\";\n    }\n}\nclass Dog extends Animal\n{\n    String speak()\n    {\n        return \"woof\";\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Animal a=new Dog();\n        System.out.println(a.speak());\n    }\n}",
    },
    # Task 125: Полиморфный список объектов
    "task_125": {
        "pascal": "type TAnimal = class procedure Speak;\n  virtual;\n  end;\n  procedure TAnimal. Speak;\nbegin\n  writeln('sound');\n  end;\nvar a:TAnimal;\nbegin\n  a:=TAnimal.Create;\n  a.Speak;\nend.",
        "python": "class Animal:\n    def speak(self):\n        return 'sound'\n    class Dog(Animal):\n        def speak(self):\n            return 'woof' pet = Dog()\n        print(pet.speak())",
        "cpp": "#include <iostream>\nclass Animal\n{\n    public: virtual void speak()\n    {\n        std::cout<<\"sound\";\n    }\n}\nclass Dog: public Animal\n{\n    public: void speak() override\n    {\n        std::cout<<\"woof\";\n    }\n}\nint main()\n{\n    Dog d;\n    d.speak();\n}",
        "csharp": "using System;\n\nclass Animal\n{\n    public virtual string Speak()\n    {\n        return \"sound\";\n    }\n}\nclass Dog :Animal\n{\n    public override string Speak()\n    {\n        return \"woof\";\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        Animal a=new Dog();\n        Console.WriteLine(a.Speak());\n    }\n}",
        "java": "class Animal\n{\n    String speak()\n    {\n        return \"sound\";\n    }\n}\nclass Dog extends Animal\n{\n    String speak()\n    {\n        return \"woof\";\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Animal a=new Dog();\n        System.out.println(a.speak());\n    }\n}",
    },
    # Task 126: Интерфейс/абстрактный тип
    "task_126": {
        "pascal": "type TAnimal = class procedure Speak;\n  virtual;\n  end;\n  procedure TAnimal.Speak;\nbegin\n  writeln('sound');\n  end;\nvar a:TAnimal;\nbegin\n  a:=TAnimal.Create;\n  a.Speak;\nend.",
        "python": "class Animal:\n    def speak(self):\n        return 'sound'\n    class Dog(Animal):\n        def speak(self):\n            return 'woof'pet = Dog()\n        print(pet.speak())",
        "cpp": "#include <iostream>\nclass Animal\n{\n    public: virtual void speak()\n    {\n        std::cout<<\"sound\";\n    }\n}\nclass Dog: public Animal\n{\n    public: void speak() override\n    {\n        std::cout<<\"woof\";\n    }\n}\nint main()\n{\n    Dog d;\n    d.speak();\n}",
        "csharp": "using System;\n\nclass Animal\n{\n    public virtual string Speak()\n    {\n        return \"sound\";\n    }\n}\nclass Dog:Animal\n{\n    public override string Speak()\n    {\n        return \"woof\";\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        Animal a=new Dog();\n        Console.WriteLine(a.Speak());\n    }\n}",
        "java": "class Animal\n{\n    String speak()\n    {\n        return \"sound\";\n    }\n}\nclass Dog extends Animal\n{\n    String speak()\n    {\n        return \"woof\";\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Animal a=new Dog();\n        System.out.println(a.speak());\n    }\n}",
    },
    # Task 127: Геометрические фигуры
    "task_127": {
        "pascal": "type TAnimal = class procedure Speak;\n  virtual;\n  end;\n  procedure TAnimal.Speak;\nbegin\n  writeln('sound');\n  end;\nvar a:TAnimal;\nbegin\n  a:=TAnimal.Create;\n  a.Speak;\nend.",
        "python": "class Animal:\n    def speak(self):\n        return 'sound'\n    class Dog(Animal):\n        def speak(self):\n            return 'woof'pet = Dog()\n        print(pet.speak())",
        "cpp": "#include <iostream>\nclass Animal\n{\n    public: virtual void speak()\n    {\n        std::cout<<\"sound\";\n    }\n}\nclass Dog: public Animal\n{\n    public: void speak() override\n    {\n        std::cout<<\"woof\";\n    }\n}\nint main()\n{\n    Dog d;\n    d.speak();\n}",
        "csharp": "using System;\n\nclass Animal\n{\n    public virtual string Speak()\n    {\n        return \"sound\";\n    }\n}\nclass Dog:Animal\n{\n    public override string Speak()\n    {\n        return \"woof\";\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        Animal a=new Dog();\n        Console.WriteLine(a.Speak());\n    }\n}",
        "java": "class Animal\n{\n    String speak()\n    {\n        return \"sound\";\n    }\n}\nclass Dog extends Animal\n{\n    String speak()\n    {\n        return \"woof\";\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Animal a=new Dog();\n        System.out.println(a.speak());\n    }\n}",
    },
    # Task 128: Финальная: система доставки
    "task_128": {
        "pascal": "type TAnimal = class procedure Speak;\n  virtual;\n  end;\n  procedure TAnimal.Speak;\nbegin\n  writeln('sound');\n  end;\nvar a:TAnimal;\nbegin\n  a:=TAnimal.Create;\n  a.Speak;\nend.",
        "python": "class Animal:\n    def speak(self):\n        return 'sound'\n    class Dog(Animal):\n        def speak(self):\n            return 'woof'pet = Dog()\n        print(pet.speak())",
        "cpp": "#include <iostream>\nclass Animal\n{\n    public: virtual void speak()\n    {\n        std::cout<<\"sound\";\n    }\n}\nclass Dog: public Animal\n{\n    public: void speak() override\n    {\n        std::cout<<\"woof\";\n    }\n}\nint main()\n{\n    Dog d;\n    d.speak();\n}",
        "csharp": "using System;\n\nclass Animal\n{\n    public virtual string Speak()\n    {\n        return \"sound\";\n    }\n}\nclass Dog:Animal\n{\n    public override string Speak()\n    {\n        return \"woof\";\n    }\n}\nclass Program\n{\n    static void Main()\n    {\n        Animal a=new Dog();\n        Console.WriteLine(a.Speak());\n    }\n}",
        "java": "class Animal\n{\n    String speak()\n    {\n        return \"sound\";\n    }\n}\nclass Dog extends Animal\n{\n    String speak()\n    {\n        return \"woof\";\n    }\n}\nclass Main\n{\n    public static void main(String[] args)\n    {\n        Animal a=new Dog();\n        System.out.println(a.speak());\n    }\n}",
    },
}


def get_reference_code(slot_id: str, language: str, *, pattern_key: str | None = None) -> str:
    """Get reference code for a slot and language."""
    import re

    from application.curriculum.content.v4_code_format import (
        format_reference_code,
        normalize_authoring_code,
    )
    from application.curriculum.content.v4_placeholder_reference import (
        get_placeholder_reference,
        is_placeholder_slot,
    )

    def _resolve_raw() -> str:
        if is_placeholder_slot(slot_id):
            return get_placeholder_reference(slot_id, language)

        pat = str(pattern_key or "").strip()
        if not pat:
            m = re.match(r"^(?:pas|py|cpp|cs|java)_(\d+)$", slot_id)
            if m:
                pat = f"task_{int(m.group(1)):03d}"
            else:
                pat = slot_id
        raw = _TASK_REFERENCE_CODE.get(pat, {}).get(language, "")
        if not raw:
            m2 = re.match(r"^task_(\d+)$", slot_id)
            if m2:
                pat = f"task_{int(m2.group(1)):03d}"
                raw = _TASK_REFERENCE_CODE.get(pat, {}).get(language, "")
        return str(raw or "")

    raw = _resolve_raw()
    if not raw:
        return ""
    if "\n" in raw or "\r" in raw:
        return normalize_authoring_code(raw)
    return format_reference_code(raw, language)
