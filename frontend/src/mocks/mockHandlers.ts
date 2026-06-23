import { mockDelay } from "@/mocks/delay"
import { MOCK_LANGUAGES } from "@/mocks/data/languages"
import { MOCK_USER } from "@/mocks/data/user"
import {
  getMockTaskById,
  getMockTasksSnapshot,
  getMockProfile,
  recordMockSubmission,
} from "@/mocks/mockStore"
import { setAuthTokens } from "@/shared/api/auth"
import { createMockAccessToken, createMockRefreshToken } from "@/mocks/mockAuthToken"
import {
  MOCK_ANALYTICS,
  DEMO_STREAK_DAYS,
  buildMockSkillProgress,
  buildMockTcSkills,
  buildMockTcSkillsByLanguage,
  buildMockTcSkillGroupsByLanguage,
  buildMockTcSkillGroupsForLanguage,
  buildMockTcSkillLanguages,
  buildMockTcTaskRecommendations,
  buildMockStudentRecommendations,
  buildMockStudentProfileExtras,
} from "@/mocks/data/profileDemo"
import type { TaskOverviewFilters, TaskOverviewResponse } from "@/shared/types/taskOverview"
import { recommendationsToLegacyList } from "@/shared/utils/studentRecommendations"

/** ~70% успех, ~30% ошибки (компиляция / тесты / линтер). */
function rollCheckOutcome() {
  const r = Math.random()
  if (r < 0.7) return { kind: "success" }
  if (r < 0.82) return { kind: "compiler" }
  if (r < 0.94) return { kind: "tests" }
  return { kind: "linter" }
}

function mockTestDurationMs(index, taskId = 0) {
  const base = 42 + (Number(taskId) % 7) * 13
  return base + index * 58 + (index % 2) * 19
}

function buildTestResults(task, outcome) {
  const cases = task?.test_cases || []
  const taskId = task?.id ?? 0
  if (!cases.length) {
    return outcome.kind === "success"
      ? [
          {
            case: 1,
            status: "PASSED",
            inputs: "",
            expected: "—",
            actual: "—",
            message: "OK",
            duration_ms: mockTestDurationMs(0, taskId),
          },
        ]
      : [
          {
            case: 1,
            status: "FAILED",
            inputs: "",
            expected: "—",
            actual: "Нет тестов",
            message: "Нет данных",
            duration_ms: 0,
          },
        ]
  }

  if (outcome.kind === "success") {
    return cases.map((tc, index) => ({
      case: index + 1,
      status: "PASSED",
      inputs: tc.inputs ?? "",
      expected: tc.output ?? "",
      actual: tc.output ?? "",
      message: "Тест пройден",
      duration_ms: mockTestDurationMs(index, taskId),
    }))
  }

  if (outcome.kind === "tests") {
    return cases.map((tc, index) => ({
      case: index + 1,
      status: index === 0 ? "FAILED" : "PASSED",
      inputs: tc.inputs ?? "",
      expected: tc.output ?? "",
      actual: index === 0 ? "неверный ответ" : tc.output ?? "",
      message: index === 0 ? "Неверный вывод" : "Тест пройден",
      duration_ms: index === 0 ? mockTestDurationMs(index, taskId) + 120 : mockTestDurationMs(index, taskId),
    }))
  }

  return cases.map((tc, index) => ({
    case: index + 1,
    status: "ERROR",
    inputs: tc.inputs ?? "",
    expected: tc.output ?? "",
    actual: "",
    message: "Не запускалось из-за ошибки компиляции",
    duration_ms: 0,
  }))
}

function buildExecutionResponse(taskId, outcome) {
  const task = getMockTaskById(taskId)
  const title = task?.title

  if (outcome.kind === "success") {
    const test_results = buildTestResults(task, outcome)
    recordMockSubmission({
      taskId,
      success: true,
      message: "Все тесты пройдены",
      title,
    })
    return {
      task_id: taskId,
      success: true,
      compiler_errors: [],
      linter_errors: [],
      pattern_errors: [],
      test_results,
      job_id: `mock-job-${Date.now()}`,
    }
  }

  if (outcome.kind === "compiler") {
    recordMockSubmission({
      taskId,
      success: false,
      message: "Ошибка компиляции",
      title,
    })
    return {
      task_id: taskId,
      success: false,
      compiler_errors: [
        {
          type: "COMPILE_ERROR",
          text: "Строка 4: ожидалось ';' перед 'return' — синтаксическая ошибка (демо).",
        },
      ],
      linter_errors: [],
      pattern_errors: [],
      test_results: buildTestResults(task, outcome),
      job_id: `mock-job-${Date.now()}`,
    }
  }

  if (outcome.kind === "linter") {
    recordMockSubmission({
      taskId,
      success: false,
      message: "Замечания линтера",
      title,
    })
    return {
      task_id: taskId,
      success: false,
      compiler_errors: [],
      linter_errors: [
        {
          type: "LINT",
          text: "Строка 2: неиспользуемая переменная `tmp` (демо).",
        },
      ],
      pattern_errors: [],
      test_results: [],
      job_id: `mock-job-${Date.now()}`,
    }
  }

  recordMockSubmission({
    taskId,
    success: false,
    message: "Не все тесты пройдены",
    title,
  })
  return {
    task_id: taskId,
    success: false,
    compiler_errors: [],
    linter_errors: [],
    pattern_errors: [],
    test_results: buildTestResults(task, outcome),
    job_id: `mock-job-${Date.now()}`,
  }
}

function toOverviewTask(task: Record<string, unknown>) {
  const showcase =
    typeof task.code_examples === "object" && task.code_examples
      ? (task.code_examples as Record<string, unknown>).curriculum_showcase
      : null
  const meta = typeof showcase === "object" && showcase ? (showcase as Record<string, unknown>) : {}
  return {
    id: task.id as number,
    slot_id: (meta.slug as string | undefined) ?? null,
    title: String(task.title ?? ""),
    language: (meta.target_language as string | undefined) ?? (task.language as string | undefined) ?? null,
    course_key: (meta.target_language as string | undefined) ?? null,
    chapter_key: (meta.collection_key as string | undefined) ?? null,
    task_format: (meta.task_format as string | undefined) ?? null,
    difficulty: (task.difficulty as string | undefined) ?? null,
    type: (task.type as string | undefined) ?? (task.task_type as string | undefined) ?? null,
    task_type: (task.task_type as string | undefined) ?? (task.type as string | undefined) ?? null,
    constructions: Array.isArray(task.constructions) ? task.constructions : [],
    attempted: Boolean(task.attempted),
    solved: Boolean(task.solved),
    completed: Boolean(task.solved),
    submissions_count: Number(task.submissions_count ?? 0),
  }
}

export const mockHandlers = {
  async getTaskOverview(_filters: TaskOverviewFilters = {}): Promise<TaskOverviewResponse> {
    await mockDelay()
    const tasks = getMockTasksSnapshot().map((task) => toOverviewTask(task as Record<string, unknown>))
    return {
      tasks,
      total: tasks.length,
      page: 1,
      page_size: tasks.length,
    }
  },

  async getTasks() {
    await mockDelay()
    return getMockTasksSnapshot()
  },

  async getTask(id) {
    await mockDelay()
    const task = getMockTaskById(id)
    if (!task) {
      const err = new Error("Задача не найдена")
      err.response = { status: 404, data: { detail: "Задача не найдена" } }
      throw err
    }
    return task
  },

  async getServerLanguages() {
    await mockDelay(200)
    return MOCK_LANGUAGES
  },

  async login() {
    await mockDelay(300)
    const accessToken = createMockAccessToken("STUDENT")
    const refreshToken = createMockRefreshToken()
    setAuthTokens({
      accessToken,
      refreshToken,
      persist: true,
    })
    return {
      access_token: accessToken,
      refresh_token: refreshToken,
      token_type: "bearer",
    }
  },

  async getMe() {
    await mockDelay(150)
    return { ...MOCK_USER }
  },

  async getStudentProfile() {
    await mockDelay()
    const stats = getMockProfile()
    return {
      ...MOCK_USER,
      ...stats,
      ...buildMockStudentProfileExtras(stats),
    }
  },

  async submitSolution(data) {
    await mockDelay(800)
    const outcome = rollCheckOutcome()
    return buildExecutionResponse(data.task_id, outcome)
  },

  async lintSolution() {
    await mockDelay(300)
    return { status: "done", linter_errors: [] }
  },

  async checkFlow(data) {
    await mockDelay(400)
    const nodes = data?.nodes || []
    const edges = data?.edges || []
    const types = nodes.map((node) => String(node.type || "").toLowerCase())
    const errors = []
    if (!nodes.length) {
      errors.push({ type: "FLOW_EMPTY", text: "Добавьте блоки в схему перед проверкой." })
    }
    if (types.length && !types.includes("start")) {
      errors.push({ type: "FLOW_START_MISSING", text: "Схема должна содержать блок «Начало»." })
    }
    if (types.length && !types.includes("end")) {
      errors.push({ type: "FLOW_END_MISSING", text: "Схема должна содержать блок «Конец»." })
    }
    const decisionIds = new Set(
      nodes.filter((node) => String(node.type).toLowerCase() === "decision").map((node) => node.id),
    )
    for (const decisionId of decisionIds) {
      const outgoing = edges.filter((edge) => edge.source === decisionId).length
      if (outgoing < 2) {
        errors.push({
          type: "FLOW_DECISION_BRANCHES",
          text: "У блока «Условие» должно быть две ветви (да и нет).",
        })
        break
      }
    }
    return {
      success: errors.length === 0,
      errors,
      execution_results: [],
      test_cases: [],
      semantic_checked: true,
    }
  },

  async submitBlockReorderSolution(taskId) {
    await mockDelay(900)
    const outcome = rollCheckOutcome()
    const base = buildExecutionResponse(Number(taskId), outcome)
    return {
      correct: base.success,
      message: base.success ? "Верное решение" : "Неверное решение",
      execution_results: base.test_results,
      execution_job_id: null,
    }
  },

  async listAccessibleAssignmentSets() {
    await mockDelay(200)
    return [
      {
        id: 1,
        name: "Демо-сборник: основы",
        title: "Демо-сборник: основы",
        total_tasks: 5,
        solved_count: 2,
        items: getMockTasksSnapshot().slice(0, 5).map((t) => ({ id: t.id, solved: t.solved })),
      },
    ]
  },

  async getNextRecommendation(currentTaskId = null) {
    await mockDelay(150)
    const list = getMockTasksSnapshot().filter((t) => !t.solved)
    const cur = Number(currentTaskId)
    const next = list.find((t) => t.id !== cur) || list[0]
    return next ? { task_id: next.id, reason: "Следующее нерешённое демо-задание" } : { task_id: null }
  },

  async getCatalogNavigation(catalogId, currentTaskId = null) {
    await mockDelay(150)
    const ids = getMockTasksSnapshot().slice(0, 5).map((t) => t.id)
    const cur = Number(currentTaskId)
    const idx = ids.indexOf(cur)
    return {
      catalog_id: catalogId,
      task_ids: ids,
      current_index: idx >= 0 ? idx : 0,
      prev_task_id: idx > 0 ? ids[idx - 1] : null,
      next_task_id: idx >= 0 && idx < ids.length - 1 ? ids[idx + 1] : null,
    }
  },

  async getStudentRecommendations() {
    await mockDelay()
    const streakDays = DEMO_STREAK_DAYS
    return buildMockStudentRecommendations(streakDays)
  },

  async getStudentAnalytics() {
    await mockDelay()
    const profile = getMockProfile()
    const streakDays = DEMO_STREAK_DAYS
    const studentRecommendations = buildMockStudentRecommendations(streakDays)
    const tcSkillsByLanguage = buildMockTcSkillsByLanguage()
    const tcSkillGroupsByLanguage = buildMockTcSkillGroupsByLanguage()
    return {
      ...MOCK_ANALYTICS,
      streak_days: streakDays,
      by_structure: buildMockSkillProgress(),
      tc_skills: buildMockTcSkills(),
      tc_skills_by_language: tcSkillsByLanguage,
      tc_skill_groups: buildMockTcSkillGroupsForLanguage("pascal"),
      tc_skill_groups_by_language: tcSkillGroupsByLanguage,
      tc_skill_languages: buildMockTcSkillLanguages(),
      tc_skills_default_language: "pascal",
      tc_task_recommendations: buildMockTcTaskRecommendations(),
      tc_task_recommendations_by_language: {
        pascal: buildMockTcTaskRecommendations(),
        python: buildMockTcTaskRecommendations(),
        cpp: buildMockTcTaskRecommendations(),
      },
      student_recommendations: studentRecommendations,
      recommendations: recommendationsToLegacyList(studentRecommendations),
      overview: {
        ...MOCK_ANALYTICS.overview,
        solved_count: profile.solved_count,
        total_tasks: profile.total_tasks,
        completion_percent: profile.progress_percent,
        streak_days: streakDays,
      },
      total_submissions: profile.attempted_count,
      accepted: profile.solved_count,
      activity: [],
    }
  },

  async listJoinedGroupsOverview() {
    await mockDelay(150)
    return [
      {
        id: 1,
        name: "ИТ-201: Алгоритмы",
        teacher: { id: 1, name: "Иванов И.И." },
        catalog_count: 2,
        task_count: 40,
        solved_count: 12,
      },
      {
        id: 2,
        name: "Подготовка к коллоквиуму",
        teacher: { id: 2, name: "Петров П.П." },
        catalog_count: 1,
        task_count: 20,
        solved_count: 5,
      },
    ]
  },
}
