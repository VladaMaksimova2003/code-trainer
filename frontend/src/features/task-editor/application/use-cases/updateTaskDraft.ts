import type { TaskDraft } from "@/features/task-editor/domain/entities"

export function updateTaskDraft(
  draft: TaskDraft,
  patch: Partial<TaskDraft>
): TaskDraft {
  return {
    ...draft,
    ...patch,
    version: draft.version + 1,
    updatedAt: new Date().toISOString(),
  }
}
