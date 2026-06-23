import { formatTaskTypeLabel } from "@/shared/types/taskLabels"
import { getLanguageLabel } from "@/shared/config/languages"
import type { TaskDto } from "@/shared/types/task"
import type { TaskOverviewItem } from "@/shared/types/taskOverview"
import type { TestCaseResult } from "@/shared/types/execution"
import {
  aggregateLanguageTrackStatus,
  type TaskListRow,
} from "@/features/student/utils/languageTrackProgress"

export type TaskStudentStatus = "solved" | "attempted" | "todo"

export function taskStudentStatus(task: TaskListRow | null | undefined): TaskStudentStatus {
  return aggregateLanguageTrackStatus(task)
}

export function taskLanguageLabel(task: TaskListRow | null | undefined): string {
  if (!task) return "—"
  const tracks = (task as TaskOverviewItem).available_language_tracks
  const slotId = String(
    (task as TaskOverviewItem).slot_id ||
      (task as TaskOverviewItem).pedagogical_slot_id ||
      "",
  )
  const isAlgoV4 = /^(py_|pas_|cpp_|cs_|java_)\d+$/i.test(slotId)
  if (isAlgoV4) {
    return ["Python", "Pascal", "C++", "C#", "Java"].join(", ")
  }
  const target =
    (task as TaskOverviewItem).target_language ||
    (task as TaskOverviewItem).language ||
    task.language ||
    task.source_language ||
    (task.lang as string | undefined)
  if (Array.isArray(tracks) && tracks.length > 1) {
    return tracks.map((track) => getLanguageLabel(String(track)) || String(track)).join(", ")
  }
  const from =
    (task.language_from as string | undefined) ||
    target ||
    task.source_language ||
    (task.lang as string | undefined)
  const to = task.language_to as string | undefined
  if (from && to && from !== to) {
    const fromLabel = getLanguageLabel(from) || from
    const toLabel = getLanguageLabel(to) || to
    return `${fromLabel} → ${toLabel}`
  }
  const lang = from || to
  if (!lang) return "—"
  return getLanguageLabel(lang) || lang
}

export function buildTaskTypeOptions(taskTypes: string[] = []): { id: string; label: string }[] {
  const normalized = Array.isArray(taskTypes) ? taskTypes : []
  const ids = normalized.length
    ? normalized
    : ["task_translate_full_program", "task_flowchart_to_code", "algorithm"]
  return ids.map((id: unknown) => ({
    id,
    label: formatTaskTypeLabel(id),
  }))
}

interface AssignmentSetLike {
  id?: number | string
  name?: string
  title?: string
  items?: Array<{ solved?: boolean }>
  tasks?: Array<{ solved?: boolean }>
  total_tasks?: number
  total?: number
  solved_count?: number
  solved?: number
  deadline_at?: string | null
  deadlineAt?: string | null
  [key: string]: unknown
}

export interface AssignmentSetCardModel {
  id: number | string | undefined
  name: string
  total: number
  solved: number
  color: "purple" | "lime"
  deadlineAt: string | null
  raw: AssignmentSetLike
}

export function mapAssignmentSetCard(set: AssignmentSetLike, index = 0): AssignmentSetCardModel {
  const items = set.items || set.tasks || []
  const total =
    typeof set.total_tasks === "number"
      ? set.total_tasks
      : set.total ?? items.length ?? 0
  const solved =
    typeof set.solved_count === "number"
      ? set.solved_count
      : set.solved ??
        items.filter((i: unknown) => i.solved).length ??
        0
  return {
    id: set.id,
    name: set.name || set.title || `Сборник #${set.id}`,
    total: Math.max(total, 0),
    solved,
    color: index % 2 === 1 ? "purple" : "lime",
    deadlineAt: set.deadline_at || set.deadlineAt || null,
    raw: set,
  }
}

export function submissionUiStatus(item: {
  success?: boolean
  status?: string
}): "accepted" | "failed" | "reviewing" {
  if (item.success === true) return "accepted"
  if (item.success === false) return "failed"
  const st = String(item.status || "").toLowerCase()
  if (st === "running" || st === "queued") return "reviewing"
  return "reviewing"
}

export type { TestCaseResult }
