export interface CreatedTask {
  taskId: number
  assignmentType: string
}

export interface AssignmentApiRequest {
  assignment_type: string
  difficulty: string
  languages: string[]
  title: string
  description: string
  patterns: string[]
  test_cases: Array<{
    name?: string
    input: unknown
    expected_output: unknown
    description?: string
  }>
  payload: Record<string, unknown>
}

export interface ITaskRepository {
  createTask(request: AssignmentApiRequest): Promise<CreatedTask>
}
