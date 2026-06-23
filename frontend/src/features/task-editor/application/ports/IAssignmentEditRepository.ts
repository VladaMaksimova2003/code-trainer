export type AuthoringTaskDto = Record<string, unknown> & {
  title?: string
  description?: string
  difficulty?: string
  language?: string
  original_code?: string
  source_code?: string
  blocks?: string[]
  correct_order?: number[]
  template?: string | null
  flow_spec?: { nodes?: unknown[]; edges?: unknown[]; flow?: unknown[] }
  diagram?: { nodes?: unknown[]; edges?: unknown[]; flow?: unknown[] }
  test_cases?: unknown[]
  constructions?: string[]
  assignment_type?: string
  task_type?: string
  type?: string
}

export interface IAssignmentEditRepository {
  loadAuthoring(taskId: number): Promise<AuthoringTaskDto>
  updateBlockReorder(taskId: number, payload: Record<string, unknown>): Promise<void>
}
