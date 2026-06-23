import type { TaskDto } from "@/shared/types/task"

import {
  CURRICULUM_LANG_ORDER,
  getLearningLanguages,
  isCurriculumMirrorTask,
} from "@/features/task-solving/model/studentUiUtils"

const CURRICULUM_LANGS = new Set(CURRICULUM_LANG_ORDER)

function languageVariantsRecord(
  task: TaskDto,
): Record<string, { template?: string | null; blocks?: unknown[] }> {
  const raw = task.language_variants
  if (raw && typeof raw === "object" && !Array.isArray(raw)) {
    return raw as Record<string, { template?: string | null; blocks?: unknown[] }>
  }
  return {}
}

/** Same DB task row holds this language implementation — switch language without changing task id. */
export function taskSupportsLearningLanguageLocally(
  task: TaskDto | null | undefined,
  language: string,
): boolean {
  if (!task) return false
  const lang = String(language || "").toLowerCase()
  if (!lang || !CURRICULUM_LANGS.has(lang)) return false

  const codeExamples = task.code_examples as Record<string, unknown> | undefined
  if (task.teacher_assembly_override || codeExamples?.teacher_assembly_override) {
    return true
  }

  if (isCurriculumMirrorTask(task) && getLearningLanguages(task).includes(lang)) {
    return true
  }

  const variant = languageVariantsRecord(task)[lang]
  if (!variant || typeof variant !== "object") return false
  const template = String(variant.template ?? "").trim()
  const blocks = variant.blocks
  return Boolean(template || (Array.isArray(blocks) && blocks.length > 0))
}

/** Mirror task ids removed — language switches stay on the current task row. */
export function isCurriculumLanguageSwitch(
  _task: TaskDto | null | undefined,
  _nextLanguage: string,
  _currentLearningLanguage: string,
): boolean {
  return false
}
