import type { TaskDraft } from "@/features/task-editor/domain/entities"
import { AssignmentEditorRepository } from "@/features/task-editor/infrastructure/repositories/AssignmentEditorRepository"

const repo = new AssignmentEditorRepository()

export async function loadAssignmentForEdit(taskId: number): Promise<TaskDraft> {
  return repo.loadForEdit(taskId)
}
