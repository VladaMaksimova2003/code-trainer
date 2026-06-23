import { TaskType } from "@/features/task-editor/domain/enums"

export type AssignmentEditorMode = "code" | "flowchart" | "blocks"

export function getAssignmentEditorMode(type: string): AssignmentEditorMode {
  const id = type as TaskType
  switch (id) {
    case TaskType.FLOWCHART_TO_CODE:
    case "blocks":
    case "diagram":
      return "flowchart"
    case TaskType.BUILD_FROM_BLOCKS:
    case "block_reorder":
    case "code_assembly":
      return "blocks"
    default:
      return "code"
  }
}

export function isTranslationAssignmentType(type: string): boolean {
  return (
    type === TaskType.TRANSLATE_SNIPPET ||
    type === TaskType.TRANSLATE_FULL_PROGRAM ||
    type === "translation" ||
    type === "translation_task"
  )
}

export function requiresReferenceCode(type: string): boolean {
  return getAssignmentEditorMode(type) !== "flowchart"
}

export function requiresFlowGraph(type: string): boolean {
  return getAssignmentEditorMode(type) === "flowchart"
}

export function inferIsDebugTaskFromTaskPayload(task: Record<string, unknown>): boolean {
  const taskType = String(task.task_type || task.type || "").toLowerCase()
  if (
    taskType === "task_build_from_blocks" ||
    taskType === "block_reorder" ||
    taskType === "code_assembly"
  ) {
    return false
  }

  const primary = String(task.primary_action || "").toLowerCase()
  if (primary === "debug") return true

  const codeExamples = task.code_examples
  if (!codeExamples || typeof codeExamples !== "object") return false

  if (Boolean((codeExamples as Record<string, unknown>).teacher_assembly_override)) {
    const showcaseOverride = (codeExamples as Record<string, unknown>).curriculum_showcase
    if (showcaseOverride && typeof showcaseOverride === "object") {
      const meta = showcaseOverride as Record<string, unknown>
      const action = String(meta.primary_action || meta.action || "").toLowerCase()
      if (action === "debug") return true
      if (action === "assemble" || action === "implement") return false
    }
  }

  const showcase = (codeExamples as Record<string, unknown>).curriculum_showcase
  if (!showcase || typeof showcase !== "object") return false

  const meta = showcase as Record<string, unknown>
  const taskFormat = String(meta.task_format || "")
  const action = String(meta.primary_action || meta.action || "").toLowerCase()
  return action === "debug" || taskFormat === "исправление" || taskFormat === "поиск_ошибки"
}

// Language options for task editor are loaded dynamically via useLanguages().
