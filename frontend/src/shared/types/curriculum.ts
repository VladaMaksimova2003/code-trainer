/**
 * Curriculum API DTO shapes — aliases to OpenAPI component schemas.
 */

import type { ApiSchema } from "./openapi"

export type CurriculumNextDto = ApiSchema["CurriculumGlobalNextResponse"]

export type PlatformCourseSummaryDto = {
  title: string
  description?: string
  author_user_id?: number | null
  author_name?: string | null
}

export type CurriculumCollectionsDto = ApiSchema["CurriculumCollectionsViewResponse"] & {
  platform_course?: PlatformCourseSummaryDto | null
}
export type CurriculumShowcaseStudentDto = ApiSchema["PascalShowcaseStudentViewResponse"]
export type CurriculumShowcaseNextDto = ApiSchema["PascalShowcaseNextResponse"]
export type CurriculumCollectionNavigationDto = ApiSchema["CurriculumCollectionNavigationResponse"]

export type CurriculumNextTaskRef = ApiSchema["CurriculumNextTaskRef"]
export type CurriculumCollectionRef = ApiSchema["CurriculumCollectionRef"]
export type CurriculumProgressSummary = ApiSchema["CurriculumProgressSummary"]
export type CurriculumCollectionSummary = ApiSchema["CurriculumCollectionSummary"]
