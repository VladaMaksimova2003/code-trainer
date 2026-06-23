import axios from "axios"
import { isMockApiEnabled } from "@/mocks/config"
import { mockHandlers } from "@/mocks/mockHandlers"
import { api } from "@/shared/api/client"
import { isCurriculumLearningLanguage } from "@/shared/config/curriculumLanguages"
import type { TaskOverviewFilters, TaskOverviewResponse } from "@/shared/types/taskOverview"
import type { TaskDto } from "@/shared/types/task"

export const TASK_OVERVIEW_STALE_MS = 5 * 60 * 1000
export const TASK_DETAIL_STALE_MS = 60_000

function buildOverviewParams(
  filters: TaskOverviewFilters,
): Record<string, string | number> {
  const params: Record<string, string | number> = {}
  if (filters.course) params.course = filters.course
  if (filters.chapter) params.chapter = filters.chapter
  if (filters.targetLanguage) params.target_language = filters.targetLanguage
  if (filters.page) params.page = filters.page
  if (filters.pageSize) params.page_size = filters.pageSize
  if (filters.search) params.search = filters.search
  if (filters.type) params.type = filters.type
  if (filters.difficulty) params.difficulty = filters.difficulty
  if (filters.pattern) params.pattern = filters.pattern
  if (filters.language) params.language = filters.language
  if (filters.status) params.status = filters.status
  if (filters.matchMode) params.match_mode = filters.matchMode
  return params
}

function normalizeOverviewResponse(data: unknown): TaskOverviewResponse {
  const payload = data as TaskOverviewResponse
  const tasks = Array.isArray(payload?.tasks) ? payload.tasks : []
  return {
    ...payload,
    tasks,
    total:
      typeof payload?.total === "number"
        ? payload.total
        : tasks.length,
  }
}

function isOverviewRouteMissing(err: unknown): boolean {
  if (!axios.isAxiosError(err)) return false
  const status = err.response?.status
  if (status === 404) return true
  if (status !== 422) return false
  const detail = err.response?.data?.detail
  if (!Array.isArray(detail)) return false
  return detail.some((item) => {
    if (!item || typeof item !== "object") return false
    const loc = (item as { loc?: unknown[] }).loc
    return Array.isArray(loc) && loc.includes("task_id")
  })
}

export async function getTaskOverview(
  filters: TaskOverviewFilters = {},
): Promise<TaskOverviewResponse> {
  if (isMockApiEnabled()) return mockHandlers.getTaskOverview(filters)
  const params = buildOverviewParams(filters)
  try {
    const res = await api.get("/tasks/overview", { params })
    return normalizeOverviewResponse(res.data)
  } catch (err) {
    if (!isOverviewRouteMissing(err)) throw err
    const res = await api.get("/tasks/", { params: { ...params, light: true } })
    return normalizeOverviewResponse(res.data)
  }
}

export const getTasks = async (): Promise<TaskDto[]> => {
  if (isMockApiEnabled()) return mockHandlers.getTasks()
  const res = await api.get("/tasks/", { params: { light: true } })
  const data = res.data as TaskOverviewResponse | { tasks?: TaskDto[] }
  return (data.tasks ?? []) as TaskDto[]
}

export const getTask = async (
  id: number | string,
  options?: { learningLanguage?: string; sourceLanguage?: string },
): Promise<TaskDto> => {
  if (isMockApiEnabled()) return mockHandlers.getTask(id)
  const params: Record<string, string> = {}
  const learningLanguage = String(options?.learningLanguage || "").toLowerCase()
  if (isCurriculumLearningLanguage(learningLanguage)) {
    params.learning_language = learningLanguage
  }
  const sourceLanguage = String(options?.sourceLanguage || "").toLowerCase()
  if (isCurriculumLearningLanguage(sourceLanguage)) {
    params.source_language = sourceLanguage
  }
  const res = await api.get(`/tasks/${id}`, { params })
  return res.data
}

export const getTaskTypes = async (): Promise<string[]> => {
  if (isMockApiEnabled()) {
    const res = await mockHandlers.getTaskOverview()
    const types = [...new Set(res.tasks.map((t) => t.type || "task_translate_full_program"))]
    return types.length ? types : ["task_translate_full_program", "task_flowchart_to_code", "algorithm"]
  }
  const res = await api.get("/tasks/types")
  const rows = res.data?.types ?? []
  const types = rows.map((row: { id?: string; name?: string } | string) =>
    typeof row === "string" ? row : row.id || row.name || "",
  )
  return types.filter(Boolean)
}
