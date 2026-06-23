/* Mock dataset for the entire prototype. Mutations stay in-memory. */
window.MOCK = (() => {
  const taskTypes = [
    { id: 'algorithm', label: 'Алгоритм' },
    { id: 'translation', label: 'Translation' },
    { id: 'diagram', label: 'Diagram' },
    { id: 'block_reorder', label: 'Block reorder' },
    { id: 'code_assembly', label: 'Code assembly' },
    { id: 'task_build_from_blocks', label: 'Build from blocks' },
    { id: 'blocks', label: 'Blocks (flowchart)' },
  ];
  const languages = ['Python', 'JavaScript', 'C++', 'Java', 'Go'];
  const patterns = ['Two pointers', 'Бинарный поиск', 'DP', 'Графы', 'Хеш-таблицы', 'Рекурсия', 'Жадные', 'Сортировки'];
  const difficulties = ['Лёгкая', 'Средняя', 'Сложная'];

  const tasks = [
    { id: 1,  title: 'Двоичный поиск', type:'algorithm', lang:'Python', diff:'Лёгкая', status:'solved', attempts:3, pattern:'Бинарный поиск', desc:'Дан отсортированный массив arr и число x. Верните индекс x или −1.', complexity:'O(log n)', catalog:'Алгоритмы · базовый' },
    { id: 2,  title: 'Сумма двух чисел', type:'algorithm', lang:'JavaScript', diff:'Средняя', status:'attempted', attempts:1, pattern:'Хеш-таблицы', desc:'Найдите два числа из массива, сумма которых равна target. Верните их индексы.', complexity:'O(n)', catalog:'Алгоритмы · базовый' },
    { id: 3,  title: 'Перевод в двоичную систему', type:'translation', lang:'C++', diff:'Средняя', status:'todo', attempts:0, pattern:'Сортировки', desc:'Переведите число n в двоичную систему счисления.', complexity:'O(log n)', catalog:'Строки и массивы' },
    { id: 4,  title: 'Сортировка слиянием', type:'block_reorder', lang:'Python', diff:'Сложная', status:'todo', attempts:0, pattern:'Сортировки', desc:'Соберите шаги сортировки слиянием в правильном порядке.', complexity:'O(n log n)', catalog:'Алгоритмы · базовый' },
    { id: 5,  title: 'Блок-схема цикла while', type:'diagram', lang:'—', diff:'Лёгкая', status:'solved', attempts:1, pattern:'Рекурсия', desc:'Соберите блок-схему цикла while.', complexity:'—', catalog:'Алгоритмы · базовый' },
    { id: 6,  title: 'Линейный поиск', type:'algorithm', lang:'Python', diff:'Лёгкая', status:'solved', attempts:2, pattern:'Two pointers', desc:'Найдите индекс x в массиве arr линейным проходом.', complexity:'O(n)', catalog:'Алгоритмы · базовый' },
    { id: 7,  title: 'Факториал через рекурсию', type:'code_assembly', lang:'Python', diff:'Лёгкая', status:'attempted', attempts:1, pattern:'Рекурсия', desc:'Соберите функцию factorial(n) из блоков.', complexity:'O(n)', catalog:'Алгоритмы · базовый' },
    { id: 8,  title: 'Развернуть массив', type:'algorithm', lang:'JavaScript', diff:'Лёгкая', status:'solved', attempts:1, pattern:'Two pointers', desc:'Разверните массив на месте.', complexity:'O(n)', catalog:'Строки и массивы' },
    { id: 9,  title: 'Найти максимум', type:'algorithm', lang:'Python', diff:'Лёгкая', status:'solved', attempts:1, pattern:'Two pointers', desc:'Найдите максимум в массиве.', complexity:'O(n)', catalog:'Алгоритмы · базовый' },
    { id: 10, title: 'Палиндром', type:'algorithm', lang:'JavaScript', diff:'Лёгкая', status:'todo', attempts:0, pattern:'Two pointers', desc:'Проверьте, является ли строка палиндромом.', complexity:'O(n)', catalog:'Строки и массивы' },
    { id: 11, title: 'Числа Фибоначчи (DP)', type:'algorithm', lang:'Python', diff:'Средняя', status:'todo', attempts:0, pattern:'DP', desc:'Верните n-ое число Фибоначчи через DP.', complexity:'O(n)', catalog:'Алгоритмы · базовый' },
    { id: 12, title: 'Кратчайший путь BFS', type:'algorithm', lang:'Python', diff:'Сложная', status:'todo', attempts:0, pattern:'Графы', desc:'Найдите кратчайший путь в невзвешенном графе BFS.', complexity:'O(V+E)', catalog:'Алгоритмы · базовый' },
    { id: 13, title: 'Anagram check', type:'algorithm', lang:'JavaScript', diff:'Лёгкая', status:'solved', attempts:2, pattern:'Хеш-таблицы', desc:'Являются ли две строки анаграммами?', complexity:'O(n)', catalog:'Строки и массивы' },
    { id: 14, title: 'Быстрая сортировка', type:'algorithm', lang:'Python', diff:'Сложная', status:'todo', attempts:0, pattern:'Сортировки', desc:'Реализуйте quicksort.', complexity:'O(n log n)', catalog:'Алгоритмы · базовый' },
    { id: 15, title: 'Скобочная последовательность', type:'algorithm', lang:'Python', diff:'Средняя', status:'todo', attempts:0, pattern:'Хеш-таблицы', desc:'Проверьте корректность скобочной последовательности.', complexity:'O(n)', catalog:'Строки и массивы' },
  ];

  const assignmentSets = [
    { id: 'spring', name: 'Алгоритмы · весна', total: 12, solved: 8, color: 'lime' },
    { id: 'strings', name: 'Строки и массивы', total: 9, solved: 2, color: 'purple' },
    { id: 'graphs', name: 'Графы — base', total: 6, solved: 0, color: 'purple' },
  ];

  const catalogs = [
    { id: 'algo-basic', name: 'Алгоритмы · базовый', taskIds: [1,2,4,5,6,7,9,11,12,14], assignedTo:['ИВТ-301','Спецкурс'] },
    { id: 'strings', name: 'Строки и массивы', taskIds: [3,8,10,13,15], assignedTo:['ИВТ-301'] },
    { id: 'recursion', name: 'Рекурсия и DP', taskIds: [7,11], assignedTo:[] },
  ];

  const groups = [
    { id: 'ivt-301', name: 'ИВТ-301', invite:'GRP-7K2A', teacher:'Алексей Петров', students:24, catalogs:['algo-basic','strings'], avgProgress:61 },
    { id: 'speccourse', name: 'Алгоритмы · спецкурс', invite:'GRP-4M9X', teacher:'Ирина Смирнова', students:12, catalogs:['algo-basic'], avgProgress:30 },
  ];

  const groupStudents = {
    'ivt-301': [
      { id:1, name:'Влада Максимова', initials:'В', solved:23, total:48, lastActive:'сегодня' },
      { id:2, name:'Никита Поляков',  initials:'Н', solved:41, total:48, lastActive:'вчера' },
      { id:3, name:'Ольга Серова',    initials:'О', solved:7,  total:48, lastActive:'5 дней назад' },
      { id:4, name:'Дмитрий Орлов',   initials:'Д', solved:32, total:48, lastActive:'сегодня' },
      { id:5, name:'Анна Кравченко',  initials:'А', solved:18, total:48, lastActive:'2 дня назад' },
    ],
    'speccourse': [
      { id:6, name:'Михаил Воронов', initials:'М', solved:14, total:30, lastActive:'сегодня' },
      { id:7, name:'Елена Тимошина', initials:'Е', solved:21, total:30, lastActive:'вчера' },
    ]
  };

  const submissions = [
    { id:101, taskId:1, title:'Двоичный поиск', lang:'Python', attempt:3, status:'accepted', date:'21 мая, 11:42' },
    { id:102, taskId:2, title:'Сумма двух чисел', lang:'JavaScript', attempt:1, status:'failed', date:'20 мая, 18:05' },
    { id:103, taskId:5, title:'Блок-схема цикла', lang:'—', attempt:2, status:'accepted', date:'19 мая, 09:30' },
    { id:104, taskId:3, title:'Перевод в двоичную', lang:'C++', attempt:1, status:'reviewing', date:'18 мая, 22:14' },
    { id:105, taskId:6, title:'Линейный поиск', lang:'Python', attempt:2, status:'accepted', date:'15 мая, 12:00' },
    { id:106, taskId:8, title:'Развернуть массив', lang:'JavaScript', attempt:1, status:'accepted', date:'12 мая, 19:30' },
  ];

  const teacherRequests = [
    { id:1, name:'Мария Кузнецова', email:'m.kuznetsova@uni.ru', dept:'Мат-фак', requestedAt:'2 дня назад', status:'pending' },
    { id:2, name:'Денис Романов',    email:'d.romanov@uni.ru',    dept:'CS',     requestedAt:'5 дней назад', status:'pending' },
    { id:3, name:'Ольга Сергеева',   email:'o.sergeeva@uni.ru',   dept:'CS',     requestedAt:'неделю назад', status:'pending' },
  ];

  const adminUsers = [
    { id:812, name:'Влада Максимова',   email:'vlada@code.dev',     initials:'В', role:'STUDENT',  blocked:false, registered:'12 фев 2026', lastLogin:'сегодня, 11:42', solved:128, groups:['ИВТ-301','Спецкурс'] },
    { id:113, name:'Алексей Петров',     email:'a.petrov@uni.ru',    initials:'А', role:'TEACHER',  blocked:false, registered:'05 янв 2026', lastLogin:'вчера, 16:21', solved:0,   groups:[] },
    { id:201, name:'Иван Соколов',       email:'ivan.s@mail.ru',     initials:'И', role:'STUDENT',  blocked:true,  registered:'01 мар 2026', lastLogin:'10 мая, 09:00', solved:14,  groups:['ИВТ-301'] },
    { id:54,  name:'София Орлова',       email:'sofia@admin.dev',    initials:'С', role:'ADMIN',    blocked:false, registered:'01 янв 2026', lastLogin:'сегодня, 09:00', solved:0,   groups:[] },
    { id:712, name:'Ирина Смирнова',     email:'i.smirnova@uni.ru',  initials:'И', role:'TEACHER',  blocked:false, registered:'14 фев 2026', lastLogin:'сегодня, 08:14', solved:0,   groups:[] },
    { id:899, name:'Никита Поляков',     email:'nikita@code.dev',    initials:'Н', role:'STUDENT',  blocked:false, registered:'18 мар 2026', lastLogin:'сегодня, 10:55', solved:41,  groups:['ИВТ-301'] },
    { id:931, name:'Ольга Серова',       email:'olga.s@code.dev',    initials:'О', role:'STUDENT',  blocked:false, registered:'02 апр 2026', lastLogin:'4 дня назад',   solved:7,   groups:['ИВТ-301'] },
    { id:1004,name:'Дмитрий Орлов',      email:'d.orlov@code.dev',   initials:'Д', role:'STUDENT',  blocked:false, registered:'10 апр 2026', lastLogin:'сегодня, 12:00', solved:32,  groups:['ИВТ-301'] },
  ];

  const adminAssignments = [
    { id:1, title:'Контест: Базовые алгоритмы', author:'Алексей Петров', workflow:'published', version:'v3', updated:'18 мая', archived:false },
    { id:2, title:'Домашняя работа №4 — DP',     author:'Ирина Смирнова', workflow:'draft',     version:'v1', updated:'15 мая', archived:false },
    { id:3, title:'Экзамен · сортировки',         author:'Алексей Петров', workflow:'review',    version:'v2', updated:'12 мая', archived:false },
    { id:4, title:'Старый контест — графы',       author:'Алексей Петров', workflow:'archived',  version:'v5', updated:'01 фев', archived:true  },
  ];

  const adminStats = {
    users: 1248, teachers: 37, students: 1175, admins: 36,
    tasks: 612, assignments: 84,
    submissionsLast30: 8412, acceptanceRate: 0.71,
    blocked: 12, pendingTeacherRequests: 3,
    breakdown: {
      roles: [{label:'Студенты', value:1175, color:'lime'}, {label:'Преподаватели', value:37, color:'purple'}, {label:'Админы', value:36, color:'purple'}, {label:'Заблокированы', value:12, color:'danger'}],
      taskTypes: [{label:'algorithm', value:312}, {label:'translation', value:84}, {label:'diagram', value:42}, {label:'block_reorder', value:96}, {label:'code_assembly', value:78}],
    }
  };

  const teacherAnalytics = {
    students: 36, weekly: 4,
    activeTasks: 42, catalogs: 4,
    acceptance: 0.71, deltaMonth: -0.03,
    bars: [50,72,30,88,100,64,46,22,78,58,92,40],
  };

  const codeSample = {
    Python: `def binary_search(arr, x):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == x:
            return mid
        elif arr[mid] < x:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1`,
    JavaScript: `function binarySearch(arr, x) {
  let lo = 0, hi = arr.length - 1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (arr[mid] === x) return mid;
    if (arr[mid] < x) lo = mid + 1;
    else hi = mid - 1;
  }
  return -1;
}`,
    'C++': `int binarySearch(vector<int>& arr, int x) {
  int lo = 0, hi = arr.size() - 1;
  while (lo <= hi) {
    int mid = (lo + hi) / 2;
    if (arr[mid] == x) return mid;
    if (arr[mid] < x) lo = mid + 1;
    else hi = mid - 1;
  }
  return -1;
}`,
  };

  const assemblyBlocks = [
    { id:'a', code:'def factorial(n):', correct:1 },
    { id:'b', code:'    if n <= 1: return 1', correct:2 },
    { id:'c', code:'    return n * factorial(n - 1)', correct:3 },
  ];
  const assemblyDistractors = [
    { id:'d1', code:'    return n + 1' },
    { id:'d2', code:'    n = n - 1' },
  ];

  // Topics/learning prefs
  const topics = ['Алгоритмы','Базы данных','Структуры данных','Сети','Веб','ML','Системы','Безопасность'];

  /* ===== CURRICULUM (Pascal track) ===== */
  // Action type → badge meta. translate=lime, assemble=purple, implement/debug=warn, analyze/recognize=muted
  const actionMeta = {
    translate:  { label:'Перенести',  kind:'lime',   icon:'⇄' },
    assemble:   { label:'Собрать',    kind:'purple', icon:'⧉' },
    implement:  { label:'Реализовать',kind:'warn',   icon:'⌨' },
    debug:      { label:'Отладить',   kind:'warn',   icon:'⊘' },
    analyze:    { label:'Разобрать',  kind:'muted',  icon:'◎' },
    recognize:  { label:'Опознать',   kind:'muted',  icon:'?' },
  };

  // Pascal chapters (collections). order = pedagogical path.
  const pascalChapters = [
    {
      id:'variables-and-io', n:1, slug:'variables-and-io',
      title:'Переменные и ввод-вывод',
      desc:'Объявления, присваивание, Readln и Writeln.',
      total:6, passed:6, completed:true, button:'Повторить', nextTaskId:201,
    },
    {
      id:'conditions', n:2, slug:'conditions',
      title:'Условия',
      desc:'if / then / else, вложенные условия, case of.',
      total:7, passed:3, completed:false, button:'Продолжить', nextTaskId:210,
    },
    {
      id:'loops', n:3, slug:'loops',
      title:'Циклы',
      desc:'for, while, repeat-until и работа со счётчиками.',
      total:8, passed:0, completed:false, button:'Начать', nextTaskId:220,
    },
    {
      id:'arrays', n:4, slug:'arrays',
      title:'Массивы и строки',
      desc:'Одномерные массивы, перебор, обработка строк.',
      total:9, passed:0, completed:false, button:'Начать', nextTaskId:230,
    },
    {
      id:'procedures', n:5, slug:'procedures',
      title:'Процедуры и функции',
      desc:'Подпрограммы, параметры, рекурсия.',
      total:10, passed:0, completed:false, button:'Начать', nextTaskId:240,
    },
  ];

  const pascalTrack = {
    language:'pascal',
    label:'Pascal',
    get total(){ return pascalChapters.reduce((s,c)=>s+c.total,0); },
    get passed(){ return pascalChapters.reduce((s,c)=>s+c.passed,0); },
    chapters: pascalChapters,
  };

  // Showcase detail for the first chapter — sections (subtopics) with task cards.
  const pascalShowcase = {
    'variables-and-io': {
      collectionId:'variables-and-io',
      title:'Переменные и ввод-вывод',
      desc:'Объявления, присваивание, Readln и Writeln.',
      total:6, passed:4, button:'Продолжить', nextTaskId:204, completed:false,
      sections:[
        { id:'program_entry', name:'Точка входа программы', tasks:[
          { task_id:201, title:'Каркас программы', action:'translate', skill:'Перенести на Pascal', desc:'Перенесите минимальную программу program/begin/end на Pascal.', diff:'Лёгкая', status:'passed', subtopic:'Точка входа программы', instruction:'Дана пустая программа на псевдокоде. Запишите её корректно на Pascal с program, begin и end.' },
        ]},
        { id:'typed_declaration', name:'Объявление переменных', tasks:[
          { task_id:202, title:'Типы переменных', action:'assemble', skill:'Собрать раздел var', desc:'Соберите блок var с корректными типами.', diff:'Лёгкая', status:'passed', subtopic:'Объявление переменных', instruction:'Соберите раздел var из блоков: целое, вещественное и строковое объявления в правильном порядке.' },
          { task_id:203, title:'Опознать тип по значению', action:'recognize', skill:'Сопоставить тип', desc:'Определите тип переменной по присвоенному значению.', diff:'Лёгкая', status:'passed', subtopic:'Объявление переменных', instruction:'Для каждого значения выберите подходящий тип Pascal: integer, real, string или boolean.' },
        ]},
        { id:'assignment', name:'Присваивание', tasks:[
          { task_id:204, title:'Оператор присваивания', action:'implement', skill:'Написать присваивание', desc:'Реализуйте серию присваиваний :=.', diff:'Средняя', status:'failed', subtopic:'Присваивание', instruction:'Объявите переменные и присвойте им значения через :=. Выведите результат в конце.' },
        ]},
        { id:'arithmetic_ops', name:'Арифметика', tasks:[
          { task_id:205, title:'Арифметические операции', action:'implement', skill:'Посчитать выражение', desc:'Вычислите выражение с div и mod.', diff:'Средняя', status:'not_started', subtopic:'Арифметика', instruction:'Прочитайте два целых числа и выведите их сумму, разность, целочастное деление div и остаток mod.' },
        ]},
        { id:'stdin_read', name:'Чтение (Readln)', tasks:[
          { task_id:206, title:'Ввод данных Readln', action:'translate', skill:'Перенести ввод', desc:'Перенесите чтение из stdin на Readln.', diff:'Средняя', status:'not_started', subtopic:'Чтение (Readln)', instruction:'Дан код ввода на Python. Перенесите его на Pascal, используя Readln для чтения двух чисел.' },
        ]},
        { id:'stdout_write', name:'Вывод (Writeln)', tasks:[
          { task_id:207, title:'Найди ошибку в выводе', action:'debug', skill:'Отладить Writeln', desc:'Исправьте форматирование вывода.', diff:'Сложная', status:'not_started', subtopic:'Вывод (Writeln)', instruction:'Программа выводит результат неправильно — лишние пробелы и неверный порядок. Найдите и исправьте ошибку в Writeln.' },
        ]},
      ],
    },
  };

  return {
    taskTypes, languages, patterns, difficulties, topics,
    tasks, assignmentSets, catalogs, groups, groupStudents,
    submissions, teacherRequests, adminUsers, adminAssignments, adminStats,
    teacherAnalytics, codeSample, assemblyBlocks, assemblyDistractors,
    actionMeta, pascalTrack, pascalShowcase,
  };
})();
