import { api } from "@/shared/api/client"

export const createTeacher = async (payload: Record<string, unknown>) => {
  const res = await api.post("/admin/create-teacher", payload)
  return res.data
}

export const listTeacherRoleRequests = async (status: string | null = null) => {
  const res = await api.get("/admin/teacher-role-requests", {
    params: status ? { status } : {},
  })
  return res.data
}

export const approveTeacherRoleRequest = async (requestId: number | string) => {
  const res = await api.post(`/admin/teacher-role-requests/${requestId}/approve`)
  return res.data
}

export const rejectTeacherRoleRequest = async (requestId: number | string) => {
  const res = await api.post(`/admin/teacher-role-requests/${requestId}/reject`)
  return res.data
}
