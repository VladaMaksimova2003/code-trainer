import type { TaskDraft } from "@/features/task-editor/domain/entities"
import { saveAssignment } from "@/features/task-editor/application/use-cases/saveAssignment"
import type { ITaskRepository } from "@/features/task-editor/application/ports/ITaskRepository"

export async function createTask(
  repository: ITaskRepository,
  draft: TaskDraft
) {
  return saveAssignment(repository, draft)
}
