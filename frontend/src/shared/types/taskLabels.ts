/**
 * Single source of truth for task / assignment type display labels.
 * API type ids are unchanged — UI strings only.
 */

import type { TaskDto } from "@/shared/types/task"

/** Pedagogical activity labels shown to students instead of raw assignment types. */
export const CURRICULUM_ACTION_LABELS: Record<string, string> = {
  assemble: "Собрать",
  implement: "Написать",
  debug: "Исправить",
  translate: "Написать",
  analyze: "Разобрать код",
  recognize: "Распознать",
}

export const TASK_TYPE_LABELS: Record<string, string> = {
  task_build_from_blocks: "Собрать",
  block_reorder: "Собрать",
  block_reorder_task: "Собрать",
  code_assembly: "Собрать",
  task_translate_snippet: "Написать",
  task_translate_full_program: "Написать",
  translation: "Написать",
  translation_task: "Написать",
  task_flowchart_to_code: "Блок-схема в код",
  blocks: "Блок-схема в код",
  diagram: "Блок-схема в код",
  diagram_task: "Блок-схема в код",
  algorithm: "Алгоритм",
  algorithm_task: "Алгоритм",
  base: "Базовое задание",
  base_task: "Базовое задание",
}

const BLOCK_ASSEMBLY_TYPES = new Set([
  "task_build_from_blocks",
  "block_reorder",
  "block_reorder_task",
  "code_assembly",
])

const TRANSLATION_TYPES = new Set([
  "task_translate_snippet",
  "task_translate_full_program",
  "translation",
  "translation_task",
])

export function resolveTaskActivityAction(
  task: Pick<TaskDto, "type" | "curriculum" | "primary_action"> | null | undefined,
): string {
  const action = String(
    (task?.curriculum as { action?: string } | undefined)?.action ||
      task?.primary_action ||
      "",
  ).toLowerCase()
  if (action) return action

  const type = String(task?.type || "")
  if (BLOCK_ASSEMBLY_TYPES.has(type)) return "assemble"
  if (TRANSLATION_TYPES.has(type)) return "implement"
  return ""
}

/** Student breadcrumb / catalog label — prefers curriculum action over assignment type. */
export function formatTaskActivityLabel(
  task: Pick<TaskDto, "type" | "curriculum" | "primary_action"> | null | undefined,
): string {
  if (!task) return "-"

  const action = resolveTaskActivityAction(task)
  if (action && CURRICULUM_ACTION_LABELS[action]) {
    return CURRICULUM_ACTION_LABELS[action]
  }

  const fromCurriculum = String(
    (task.curriculum as { action_label?: string } | undefined)?.action_label || "",
  ).trim()
  if (fromCurriculum) return fromCurriculum

  return formatTaskTypeLabel(task.type)
}

/** Student/catalog UI — fallback capitalizes underscore segments. */
export function formatTaskTypeLabel(type: string | null | undefined): string {
  if (!type) return "-"
  const key = String(type)
  if (TASK_TYPE_LABELS[key]) return TASK_TYPE_LABELS[key]
  return key
    .replace(/^task_/, "")
    .replace(/_task$/i, "")
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ")
}

/** Teacher editor UI — fallback uses spaced slug. */
export function formatAssignmentTypeLabel(assignmentTypeId: string): string {
  if (TASK_TYPE_LABELS[assignmentTypeId]) {
    return TASK_TYPE_LABELS[assignmentTypeId]
  }
  let slug = assignmentTypeId.replace(/^task_/, "").replace(/_task$/i, "")
  return slug.replace(/_/g, " ").trim() || assignmentTypeId
}

/** Normalize stored/public type to creatable assignment_type id. */
export function toAssignmentTypeId(raw: string): string {
  const map: Record<string, string> = {
    block_reorder: "task_build_from_blocks",
    code_assembly: "task_build_from_blocks",
    blocks: "task_flowchart_to_code",
    diagram: "task_flowchart_to_code",
    translation: "task_translate_full_program",
    algorithm: "algorithm",
  }
  if (raw.startsWith("task_")) return raw
  return map[raw] ?? raw
}

/** algorithm_task.py → algorithm; block_reorder_task.py → block reorder */
export function formatTaskModuleLabel(moduleName: string): string {
  let slug = moduleName.replace(/\.py$/i, "")
  if (slug.endsWith("_task")) {
    slug = slug.slice(0, -"_task".length)
  }
  return slug.replace(/_/g, " ").trim()
}
