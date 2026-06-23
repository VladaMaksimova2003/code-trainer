export const MOCK_USER = {
  id: 9001,
  email: "student.demo@praktika.local",
  name: "Анна Демонстрационная",
  about: "Учусь переводить алгоритмы между языками и собирать код по блок-схемам.",
  roles: ["STUDENT"],
  normalized_roles: ["student"],
}

export const MOCK_STUDENT_PROFILE = {
  ...MOCK_USER,
  progress_percent: 42,
  solved_count: 8,
  attempted_count: 14,
  total_tasks: 20,
  streak_days: 5,
  solved_task_ids: [101, 102, 104, 106, 108, 110, 112, 115],
  recent_results: [
    { task_id: 115, task_title: "Сортировка выбором", success: true, at: "2026-05-27T10:12:00Z", message: "Все тесты пройдены" },
    { task_id: 114, task_title: "Палиндром по блок-схеме", success: false, at: "2026-05-27T09:40:00Z", message: "Неверный вывод на тесте 2" },
    { task_id: 113, task_title: "Таблица умножения (схема)", success: true, at: "2026-05-26T18:05:00Z", message: "Все тесты пройдены" },
    { task_id: 111, task_title: "Сборка: цикл for", success: false, at: "2026-05-26T16:22:00Z", message: "Ошибка компиляции" },
    { task_id: 109, task_title: "Максимум в массиве", success: true, at: "2026-05-25T14:00:00Z", message: "Все тесты пройдены" },
  ],
}
