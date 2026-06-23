import type { TaskTypeOption } from "@/features/task-editor/application/ports/ITaskTypeRepository"
import type { ITaskTypeRepository } from "@/features/task-editor/application/ports/ITaskTypeRepository"

export async function loadTaskTypes(
  repository: ITaskTypeRepository
): Promise<TaskTypeOption[]> {
  return repository.fetchTypes()
}
