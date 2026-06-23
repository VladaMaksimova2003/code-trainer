import { MOCK_STUDENT_PROFILE } from "@/mocks/data/user"
import { cloneMockTasks } from "@/mocks/data/tasks"
import { pickConstructionHintsForTask } from "@/mocks/data/constructionHints"

const STORAGE_KEY = "code-trainer-mock-store-v1"

let tasks = cloneMockTasks()
let solvedIds = new Set(MOCK_STUDENT_PROFILE.solved_task_ids)
let attemptedIds = new Set([...solvedIds, 114, 111])
const recentResults = [...MOCK_STUDENT_PROFILE.recent_results]

function loadPersisted() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) return
    const data = JSON.parse(raw)
    if (Array.isArray(data.solvedIds)) {
      solvedIds = new Set(data.solvedIds)
    }
    if (Array.isArray(data.attemptedIds)) {
      attemptedIds = new Set(data.attemptedIds)
    }
  } catch {
    /* ignore */
  }
}

function persist() {
  try {
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        solvedIds: [...solvedIds],
        attemptedIds: [...attemptedIds],
      }),
    )
  } catch {
    /* ignore */
  }
}

loadPersisted()

export function getMockTasksSnapshot() {
  return tasks.map((task) => enrichMockTask(task, task.id))
}

function enrichMockTask(task, num) {
  return {
    ...task,
    solved: solvedIds.has(num),
    attempted: attemptedIds.has(num),
    submissions_count: attemptedIds.has(num) ? 1 : 0,
    construction_hints: pickConstructionHintsForTask(task),
  }
}

export function getMockTaskById(id) {
  const num = Number(id)
  const task = tasks.find((t) => t.id === num)
  if (!task) return null
  return enrichMockTask(task, num)
}

export function recordMockSubmission({ taskId, success, message, title }) {
  const id = Number(taskId)
  attemptedIds.add(id)
  if (success) {
    solvedIds.add(id)
  }
  recentResults.unshift({
    task_id: id,
    task_title: title || tasks.find((t) => t.id === id)?.title || `Задача ${id}`,
    success: Boolean(success),
    at: new Date().toISOString(),
    message: message || (success ? "Все тесты пройдены" : "Проверка не пройдена"),
  })
  if (recentResults.length > 12) {
    recentResults.length = 12
  }
  persist()
}

export function getMockProfile() {
  const total = tasks.length
  const solved_count = solvedIds.size
  const attempted_count = attemptedIds.size
  return {
    progress_percent: total ? Math.round((solved_count / total) * 100) : 0,
    solved_count,
    attempted_count,
    total_tasks: total,
    solved_task_ids: [...solvedIds],
    recent_results: [...recentResults],
  }
}

export function resetMockStore() {
  tasks = cloneMockTasks()
  solvedIds = new Set(MOCK_STUDENT_PROFILE.solved_task_ids)
  attemptedIds = new Set([...solvedIds, 114, 111])
  recentResults.length = 0
  recentResults.push(...MOCK_STUDENT_PROFILE.recent_results)
  persist()
}
