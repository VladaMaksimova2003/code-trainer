import type { TaskDraft } from "@/features/task-editor/domain/entities"
import {
  getAssignmentEditorMode,
  requiresFlowGraph,
  requiresReferenceCode,
} from "@/features/task-editor/domain/assignmentRules"
import { validateFlowchartAssignment } from "@/features/task-editor/domain/validateFlowchartAssignment"

export interface ValidationResult {
  valid: boolean
  errors: string[]
}

export function validateAssignmentDraft(draft: TaskDraft): ValidationResult {
  const errors: string[] = []

  if (!draft.title.trim()) errors.push("Укажите название")
  if (!draft.description.trim()) errors.push("Укажите описание")
  if (!draft.languages.length) errors.push("Выберите язык программы")

  if (requiresReferenceCode(draft.type) && !draft.code.code.trim()) {
    errors.push("Укажите код программы")
  }

  if (requiresFlowGraph(draft.type)) {
    errors.push(...validateFlowchartAssignment(draft))
  }

  return { valid: errors.length === 0, errors }
}
