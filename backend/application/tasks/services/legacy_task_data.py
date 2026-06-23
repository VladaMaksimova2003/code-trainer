from typing import Any

LEGACY_TASKS_DB: dict[int, dict[str, Any]] = {1: {'id': 1,
     'title': 'Sum of Numbers',
     'description': 'Напишите функцию, которая принимает N чисел и выводит их сумму.',
     'difficulty': 'easy',
     'type': 'algorithm',
     'solution_description': 'Считайте N, затем N чисел. Идите по массиву циклом, накопите сумму в переменной и '
                             'выведите результат.',
     'constructions': ['for_loop', 'binary_expression'],
     'test_cases': [{'inputs': '3\n1 2 3', 'output': '6'},
                    {'inputs': '2\n10 20', 'output': '30'},
                    {'inputs': '4\n-1 0 1 2', 'output': '2'}],
     'code_examples': {'cpp': '#include <iostream>\n'
                              'using namespace std;\n'
                              'int main() {\n'
                              '    int n; cin >> n;\n'
                              '    int sum = 0, x;\n'
                              '    for (int i = 0; i < n; i++) { cin >> x; sum += x; }\n'
                              '    cout << sum << endl;\n'
                              '    return 0;\n'
                              '}',
                       'python': 'n = int(input())\n'
                                 'nums = list(map(int, input().split()))\n'
                                 'total = 0\n'
                                 'for num in nums:\n'
                                 '    total += num\n'
                                 'print(total)'}},
 2: {'id': 2,
     'title': 'Max in Array',
     'description': 'Переведите код с C++ на Python. Найдите максимум из N чисел.',
     'difficulty': 'easy',
     'type': 'translation',
     'constructions': ['function_definition', 'for_loop', 'if_statement', 'return_statement'],
     'test_cases': [{'inputs': '3\n1 5 3', 'output': '5'},
                    {'inputs': '4\n-1 -5 -3 -2', 'output': '-1'},
                    {'inputs': '1\n42', 'output': '42'}],
     'code_examples': {'cpp': '#include <iostream>\n'
                              'using namespace std;\n'
                              'int main() {\n'
                              '    int n; cin >> n;\n'
                              '    int mx, x; cin >> mx;\n'
                              '    for (int i = 1; i < n; i++) {\n'
                              '        cin >> x;\n'
                              '        if (x > mx) mx = x;\n'
                              '    }\n'
                              '    cout << mx << endl;\n'
                              '    return 0;\n'
                              '}',
                       'python': 'n = int(input())\nnums = list(map(int, input().split()))\nprint(max(nums))'}},
 3: {'id': 3,
     'title': 'Fibonacci',
     'description': 'Вычислите N-е число Фибоначчи (0-индексация).',
     'difficulty': 'medium',
     'type': 'algorithm',
     'solution_description': 'Используйте базовые случаи n <= 1, иначе возвращайте сумму двух предыдущих значений. Для '
                             'больших n лучше перейти к итеративному решению.',
     'constructions': ['if_statement', 'return_statement'],
     'test_cases': [{'inputs': '0', 'output': '0'},
                    {'inputs': '1', 'output': '1'},
                    {'inputs': '7', 'output': '13'},
                    {'inputs': '10', 'output': '55'}],
     'code_examples': {'cpp': '#include <iostream>\n'
                              'using namespace std;\n'
                              'int fib(int n) {\n'
                              '    if (n <= 1) return n;\n'
                              '    return fib(n-1) + fib(n-2);\n'
                              '}\n'
                              'int main() {\n'
                              '    int n; cin >> n;\n'
                              '    cout << fib(n) << endl;\n'
                              '    return 0;\n'
                              '}',
                       'python': 'def fib(n):\n'
                                 '    if n <= 1:\n'
                                 '        return n\n'
                                 '    return fib(n-1) + fib(n-2)\n'
                                 '\n'
                                 'n = int(input())\n'
                                 'print(fib(n))'}},
 4: {'id': 4,
     'title': 'Код по блок-схеме: чётное / нечётное',
     'description': 'По блок-схеме напишите программу: ввод N, вывод Even или Odd.',
     'difficulty': 'easy',
     'type': 'blocks',
     'constructions': ['if_statement'],
     'test_cases': [{'inputs': '4', 'output': 'Even'},
                    {'inputs': '3', 'output': 'Odd'},
                    {'inputs': '0', 'output': 'Even'}],
     'code_examples': {'python': "n = int(input())\nif n % 2 == 0:\n    print('Even')\nelse:\n    print('Odd')",
                       'cpp': '#include <iostream>\n'
                              'using namespace std;\n'
                              'int main() {\n'
                              '    int n;\n'
                              '    cin >> n;\n'
                              '    if (n % 2 == 0)\n'
                              '        cout << "Even" << endl;\n'
                              '    else\n'
                              '        cout << "Odd" << endl;\n'
                              '    return 0;\n'
                              '}'},
     'flow_spec': {'allowed_blocks': ['start', 'input', 'decision', 'process', 'loop', 'output', 'end'],
                   'required_sequence': ['start', 'input', 'decision', 'output', 'output', 'end'],
                   'required_text_checks': [{'type': 'input', 'contains_any': ['n']},
                                            {'type': 'decision',
                                             'contains_any': ['mod 2 == 0', '% 2 == 0', 'n % 2 == 0']},
                                            {'type': 'output', 'contains_any': ['even']},
                                            {'type': 'output', 'contains_any': ['odd']}],
                   'student_reference_languages': ['cpp']}},
 5: {'id': 5,
     'title': 'Код по блок-схеме: таблица умножения',
     'description': 'По блок-схеме напишите программу: ввод N, таблица N×i для i от 1 до 10.',
     'difficulty': 'easy',
     'type': 'blocks',
     'constructions': ['for_loop'],
     'test_cases': [{'inputs': '2',
                     'output': '2 * 1 = 2\n'
                               '2 * 2 = 4\n'
                               '2 * 3 = 6\n'
                               '2 * 4 = 8\n'
                               '2 * 5 = 10\n'
                               '2 * 6 = 12\n'
                               '2 * 7 = 14\n'
                               '2 * 8 = 16\n'
                               '2 * 9 = 18\n'
                               '2 * 10 = 20'},
                    {'inputs': '3',
                     'output': '3 * 1 = 3\n'
                               '3 * 2 = 6\n'
                               '3 * 3 = 9\n'
                               '3 * 4 = 12\n'
                               '3 * 5 = 15\n'
                               '3 * 6 = 18\n'
                               '3 * 7 = 21\n'
                               '3 * 8 = 24\n'
                               '3 * 9 = 27\n'
                               '3 * 10 = 30'}],
     'code_examples': {'python': "n = int(input())\nfor i in range(1, 11):\n    print(f'{n} * {i} = {n * i}')"},
     'flow_spec': {'allowed_blocks': ['start', 'input', 'decision', 'process', 'loop', 'output', 'end'],
                   'required_sequence': ['start', 'input', 'process', 'decision', 'output', 'process', 'end'],
                   'required_text_checks': [{'type': 'input', 'contains_any': ['n']},
                                            {'type': 'process', 'contains_any': ['i = 1', 'i=1']},
                                            {'type': 'decision', 'contains_any': ['i <= 10', 'i≤10', 'i < 11']},
                                            {'type': 'output', 'contains_any': ['print', 'n * i', 'n*i']},
                                            {'type': 'process', 'contains_any': ['i = i + 1', 'i=i+1', 'i++']}]}},
 6: {'id': 6,
     'title': 'Код по блок-схеме: палиндром',
     'description': 'По блок-схеме напишите программу: проверка палиндрома без учёта регистра.',
     'difficulty': 'medium',
     'type': 'blocks',
     'constructions': ['if_statement'],
     'test_cases': [{'inputs': 'Level', 'output': 'Palindrome'},
                    {'inputs': 'hello', 'output': 'Not palindrome'},
                    {'inputs': 'aba', 'output': 'Palindrome'}],
     'code_examples': {'python': 's = input().strip()\n'
                                 'normalized = s.lower()\n'
                                 'if normalized == normalized[::-1]:\n'
                                 "    print('Palindrome')\n"
                                 'else:\n'
                                 "    print('Not palindrome')"},
     'flow_spec': {'allowed_blocks': ['start', 'input', 'decision', 'process', 'loop', 'output', 'end'],
                   'required_sequence': ['start',
                                         'input',
                                         'process',
                                         'process',
                                         'decision',
                                         'decision',
                                         'process',
                                         'process',
                                         'decision',
                                         'output',
                                         'output',
                                         'end'],
                   'required_text_checks': [{'type': 'input', 'contains_any': ['s', 'string', 'строк']},
                                            {'type': 'process', 'contains_any': ['tolower', 'lower', 'ниж']},
                                            {'type': 'process',
                                             'contains_any': ['left = 0', 'right = len', 'right=len']},
                                            {'type': 'decision', 'contains_any': ['left < right', 'left<right']},
                                            {'type': 'decision',
                                             'contains_any': ['s[left] == s[right]', 's[left]==s[right]']},
                                            {'type': 'process',
                                             'contains_any': ['ispalindrome = false', 'ispalindrome=false', 'false']},
                                            {'type': 'process',
                                             'contains_any': ['left++', 'right--', 'left = left + 1']},
                                            {'type': 'decision', 'contains_any': ['ispalindrome']},
                                            {'type': 'output', 'contains_any': ['palindrome']},
                                            {'type': 'output', 'contains_any': ['not palindrome', 'not']}]}},
 7: {'id': 7,
     'title': 'Код по блок-схеме: пузырьковая сортировка',
     'description': 'По блок-схеме напишите программу: сортировка массива, вывод после каждого прохода.',
     'difficulty': 'hard',
     'type': 'blocks',
     'constructions': ['nested_loops', 'if_statement'],
     'test_cases': [{'inputs': '3\n3 2 1', 'output': '2 1 3\n1 2 3'}, {'inputs': '2\n2 1', 'output': '1 2'}],
     'code_examples': {'python': 'n = int(input())\n'
                                 'arr = list(map(int, input().split()))\n'
                                 'for i in range(n - 1):\n'
                                 '    for j in range(0, n - 1 - i):\n'
                                 '        if arr[j] > arr[j + 1]:\n'
                                 '            arr[j], arr[j + 1] = arr[j + 1], arr[j]\n'
                                 '    print(*arr)'},
     'flow_spec': {'allowed_blocks': ['start', 'input', 'decision', 'process', 'loop', 'output', 'end'],
                   'required_sequence': ['start',
                                         'input',
                                         'input',
                                         'process',
                                         'decision',
                                         'process',
                                         'decision',
                                         'decision',
                                         'process',
                                         'process',
                                         'output',
                                         'process',
                                         'end'],
                   'required_text_checks': [{'type': 'input', 'contains_any': ['n']},
                                            {'type': 'input', 'contains_any': ['array', 'arr', 'a[]']},
                                            {'type': 'process', 'contains_any': ['i = 0', 'i=0']},
                                            {'type': 'decision', 'contains_any': ['i < n - 1', 'i<n-1', 'i < n-1']},
                                            {'type': 'process', 'contains_any': ['j = 0', 'j=0']},
                                            {'type': 'decision',
                                             'contains_any': ['j < n - i - 1', 'j<n-i-1', 'j < n-i-1']},
                                            {'type': 'decision',
                                             'contains_any': ['a[j] > a[j+1]', 'arr[j] > arr[j+1]', '>']},
                                            {'type': 'process', 'contains_any': ['swap', 'arr[j], arr[j+1]']},
                                            {'type': 'process', 'contains_any': ['j++', 'j = j + 1', 'j=j+1']},
                                            {'type': 'output', 'contains_any': ['print array', 'print', 'array']},
                                            {'type': 'process', 'contains_any': ['i++', 'i = i + 1', 'i=i+1']}]}},
 8: {'id': 8,
     'title': 'Perfect Grade Students',
     'description': 'В университете проводятся курсы программирования. Преподаватель хочет узнать, сколько студентов '
                    'сдали все контрольные работы на "отлично". Для этого ему дан список студентов с количеством '
                    'сданных контрольных работ и их оценками.',
     'difficulty': 'medium',
     'type': 'algorithm',
     'solution_description': 'Необходимо пройти по списку студентов, проверить у каждого студента количество '
                             'контрольных работ и оценки, определить, кто сдал все работы на отлично, и подсчитать '
                             'общее количество таких студентов.',
     'constructions': ['for_loop', 'if_statement', 'binary_expression'],
     'test_cases': [{'inputs': '3\n2 5 5\n3 5 5 5\n2 4 5', 'output': '2'},
                    {'inputs': '2\n4 5 5 5 5\n3 5 5 4', 'output': '1'},
                    {'inputs': '1\n1 5', 'output': '1'}],
     'code_examples': {'python': 'n = int(input())\n'
                                 'count = 0\n'
                                 'for i in range(n):\n'
                                 '    data = list(map(int, input().split()))\n'
                                 '    num_grades = data[0]\n'
                                 '    grades = data[1:]\n'
                                 '    all_perfect = True\n'
                                 '    for grade in grades:\n'
                                 '        if grade != 5:\n'
                                 '            all_perfect = False\n'
                                 '            break\n'
                                 '    if all_perfect:\n'
                                 '        count += 1\n'
                                 'print(count)',
                       'cpp': '#include <iostream>\n'
                              'using namespace std;\n'
                              'int main() {\n'
                              '    int n;\n'
                              '    cin >> n;\n'
                              '    int count = 0;\n'
                              '    for (int i = 0; i < n; i++) {\n'
                              '        int num_grades;\n'
                              '        cin >> num_grades;\n'
                              '        bool all_perfect = true;\n'
                              '        for (int j = 0; j < num_grades; j++) {\n'
                              '            int grade;\n'
                              '            cin >> grade;\n'
                              '            if (grade != 5) {\n'
                              '                all_perfect = false;\n'
                              '            }\n'
                              '        }\n'
                              '        if (all_perfect) {\n'
                              '            count++;\n'
                              '        }\n'
                              '    }\n'
                              '    cout << count << endl;\n'
                              '    return 0;\n'
                              '}'}}}
