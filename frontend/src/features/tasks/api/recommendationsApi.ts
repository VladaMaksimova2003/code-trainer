import { api } from "@/shared/api"
import { isMockApiEnabled } from "@/mocks/config"
import { mockHandlers } from "@/mocks/mockHandlers"
import type {
  AssignmentSetDto,
  CatalogNavigationDto,
  NextRecommendationDto,
} from "@/shared/types/analytics"

export const getNextRecommendation = async (
  currentTaskId: number | string | null = null,
): Promise<NextRecommendationDto | null> => {
  if (isMockApiEnabled()) return mockHandlers.getNextRecommendation(currentTaskId) as Promise<NextRecommendationDto | null>
  const params: Record<string, number | string> = {}
  if (currentTaskId != null) {
    params.current_task_id = currentTaskId
  }
  const res = await api.get("/student/recommendations/next", { params })
  return res.data as NextRecommendationDto | null
}

export const getCatalogNavigation = async (
  catalogId: number | string,
  currentTaskId: number | string | null = null,
): Promise<CatalogNavigationDto> => {
  if (isMockApiEnabled()) {
    return mockHandlers.getCatalogNavigation(catalogId, currentTaskId) as Promise<CatalogNavigationDto>
  }
  const params: Record<string, number | string> = {}
  if (currentTaskId != null) {
    params.current_task_id = currentTaskId
  }
  const res = await api.get(`/student/recommendations/catalogs/${catalogId}/navigation`, { params })
  return res.data as CatalogNavigationDto
}

export const listAccessibleAssignmentSets = async (): Promise<AssignmentSetDto[]> => {
  if (isMockApiEnabled()) return mockHandlers.listAccessibleAssignmentSets() as Promise<AssignmentSetDto[]>
  const res = await api.get("/assignment-sets")
  return res.data as AssignmentSetDto[]
}
