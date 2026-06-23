import { api } from "@/shared/api"
import { isMockApiEnabled } from "@/mocks/config"
import { mockHandlers } from "@/mocks/mockHandlers"
import type {
  StudentAnalyticsDto,
  StudentRecommendations,
  TeacherAnalyticsDto,
  TeacherSubmissionDetailDto,
  TeacherSubmissionsListDto,
} from "@/shared/types/analytics"

export const getStudentAnalytics = async (): Promise<StudentAnalyticsDto> => {
  if (isMockApiEnabled()) return mockHandlers.getStudentAnalytics() as Promise<StudentAnalyticsDto>
  const res = await api.get("/student/analytics")
  return res.data as StudentAnalyticsDto
}

export const getStudentRecommendations = async (): Promise<StudentRecommendations> => {
  if (isMockApiEnabled() && mockHandlers.getStudentRecommendations) {
    return mockHandlers.getStudentRecommendations() as Promise<StudentRecommendations>
  }
  const res = await api.get("/student/recommendations")
  return res.data as StudentRecommendations
}

export const getTeacherAnalytics = async (): Promise<TeacherAnalyticsDto> => {
  const res = await api.get("/teacher/analytics")
  return res.data as TeacherAnalyticsDto
}

export const getTeacherSubmissions = async (
  params: Record<string, unknown> = {},
): Promise<TeacherSubmissionsListDto> => {
  const res = await api.get("/teacher/submissions", { params })
  return res.data as TeacherSubmissionsListDto
}

export const getTeacherSubmissionDetail = async (
  submissionId: number | string,
): Promise<TeacherSubmissionDetailDto> => {
  const res = await api.get(`/teacher/submissions/${submissionId}`)
  return res.data as TeacherSubmissionDetailDto
}
