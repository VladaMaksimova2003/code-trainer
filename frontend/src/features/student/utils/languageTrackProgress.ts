import type { TaskDto } from "@/shared/types/task"
import type { TaskOverviewItem } from "@/shared/types/taskOverview"

export type LanguageTrackState = "solved" | "attempted" | "todo"

export type TaskListRow = TaskDto | TaskOverviewItem

export const TASK_LANGUAGE_TRACKS = [
  { id: "python", label: "Python" },
  { id: "pascal", label: "Pascal" },
  { id: "cpp", label: "C++" },
  { id: "csharp", label: "C#" },
  { id: "java", label: "Java" },
] as const

function normalizeTrackId(raw: string | null | undefined): string {
  const value = String(raw || "").trim().toLowerCase()
  if (value === "c#" || value === "cs") return "csharp"
  if (value === "c++") return "cpp"
  if (value === "py") return "python"
  return value
}

function isAlgoV4Slot(task: TaskListRow): boolean {
  const slotId = String(
    (task as TaskOverviewItem).slot_id ||
      (task as TaskOverviewItem).pedagogical_slot_id ||
      "",
  )
  return /^(py_|pas_|cpp_|cs_|java_)\d+$/i.test(slotId)
}

function availableTrackIds(task: TaskListRow): Set<string> {
  const tracks = (task as TaskOverviewItem).available_language_tracks
  if (Array.isArray(tracks) && tracks.length > 0) {
    return new Set(tracks.map((track) => normalizeTrackId(String(track))))
  }
  if (isAlgoV4Slot(task)) {
    return new Set(TASK_LANGUAGE_TRACKS.map((track) => track.id))
  }
  const single =
    normalizeTrackId(
      (task as TaskOverviewItem).target_language ||
        (task as TaskOverviewItem).language ||
        task.language ||
        task.source_language ||
        (task.lang as string | undefined),
    ) || "python"
  return new Set([single])
}

export interface LanguageMatrixEntry {
  id: string
  label: string
  state: LanguageTrackState
  available: boolean
}

export function buildLanguageMatrix(task: TaskListRow | null | undefined): LanguageMatrixEntry[] {
  if (!task) {
    return TASK_LANGUAGE_TRACKS.map((track) => ({
      ...track,
      state: "todo" as const,
      available: false,
    }))
  }

  const available = availableTrackIds(task)
  const apiStates = (task as TaskOverviewItem).language_track_states ?? {}
  const hasApiStates = Object.keys(apiStates).length > 0
  const globalSolved = Boolean(task.solved)
  const globalAttempted = Boolean(task.attempted)

  return TASK_LANGUAGE_TRACKS.map((track) => {
    const fromApi = apiStates[track.id] as LanguageTrackState | undefined
    if (fromApi === "solved" || fromApi === "attempted" || fromApi === "todo") {
      return { ...track, state: fromApi, available: available.has(track.id) }
    }

    const isAvailable = available.has(track.id)
    if (hasApiStates || !isAvailable) {
      return { ...track, state: "todo" as const, available: isAvailable }
    }

    if (globalSolved) {
      return { ...track, state: "solved" as const, available: true }
    }
    if (globalAttempted) {
      return { ...track, state: "attempted" as const, available: true }
    }
    return { ...track, state: "todo" as const, available: true }
  })
}

function relevantMatrixEntries(matrix: LanguageMatrixEntry[]): LanguageMatrixEntry[] {
  const availableEntries = matrix.filter((entry) => entry.available)
  return availableEntries.length > 0 ? availableEntries : matrix.slice(0, 1)
}

export function aggregateLanguageTrackStatus(
  task: TaskListRow | null | undefined,
): LanguageTrackState {
  const matrix = buildLanguageMatrix(task)
  const pool = relevantMatrixEntries(matrix)
  const solvedCount = pool.filter((entry) => entry.state === "solved").length
  if (solvedCount === pool.length && solvedCount > 0) return "solved"
  if (solvedCount > 0 || pool.some((entry) => entry.state === "attempted")) return "attempted"
  return "todo"
}

export function languageStatusLabel(state: LanguageTrackState): string {
  if (state === "solved") return "пройдено"
  if (state === "attempted") return "в процессе"
  return "не начато"
}
