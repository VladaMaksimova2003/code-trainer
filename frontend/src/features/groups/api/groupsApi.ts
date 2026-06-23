import { api } from "@/shared/api"
import { isMockApiEnabled } from "@/mocks/config"
import { mockHandlers } from "@/mocks/mockHandlers"
import type {
  GroupDashboardDto,
  GroupDto,
  GroupInvitationDto,
  GroupWorkspaceDto,
  StudentAssignedCatalogSummaryDto,
  StudentJoinedGroupOverviewDto,
  StudentTasksProgressDto,
} from "@/shared/types/groups"

export const listMyTeacherGroups = async (): Promise<GroupDto[]> => {
  const res = await api.get("/groups/mine")
  return res.data as GroupDto[]
}

export const createTeacherGroup = async (payload: Record<string, unknown>): Promise<GroupDto> => {
  const res = await api.post("/groups", payload)
  return res.data as GroupDto
}

export const deleteTeacherGroup = async (groupId: number | string): Promise<void> => {
  await api.delete(`/groups/${groupId}`)
}

export const generateGroupInvitation = async (
  groupId: number | string,
  payload: Record<string, unknown> = {},
): Promise<GroupInvitationDto> => {
  const res = await api.post(`/groups/${groupId}/invitations`, payload)
  return res.data as GroupInvitationDto
}

export const listJoinedGroups = async (): Promise<GroupDto[]> => {
  const res = await api.get("/groups/joined")
  return res.data as GroupDto[]
}

export const joinGroupByCode = async (code: string): Promise<GroupDto> => {
  const res = await api.post("/groups/join", { code })
  return res.data as GroupDto
}

export const getGroupDashboard = async (
  groupId: number | string,
  params: Record<string, unknown> = {},
): Promise<GroupDashboardDto> => {
  const res = await api.get(`/groups/${groupId}/dashboard`, { params })
  return res.data as GroupDashboardDto
}

export const assignCatalogToGroup = async (
  groupId: number | string,
  payload: Record<string, unknown>,
): Promise<Record<string, unknown>> => {
  const res = await api.post(`/groups/${groupId}/catalogs`, payload)
  return res.data as Record<string, unknown>
}

export const listJoinedGroupsOverview = async (): Promise<StudentJoinedGroupOverviewDto[]> => {
  if (isMockApiEnabled() && mockHandlers.listJoinedGroupsOverview) {
    return mockHandlers.listJoinedGroupsOverview() as Promise<StudentJoinedGroupOverviewDto[]>
  }
  const res = await api.get("/groups/joined/overview")
  return res.data as StudentJoinedGroupOverviewDto[]
}

export const listAssignedCatalogs = async (): Promise<StudentAssignedCatalogSummaryDto[]> => {
  const res = await api.get("/groups/joined/assigned-catalogs")
  return res.data as StudentAssignedCatalogSummaryDto[]
}

export const getMyGroupWorkspace = async (groupId: number | string): Promise<GroupWorkspaceDto> => {
  const res = await api.get(`/groups/${groupId}/workspace`)
  return res.data as GroupWorkspaceDto
}

export const getMyGroupCatalogs = async (groupId: number | string): Promise<Record<string, unknown>> => {
  const res = await api.get(`/groups/${groupId}/my-catalogs`)
  return res.data as Record<string, unknown>
}

export const getStudentGroupTasksProgress = async (
  groupId: number | string,
  studentId: number | string,
): Promise<StudentTasksProgressDto> => {
  const res = await api.get(`/groups/${groupId}/students/${studentId}/tasks-progress`)
  return res.data as StudentTasksProgressDto
}
