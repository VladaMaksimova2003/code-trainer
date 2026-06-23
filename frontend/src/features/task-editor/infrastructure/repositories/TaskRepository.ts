import type {
  AssignmentApiRequest,
  CreatedTask,
  ITaskRepository,
} from "@/features/task-editor/application/ports/ITaskRepository"
import { httpClient } from "@/features/task-editor/infrastructure/api/httpClient"

export class TaskRepository implements ITaskRepository {
  async createTask(request: AssignmentApiRequest): Promise<CreatedTask> {
    const res = await httpClient.post<{
      task_id: number
      assignment_type: string
    }>("/tasks/assignments/", request)
    return {
      taskId: res.data.task_id,
      assignmentType: res.data.assignment_type,
    }
  }
}
