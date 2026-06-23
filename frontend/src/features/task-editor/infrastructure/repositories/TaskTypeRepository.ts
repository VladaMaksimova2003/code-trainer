import type {
  ITaskTypeRepository,
  TaskTypeOption,
} from "@/features/task-editor/application/ports/ITaskTypeRepository"
import { httpClient } from "@/features/task-editor/infrastructure/api/httpClient"

export class TaskTypeRepository implements ITaskTypeRepository {
  async fetchTypes(): Promise<TaskTypeOption[]> {
    const res = await httpClient.get<{ types: TaskTypeOption[] }>("/tasks/types")
    return res.data.types ?? []
  }
}
