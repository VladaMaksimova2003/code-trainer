import { api } from "@/shared/api/client"

export const createCodeAssemblyTask = async (payload: Record<string, unknown>) => {
  const res = await api.post("/tasks/code-assembly", payload)
  return res.data
}

export const createAssignment = async (payload: Record<string, unknown>) => {
  const res = await api.post("/tasks/assignments/", payload)
  return res.data
}

export const getCodeAssemblyTask = async (taskId: number | string) => {
  const res = await api.get(`/tasks/code-assembly/${taskId}`)
  return res.data
}

export const getCodeAssemblyAuthorTask = async (taskId: number | string) => {
  const res = await api.get(`/tasks/code-assembly/${taskId}/author`)
  return res.data
}

export const updateCodeAssemblyTask = async (taskId: number | string, payload: Record<string, unknown>) => {
  const res = await api.put(`/tasks/code-assembly/${taskId}`, payload)
  return res.data
}
