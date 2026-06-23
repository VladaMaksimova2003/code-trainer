export interface TaskTypeOption {
  id: string
  name: string
}

export interface ITaskTypeRepository {
  fetchTypes(): Promise<TaskTypeOption[]>
}
