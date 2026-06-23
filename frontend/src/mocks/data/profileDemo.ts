/** Демо-данные для вкладки «Прогресс» и карточки профиля. */

import { buildSkillProgress } from "@/shared/config/skillGroups"
import { getMockTasksSnapshot } from "@/mocks/mockStore"
import { buildStudentRecommendations, recommendationsToLegacyList } from "@/shared/utils/studentRecommendations"

import { formatUtcDateKey, utcTodayStart } from "@/shared/utils/activityStats"

function buildActivityByDate() {
  const byDate = {}
  const today = utcTodayStart()
  const dayMs = 24 * 60 * 60 * 1000
  for (let i = 0; i < 180; i += 1) {
    const d = new Date(today.getTime() - i * dayMs)
    const key = formatUtcDateKey(d)
    const weekday = d.getUTCDay()
    const base = weekday === 0 || weekday === 6 ? 0 : 1
    byDate[key] = base && Math.random() > 0.35 ? Math.floor(Math.random() * 4) + 1 : 0
  }
  return byDate
}

const ACTIVITY = buildActivityByDate()

export const DEMO_STREAK_DAYS = 5

/** Навыки по демо-задачам (те же правила, что на бэкенде). */
export function buildMockSkillProgress() {
  const tasks = getMockTasksSnapshot()
  return buildSkillProgress(
    tasks.map((task) => ({
      id: task.id,
      constructions: task.constructions,
      solved: task.solved,
    })),
  )
}

/** Display TC progress for demo profile tab (registry order subset). */
export function buildMockTcSkills() {
  return buildMockTcSkillsForLanguage("pascal")
}

export function buildMockTcSkillsForLanguage(language: string) {
  const rows = [
    { id: "tc_program_structure", label: "Структура программы", total: 10, solved: 8, percent: 80 },
    { id: "tc_variables_types", label: "Переменные и типы", total: 10, solved: 6, percent: 60 },
    { id: "tc_assignment", label: "Присваивание", total: 10, solved: 9, percent: 90 },
    { id: "tc_conditionals", label: "Условия", total: 10, solved: 4, percent: 40 },
    { id: "tc_loops", label: "Циклы", total: 20, solved: 6, percent: 30 },
    { id: "tc_functions", label: "Функции", total: 8, solved: 0, percent: 0 },
    { id: "tc_arrays", label: "Массивы", total: 10, solved: 2, percent: 20 },
  ]
  if (language === "cpp") {
    return rows.map((row) =>
      row.id === "tc_loops"
        ? { ...row, solved: 10, percent: 50 }
        : row.id === "tc_functions"
          ? { ...row, solved: 2, percent: 25 }
          : row,
    )
  }
  if (language === "python") {
    return rows.map((row) =>
      row.id === "tc_assignment" ? { ...row, solved: 10, percent: 100 } : row,
    )
  }
  return rows
}

export function buildMockTcSkillsByLanguage() {
  return {
    pascal: buildMockTcSkillsForLanguage("pascal"),
    python: buildMockTcSkillsForLanguage("python"),
    cpp: buildMockTcSkillsForLanguage("cpp"),
  }
}

export function buildMockTcSkillGroupsForLanguage(language: string) {
  const rows = [
    { id: "basics", label: "Основы программы", total: 128, solved: 8, percent: 6.3 },
    { id: "control_flow", label: "Условия и циклы", total: 96, solved: 3, percent: 3.1 },
    { id: "functions", label: "Функции и рекурсия", total: 72, solved: 2, percent: 2.8 },
    { id: "collections", label: "Массивы и коллекции", total: 64, solved: 1, percent: 1.6 },
    { id: "algorithms", label: "Алгоритмы на данных", total: 40, solved: 0, percent: 0 },
    { id: "modules_files", label: "Модули и файлы", total: 24, solved: 0, percent: 0 },
    { id: "oop", label: "Объектно-ориентированное программирование", total: 32, solved: 0, percent: 0 },
    { id: "structures", label: "Структуры данных", total: 28, solved: 0, percent: 0 },
  ]
  if (language === "cpp") {
    return rows.map((row) =>
      row.id === "control_flow" ? { ...row, solved: 5, percent: 5.2 } : row,
    )
  }
  return rows
}

export function buildMockTcSkillGroupsByLanguage() {
  return {
    pascal: buildMockTcSkillGroupsForLanguage("pascal"),
    python: buildMockTcSkillGroupsForLanguage("python"),
    cpp: buildMockTcSkillGroupsForLanguage("cpp"),
  }
}

export function buildMockTcSkillLanguages() {
  return [
    { code: "pascal", label: "Pascal" },
    { code: "python", label: "Python" },
    { code: "cpp", label: "C++" },
  ]
}

export function buildMockTcTaskRecommendations() {
  const tasks = getMockTasksSnapshot()
  const open = tasks.find((task) => !task.solved)
  if (!open) return []
  return [
    {
      task_id: open.id,
      title: open.title,
      language: "python",
      difficulty: open.difficulty || "easy",
      reason: "Мало решённых задач по темам: Функции, Циклы",
      weak_tc_ids: ["tc_functions", "tc_loops"],
      weak_tc_labels: ["Функции", "Циклы"],
      score: 170,
    },
  ]
}

export function buildMockStudentRecommendations(streakDays = DEMO_STREAK_DAYS) {
  const tasks = getMockTasksSnapshot()
  const skillProgress = buildMockSkillProgress()
  const recentResults = tasks
    .filter((task) => task.attempted)
    .slice(0, 20)
    .map((task) => ({
      success: Boolean(task.solved),
      message: task.solved ? "Все тесты пройдены" : "Неверный вывод",
    }))

  return buildStudentRecommendations({
    skillProgress,
    streakDays,
    recentResults,
    tasks,
  })
}

export function buildMockRecommendations(streakDays = DEMO_STREAK_DAYS) {
  return recommendationsToLegacyList(buildMockStudentRecommendations(streakDays))
}

export const MOCK_ANALYTICS = {
  streak_days: DEMO_STREAK_DAYS,
  overview: {
    level: "Средний",
    completion_percent: 42,
    solved_count: 8,
    total_tasks: 20,
    success_rate: 76,
    total_submissions: 24,
    streak_days: DEMO_STREAK_DAYS,
  },
  recommendations: buildMockRecommendations(DEMO_STREAK_DAYS),
  student_recommendations: buildMockStudentRecommendations(DEMO_STREAK_DAYS),
  by_language: [
    { language: "python", percent: 78 },
    { language: "cpp", percent: 55 },
    { language: "java", percent: 32 },
  ],
}

export function buildMockStudentProfileExtras(stats) {
  const recent_submissions = (stats.recent_results || []).map((row, index) => ({
    id: 9000 + index,
    task_id: row.task_id,
    task_title: row.task_title,
    success: row.success,
    status: row.success ? "accepted" : "failed",
    created_at: row.at,
    language: "python",
  }))

  return {
    display_name: "Анна Демонстрационная",
    solved_tasks_count: stats.solved_count,
    success_rate: 76,
    streak_days: DEMO_STREAK_DAYS,
    activity_by_date: ACTIVITY,
    recent_submissions,
  }
}
