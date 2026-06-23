/**
 * Analytics and recommendations API DTO shapes — OpenAPI aliases where typed.
 */

import type { ApiSchema } from "./openapi"
import type {
  LegacyRecommendationItem,
  SkillProgressRow,
  StudentRecommendations,
} from "@/shared/utils/studentRecommendations"

export type NextRecommendationDto = ApiSchema["NextRecommendationResponse"]
export type CatalogNavigationDto = ApiSchema["CatalogNavigationResponse"]
export type AssignmentSetDto = ApiSchema["AssignmentSetResponse"]
export type AssignmentSetItem = ApiSchema["AssignmentSetItemResponse"]

export type StudentAnalyticsDto = ApiSchema["StudentAnalyticsResponse"]
export type TeacherAnalyticsDto = ApiSchema["TeacherAnalyticsResponse"]
export type TeacherSubmissionsListDto = ApiSchema["TeacherSubmissionsListResponse"]
export type TeacherSubmissionDetailDto = ApiSchema["TeacherSubmissionDetailResponse"]

export type AnalyticsOverview = ApiSchema["AnalyticsOverviewResponse"]
export type AnalyticsLanguageRow = ApiSchema["AnalyticsLanguageRowResponse"]
export type AnalyticsStructureRow = ApiSchema["AnalyticsStructureRowResponse"]
export type AnalyticsActivityRow = ApiSchema["AnalyticsActivityRowResponse"]
export type AnalyticsPerTaskRow = ApiSchema["AnalyticsPerTaskRowResponse"]
export type AnalyticsErrorBreakdownRow = ApiSchema["AnalyticsErrorBreakdownResponse"]
export type DisplayTcSkillRow = ApiSchema["DisplayTcSkillRowResponse"]
export type TcTaskRecommendation = ApiSchema["TcTaskRecommendationResponse"]

export type { SkillProgressRow, StudentRecommendations, LegacyRecommendationItem }
