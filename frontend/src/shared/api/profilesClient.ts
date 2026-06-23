import { isMockApiEnabled } from "@/mocks/config"
import { mockHandlers } from "@/mocks/mockHandlers"
import { api } from "@/shared/api/client"
import type { TaskDto } from "@/shared/types/task"

export const getMyTeacherProfile = async () => {
  const res = await api.get("/teacher/profile")
  return res.data
}

export const getStudentProfile = async () => {
  if (isMockApiEnabled()) return mockHandlers.getStudentProfile()
  const res = await api.get("/student/profile")
  return res.data
}

export const requestTeacherRole = async (message: string | null = null) => {
  const res = await api.post("/student/teacher-role-request", { message })
  return res.data
}

export const getTeacherProfile = async (teacherId: number | string) => {
  const res = await api.get(`/teacher/${teacherId}/profile`)
  return res.data
}

export const getTeacherTasksList = async (teacherId: number | string): Promise<TaskDto[]> => {
  const res = await api.get(`/teacher/${teacherId}/tasks`)
  return res.data.tasks ?? []
}

export const getTeacherActivity = async (teacherId: number | string) => {
  const res = await api.get(`/teacher/${teacherId}/activity`)
  return res.data
}
