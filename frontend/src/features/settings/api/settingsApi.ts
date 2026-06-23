import { api } from "@/shared/api"
import { getRefreshToken } from "@/shared/api/auth"
import type {
  AccountSettingsDto,
  LearningPreferencesDto,
  TeacherOverviewDto,
  TeacherSettingsDto,
} from "@/shared/types/settings"

export const getAccountSettings = async (): Promise<AccountSettingsDto> => {
  const res = await api.get("/settings/account")
  return res.data as AccountSettingsDto
}

export const updateAccountSettings = async (payload: Record<string, unknown>): Promise<AccountSettingsDto> => {
  const res = await api.patch("/settings/account", payload)
  return res.data as AccountSettingsDto
}

export const sendChangeEmailCode = async (email: string): Promise<void> => {
  await api.post("/settings/email/send-code", { email })
}

export const changePassword = async (payload: Record<string, unknown>): Promise<void> => {
  await api.post("/settings/change-password", payload)
}

export const logoutSession = async (): Promise<void> => {
  const refreshToken = getRefreshToken()
  if (!refreshToken) return
  await api.post("/settings/logout", { refresh_token: refreshToken })
}

export const logoutAllSessions = async (): Promise<void> => {
  await api.post("/settings/logout-all")
}

export const getLearningPreferences = async (): Promise<LearningPreferencesDto> => {
  const res = await api.get("/settings/learning")
  return res.data as LearningPreferencesDto
}

export const updateLearningPreferences = async (payload: Record<string, unknown>): Promise<LearningPreferencesDto> => {
  const res = await api.patch("/settings/learning", payload)
  return res.data as LearningPreferencesDto
}

export const getTeacherSettings = async (): Promise<TeacherSettingsDto> => {
  const res = await api.get("/settings/teacher")
  return res.data as TeacherSettingsDto
}

export const updateTeacherSettings = async (payload: Record<string, unknown>): Promise<TeacherSettingsDto> => {
  const res = await api.patch("/settings/teacher", payload)
  return res.data as TeacherSettingsDto
}

export const getTeacherOverview = async (): Promise<TeacherOverviewDto> => {
  const res = await api.get("/settings/teacher/overview")
  return res.data as TeacherOverviewDto
}
