import { api } from "@/shared/api"

/** Users */
export async function fetchAdminUsers(includeDeleted = false) {
  const res = await api.get("/admin/users", {
    params: { include_deleted: includeDeleted },
  })
  return res.data
}

export async function fetchAdminUser(userId) {
  const res = await api.get(`/admin/users/${userId}`)
  return res.data
}

export async function patchAdminUserBlocked(userId, blocked) {
  await api.patch(`/admin/users/${userId}/blocked`, { blocked })
}

export async function deleteAdminUser(userId) {
  await api.delete(`/admin/users/${userId}`)
}

export async function assignAdminUserRole(userId, role) {
  const res = await api.post(`/admin/users/${userId}/roles`, { role })
  return res.data
}

export async function removeAdminUserRole(userId, role) {
  const res = await api.delete(`/admin/users/${userId}/roles/${role}`)
  return res.data
}

/** Assignments */
export async function fetchAdminAssignments(includeDeleted = true) {
  const res = await api.get("/admin/assignments", {
    params: { include_deleted: includeDeleted },
  })
  return res.data
}

export async function patchAssignmentWorkflow(taskId, status) {
  await api.patch(`/admin/assignments/${taskId}/workflow-status`, { status })
}

export async function archiveAdminAssignment(taskId) {
  await api.post(`/admin/assignments/${taskId}/archive`)
}

export async function fetchAssignmentVersions(taskId) {
  const res = await api.get(`/admin/assignments/${taskId}/versions`)
  return res.data
}

export async function createAssignmentVersion(taskId) {
  const res = await api.post(`/admin/assignments/${taskId}/versions`)
  return res.data
}

export async function activateAssignmentVersion(taskId, versionId) {
  await api.post(`/admin/assignments/${taskId}/versions/${versionId}/activate`)
}

/** Statistics */
export async function fetchAdminStatistics() {
  const res = await api.get("/admin/statistics")
  return res.data
}

/** Teacher role requests */
export async function fetchTeacherRoleRequests(status = null) {
  const res = await api.get("/admin/teacher-role-requests", {
    params: status ? { status } : {},
  })
  return res.data
}

export async function approveTeacherRoleRequest(requestId) {
  const res = await api.post(`/admin/teacher-role-requests/${requestId}/approve`)
  return res.data
}

export async function rejectTeacherRoleRequest(requestId) {
  const res = await api.post(`/admin/teacher-role-requests/${requestId}/reject`)
  return res.data
}

/** Create teacher */
export async function createAdminTeacher(payload) {
  const res = await api.post("/admin/create-teacher", payload)
  return res.data
}

/** Create administrator */
export async function createAdminAccount(payload) {
  const res = await api.post("/admin/create-admin", payload)
  return res.data
}

/** Pedagogical display TC cards (tc_display_registry.json) */
export async function fetchAdminTcConcepts() {
  const res = await api.get("/admin/tc-concepts")
  return res.data
}

export async function fetchAdminTcConcept(conceptId: string) {
  const res = await api.get(`/admin/tc-concepts/${encodeURIComponent(conceptId)}`)
  return res.data
}

export async function patchAdminTcConcept(conceptId, patch) {
  const res = await api.patch(`/admin/tc-concepts/${conceptId}`, patch)
  return res.data
}

